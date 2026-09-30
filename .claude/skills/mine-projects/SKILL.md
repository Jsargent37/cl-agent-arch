---
name: mine-projects
description: Mine all sibling projects' own knowledge registries for lessons/procedures/guardrails universal across 2+ of the user's own projects, promote them into the deployed standard template, and push the standardized changes down to every sibling project. Use periodically to keep the projects-level standard current, or when asked to run a cross-project mining pass.
---

# mine-projects

Implements the tier-2 half of the cross-project lesson sync design
(`Documents/projects/docs/superpowers/specs/2026-09-23-cross-project-lesson-sync-v2-design.md`).
Mirrors `mine-registries`' collect → consolidate → graduate → apply idiom, scoped across sibling
projects instead of within one project.

## 1. Collect

Read `Documents/projects/PROJECTS.md` to enumerate sibling projects, excluding `project-skill` from
this collection step (its registries describe building the distillation tooling itself, not
candidate universal lessons — it still receives step 5's push-down like any other sibling).

For each remaining sibling project, read its `docs/memory/PROCEDURES.yaml` and
`docs/memory/GUARDRAILS.yaml` directly (deterministic — no subagent needed). Collect only the
types `mine-registries` actually graduates at tier 1 — lessons, soft guardrails, and semantics
entries have no tier-1 graduation path, so they are never candidates here, regardless of count:
- **Procedures** with `promotion_count >= 2`.
- **Guardrails** with `enforceability: hard`, any count.

Exclude any entry with `status: retired` from either list — a sibling retiring an entry means it
no longer applies even locally, so it is never a cross-project candidate regardless of count or
enforceability.

Additionally exclude any entry whose `id` already exists in the deployed standard's own
`docs/memory/PROCEDURES.yaml`/`GUARDRAILS.yaml` — a sibling's seed guardrails (present in every
project because they came from the template) are not "cross-project candidates," they're already
standardized.

If fewer than two sibling projects have any matured, not-already-standardized entries at all,
record that and stop — there is nothing to cross-compare yet.

## 2. Cross-project consolidate

Dispatch a Haiku "digest" subagent per collected entry (in parallel), given the entry plus its
source episodes/`draft_ref` content — same digest approach as `mine-registries` step 3 — to expand
each entry into what it actually covers: real steps, commands, and rules, not just its terse
`summary`/`content`.

Once every digest is ready, dispatch one batch-compare subagent per registry, given every digest
from that registry **tagged with which sibling project it came from**. It proposes groups of
entries — from *different* sibling projects — describing the same generalizable pattern. This is
the tier-2 maturity bar: an entry must recur across **2 or more distinct sibling projects** to
become a cross-project candidate (a single project's own maturity, from step 1, is a prerequisite,
not the bar itself).

If no cross-project matches are found, record that and stop — a clean pass with zero universal
candidates is a normal, expected outcome, especially while sibling projects' own registries are
still shallow.

## 3. Graduate

For each cross-project candidate: this is new shared content entering the deployed standard for
the first time, not a merge — per the confirm-on-concern rule, auto-apply by default, and pause
for an explicit confirm only when genuinely uncertain (real ambiguity in the skill-vs-agent
judgment below, or doubt about whether the pattern is truly universal rather than a coincidence
across two projects).

Write the entry into the deployed standard's registries at
`Documents/projects/.claude/skills/new-project/assets/template/docs/memory/*.yaml` as
**`status: promoted`** (not `draft`) — this is what stops a sibling's own `mine-registries` from
re-graduating a pushed-down entry into a duplicate `pm-` skill once it arrives there in step 5.
Union the source entries' `episodes` lists (namespaced per sibling project, e.g.
`<project-name>/2026-07-09-some-episode`) and sum their `promotion_count`.

For a recurring **procedure** candidate specifically, apply the same skill-vs-agent Haiku judgment
`mine-registries` uses: *is this a narrow, mechanical, single-purpose task reliable enough for a
Haiku-tier model to execute alone, with no orchestration of other subagents?* If yes, read and
follow the agent-authoring procedure at
`Documents/projects/.claude/skills/new-project/assets/template/.claude/skills/creating-agents/SKILL.md`
directly (don't invoke `creating-agents` by name — the projects root has no top-level skill by
that name). Author `Documents/projects/.claude/skills/new-project/assets/template/.claude/agents/
pm-<slug>.md` with `promoted_to` set to that same path, `status: promoted`, `model: haiku` hardcoded,
tools scoped to the minimum needed. If no — including genuine doubt — invoke
`superpowers:writing-skills` to author `Documents/projects/.claude/skills/new-project/assets/
template/.claude/skills/pm-<slug>/SKILL.md` instead, with `promoted_to` set to that path.

If genuinely uncertain whether the skill-vs-agent judgment or the universality of the pattern is
right, hold the proposal and ask the user before writing anything for that specific candidate —
other candidates in the same run that aren't in doubt still proceed on their own.

## 4. Apply

Write the deployed standard's registry changes and any new `pm-` skill/agent file (per step 3's
confirm-on-concern outcome for each candidate). Then run the template's bundled checker to catch
any resulting inconsistency:

```
uv run --project Documents/projects/.claude/skills/new-project/assets/template/docs/tools python Documents/projects/.claude/skills/new-project/assets/template/docs/tools/check_registries.py
```

The script finds its target registries relative to its own location, three directories up from
itself, so running this exact copy checks the deployed template's own `docs/memory/`. Fix any
violation it reports before considering the pass done.

## 5. Push down

Invoke the `push-down-standardize` skill by name to fan the applied changes out to every sibling
project, including `project-skill`'s own `.claude/skills/`/`docs/memory/`.

Additionally, for each cross-project candidate that graduated in step 3: for every sibling project
that *contributed* an entry to that candidate (from step 2's cross-project consolidation, not just
whichever one sibling's id happens to already match the deployed standard's new entry), directly
edit that sibling's own `docs/memory/PROCEDURES.yaml`/`GUARDRAILS.yaml` to set its original,
contributing entry's `status: promoted` and `promoted_to` pointing at the deployed template's new
skill/agent path. This is a direct, deterministic edit `mine-projects` makes itself — not routed
through `push-down-standardize`, which only ever propagates the deployed standard's own content
downward; a contributing sibling's pre-existing entry has no corresponding deployed-standard entry
under the *same* id to sync via that mechanism, so it needs its own explicit write. This closes the
loop for every contributor, fixing the v2 defect where only one contributor (whichever one's id
happened to match) was protected from being re-graduated into a duplicate `pm-` skill by that
sibling's own next `mine-registries` run — the rest, with 3 or more contributors, were not.
