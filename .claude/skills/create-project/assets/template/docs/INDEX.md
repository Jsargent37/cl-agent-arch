---
tags: [index]
---

# Architecture Index — {{PROJECT_NAME}}

A map of the project's structure. Keep this current (`closeout` will prompt you when structure changes).

## Root
- `CLAUDE.md` — imports AGENTS.md
- `AGENTS.md` — agent working guidelines
- `README.md` — project overview

## docs/
- `ONBOARDING.md` — get-up-to-speed reading order
- `INDEX.md` — this file
- `CODE_STANDARDS.md` — engineering standards
- `BACKLOG.md` — deferred improvements
- `memory/SEMANTICS.md` — project language + applicability-tag vocabulary
- `memory/PROCEDURES.md` — repeatable multi-step procedures
- `memory/GUARDRAILS.md` — enforcement rules (hard/soft)
- `memory/LESSONS.md` — narrative/scope-limited findings
- `memory/ARCHIVE.md` — collapsed/superseded registry content, kept for `distilled_into` cross-references
- `memory/VERDICTS.md` — shared verdict vocabulary (`Keep`/`Improve`/`Update`/`Retire`/`Merge into
  <target>`) used by `distill`, `drift-check`, and `graduate-to-template` when proposing changes
- `memory/promotion-drafts/` — standalone draft content for long promotion candidates
- `episodes/` — per-task records
- `reviews/` — pr-review reports
- `tools/` — Python registry tooling: `check_registries.py`, `registry_index.py`, `graduate_guardrail.py`
  (plus their tests), managed with `uv`/`pyproject.toml`

## .claude/skills/
- `new-task/scripts/branch-if-git.sh` — per-episode branch creation
- `code-review/scripts/code-review-commit.sh` — PASS-gated commit
- `closeout/scripts/merge-if-git.sh` — episode-branch merge/cleanup
- `distill/scripts/tally-signals.sh` — signal tally across episodes
- `drift-check/scripts/inventory.sh` — structure drift inventory

## Source
TODO: document the code/source layout here as it is created.
