---
name: drift-check
description: Audit every skill and agent in this project (hand-written or produced by distill/graduate-to-template) for staleness, drift, or redundancy, and prune LESSONS.md. Use periodically, or when asked for a skill audit/cleanup — never automatically.
---

# drift-check

## Modes
- **Quick Scan**: re-evaluate only skills/agents modified since the last recorded `drift-check`
  run.
- **Full Scan**: evaluate every skill and agent, and also run the LESSONS.md pruning pass (step 3).

## 1. Inventory
Run `.claude/skills/drift-check/scripts/inventory.sh` for a Full Scan, or
`.claude/skills/drift-check/scripts/inventory.sh --quick` for a Quick Scan
(reports only skills changed since the last run, via its own cache file). Also list
`.claude/agents/*.md` directly (the script only inventories `.claude/skills/*/SKILL.md`) — for
Quick Scan, narrow this to files modified since the last recorded `drift-check` run. Note the run
date and mode in the active episode's `## Log` each time this skill runs, so the next run has a
reference point.

## 2. Evaluate and verdict
For each candidate, read its `SKILL.md`/agent file and any scripts it wraps. Evaluate: is it still
accurate, does it duplicate another skill's or agent's purpose, is it stale relative to how the
project actually works now. Assign one [verdict](../../../docs/memory/VERDICTS.md)
per artifact — Keep / Improve / Update / Retire / Merge into `<target>` — each with a concrete,
evidence-based justification; "unchanged" alone is not a justification, restate why it's still
correct.

## 3. LESSONS.md pruning (Full Scan only)
Read `docs/memory/LESSONS.md`. Propose merging near-duplicate entries into one more general entry,
and retiring entries superseded by a since-promoted guardrail or procedure (link to what now
covers them). `LESSONS.md` has no graduation-based escape valve and is not part of `new-task`'s
required onboarding read, so this is its only bound over a project's life.

## 4. Present and apply
Present results as a table: artifact · verdict · justification, plus any proposed `LESSONS.md`
consolidations. Apply nothing without explicit user confirmation.

## Notes
This is the mechanism that catches drift *after* the fact — a `distill`-generated skill/agent
going stale, or two artifacts overlapping after later independent edits — complementing
`distill`'s and `graduate-to-template`'s before-creation anti-duplication checks.
