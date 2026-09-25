---
tags:
  - memory
  - memory/guardrail
  - guardrails
aliases:
  - Guardrails
  - Guardrail Memory
date: __DATE__
---

# __REPO_NAME__ Guardrails

Hard must/must-not rules, routed to the cheapest enforcement tier that can
actually enforce them. This file is a **reference registry, not required
reading at onboarding** — only `judgment`-tier rules carry an always-read
cost, and those are surfaced as one-liners in [CLAUDE.md](../../CLAUDE.md).
Consult this file directly when running `/distill`, `/graduate-to-template`, or
`/code-review`.

## Enforcement Tiers

| Tier | Where it lives | Standing cost |
|---|---|---|
| `script` | Pre-commit hook or test | Zero — runs outside the model |
| `review` | `/code-review` checklist item | Near-zero — loads only during review |
| `judgment` | One line in [CLAUDE.md](../../CLAUDE.md) | The only tier with an always-read cost |

## Rules

### example-guardrail-name
```yaml
rule: "Replace with the exact must/must-not statement."
enforce: judgment            # script | review | judgment
severity: high                 # low | medium | high
promotions: 1
episodes: ["episode-name-1"]
created: __DATE__
updated: __DATE__
```
- Supported by: [episode-name-1](Episodes/episode-name-1.md)

## Update Rule

- Promotion is a judgment call, not a fixed episode count: promote after a
  single episode when the rule is high-severity and/or cheap to route (an
  obvious `script`- or `review`-tier check); otherwise hold for a second
  corroborating episode, same as Semantics/Procedures/Lessons.
- Tier and severity are **proposed by `/distill`, confirmed by the user**
  before being written — a wrong `script`-tier guess produces a broken
  hook, and a wrong `judgment`-tier guess adds a permanent always-read line
  for something that could have been enforced for free.
- **Every entry's YAML block must include an `episodes` field, and every entry must have a matching markdown link line.**
- Guardrails do not graduate into skills — they stay in this registry, routed by tier.

---

See also: [Semantics](Semantics.md) | [Procedures](Procedures.md) | [Lessons](Lessons.md) | [Episodes](Episodes/README.md)
