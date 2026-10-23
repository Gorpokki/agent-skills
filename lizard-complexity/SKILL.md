---
name: lizard-complexity
description: Measure a fixed source scope, simplify one safe candidate, validate it, and repeat the Lizard measurement workflow until targets are met or no safe improvement remains. Use for code architecture, design, writing, and review work.
---

# Lizard complexity wiggle loop

## Ordered workflow

1. **Set scope and checks.** Load ponytail and the task's required review skill. Record the task ID, Lizard version, source paths, immutable comparison base, and required behavior checks. For dedicated cleanup, scan the authorized source tree, such as `src`. For a narrow ticket, scan its containing source module. Call that module a module; its average is not a codebase average. Keep edit authority within the ticket. Keep these paths and exclusions fixed across passes. Include added files beneath those paths. For prose or unsupported-only work, report skipped files and review manually. Stop measurement rounds. For design without source, review the proposed structure directly. Do not claim measured improvement.

2. **Measure before choosing an approach.** Run native Lizard on the scope, even when the repository diff is empty. Run the existing helper once for the initial change comparison, with `TASK_ID` set. An empty change comparison is valid baseline metadata. It is not a scope measurement. With Git working edits, omit `--head`; `--head HEAD` excludes those edits. For reviews, measure the actual base and head. Review authority does not permit automatic source edits. Record unsupported formats and exclusions. No parsed functions means unavailable coverage, not a passing target.

3. **Select one useful change.** Implement the assigned behavior first when the task requires implementation. Measure that candidate before starting cleanup. Rank warning functions, files above average 3, and the highest-CCN functions. Inspect the selected function, its callers, and medium-complexity neighbors. Choose one coherent simplification within authorized scope. State its expected benefit before editing. Reconsider warning-free code when the average or local control flow remains poor.

4. **Apply ponytail.** Remove speculative code, reuse repository code, then prefer standard and native facilities. Next, use installed dependencies, a clear single expression, or the minimum required code. Preserve behavior, generated output, interfaces, required tests, and accessibility. Preserve every security measure, trust-boundary validation, and error handler that prevents data loss. Use a focused helper only when it clarifies one responsibility. A lower average from extra wrappers or trivial functions does not establish improvement. Preserve the same test and generated-code coverage. Add no suppressions or generated markers to obtain a passing result.

5. **Measure the candidate.** Repeat the same scope scan and helper comparison after the change. Compare it with both the initial scope baseline and the preceding candidate. Record the affected function's CCN, NLOC, tokens, parameters, and physical length. Also inspect total code and function count. A necessary test increase is acceptable when explained. Keep changes only when they improve actual readability or remove needless control flow. Treat native Lizard exit 1 as valid warning evidence. Treat helper exit 2 as a measurement failure.

6. **Run checks last.** Run required formatting, type, and lint checks, then the required behavior tests. Use existing checks when they cover the change. Add one focused regression check when behavior needs proof. A failed check requires repair or removal of this worker's candidate changes. Preserve unrelated work. After every repair, repeat measurement and checks. Commit verified chunks only when the parent task permits commits, using its version-control and message rules.

7. **Choose the next pass or stop.** Use the stop table below after tests pass. If targets remain unmet and another safe candidate exists, return to step 3 automatically. Re-rank from the latest scope scan. Do not stop after one improvement solely because its warnings disappear. Repeat within the current worker. Existing supervision owns any later context handoff. Create no nested agent runner, shell daemon, scheduler, or new loop framework.

8. **Report once.** State the stop reason, scope, exclusions, version, base, and number of accepted passes. Give scope baseline→final averages, per-file exceptions, and raw warning counts. Separately give helper baseline→final worst CCN, warnings, NLOC, tokens, functions, and maximum parameters. Name the useful changes and link their diffs or exact function locations. Explain retained increases and remaining difficult functions. State the final test command and result. Each pass record needs only its selected function, metric change, diff reference, and test result. Keep scope snapshots in task evidence. Existing helper calls retain their existing audit-log contract.

## Stop rules

These are local operating rules. The task's explicit targets take precedence. Otherwise, use scope average CCN ≤2, each file average CCN ≤3, and zero raw warnings as default targets. The ≤2 cutoff makes the article's approximate preference checkable. It is an adaptation, not a quoted article threshold. Use unrounded averages. Native tables round to one decimal and can hide a value just above 3.

| Condition | Action and result |
|---|---|
| Targets pass; coverage is valid; required checks pass | Stop: **target met**. Include any useful remaining observations. |
| Targets fail; another safe simplification exists | Select the next candidate and repeat. |
| Targets fail; all remaining candidates need weaker safeguards, worse readability, or edits outside authority | Stop: **no safe improvement remains**. List retained values and reasons. The target remains unmet. |
| A behavior check or required tool fails | Repair or withdraw the candidate. Apply the parent task's blocker policy when repair cannot proceed. |
| No supported functions, no source for a design, or unsupported-only work | Stop measurements: **coverage unavailable**. Review manually and report the limit. |
| The task ends, the supervisor stops work, or an explicit budget ends | Preserve verified work and report remaining targets. Do not declare metric success. |

## Commands and helper scope

Keep installed Lizard **1.24.1**. Matching the article's workflow does not require downgrading to **1.21.2**. Run from the repository root. Substitute the fixed source paths and the recorded comparison base.

```sh
lizard src
TASK_ID=<task-id> "$(uv tool dir)/lizard/bin/python" \
  "path/to/lizard-complexity/measure.py" --base <immutable-base>
```

The first command supplies function rankings, file averages, and scope totals. Use this exact readout for stop decisions. Pass the same scope paths after `-`:

```sh
PYTHONDONTWRITEBYTECODE=1 "$(uv tool dir)/lizard/bin/python" -B - src <<'PY'
import json, sys, lizard
infos = list(lizard.analyze(sys.argv[1:]))
funcs = [f for i in infos for f in i.function_list]
limits = {'cyclomatic_complexity': 15, 'length': 1000, 'nloc': 1000000, 'parameter_count': 100}
print(json.dumps({
    'files': len(infos), 'functions': len(funcs),
    'avg_ccn': sum(f.cyclomatic_complexity for f in funcs) / len(funcs) if funcs else None,
    'file_avg_ccn': {i.filename: i.average_cyclomatic_complexity for i in infos if i.function_list},
    'raw_warnings': sum(any(getattr(f, k) > v for k, v in limits.items()) for f in funcs),
}))
PY
```

Scope average means total function CCN divided by total function count. It does not mean the average of file averages. Files without functions remain in coverage counts. They provide no function-average evidence. Raw warning counts ignore inline warning forgiveness and whitelist entries. Generated-code parsing exclusions still affect coverage and must remain visible.

**Change to `measure.py`: none.** Its current changed-file comparison and locked log remain useful. Do not add a source-tree mode, loop state, automatic edits, thresholds framework, or extra dependencies. The exact readout is a short skill command using the installed analyzer. A logging-location change needs separate justification.

## References and limits

See [Simplifying AI-Generated Code with Lizard](https://rng.md/posts/simplifying-ai-generated-code-with-lizard/) and [Wiggum Loop](https://rng.md/posts/wiggum-loop/) for the repeated measure-simplify-measure idea. The articles do not supply the local stalled-improvement rule or exact average cutoff.

CCN means cyclomatic complexity: an estimate of independent control-flow paths in a function. NLOC means lines of code without comments. The helper reports raw threshold crossings, including functions with suppression comments. Supported and unsupported formats depend on the installed reader; report skipped files and inspect them manually. Lizard uses partial parsers, so macros, unusual syntax, generated-code markers, and nesting can distort results.

Each helper invocation appends one locked JSON line to a user-local usage log, recording its existing audit fields. Empty and unsupported-only diffs still produce a line.
