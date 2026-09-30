---
name: pr-review
description: Bug- and improvement-focused review of a change set that produces a triaged report .md (Critical = bugs, Medium = improvements, Low = cleanup). Report-only — never edits code. Use to review a PR or a body of changes without entering a fix loop.
---

# pr-review

## 1. Resolve the change set
- If a git repo exists: diff the branch against its base (e.g. `git diff main...HEAD`; confirm the base with the user if unsure).
- Else: use the active episode's `## Files touched`.
- Else: ask the user which files/range to review.
Local only — do not use `gh` or post anywhere.

## 2. Dispatch focused reviewers
Dispatch ~3 subagents in parallel, each reviewing the change set against `docs/CODE_STANDARDS.md` + `docs/memory/PROCEDURES.md`/`GUARDRAILS.md`/`LESSONS.md`/`SEMANTICS.md`:
- **bug-hunting** (highest priority) — correctness, edge cases, regressions.
- **improvements** — design / readability / robustness / testing opportunities.
- **cleanup** — dead code, redundancy, minor naming/formatting.
Each returns findings as `file:line` + a concrete recommendation.

## 3. Compile a triaged report
Group findings by priority: **Critical = bug fixes · Medium = improvements · Low = cleanup**. Within each, list `file:line` + recommendation.

## 4. Write the report
Write to `docs/reviews/{date}-{slug}-pr-review.md` with frontmatter `tags: [review]` and a header naming the change set reviewed. If an episode is active, add a pointer to the report in its `## Log`. Do NOT edit any code.
