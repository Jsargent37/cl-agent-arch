---
tags:
  - memory
  - memory/lesson
  - lessons
aliases:
  - Lessons
  - Lesson Memory
date: __DATE__
---

# __REPO_NAME__ Lessons

What worked, what failed, and why — distilled to a short takeaway. This
file is a **reference registry, not required reading at onboarding**;
consult it during `/code-review` or when a task resembles a past failure.
Since most lessons never graduate into a skill or tool, `/drift-check`
prunes this file periodically (merging near-duplicates, retiring lessons
superseded by a since-promoted guardrail or procedure) so it stays usable
over a project's life.

## Entries

### example-lesson-name
```yaml
promotions: 2
takeaway: |
  Replace with a concise takeaway, five lines maximum. State what
  happened, why it happened, and what to do differently — as few words
  as the lesson allows.
episodes: ["episode-name-1", "episode-name-2"]
created: __DATE__
updated: __DATE__
```
- Supported by: [episode-name-1](Episodes/episode-name-1.md), [episode-name-2](Episodes/episode-name-2.md)

## Update Rule

- `takeaway` is capped at **5 lines** — refine and shorten rather than hardcoding to exactly one line.
- Update this file only when the lesson is supported by at least two episode files.
- **Every entry's YAML block must include an `episodes` field, and every entry must have a matching markdown link line.**
- `/distill` extracts a lesson into a skill, tool, or `/code-review` checklist item only when it is genuinely actionable and recurring — most lessons stay as a permanent registry entry here.

---

See also: [Semantics](Semantics.md) | [Procedures](Procedures.md) | [Guardrails](Guardrails.md) | [Episodes](Episodes/README.md)
