---
tags: [reference]
---

# new-project adaptive interview

Ask only what helps; gauge depth from the answers. Stop early if the project is simple. Map each answer to a destination file.

| Ask about | Destination | If unclear |
|---|---|---|
| One-paragraph purpose / what it does | README.md, INDEX intro | leave `TODO:` in README |
| Key domain terms & acronyms | docs/memory/SEMANTICS.yaml | leave the seed terms only |
| Known conventions / rules | docs/memory/PROCEDURES.yaml (procedures) or docs/memory/GUARDRAILS.yaml (hard/soft rules) | leave the seed entries only |
| Tech stack & rough folder structure | docs/INDEX.md "Source", README "Getting started" | leave `TODO:` in INDEX |
| Uses Python? | triggers `uv venv` + `pyproject.toml` | ask once; default no |
| Want a git repo? | triggers `git init` + `.gitignore` | ask once; default no |

Principles:
- Pre-fill only what the user made clear. Never invent specifics — use a `TODO:` marker instead.
- Prefer 1–2 sentence answers; don't over-interview a small project.
- Confirm the project name and derived `<slug>` before creating anything.
