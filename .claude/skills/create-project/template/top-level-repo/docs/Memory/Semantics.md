---
tags:
  - memory
  - memory/semantic
  - stable-facts
aliases:
  - Semantics
  - Semantic Memory
date: __DATE__
---

# __REPO_NAME__ Semantic Memory

Each entry is a heading followed by a fenced YAML block, plus a markdown
link line so Obsidian's graph view stays connected to the supporting
episodes. Delete the example below once real entries exist.

## Stable Facts

### example-fact-name
```yaml
promotions: 2
description: "Replace with a durable project fact or policy."
episodes: ["episode-name-1", "episode-name-2"]
created: __DATE__
updated: __DATE__
```
- Supported by: [episode-name-1](Episodes/episode-name-1.md), [episode-name-2](Episodes/episode-name-2.md)

## User Preferences

> Same entry format as above — stable user or repo preferences that matter across tasks.

## Policies And Concepts

> Same entry format as above — stable policies, definitions, or domain
> concepts. Guardrails (hard must/must-not rules) belong in
> [Guardrails](Guardrails.md), not here — Semantics is for descriptive
> facts, Guardrails is for enforceable rules.

## Update Rule

- Keep this file focused on durable facts.
- Update this file only when the learning is supported by at least two episode files.
- **Every entry's YAML block must include an `episodes` field, and every entry must have a matching markdown link line.**
- Promoted directly during `/closeout` — unlike Procedures/Guardrails/Lessons, Semantics is not part of the `/distill` pipeline.
- Move workflows and playbooks to [Procedures](Procedures.md).

---

See also: [Procedures](Procedures.md) | [Guardrails](Guardrails.md) | [Lessons](Lessons.md) | [Episodes](Episodes/README.md)
