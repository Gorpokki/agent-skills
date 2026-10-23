---
name: grill-with-reading
description: Grill a design after the user reads the original sources and takes a quiz on the core ideas. Use when a design decision rests on research the user has not read, or the user asks for required reading or a quiz before grilling.
---

The user decides better after reading the **originals**: the papers, specs, docs and repos behind the research. Your job is to find them, teach their core ideas, check the learning, then grill.

## 1. Trace the research to its originals

Reread the existing research only to find its sources. Trace each claim the coming decisions rest on to the original that states it. When no research exists, find the originals yourself. Open each one and copy the exact section titles you will assign.

Done when every claim you will teach has an original, a verified section, and a label: observed in the source, your inference, or untested here.

## 2. Draft the design tree

Map the decisions as `grilling` does, from your own reading. Then pick the **core ideas**: the concepts those decisions depend on. Teach only those.

## 3. Build one learning page

One self-contained HTML page, top to bottom:

1. **Required reading.** For each original: link, exact sections, reading order, and one line on why it matters for the coming decisions. Put optional depth in a separate list below.
2. **Explainer.** Use the Background and Intuition shape of `explain-diff-html`: background for beginners, then each core idea with a worked example and a diagram. Add a code walkthrough only when the topic is code.
3. **Quiz.** One item per core idea. Write scenario items that apply the reading; each has exactly one answer the assigned sections prove. Follow the quiz rules in the `teach` skill: equal-length choices, varied answer position, instant feedback. After each click, explain why every choice is right or wrong and link the proving section.

The quiz answers stay on the page, with the user. Quiz answers check learning; design approvals come only from grilling.

Done when every quiz item maps to an assigned section and every core idea has an item.

## 4. Wait, then grill

Send the page and wait until the user says they are done. Then call the Skill tool for `grilling` with your design tree.

When a later question needs an idea the reading did not cover, explain it inside that question with a link to its original.
