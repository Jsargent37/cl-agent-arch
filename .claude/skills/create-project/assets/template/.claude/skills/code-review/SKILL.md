---
name: code-review
description: Structured review of the current task's changes against the project's CODE_STANDARDS and knowledge registries, with an explicit PASS/FAIL gate per category. Reports issues and offers to apply the safe fixes on confirmation. Use before testing, closeout, or any time a review is requested.
---

# code-review

## 1. Resolve the change set
- If a git repo exists: `git diff` and `git diff --staged` (confirm the base branch with the user
  if unsure).
- Else: use the active episode's `## Files touched`.
- Else: ask the user which files to review.

## 2. Review
Check the changed code against `docs/CODE_STANDARDS.md` (DRY/SOLID/KISS/OOP, ≤50 LoC functions,
naming, comments ≤2 lines, public-only docstrings, dead code, logging/error handling, tests, doc
currency) plus `docs/memory/PROCEDURES.md`, `docs/memory/GUARDRAILS.md`, `docs/memory/LESSONS.md`,
and `docs/memory/SEMANTICS.md`. Keep it scoped to the diff, not the whole codebase. Also confirm
the implementation matches the task's stated goal/plan, and that no unrelated changes are included.

## 3. Report

```
## Code Review Report

### Goal Alignment
Status: PASS | FAIL
- [action item if FAIL]

### Tests
Status: PASS | FAIL
- [action item if FAIL]

### DRY / SOLID / KISS / OOP
Status: PASS | FAIL
- [action item if FAIL, cite the specific principle]

### Registries (Procedures/Guardrails/Lessons/Semantics)
Status: PASS | FAIL
- [action item if FAIL]

### Overall
Status: PASS | FAIL
```

An overall FAIL blocks progression to testing or closeout — fix the identified issues and re-run
`code-review` before continuing.

## 4. Offer fixes
Offer to apply the safe/low-risk fixes (naming, obvious duplication, formatting). Apply only on
the user's confirmation; leave judgment calls to them.

## 5. Record
Append a one-line summary to the active episode's `## Log` (e.g. "code-review: PASS; 2 safe fixes
applied" or "code-review: FAIL — goal alignment, tests").

## 6. Commit (conditional)
On an Overall PASS (after step 4's fixes, if any, are applied): run
`scripts/code-review-commit.sh "<descriptive message>"`. It reports `not-a-git-repo` for a
non-git project (nothing to do) or commits and reports the message. Skip this step entirely on a
FAIL — nothing gets committed until `code-review` actually passes.
