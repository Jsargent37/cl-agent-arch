---
tags: [memory, memory/guardrail]
---

# Guardrails

Hard/soft enforcement rules. Each entry carries an enforcement `tier` (`script`/`review`/
`judgment`) and `severity` (`low`/`medium`/`high`) once graduated, routing it to the cheapest
mechanism that can actually enforce it. Populated by `distill`.

## Entries

### follow-code-standards
```yaml
summary: Follow CODE_STANDARDS.md for all code
applicability: [code-standards]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Follow CODE_STANDARDS.md for all code.
enforceability: hard
tier: null
severity: null
hook: null
```
- Supported by: (none yet)

### keep-episode-current
```yaml
summary: Keep episode Log, Files touched, and Promotion candidates current
applicability: [episode]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Keep the active episode's "## Log", "## Files touched", and "## Promotion candidates" current as you work.
enforceability: soft
tier: null
severity: null
hook: null
```
- Supported by: (none yet)

### no-global-python
```yaml
summary: Never install into or use a global/system Python
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Never install into or use a global/system Python. `pip install` is denied by settings.
enforceability: hard
tier: null
severity: null
hook: null
```
- Supported by: (none yet)

## Update Rule

- `tier` is decided by `distill`'s Graduate step BEFORE routing, not assigned as a byproduct of
  which tool happened to handle graduation: `distill` first judges whether the rule is mechanizable
  as a `PreToolUse` hook/permission rule (concrete, checkable condition and action -> `script`),
  cheaply checkable by a human/reviewing agent but not mechanically (-> `review`), or a
  human-judgment rule stated in prose with no checkable condition at all (-> `judgment`). Only
  after that decision does a `script`-tier candidate get routed to `graduate_guardrail.py` to
  generate the hook/permission-rule artifact; `review`/`judgment`-tier candidates graduate as plain
  registry entries (`promoted_to: null` — there is no external artifact, the registry entry itself
  is the enforcement record).
- `tier` and `severity` are proposed by `distill`'s Graduate step and confirmed by the user
  before being written — a wrong `script`-tier guess produces a broken hook, and a wrong
  `judgment`-tier guess adds a permanent always-read line for something that could have been
  enforced for free.
- `enforceability: hard` graduates on first occurrence (any `promotion_count`); `soft` never
  graduates automatically — it stays `status: draft`, and never carries a `tier` (a tier only
  exists once an entry actually graduates, and soft guardrails never do).
- Every entry's YAML block must include an `episodes` field; when non-empty, add matching
  `[episode-name](../episodes/episode-name.md)` links to the "Supported by" line.

---

See also: [Procedures](PROCEDURES.md) | [Lessons](LESSONS.md) | [Semantics](SEMANTICS.md)
