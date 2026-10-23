"""Prototype: measure changed files without checking out either revision."""
import argparse
import datetime
import fcntl
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

import lizard
from lizard_languages import get_reader_for

LOG = Path.home() / '.local/share/lizard-complexity/usage.jsonl'
LIMITS = {'cyclomatic_complexity': 15, 'length': 1000, 'parameter_count': 100}


def run(repo, *args):
    return subprocess.check_output(args, cwd=repo, stderr=subprocess.PIPE).decode('utf-8', 'surrogateescape')


def revisions(repo, base, head):
    vcs = 'jj' if (repo / '.jj').is_dir() else 'git'
    if vcs == 'jj':
        # Snapshot once, then pin both revisions so later reads use the same tree.
        if head is None:
            run(repo, 'jj', '--no-pager', 'diff', '--name-only')
        def resolve(ref):
            ids = run(repo, 'jj', '--ignore-working-copy', 'log', '-r', ref,
                      '--no-graph', '-T', 'commit_id ++ "\\n"').splitlines()
            if len(ids) != 1:
                raise ValueError('Select one revision; pass --base for a merge.')
            return ids[0]
        return vcs, resolve(base or '@-'), resolve(head or '@')
    base = run(repo, 'git', 'rev-parse', '--verify', (base or 'HEAD') + '^{commit}').strip()
    head = run(repo, 'git', 'rev-parse', '--verify', head + '^{commit}').strip() if head else None
    return vcs, base, head


def changes(repo, vcs, base, head):
    if vcs == 'jj':
        template = 'status_char ++ "\\0" ++ source.path().display() ++ "\\0" ++ target.path().display() ++ "\\0"'
        fields = run(repo, 'jj', '--ignore-working-copy', 'diff', '--from', base,
                     '--to', head, '-T', template).split('\0')[:-1]
        return [(None if s == 'A' else old, None if s == 'D' else new)
                for s, old, new in zip(fields[::3], fields[1::3], fields[2::3])]
    args = ['git', 'diff', '--no-ext-diff', '--no-renames', '--name-status', '-z', base]
    fields = run(repo, *args, *([head] if head else []), '--').split('\0')[:-1]
    pairs = [(None if s == 'A' else p, None if s == 'D' else p)
             for s, p in zip(fields[::2], fields[1::2])]
    if head is None:
        pairs += [(None, p) for p in run(repo, 'git', 'ls-files', '--others',
                  '--exclude-standard', '-z').split('\0') if p]
    return pairs


def source(repo, vcs, ref, path):
    if ref is None:
        file = repo / path
        if file.is_symlink():
            return None
        return file.read_text(encoding='utf-8')
    if vcs == 'jj':
        return run(repo, 'jj', '--ignore-working-copy', 'file', 'show', '-r', ref,
                   'file:' + path)
    return run(repo, 'git', 'show', ref + ':' + path)


def measure(repo, vcs, ref, paths):
    functions, skipped, file_nloc = [], [], 0
    for path in paths:
        if not get_reader_for(path):
            skipped.append(path)
            continue
        text = source(repo, vcs, ref, path)
        if text is None or '\0' in text:
            skipped.append(path)
            continue
        info = lizard.analyze_file.analyze_source_code(path, text)
        file_nloc += info.nloc
        for f in info.function_list:
            functions.append({'file': path, 'name': f.name, 'line': f.start_line,
                              'ccn': f.cyclomatic_complexity, 'nloc': f.nloc,
                              'tokens': f.token_count, 'parameters': f.parameter_count,
                              'length': f.length,
                              'warning': any(getattr(f, k) > v for k, v in LIMITS.items())})
    summary = {'files': len(paths) - len(skipped), 'functions': len(functions),
               'warnings': sum(f['warning'] for f in functions), 'nloc': file_nloc,
               'tokens': sum(f['tokens'] for f in functions),
               'total_ccn': sum(f['ccn'] for f in functions),
               'worst_ccn': max((f['ccn'] for f in functions), default=0),
               'max_length': max((f['length'] for f in functions), default=0),
               'max_parameters': max((f['parameters'] for f in functions), default=0)}
    return summary, functions, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    parser.add_argument('--base', help='Git: HEAD. jj: @-. Select one revision.')
    parser.add_argument('--head', help='Git: working files, including untracked. jj: @.')
    args = parser.parse_args()
    record = {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'task': os.environ.get('TASK_ID') or str(Path.cwd()),
              'repo': str(Path(args.repo).resolve()), 'status': 'error',
              'file_count': 0, 'warning_count': None,
              'worst_ccn_before': None, 'worst_ccn_after': None,
              'lizard_version': importlib.metadata.version('lizard'), 'thresholds': LIMITS}
    try:
        location = Path(args.repo).resolve()
        jj_root = next((p for p in (location, *location.parents) if (p / '.jj').is_dir()), None)
        repo = jj_root or Path(run(location, 'git', 'rev-parse', '--show-toplevel').strip())
        record['repo'] = str(repo)
        vcs, base, head = revisions(repo, args.base, args.head)
        record.update(vcs=vcs, base=base, head=head or 'working-copy')
        pairs = changes(repo, vcs, base, head)
        record['file_count'] = len(pairs)
        before, old_funcs, old_skip = measure(repo, vcs, base, sorted({p for p, _ in pairs if p}))
        after, new_funcs, new_skip = measure(repo, vcs, head, sorted({p for _, p in pairs if p}))
        record.update(status='ok', before=before, after=after,
                      delta={k: after[k] - before[k] for k in before},
                      warning_count=after['warnings'], worst_ccn_before=before['worst_ccn'],
                      worst_ccn_after=after['worst_ccn'], skipped_before=old_skip, skipped_after=new_skip)
        for label, funcs in [('before', old_funcs), ('after', new_funcs)]:
            print(label + ' hotspots (top five; raw thresholds, no suppression):')
            for f in sorted(funcs, key=lambda f: (f['ccn'], f['nloc']), reverse=True)[:5]:
                print(json.dumps(f))
        for f in new_funcs:
            if f['warning']:
                print('warning: ' + json.dumps(f))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        record['error'] = str(error)
        if isinstance(error, subprocess.CalledProcessError):
            record['error'] += ': ' + error.stderr.decode(errors='replace')
    # One locked append per invocation, including no-op, unsupported, and failed runs.
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a') as log:
        fcntl.flock(log, fcntl.LOCK_EX)
        log.write(json.dumps(record, ensure_ascii=True) + '\n')
        log.flush()
    print(json.dumps(record, ensure_ascii=True))
    return 0 if record['status'] == 'ok' else 2


if __name__ == '__main__':
    sys.exit(main())
