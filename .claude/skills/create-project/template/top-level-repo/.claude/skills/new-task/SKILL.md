---
name: new-task
description: Start a new task in the current repo by creating a dated branch, copying the episode template, and updating docs/NOTES.md.
---

# new-task

Use this skill to start a new task in this repo.

## When to use

- User asks to start a new task, feature, or fix
- User says "begin work on X", "create a branch for X", or "start task X"

## What it does

1. Validates the repo is in a clean starting state (on default branch, in repo root).
2. Creates a dated branch: `YYYY-MM-DD-<kebab-task-name>`.
3. Copies the episode template for the new branch.
4. Updates the Active Branch line in `docs/NOTES.md`.
5. Prints the required read-order checklist and next steps.

## How to invoke

Ask the user for the task name if not already provided, then run:

```bash
bash .claude/skills/new-task/scripts/new-task.sh "<task name>"
```

After the script succeeds:

1. Read the required docs in order: ONBOARDING → TASK → README → ROADMAP → Semantics → Procedures → recent Episodes.
2. Confirm the active goal in `docs/ROADMAP.md`.
3. Set `## Current Work` and `## Next` in `docs/NOTES.md`.
4. Write the initial implementation plan to the new episode file before coding begins (use planning mode: /plan).

## Notes

- The script aborts if you are already on a feature branch. Always start from the default branch.
- The branch name is derived from today's date and the task name, lowercased and hyphenated.
- The episode file is created at `docs/Memory/Episodes/<branch-name>.md`.
