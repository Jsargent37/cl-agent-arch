---
tags: [guidelines]
---

# {{PROJECT_NAME}} — Agent Guidelines

These are the working guidelines for every agent in this project. CLAUDE.md imports this file, so this is the single source of guidelines.

## Getting started
New here? Read [docs/ONBOARDING.md](docs/ONBOARDING.md) first. To start a task, use the `new-task` skill; to finish, use `closeout`.

## Engineering standards
Follow [docs/CODE_STANDARDS.md](docs/CODE_STANDARDS.md) for all code you write or review. It is the canonical, universal standard.

## How we work
- Project language + applicability tags: [docs/memory/SEMANTICS.md](docs/memory/SEMANTICS.md).
- Procedures, guardrails, and lessons: [docs/memory/PROCEDURES.md](docs/memory/PROCEDURES.md),
  [docs/memory/GUARDRAILS.md](docs/memory/GUARDRAILS.md),
  [docs/memory/LESSONS.md](docs/memory/LESSONS.md).
- Every task is recorded as an *episode* in `docs/episodes/`. Keep the active episode's `## Log`, `## Files touched`, and `## Promotion candidates` current as you work.

## Python (whenever Python is used)
- Use a local `uv` virtual environment (`.venv`) and maintain `pyproject.toml`.
- Manage dependencies with `uv add`; run code with `uv run`.
- Never install into or use a global/system Python. `pip install` is denied by settings.

## Project skills
`new-task` · `code-review` · `pr-review` · `agent-code-review` · `closeout` · `distill` · `drift-check` · `creating-agents` (see [docs/ONBOARDING.md](docs/ONBOARDING.md)).
