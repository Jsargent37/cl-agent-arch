---
name: code-review
description: Perform a structured code review of the current branch before testing or closeout, checking goal alignment, tests, DRY, SOLID, and KISS.
---

# code-review

Use this skill to perform a structured code review of the current branch's changes.

## When to use

- Before testing, per the task lifecycle in `docs/TASK.md`
- Any time the user asks for a code review
- Invoked automatically at the start of `/closeout`

## What it does

Reviews all changes on the current branch against five quality principles and produces a structured pass/fail report. An overall FAIL blocks progression to testing.

## How to invoke

Read the changed files and evaluate them against the criteria below. If the overall result is PASS, run the commit script with a message describing what was changed:

```
/code-review
```

```bash
bash .claude/skills/code-review/scripts/code-review-commit.sh "<what-was-changed>"
```

## Review Criteria

### Goal Alignment
- The implementation matches the task goal as stated in the implementation plan.
- No unrelated changes are included.
- The implementation follows repo procedures (see `docs/TASK.md`, `docs/Memory/Procedures.md`).

### Tests
- All tests required by the implementation plan are present and pass.
- Tests verify behavior, not just that code runs.
- Edge cases identified in the plan are covered.

### DRY (Don't Repeat Yourself)
- No logic is duplicated across files or functions.
- Shared behavior is extracted into a single location and reused.

### SOLID
- **Single Responsibility**: each class, module, or function has one reason to change.
- **Open/Closed**: behavior is extended by addition, not by modifying existing code.
- **Liskov Substitution**: subtypes are substitutable for their base types without altering correctness.
- **Interface Segregation**: callers are not forced to depend on interfaces they do not use.
- **Dependency Inversion**: high-level modules depend on abstractions, not concrete implementations.

### KISS (Keep It Simple)
- The implementation is the simplest solution that correctly meets the requirements.
- No speculative generality: no code exists in anticipation of future needs not in the current plan.
- Logic is readable without needing a comment to explain what it does.

## Output Format

```
## Code Review Report

### Goal Alignment
Status: PASS | FAIL
- [action item if FAIL]

### Tests
Status: PASS | FAIL
- [action item if FAIL]

### DRY
Status: PASS | FAIL
- [action item if FAIL]

### SOLID
Status: PASS | FAIL
- Single Responsibility: PASS | FAIL — [note]
- Open/Closed: PASS | FAIL — [note]
- Liskov Substitution: PASS | FAIL — [note]
- Interface Segregation: PASS | FAIL — [note]
- Dependency Inversion: PASS | FAIL — [note]

### KISS
Status: PASS | FAIL
- [action item if FAIL]

### Overall
Status: PASS | FAIL

[If FAIL: list all required changes before proceeding to testing.]
```

## Notes

- A review that passes all five sections is required before testing begins.
- If the review fails, fix the identified issues and re-run `/code-review`.
- Do not proceed to testing while any section is marked FAIL.
- The commit message must describe the actual changes (e.g. `feat: add sqrt script`, `fix: handle negative input in calculator`). Do not use a generic message like "code review passed".
