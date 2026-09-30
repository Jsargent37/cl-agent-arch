---
name: code-review
description: Fast, single-pass quality review of the changes made in the current task, against the project's CODE_STANDARDS plus the knowledge registries. Reports issues and offers to apply the safe fixes on confirmation. Use for a quick pass while working, before pr-review or closeout.
---

# code-review

## 1. Resolve the change set
- If a git repo exists: `git diff` and `git diff --staged`.
- Else: use the active episode's `## Files touched`.
- Else: ask the user which files to review.

## 2. Review (scoped to what changed)
Check the changed code against `docs/CODE_STANDARDS.md` (DRY/SOLID/KISS/OOP, ≤50 LoC functions, naming, comments ≤2 lines, public-only docstrings, dead code, logging/error handling, tests, doc currency) plus `docs/memory/PROCEDURES.yaml`, `docs/memory/GUARDRAILS.yaml`, `docs/memory/LESSONS.yaml`, and `docs/memory/SEMANTICS.yaml`. Keep it light — focus on the diff, not the whole codebase.

## 3. Report
For each issue: `file:line` · severity (critical/high/medium/low) · principle · current → suggested fix. End with counts by severity and what the code does well.

## 4. Offer fixes
Offer to apply the safe/low-risk fixes (naming, obvious duplication, formatting). Apply only on the user's confirmation; leave judgment calls to them.

## 5. Record
Append a one-line summary to the active episode's `## Log` (e.g. "code-review: 2 high / 3 medium; applied 3 safe fixes").
