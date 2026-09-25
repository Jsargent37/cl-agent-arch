---
tags:
  - memory
  - memory/procedure
  - workflows
aliases:
  - Procedures
  - Procedure Memory
date: __DATE__
---

# __REPO_NAME__ Procedure Memory

Each entry holds a refined, condensed version of a corroborated workflow —
distilled from the supporting episodes' `signals`, not copied narrative.
This is what lets a task run the procedure without reopening any episode
file.

> Populated by running `/distill` **on demand** — never automatically at
> `/closeout`. See [Episodes/README](Episodes/README.md) for the signal
> schema and promotion gate.

## Recurring Workflows

### example-procedure-name
```yaml
promotions: 2
description: "Replace with a one-line summary of the workflow."
steps:
  - "Replace with the first concrete step."
  - "Replace with the next concrete step."
episodes: ["episode-name-1", "episode-name-2"]
created: __DATE__
updated: __DATE__
origin: project              # project | template (set by graduate-to-template)
distilled_into: null          # skill or tool id, once graduated out of this file
```
- Supported by: [episode-name-1](Episodes/episode-name-1.md), [episode-name-2](Episodes/episode-name-2.md)

## Tooling Routines

> Same entry format as above — for tool-use patterns or command habits.

## Playbooks

> Same entry format as above — for procedures that should survive across branches.

## Update Rule

- Keep this file focused on how to do things, in refined/condensed form — not full episode narrative.
- Entries are written and revised by `/distill`, on demand, from episode `signals` — never written inline during `/closeout`.
- Update this file only when the workflow is supported by at least two episode files.
- **Every entry's YAML block must include an `episodes` field, and every entry must have a matching markdown link line.**
- Once a procedure graduates into a full skill or tool (`distilled_into` is set), its `steps` field collapses to `null` and the full prior body moves to [Archive](Archive.md).
- Move durable facts to [Semantics](Semantics.md). Move hard rules to [Guardrails](Guardrails.md). Move narrative lessons to [Lessons](Lessons.md).

---

See also: [Semantics](Semantics.md) | [Guardrails](Guardrails.md) | [Lessons](Lessons.md) | [Archive](Archive.md) | [Episodes](Episodes/README.md)
