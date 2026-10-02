---
tags: [onboarding]
---

# Onboarding — {{PROJECT_NAME}}

Read these in order to get up to speed. This is the curated layer — you do NOT need to read every episode.

1. [AGENTS.md](../AGENTS.md) — working guidelines
2. [CODE_STANDARDS.md](CODE_STANDARDS.md) — engineering standards
3. [README.md](../README.md) — what this project is
4. [INDEX.md](INDEX.md) — architecture / folder & file map
5. [memory/SEMANTICS.md](memory/SEMANTICS.md) — project language (terms, acronyms) + applicability-tag vocabulary
6. [memory/PROCEDURES.md](memory/PROCEDURES.md), [memory/GUARDRAILS.md](memory/GUARDRAILS.md), [memory/LESSONS.md](memory/LESSONS.md) — project working rules, guardrails, and lessons
7. Skim [BACKLOG.md](BACKLOG.md) — deferred work

Then pull a specific episode from `episodes/` only if it is relevant to your task.

## Markdown conventions (Obsidian + VSCode)
All docs use YAML frontmatter `tags:` and standard relative Markdown links so they render in both VSCode preview and Obsidian. Key rules:
- **Every link must point to a specific openable file** — `[text](relative/path.md)`, resolved from the linking file's location.
- **Never link a bare folder** — link its `README.md`/`INDEX.md` instead, or use inline code (`` `path/` ``) if there's nothing worth opening.
- **Never use `[[wikilinks]]`** in body text — the only exception is the `related:` frontmatter property.

Full rules: `reference/md-conventions.md` in the `create-project` skill folder (outside this project). In Obsidian: Settings → Files & Links → "Use [[Wikilinks]]" OFF, "New link format" = Relative path. Open the folder containing your projects as the vault.

## Working
Use `new-task` to onboard and open an episode; `closeout` to finalize. Reviews: `code-review` (quick), `pr-review` (triaged report), `agent-code-review` (deep, fixes in a loop).
