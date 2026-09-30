---
tags:
  - memory
  - memory/episode
  - episodes
aliases:
  - Episodes
  - Episode Records
date: __DATE__
---

# __REPO_NAME__ Episode Records

Create one file per branch or task update using a name like:

- `YYYY-MM-DD-branch-or-task.md`

Each episode must capture:

- why the change happened
- the pre-change repo state
- the post-change repo state

Each episode may also capture, when useful:

- procedures added or changed
- new semantic understanding
- issues encountered
- abandoned attempts
- what worked or failed and why

## Linking Rules

- Tag each episode with `#memory/episode` in its YAML frontmatter.
- Use markdown links inside episodes to reference any docs they relate to (e.g., [Semantics](../Semantics.md), [Procedures](../Procedures.md), other episodes).
- When an episode leads to a promotion into [Semantics](../Semantics.md) or [Procedures](../Procedures.md), the promoted entry **must** link back to this episode and any other supporting episodes.

## Signal Schema

Episodes emit a `signals:` list in frontmatter — one entry per reusable
pattern the episode produced. Most episodes emit nothing; that selectivity
is the first filter.

```yaml
signals:
  - kind: procedure          # procedure | guardrail | lesson
    id: report-screenshot
    note: "headless screenshot to verify Plotly render before shipping"
    enforce: null             # guardrail only: script | review | judgment
    severity: null            # guardrail only: low | medium | high
    scope: project             # project | global (global = candidate for graduate-to-template)
```

Signals are never deleted, even after a promoted entry collapses or is
superseded — they remain the permanent provenance/audit trail.

## Promotion Gates By Kind

| Kind | Gate | Destination |
|---|---|---|
| `procedure` | id recurs in ≥2 episodes | refined-body entry in [Procedures](../Procedures.md); extracted into a skill/tool only once complex or reused enough to warrant it |
| `guardrail` | judgment call: 1 episode if high-severity and/or cheap to route, else ≥2 | tiered entry in [Guardrails](../Guardrails.md) |
| `lesson` | id recurs in ≥2 episodes | capped entry (≤5 lines) in [Lessons](../Lessons.md) |

`distill` (run on demand, never automatically) is what reads these signals
and performs the promotion — closeout only captures them.

## Closeout Order

1. Write or update the episode first.
2. Review it against prior episodes.
3. Only then consider updates to [Semantics](../Semantics.md) or [Procedures](../Procedures.md).

## Promotion Rule

- [Semantics](../Semantics.md) and [Procedures](../Procedures.md) should be updated only when the learning is supported by at least two episode files.
- Single-episode learning stays in the episode history until it is corroborated.
- **Promoted entries must link to all supporting episodes so the graph stays connected.**

## After Each Episode

1. Review it for semantic-memory updates → [Semantics](../Semantics.md).
2. Review it for procedure-memory updates → [Procedures](../Procedures.md).
3. Clean up [Notes](../../NOTES.md).
