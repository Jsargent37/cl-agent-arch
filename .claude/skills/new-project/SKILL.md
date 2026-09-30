---
name: new-project
description: Scaffold a new project folder with the standard documentation + memory architecture (root CLAUDE.md/AGENTS.md/README.md; docs with ONBOARDING/INDEX/CODE_STANDARDS/BACKLOG/memory/episodes/reviews), the project-scoped skills, and a settings.json policy. Use when starting, bootstrapping, or setting up a new project.
---

# new-project

Scaffolds a new project from the bundled template in `assets/template/`.

## 1. Locate the Projects root
The Projects root is two levels up from this skill folder (`…/.claude/skills/new-project` → the parent of `.claude`). New projects are created as subfolders there. Confirm the root with the user if ambiguous.

## 2. Name + slug
Ask for the project name. Derive a kebab-case `<slug>`. Verify `<root>/<slug>` does not already exist.

## 3. Adaptive interview
Follow [reference/interview.md](reference/interview.md). Cover purpose, key terms, known rules, tech stack & structure, Python?, git? Ask only what helps; gauge depth from the answers.

## 4. Copy + substitute
Copy the entire `assets/template/` tree **recursively, including dotfiles** (`.claude/`, `.gitkeep`) → `<root>/<slug>/`. Then in every copied file replace `{{PROJECT_NAME}}`, `{{SLUG}}`, `{{DATE}}` (today, `YYYY-MM-DD`), and `{{PROJECT_ABS_PATH}}` (the absolute filesystem path of the new project folder, `<root>/<slug>`, OS-native separators). See [reference/md-conventions.md](reference/md-conventions.md) for link and frontmatter conventions to follow in generated files.

> **Note:** `docs/episodes/_TEMPLATE.md` intentionally contains no `{{ }}` tokens — leave its `YYYY-MM-DD` / `<slug>` / `<session-name>` placeholders untouched for `new-task` to fill per task.

`.claude/settings.local.json` sets `autoMemoryDirectory` to `<PROJECT_ABS_PATH>/docs/memory/claude` so the project's auto-memory stays local to the project instead of the global default. This must be an absolute path — a relative one won't resolve correctly outside this project's working directory.

## 5. Pre-fill (adaptive)
Fill what the interview made clear — README overview, INDEX structure, additional `SEMANTICS.yaml` terms, additional `PROCEDURES.yaml`/`GUARDRAILS.yaml` entries (same schema as the seed entries already in the template — `id`/`summary`/`applicability`/`status: draft`/`promotion_type: null`/`promoted_to: null`/`promotion_count: 1`/`episodes: []`/`content`; GUARDRAILS entries also need `enforceability: hard|soft` and `hook: null`). Any new `applicability` tag must first exist as an `id` in `SEMANTICS.yaml` — add the term there before referencing it. Where something is unclear, leave a `TODO:` marker — never invent specifics.

## 6. Conditionals
- **Python:** run `uv venv` in the project and create a `pyproject.toml` (project name + metadata).
- **Git:** if wanted, `git init` and write a `.gitignore` (include `.venv/`, `__pycache__/`, `.DS_Store`, editor cruft).

## 7. Register
Append an entry to `<root>/PROJECTS.md` — `- [{{PROJECT_NAME}}](<slug>/README.md) — <one-line purpose> (created {{DATE}})`. Create `PROJECTS.md` (with frontmatter `tags: [registry]` and a `# Projects` heading) if it does not exist.

## 8. Report
Summarize what was created, list outstanding `TODO:` markers, and suggest running `/new-task` in the new project to begin.
