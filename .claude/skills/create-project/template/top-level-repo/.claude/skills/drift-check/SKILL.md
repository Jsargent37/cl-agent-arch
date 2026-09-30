---
name: drift-check
description: Audit all skills/agents/tools (hand-written or produced by distill/graduate-to-template) for staleness, drift, or redundancy. Also prunes Lessons.md. Run on demand only.
---

# drift-check

Use this skill to periodically audit every skill, agent, and tool in the
repo — regardless of whether it was hand-written, produced by `/distill`,
or promoted from another project — for quality and redundancy.

## When to use

- The user explicitly asks for a skill audit, drift check, or cleanup
- Periodically, at the user's discretion — never automatically

## Modes

- **Quick Scan** (5–10 min): re-evaluate only skills modified since the
  last run.
  ```bash
  bash .claude/skills/drift-check/scripts/inventory.sh --quick
  ```
- **Full Scan** (20–30 min): evaluate every skill.
  ```bash
  bash .claude/skills/drift-check/scripts/inventory.sh
  ```

## What it does

1. Run the inventory script for the chosen mode to get the candidate list.
2. For each candidate, read its `SKILL.md` and any scripts it wraps.
   Evaluate against a checklist: is it still accurate, does it duplicate
   another skill's purpose, is it stale relative to how the repo actually
   works now.
3. Assign one verdict per artifact: **Keep** (useful and current),
   **Improve** (needs specific changes — name them), **Update** (outdated
   references — name them), **Retire** (low quality/stale — say why),
   **Merge into \<target\>** (overlapping content — name the target).
   Every verdict needs a concrete, evidence-based justification — "unchanged"
   alone is not a justification; restate why it's still correct.
4. Present results in a table: artifact, verdict, justification.
5. **Lessons.md pruning (Full Scan only):** read
   `docs/Memory/Lessons.md`. Propose merging near-duplicate entries into
   one more general entry, and retiring entries superseded by a
   since-promoted guardrail or procedure (link to what now covers them).
   Lessons.md has no graduation-based escape valve and is not a required
   onboarding read, so this is its only bound over a project's life.
6. **Present all proposed consolidations. Apply nothing without user
   confirmation.**

## Notes

- This is the mechanism that catches drift *after* the fact — a
  `distill`-generated skill going stale, or two artifacts overlapping
  after later independent edits — complementing `distill`'s and
  `graduate-to-template`'s before-creation anti-duplication checks.
