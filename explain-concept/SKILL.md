---
name: explain-concept
description: Explain a concept to the user with a quick inline visual, then a concept page with examples from the user's own projects and a quiz, served in Plannotator.
disable-model-invocation: true
argument-hint: "Which concept? Leave empty for the one just discussed."
---

Explain the concept named in the arguments. With no arguments, explain the concept of the last answer.

## 1. Show it inline first

Load `show-me` and give the smallest view that makes the key point clear: one diagram, table, or sketch in chat. Stop here if the user only wants the quick answer.

## 2. Ground it in the user's projects

Find which of the user's projects the concept touches. Take every example from those projects: real files, real names, real counts.

- Compute numbers from the files. Cite `path:line` or the commit.
- Read decision records (ADRs) and tickets that use the concept. A live case where the concept matters, such as a bug or an open ticket, is the best example.
- Mark anything you did not check as "not verified".

## 3. Write the concept page

Load `explain-diff-html`. Use its format, but swap the Code section for examples:

- **Background**: a beginner part the reader can skip, then the narrow part for this project. Say here what other fields call the concept (math, software engineering, the project's domain).
- **Idea**: one diagram family, reused. Make it interactive when a click shows the idea better than text.
- **Examples**: the real data from step 2, with the live case.
- **Quiz**: one multiple-choice question per key idea, at least three, with feedback for every answer. Follow the quiz rules in `teach`: options of the same length, no clues in the format.

Write in ASD-STE100 Simplified Technical English. Explain each term where it first appears, inline or on hover; never only in a glossary at the top. Light theme. One self-contained HTML file that works on a phone. Save it in a concepts folder outside the project repository, using the date and concept slug in its filename.

## 4. Deliver it in Plannotator

Run `plannotator annotate <file> --browser none` in the background. Give the user the printed URL. Never open or focus a browser yourself. Keep the server up until the user closes it or sends feedback. Handle the feedback as `plannotator-annotate` says.

## 5. Capture the terms

Load `domain-modeling`. When the concept gives the project a new term, suggest a `GLOSSARY.md` entry in that project's format. The user decides; write it only on a yes. A change in a repo follows the repo's own ticket and PR rules.

Hand over to `teach` only when the user asks for a longer course. Then use this page as its first lesson.
