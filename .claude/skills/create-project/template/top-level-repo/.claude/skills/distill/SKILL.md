---
name: distill
description: Promote episode signals into Procedures/Guardrails/Lessons entries and, when warranted, into project skills/tools/agents. Run on demand only — never automatically.
---

# distill

Use this skill to promote corroborated episode `signals` into memory
entries, and to extract heavily-used or complex procedures into full
skills or tools.

## When to use

- The user explicitly asks to run `/distill`, "promote memory", or "turn
  this procedure into a skill"
- **Never** run this automatically as part of `/closeout` or on a schedule
  — it is always a deliberate, separate invocation.

## What it does

1. Tally signals across episodes:
   ```bash
   bash .claude/skills/distill/scripts/tally-signals.sh docs/Memory/Episodes
   ```
   This prints `kind<TAB>id<TAB>count<TAB>episode-files` rows — the derived
   staging queue. Nothing is stored between runs; it's recomputed live.
2. For each row crossing its category's promotion gate (see
   [Episodes/README](../../../docs/Memory/Episodes/README.md)):
   - **procedure** — write or update the refined-body entry in
     `docs/Memory/Procedures.md` (heading + YAML block: `promotions`,
     `description`, `steps`, `episodes`, `created`, `updated`, `origin`,
     `distilled_into`). If the `id` already has `distilled_into` set (it's
     already a skill/tool) and newer episodes diverge from that artifact,
     propose a revision to the artifact instead of editing the registry
     entry directly.
   - **guardrail** — propose a `tier` (`script`/`review`/`judgment`) and
     `severity` (`low`/`medium`/`high`); apply the judgment-call gate (1
     episode if high-severity/cheap-to-route, else ≥2); write the entry to
     `docs/Memory/Guardrails.md`. If tier is `script`, also propose a
     pre-commit hook stub; if `review`, propose a `/code-review` checklist
     line.
   - **lesson** — write or update the entry in `docs/Memory/Lessons.md`,
     `takeaway` capped at 5 lines.
3. **Anti-duplication check, before creating any new skill/tool/agent:**
   read the descriptions in every existing `.claude/skills/*/SKILL.md`,
   `.claude/agents/*.md`, and `scripts/*` file. If the candidate procedure
   overlaps in purpose with an existing artifact — not just an exact `id`
   match, a similar description or purpose — propose **Update** or
   **Merge** into that artifact instead of creating a new one. Use the
   same verdict vocabulary as `/drift-check`: Keep / Improve / Update /
   Retire / Merge-into-\<target\>.
4. Decide whether a procedure is complex/reused enough to extract into a
   full skill (`.claude/skills/<id>/SKILL.md`) or tool
   (`scripts/<id>.sh`) — this is a judgment call informed by step count and
   recurrence, not a fixed threshold. Most procedures stay as a refined
   registry entry; only extract when the entry has grown into something
   genuinely worth loading on demand rather than reading inline.
5. **Present a report of every proposed write, extraction, and collapse.
   Write nothing without explicit user confirmation.**
6. On approval:
   - Write the memory-file changes.
   - Create or update any skills/tools/agents.
   - For a procedure that just graduated: set its Procedures.md entry's
     `distilled_into` to the new artifact id, collapse `steps` to `null`,
     and move the full pre-collapse YAML block to `docs/Memory/Archive.md`
     under a new `### <entry-name>` heading with `collapsed_on`,
     `distilled_into`, `original_promotions`, and `episodes` fields.

## Notes

- `distill` never runs as part of `/closeout` and is never scheduled.
- Semantics.md is not part of this pipeline — it is promoted directly
  during `/closeout` (see `docs/Memory/Semantics.md`'s Update Rule).
