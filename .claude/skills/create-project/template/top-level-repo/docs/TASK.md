---
tags:
  - process
  - task-lifecycle
aliases:
  - Task Workflow
date: __DATE__
---

# __REPO_NAME__ Task Workflow

This file defines the mandatory lifecycle for handling a task in this repo.

## Task Order

1. Run `/new-task` to create a dated branch, episode file, and update [Notes](NOTES.md).
2. Create an implementation plan for the task (use planning mode: /plan).
3. Record the initial implementation plan in [Notes](NOTES.md) and the task episode before coding begins.
4. Implement the planned code changes.
5. Run `/code-review` to review the implementation against the plan, the repo procedures, and the task goal.
6. If the review fails, fix the code and run `/code-review` again.
7. If the review passes, run the required tests.
8. If tests fail, review the code and/or plan, update the plan if needed, record any plan changes in [Notes](NOTES.md) and the episode, implement the changes, and test again.
9. If tests pass, present the changes to the user for review.
10. If the user approves, run `/closeout`.
11. If the user requests changes, review the code and/or plan, record any plan changes, implement the requested changes, and repeat the review and test loop.

## Branch Rule

- Every task starts on a new branch.
- Use the repo's normal branch naming conventions.
- Do not implement the task on the default branch.

## Implementation Plan Requirements

A good implementation plan should:

- minimize the number of code changes
- follow all relevant procedures in the repo
- describe the high-level coding changes to make
- describe the general organization of the work
- define the tests required to validate the change
- state what success looks like
- aim for DRY, SOLID, and KISS design
- produce clear, well-structured object-oriented code where the language and codebase support it

## Planning Record Rule

- The initial plan must be recorded in [Notes](NOTES.md) and in the task episode before coding begins.
- If the plan changes later, record the change in the same places before continuing.
- Keep the plan history clear enough that a later reader can see what changed and why.

## Review Rule

- Code review happens before testing.
- Review should confirm that the implementation follows repo [Procedures](Memory/Procedures.md), matches the goal, and keeps the change set as small and clean as practical.
- If the review finds a mismatch, fix the implementation before moving to testing.

## Testing Rule

- Run the tests required by the implementation plan.
- If the task does not pass the required tests, the task is not ready for user review.
- Failed tests require another review of the code and possibly the plan.

## User Approval Gate

- Passing tests is not the final step.
- After review and testing pass, present the changes to the user for review.
- Only after user approval should the task move into closeout.

## Closeout Link

- Run `/closeout` to close out the current task branch. See `.claude/skills/closeout/SKILL.md` for the complete procedure.
- Episode creation and Semantics promotion still happen during closeout. Procedures/Guardrails/Lessons promotion does not — it happens only by running `/distill` on-demand, separately. Cross-project promotion into the shared template happens only by running `/graduate-to-template`, also on-demand. Neither is ever part of this task lifecycle's mandatory steps.

---

See also: [Onboarding](ONBOARDING.md) | [Notes](NOTES.md) | [Procedures](Memory/Procedures.md) | [Episodes](Memory/Episodes/README.md)
