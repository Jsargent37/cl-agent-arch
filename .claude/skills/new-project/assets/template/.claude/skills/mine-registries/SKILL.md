---
name: mine-registries
description: Run the on-demand, batched mining pass over the four knowledge registries (GUARDRAILS/PROCEDURES/LESSONS/SEMANTICS.yaml) — reconciles tags, cross-consolidates duplicates, prunes dead drafts, and graduates mature candidates to hooks/skills/agents. Use when asked to run a mining pass, or periodically to keep the registries from growing unbounded.
---

# mine-registries

Nothing in any step below writes anything until the final aggregate confirm (step 6) — every step
only produces a proposal.

## 1. Collect

Read `docs/memory/GUARDRAILS.yaml`, `docs/memory/PROCEDURES.yaml`, `docs/memory/LESSONS.yaml`, and
`docs/memory/SEMANTICS.yaml` directly. Collect every entry across the first three registries with
`status: draft`. This step is deterministic — do it yourself, no subagent needed.

## 2. Reconcile tags

Scan the collected entries' `applicability` lists for provisional tags (any tag not already a term
id in `SEMANTICS.yaml`). For each provisional tag found, dispatch a Haiku subagent (batch several
provisional tags into one dispatch when there are multiple) with: the tag, the entries that use it,
and the full current `SEMANTICS.yaml`. It proposes either:
- **Add as a new term** — a new `SEMANTICS.yaml` entry for the tag, or
- **Map onto an existing term** — an existing term id that means the same thing, plus the updated
  `applicability` lists for every entry that used the provisional tag.

If no provisional tags are found, record that and move to step 3 — a clean pass is a normal outcome,
not a failure.

## 3. Cross-consolidate

For every draft entry from step 1, dispatch a Haiku "digest" subagent in parallel — one per entry —
given the entry plus the full content of every episode file it cites (`docs/episodes/<id>.md`) and
its `draft_ref` file if it has one (`docs/memory/promotion-drafts/<slug>.md`). Each digest subagent
returns an in-depth summary of what the entry actually covers: real steps, commands, and code used —
not just its terse `summary`/`content` field.

Once every digest is ready, dispatch one batch-compare subagent per registry (fewer if the combined
digest volume is small enough for one subagent) with every digest from that registry. It proposes
merge groups: entries whose digests describe the same generalizable pattern, even when their
`applicability` tags don't overlap — cross-domain duplicates must be caught, so comparison is never
scoped to shared/adjacent tags.

For every proposed merge: union the merged entries' `episodes` lists, sum their `promotion_count`,
and combine their `content`/`draft_ref`. If any merged entry has a `draft_ref` file, the proposal
names one surviving file that gets the combined content and marks the other draft file for deletion
— never leave two `promotion-drafts/*.md` files for one merged entry.

## 4. Prune

Dispatch a Haiku subagent with every entry (post-consolidation) that has `promotion_count: 1`. It
flags entries with no realistic promotion path and no ongoing relevance, proposing deletion. Never
send an entry with `promotion_count >= 2`, or any `enforceability: hard` guardrail, to this step —
those are excluded from pruning regardless of count. Any pruned entry's `draft_ref` file (if any) is
proposed for deletion alongside the registry entry — never leave an orphaned
`promotion-drafts/*.md` file with no entry pointing to it.

## 5. Graduate

For each entry (post-consolidation, post-prune) meeting its registry's maturity bar:
- **Procedures**: `promotion_count >= 2`.
- **Guardrails with `enforceability: hard`**: any count — a hard guardrail is worth enforcing on
  first occurrence.
- **Guardrails with `enforceability: soft`, and all `LESSONS.yaml` entries**: never graduated. They
  stay `status: draft` regardless of `promotion_count`, continuing to surface only via the new-task
  relevance pass.

For each graduating **hard guardrail**: queue a `graduate_guardrail.py <id>` invocation (no
`--apply` flag = propose mode) to capture its proposed mechanism/target for the aggregate diff
below — do not pass `--apply` yet.

For each graduating **procedure**: dispatch a Haiku subagent with the merged entry's full digest
(from step 3) and this test: *is this a narrow, mechanical, single-purpose task reliable enough for
a Haiku-tier model to execute alone, with no orchestration of other subagents?* If yes, invoke the
`creating-agents` skill to author a `.claude/agents/pm-<slug>.md` file (hardcoding `model: haiku`,
scoping `tools` to the minimum needed). If no — including any case of genuine doubt — write a
`.claude/skills/pm-<slug>/SKILL.md` file directly, following the imperative-step format used by the
project skills (see any existing skill in `.claude/skills/` as a template). Hold the authored file
as a proposed diff; do not write it yet.

## 6. Propose, then apply on confirm

Present one aggregate diff covering every proposal from steps 2-5: tag reconciliations, merges
(including which `draft_ref` files are combined/deleted), prunes (including which `draft_ref` files
are deleted), graduations (including the full text of any new `.claude/agents/*.md` or
`.claude/skills/*/SKILL.md` file), and the `graduate_guardrail.py` invocations queued for
hard-guardrail candidates. Nothing is written — no registry YAML, no `promotion-drafts/` file
change, no new skill/agent file, no `settings.json` change — until the user confirms.

On confirmation:
1. Write every registry YAML change, `promotion-drafts/` file change, and new skill/agent file.
2. Re-run each queued `graduate_guardrail.py <id> --apply`.
   - **If `docs/tools/graduate_guardrail.py` does not exist:** apply the guardrail graduation
     manually (add the appropriate `settings.json` hook or deny rule by hand) and note the tool is
     not installed. The registry tools are not bundled in this template — they can be obtained from
     the `new-project` skill source or added manually.
3. Run `uv run --project docs/tools python docs/tools/check_registries.py`. Fix any violation it
   reports (a bad tag merge, an orphaned `promoted_to` path, a dangling `draft_ref`) before
   considering the pass done.
   - **If `docs/tools/check_registries.py` does not exist:** manually verify: no entry has an
     `applicability` tag missing from `SEMANTICS.yaml`, no `promoted_to` path points to a
     non-existent file, no `draft_ref` points to a missing `promotion-drafts/` file.
