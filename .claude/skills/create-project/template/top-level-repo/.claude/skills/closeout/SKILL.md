---
name: closeout
description: Close out an approved task branch by reviewing changes, updating episode and memory docs, cleaning notes, and merging to the default branch.
---

# closeout

Use this skill to close out the current task branch after user approval.

## When to use

- User approves the completed work and asks to close out or merge
- User says "close out", "merge this", "finish up", or "wrap up the task"

## How to invoke

```
/closeout
```

## Closeout Sequence

Follow these steps in order. Do not skip or reorder.

### Step 1: Code Review

Run `/code-review` on the current branch changes.

- If the review fails, stop. Fix the identified issues and re-run `/code-review` before continuing.
- Only proceed when the overall review status is PASS.

### Step 2: Present Changes for User Approval

Summarize the changes made on this branch:
- What was changed and why
- Any deviations from the original plan and the reason for each
- Test results

Ask the user explicitly: "Do you approve these changes?"

- If the user requests changes, stop. Make the changes, re-run `/code-review`, and restart the approval step.
- Only proceed when the user explicitly approves.

### Step 3: Write or Update the Episode File

Write or update the episode file for this branch at:
`docs/Memory/Episodes/<branch-name>.md`

Ensure the episode file has proper YAML frontmatter:

```yaml
---
tags:
  - memory/episode
date: YYYY-MM-DD
---
```

Fill in all required sections:
- Why This Change Happened
- Pre-Change Repo State
- Post-Change Repo State

Fill in optional sections where they add meaningful signal.

Fill in the `signals` frontmatter field with one entry per reusable
pattern this episode produced (procedure, guardrail, or lesson candidate).
Leave it as `signals: []` if nothing reusable came out of this episode —
most episodes emit nothing. See
[Episodes/README](../../../docs/Memory/Episodes/README.md) for the schema.

Use standard markdown links to reference any related docs (e.g., `[Semantics](../Semantics.md)`, `[Procedures](../Procedures.md)`, `[Roadmap](../../ROADMAP.md)`, other `[episode-name](episode-name.md)` files).

### Step 4: Review Episode Against Prior Episodes

Read the new episode alongside recent episode files in `docs/Memory/Episodes/`.

Identify any patterns, learnings, or workflows that now appear in two or more episodes.

### Step 5: Conditional Semantics Promotion

- Update `docs/Memory/Semantics.md` only if a stable fact or policy is now supported by at least two episode files.
- If the learning appears in only one episode, leave it there. Do not promote.
- **Every promoted entry's YAML block must include an `episodes` field, and every entry must have a matching markdown link line.** For example:
  ```
  ### always-lint-before-tests
  ```yaml
  promotions: 2
  description: "Always run lint before tests."
  episodes: ["2026-04-15-add-linting", "2026-04-22-fix-ci-pipeline"]
  created: 2026-04-15
  updated: 2026-04-22
  ```
  - Supported by: [2026-04-15-add-linting](Episodes/2026-04-15-add-linting.md), [2026-04-22-fix-ci-pipeline](Episodes/2026-04-22-fix-ci-pipeline.md)
  ```
- Do **not** promote into `docs/Memory/Procedures.md`, `docs/Memory/Guardrails.md`, or `docs/Memory/Lessons.md` here. Those are populated by running `/distill` **on demand**, separately from closeout — never automatically as part of this sequence.
- This ensures both the Obsidian graph and GitHub render connected, navigable documentation.

### Step 6: Update README.md and ROADMAP.md

- Update `docs/README.md` if the live project description or state changed.
- Update `docs/ROADMAP.md` if priorities or completion status changed.
- Link completed roadmap items to their [episode](docs/Memory/Episodes/README.md) file.

### Step 7: Clean NOTES.md

Reset `docs/NOTES.md` to its placeholder state:
- `## Current Work` → `-`
- `## Next` → `-`
- `## Active Branch` → `-`
- `## Scratch` → `-`
- `## Open Questions` → `-`

### Step 8: Run closeout.sh

```bash
bash "$(git rev-parse --show-toplevel)/.claude/skills/closeout/scripts/closeout.sh" --yes
```

Pass `--no-delete` to keep the branch after merging:

```bash
bash "$(git rev-parse --show-toplevel)/.claude/skills/closeout/scripts/closeout.sh" --yes --no-delete
```

## Notes

- Steps 1–7 are agent steps. Step 8 is the script.
- The code review in Step 1 and user approval in Step 2 are hard gates — neither can be skipped.
- Semantics promotion in Step 5 requires two or more supporting episodes. One episode is never enough to promote. Procedures/Guardrails/Lessons promotion happens only via a separate, on-demand `/distill` run — never inline during closeout.
- NOTES.md is cleaned in Step 7 before the merge, so its cleaned state is included in the merge commit.
- All documentation uses standard markdown links with YAML frontmatter tags — compatible with both GitHub and Obsidian graph view.
