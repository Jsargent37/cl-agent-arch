---
name: creating-agents
description: Use when authoring a new narrowly-scoped automated helper for a single mechanical, low-judgment task — covers the decision of when to delegate vs. keep a full skill, and (for Claude Code) the required subagent frontmatter and file location. Used by distill for procedure-to-helper graduation, and directly by a human authoring one by hand.
---

# creating-agents

## When to delegate to a narrow helper vs. write a skill

Before authoring anything, apply this test: **is this a narrow, mechanical, single-purpose task
reliable enough for a small/cheap model tier to execute alone, with no orchestration of other
subagents or tools beyond the minimum it needs?** If yes, author a narrow helper. If the task
needs multi-step orchestration, judgment calls beyond that tier's reliability, or coordinates
multiple subagents, it should be a skill instead — default to skill on any doubt. A procedure
misclassified as a narrow helper produces something that silently fails or hallucinates on
reasoning it can't reliably do; that's worse than routing it to a skill a capable model executes
directly.

## Platform mechanics

This project's coding agent platform determines how a narrow helper is actually authored and
invoked. Below is Claude Code's mechanism; adapt this section if the project is used with a
different platform that offers an equivalent delegation feature, and skip authoring a helper
entirely (write a skill instead) on a platform with no such mechanism.

### Claude Code

File location: `.claude/agents/<name>.md` — project-scoped, alongside this project's
`.claude/skills/`.

Required frontmatter:

```yaml
---
name: kebab-case-unique-name
description: When the platform should delegate to this helper — be specific enough that automatic delegation picks it correctly.
tools: Read, Grep, Bash        # scope to the minimum this helper's task actually needs — never a blanket inherit-all
model: haiku                    # mandatory for any helper authored via this skill — never left to inherit
---
```

Only `name` and `description` are required by Claude Code itself, but this skill additionally
requires `model: haiku` and an explicit, minimal `tools` list for every helper it produces — the
whole point of this path is routing narrow work to the cheapest reliable tier, and an unscoped
`tools` list defeats the enforcement/focus benefit of using a dedicated helper at all.

## Body (system prompt)

The body is the helper's entire system prompt — it does not see the rest of the platform's
default system prompt, the invoking conversation's history, or any skill unless explicitly
preloaded. Write it as direct instructions to whatever executes the task, not prose describing
the helper to a human reader: "Read the file at the given path and report X" — not "This helper
reads files and reports X."

Keep the body to exactly the steps the narrow task requires. If you find yourself writing
branching logic, exception handling for multiple distinct failure modes, or coordination with
other subagents into the body, that's a signal that the underlying task failed the when-to-use
test above and belongs in a skill instead.

## Naming for mined helpers

Whenever this skill is invoked for registry/mining-related work — e.g. by `distill` for
procedure-to-helper graduation, or by `graduate-to-template` when it creates a helper for
promoting a proven pattern up to the shared template — the produced `name` is prefixed `pm-`
(e.g. `pm-v11-transcription-runbook`) so mined/graduated helpers are visually distinguishable from
hand-authored ones at a glance.

## Worked example (Claude Code)

A procedure entry like "ship code to a GCE VM as a GCS tarball, never git clone" is narrow,
mechanical, and doesn't require judgment calls beyond following fixed steps — a good candidate:

```yaml
---
name: pm-gce-tarball-deploy
description: Ship code to an ephemeral GCE VM as a GCS tarball. Use when deploying code to a GCE VM that has no GitHub credentials for private repos.
tools: Bash, Read
model: haiku
---

Package the given local directory as a tarball, upload it to the GCS path provided, then SSH into
the target VM and extract it to the given destination path. Never attempt `git clone` on the VM —
it has no GitHub credentials for private repos. Report the final extracted path and the tarball's
GCS URI when done.
```
