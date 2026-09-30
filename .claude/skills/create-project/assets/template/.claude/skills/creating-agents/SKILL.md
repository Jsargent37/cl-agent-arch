---
name: creating-agents
description: Use when authoring a new custom subagent at .claude/agents/<name>.md — covers required frontmatter, model/tool scoping, and how to write a narrowly-scoped Haiku-executable agent. Used by mine-registries for procedure-to-agent graduation, and directly by a human authoring an agent by hand.
---

# creating-agents

## When to use an agent vs a skill

Before authoring anything, apply this test: **is this a narrow, mechanical, single-purpose task
reliable enough for a Haiku-tier model to execute alone, with no orchestration of other subagents?**
If yes, write an agent. If the task needs multi-step orchestration, judgment calls beyond Haiku-tier
reliability, or coordinates multiple subagents, it should be a skill instead — default to skill on
any doubt. A procedure misclassified as an agent produces a subagent that silently fails or
hallucinates on the reasoning it can't reliably do; that's worse than routing it to a skill a
capable model executes directly.

## File location

`.claude/agents/<name>.md` — project-scoped, alongside this project's `.claude/skills/`.

## Required frontmatter

```yaml
---
name: kebab-case-unique-name
description: When Claude should delegate to this agent — be specific enough that automatic delegation picks it correctly.
tools: Read, Grep, Bash        # scope to the minimum this agent's task actually needs — never a blanket inherit-all
model: haiku                    # mandatory for any agent authored via this skill — never left to inherit
---
```

Only `name` and `description` are required by Claude Code itself, but this skill additionally
requires `model: haiku` and an explicit, minimal `tools` list for every agent it produces — the
whole point of the agent path is routing narrow work to the cheapest reliable tier, and an unscoped
`tools` list defeats the enforcement/focus benefit of using a dedicated agent at all.

## Body (system prompt)

The body is the agent's entire system prompt — it does not see the rest of Claude Code's default
system prompt, the invoking conversation's history, or any skill unless explicitly preloaded via
`skills:`. Write it as direct instructions to the agent performing the task, not prose describing
the agent to a human reader: "Read the file at the given path and report X" — not "This agent reads
files and reports X."

Keep the body to exactly the steps the narrow task requires. If you find yourself writing branching
logic, exception handling for multiple distinct failure modes, or coordination with other subagents
into the body, that's a signal that the underlying task failed the when-to-use test above and belongs
in a skill instead.

## Naming for mined agents

When this skill is invoked by `mine-registries` (as opposed to a human authoring an agent directly),
the produced `name` is prefixed `pm-` (e.g. `pm-tarball-deploy`) so mined agents are visually
distinguishable from hand-authored ones at a glance.

## Worked example

A procedure entry like "package and deploy code to a remote server as a tarball" is narrow,
mechanical, and doesn't require judgment calls beyond following fixed steps — a good agent
candidate:

```yaml
---
name: pm-tarball-deploy
description: Package a local directory as a tarball and deploy it to a remote server. Use when deploying code to a server without pushing to a remote repository.
tools: Bash, Read
model: haiku
---

Package the given local directory as a tarball, upload it to the target server path provided, then
extract it at the given destination. Report the final extracted path when done.
```
