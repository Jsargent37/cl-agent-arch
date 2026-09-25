---
tags:
  - process
  - onboarding
aliases:
  - Agent Onboarding
date: __DATE__
---

# __REPO_NAME__ Agent Onboarding

This file is the first required read for any agent working in this repo.

## Required Read Order

Read these files in order before making substantive changes:

1. [Onboarding](ONBOARDING.md) (this file)
2. [Task Workflow](TASK.md)
3. [Project README](README.md)
4. [Roadmap](ROADMAP.md)
5. [Semantics](Memory/Semantics.md)
6. [Procedures](Memory/Procedures.md)
7. The most recent files in [Episodes](Memory/Episodes/README.md)

## Operating Contract

- Follow this process from the outset of the repo.
- Follow [Task Workflow](TASK.md) for the task lifecycle on every task.
- Keep [Project README](README.md) current.
- Use [Notes](NOTES.md) as the shared scratchpad during active work. Both Claude and Codex write scratch notes there.
- `CLAUDE.md` holds shared Claude/Codex operating rules. `AGENTS.md` points to it for Codex. Track the active task and next steps in [Notes](NOTES.md).
- Before memory compression or handoff, dump important context, decisions, failures, and unresolved questions into [Notes](NOTES.md).
- Clean [Notes](NOTES.md) at the end of every session.

## Task Start

1. Read the required files in the order above.
2. Confirm the active goal in [Roadmap](ROADMAP.md).
3. Run `/new-task` to create the branch and episode file. Then follow [Task Workflow](TASK.md) for the full task lifecycle.
4. Set `## Current Work` and `## Next` in [Notes](NOTES.md).
5. Start capturing branch-specific scratch notes in [Notes](NOTES.md) immediately.

## Task Closeout

Run `/closeout` to close out the current task branch. The closeout skill defines the full sequence including code review, user approval, episode writing, memory promotion, and merge. See `.claude/skills/closeout/SKILL.md` for the complete procedure.

## Memory Promotion Rule

- [Semantics](Memory/Semantics.md) is for stable facts and policies that have held across multiple episodes.
- [Procedures](Memory/Procedures.md) is for repeatable workflows that have held across multiple episodes.
- Neither file should be updated from a single episode alone.
- If evidence is thin, keep the note in the episode history until the pattern repeats.
- **Every promoted item must link to the episode files that support it.**

## Reference-Only Memory Files

- [Guardrails](Memory/Guardrails.md) and [Lessons](Memory/Lessons.md) are
  **not** part of the required-read order above. Only their `judgment`-tier
  guardrail one-liners (already surfaced in [CLAUDE.md](../CLAUDE.md)) are
  always-read. Consult the full files during `/code-review` or when running
  `/distill`.
- [Archive](Memory/Archive.md) is reference-only and excluded from every
  required-read list.
- `/distill` and `/graduate-to-template` are invoked deliberately, on demand —
  never automatically as part of `/closeout` or on a schedule. Episodes do
  capture a `signals:` block at every closeout (near-zero cost); that is
  not the same as running distillation.
