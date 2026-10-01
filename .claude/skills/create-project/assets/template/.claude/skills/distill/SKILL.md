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

Also run `.claude/skills/distill/scripts/tally-signals.sh docs/episodes` to tally cross-episode
`signals:` occurrences (one `kind\tid\tcount\tscope\tseverity\tepisodes` line per distinct kind+id
pair — `scope` is `global` if any contributing signal said `scope: global`, else `project`;
`severity` is the highest severity seen across contributing signals, or empty if none specified).
Treat an id with count ≥2, or a `guardrail` signal with `severity: high` (readable directly off the
`severity` column — no need to re-parse raw episode files), the same as a `status: draft` registry
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

For each graduating **hard guardrail**, first decide its `tier` yourself, BEFORE deciding how to
route it:
- **`script`** — the rule has a concrete, checkable condition and action: a specific command,
  file pattern, or tool call that a `PreToolUse` hook or permission rule could mechanically block
  or allow. Only a `script`-tier candidate is eligible for `graduate_guardrail.py`.
- **`review`** — the rule is cheaply checkable by a human or reviewing agent but not by a simple
  mechanical condition (e.g. a `/code-review` checklist line).
- **`judgment`** — the rule is a human-judgment rule stated in prose, with no CLI verb or checkable
  condition at all (e.g. `follow-code-standards` in the template's seed `GUARDRAILS.md` — "follow
  CODE_STANDARDS.md for all code" has nothing a hook could check, so it lands here, never
  `script`, regardless of how often it's cited).

Also always propose a `severity` (`low`/`medium`/`high`) for every graduating guardrail, based on
how costly a violation would be — this applies to all three tiers, not just `script`.

Only after tier is decided:
- **`script`-tier**: queue a `graduate_guardrail.py <id> --severity <severity>` invocation (propose
  mode first, to capture its proposed mechanism/target for the aggregate diff below) — do not pass
  `--apply` yet. `graduate_guardrail.py` stamps `tier: script` itself; never route a `review`- or
  `judgment`-tier candidate to it.
- **`review`/`judgment`-tier**: these graduate as plain registry entries, without going through
  `graduate_guardrail.py` — there is no hook or permission-rule artifact to generate. Hold the
  proposed entry update as part of the aggregate diff: `status: promoted`, `promotion_type: null`
  (the guardrail isn't becoming a skill/hook/agent file — `promotion_type` only names that kind of
  artifact; `tier` already records that this graduated as `review`/`judgment`), `promoted_to: null`
  (no external artifact — the registry entry itself is the enforcement record), `tier` and
  `severity` as decided above.

The user confirms tier/severity, and the resulting registry update, along with everything else in
step 6.

For each graduating **procedure**: dispatch a subagent with the merged entry's full digest
(from step 3) and this test: *is this a narrow, mechanical, single-purpose task reliable enough for
a small/cheap model tier to execute alone, with no orchestration of other subagents?* If yes, invoke
the `creating-agents` skill to author a `pm-<slug>` helper (see its `## Platform mechanics` section
for the file location and required frontmatter on this project's platform). If no — including any case of genuine doubt — author a
`.claude/skills/pm-<slug>/SKILL.md` file instead. Hold the authored file as a proposed diff; do
not write it yet.

Whenever a graduating procedure gets its own skill/agent file this way, also hold, as part of the
same proposed diff: setting that `PROCEDURES.md` entry's `distilled_into` to the new skill/agent's
id, moving its full `content` verbatim into a new same-id entry in `docs/memory/ARCHIVE.md`
(fields: `collapsed_on` (today's date), `distilled_into` (same id), `original_promotions` (the
entry's final `promotion_count`), `episodes` (copied as-is), `content` (the moved text)), and
clearing the `PROCEDURES.md` entry's own `content` to `null`. Also set the SAME
`status`/`promotion_type`/`promoted_to` fields on the `PROCEDURES.md` entry that a normal
(non-collapsed) graduation would set (`status: promoted`, `promotion_type` describing the
skill/agent mechanism, `promoted_to` the new skill/agent **file's path** — e.g.
`.claude/skills/pm-<slug>/SKILL.md` or `.claude/agents/pm-<slug>.md`, not a bare id/name, since
`check_registries.py` requires `promoted_to` to resolve to an actual file) — a collapsed entry must be
recognized as already-promoted, the same as any other graduated entry, so a future `distill` pass
never re-collects or re-graduates it. A procedure that graduates via `graduate_guardrail.py`
(guardrails only) never collapses this way — this only applies to `PROCEDURES.md` entries gaining
a dedicated skill/agent file.

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
2. Re-run each queued `graduate_guardrail.py <id> --severity <severity> --apply`.
3. Run `uv run --project docs/tools python docs/tools/check_registries.py`. Fix any violation it
   reports (a bad tag merge, an orphaned `promoted_to` path, a dangling `draft_ref`, a
   `distilled_into` with no matching `ARCHIVE.md` entry) before considering the pass done.
