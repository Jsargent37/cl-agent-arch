---
name: distill
description: Run the on-demand, batched mining pass over the four knowledge registries (GUARDRAILS/PROCEDURES/LESSONS/SEMANTICS.md) — reconciles tags, cross-consolidates duplicates, prunes dead drafts, and graduates mature candidates to hooks/skills/agents. Use when asked to run a mining pass, or periodically to keep the registries from growing unbounded.
---

# distill

Nothing in any step below writes anything until the final aggregate confirm (step 6) — every step
only produces a proposal.

## 1. Collect

Read `docs/memory/GUARDRAILS.md`, `docs/memory/PROCEDURES.md`, `docs/memory/LESSONS.md`, and
`docs/memory/SEMANTICS.md` directly. Collect every entry across the first three registries with
`status: draft`. This step is deterministic — do it yourself, no subagent needed.

Also run `scripts/tally-signals.sh docs/episodes` to tally cross-episode `signals:` occurrences
(one `kind\tid\tcount\tepisodes` line per distinct kind+id pair). Treat an id with count ≥2 (or
count ≥1 for a `guardrail` signal noted `severity: high`) the same as a `status: draft` registry
entry for the rest of this pass, even if it has no registry entry yet — this is what lets a pattern
surface before anyone has manually drafted it. Treat any `scope: global` signal as an immediate
cross-project candidate: flag it in step 6's aggregate diff as "also consider running
`graduate-to-template`" rather than waiting for `graduate-to-template` to rediscover it later by
cross-referencing sibling registries.

## 2. Reconcile tags

Scan the collected entries' `applicability` lists for provisional tags (any tag not already a term
id in `SEMANTICS.md`). For each provisional tag found, dispatch a subagent (batch several
provisional tags into one dispatch when there are multiple) with: the tag, the entries that use it,
and the full current `SEMANTICS.md`. It proposes either:
- **Add as a new term** — a new `SEMANTICS.md` entry for the tag, or
- **Map onto an existing term** — an existing term id that means the same thing, plus the updated
  `applicability` lists for every entry that used the provisional tag.

If no provisional tags are found, record that and move to step 3 — a clean pass is a normal outcome,
not a failure.

## 3. Cross-consolidate

For every draft entry from step 1, dispatch a "digest" subagent in parallel — one per entry —
given the entry plus the full content of every episode file it cites (`docs/episodes/<id>.md`) and
its `draft_ref` file if it has one (`docs/memory/promotion-drafts/<slug>.md`). Each digest subagent
returns an in-depth summary of what the entry actually covers: real steps, commands, and code used —
not just its terse `summary`/`content` field.

Once every digest is ready, dispatch one batch-compare subagent per registry (fewer if the combined
digest volume is small enough for one subagent) with every digest from that registry. It proposes
merge groups using the [shared verdict vocabulary](../../../docs/memory/VERDICTS.md)'s
"Merge into `<target>`": entries whose digests describe the same generalizable pattern, even when
their `applicability` tags don't overlap — cross-domain duplicates must be caught, so comparison is
never scoped to shared/adjacent tags.

For every proposed merge: union the merged entries' `episodes` lists, sum their `promotion_count`,
and combine their `content`/`draft_ref`. If any merged entry has a `draft_ref` file, the proposal
names one surviving file that gets the combined content and marks the other draft file for deletion
— never leave two `promotion-drafts/*.md` files for one merged entry.

## 4. Prune

Dispatch a subagent with every entry (post-consolidation) that has `promotion_count: 1`. It
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
- **Guardrails with `enforceability: soft`, and all `LESSONS.md` entries**: never graduated. They
  stay `status: draft` regardless of `promotion_count`, continuing to surface only via the new-task
  relevance pass.

For each graduating **hard guardrail**: queue a `graduate_guardrail.py <id>` invocation (propose
mode first, to capture its proposed mechanism/target/`tier: script` for the aggregate diff below)
— do not pass `--apply` yet.

For each graduating guardrail (hard or soft) that isn't handled by `graduate_guardrail.py`
(i.e. any `review`- or `judgment`-tier candidate — `graduate_guardrail.py` only ever proposes
`script` tier): propose the `tier` (`review` or `judgment`) and `severity`
(`low`/`medium`/`high`) yourself, based on how cheaply the rule can be checked (a `/code-review`
checklist line = `review`; nothing cheaper works = `judgment`) and how costly a violation would
be. Hold this as part of the aggregate diff — the user confirms tier/severity along with
everything else in step 6.

For each graduating **procedure**: dispatch a subagent with the merged entry's full digest
(from step 3) and this test: *is this a narrow, mechanical, single-purpose task reliable enough for
a small/cheap model tier to execute alone, with no orchestration of other subagents?* If yes, invoke
the `creating-agents` skill to author a helper (Claude Code: `.claude/agents/pm-<slug>.md`,
hardcoding `model: haiku`, scoping `tools` to the minimum needed — see `creating-agents/SKILL.md`
for the platform-specific mechanics). If no — including any case of genuine doubt — author a
`.claude/skills/pm-<slug>/SKILL.md` file instead. Hold the authored file as a proposed diff; do
not write it yet.

Whenever a graduating procedure gets its own skill/agent file this way, also hold, as part of the
same proposed diff: setting that `PROCEDURES.md` entry's `distilled_into` to the new skill/agent's
id, moving its full `content` verbatim into a new same-id entry in `docs/memory/ARCHIVE.md`
(fields: `collapsed_on` (today's date), `distilled_into` (same id), `original_promotions` (the
entry's final `promotion_count`), `episodes` (copied as-is), `content` (the moved text)), and
clearing the `PROCEDURES.md` entry's own `content` to `null`. A procedure that graduates via
`graduate_guardrail.py` (guardrails only) never collapses this way — this only applies to
`PROCEDURES.md` entries gaining a dedicated skill/agent file.

## 6. Propose, then apply on confirm

Present one aggregate diff covering every proposal from steps 2-5: tag reconciliations, merges
(including which `draft_ref` files are combined/deleted), prunes (including which `draft_ref` files
are deleted), graduations (including the full text of any new `.claude/agents/*.md` or
`.claude/skills/*/SKILL.md` file, and the proposed `tier`/`severity` for every graduating
guardrail), and the `graduate_guardrail.py` invocations queued for hard-guardrail candidates.
Nothing is written — no registry file, no `promotion-drafts/` file change, no new skill/agent
file, no `settings.json` change — until the user confirms.

On confirmation:
1. Write every registry file change (including any `ARCHIVE.md` additions and the matching
   `PROCEDURES.md` collapse), `promotion-drafts/` file change, and new skill/agent file.
2. Re-run each queued `graduate_guardrail.py <id> --apply`.
3. Run `uv run --project docs/tools python docs/tools/check_registries.py`. Fix any violation it
   reports (a bad tag merge, an orphaned `promoted_to` path, a dangling `draft_ref`, a
   `distilled_into` with no matching `ARCHIVE.md` entry) before considering the pass done.
