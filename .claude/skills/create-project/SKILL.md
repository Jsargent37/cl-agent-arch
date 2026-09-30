---
name: create-project
description: Scaffold a new project folder with the standard documentation + memory architecture (root CLAUDE.md/AGENTS.md/README.md; docs with ONBOARDING/INDEX/CODE_STANDARDS/BACKLOG/memory/episodes/reviews), the project-scoped skills mirrored into both .claude/skills/ and .agents/skills/, and a settings.json policy. Use when starting, bootstrapping, or setting up a new project.
---

# create-project

Scaffolds a new project from the bundled template in `assets/template/`.

## When to use
- User asks to create a new project, repo, or workspace as a direct child of the projects root.
- Not for repo-local tasks inside an existing project — those use that project's own
  `.claude/skills/`.

## 1. Locate the projects root
The projects root is two levels up from this skill folder (`…/.claude/skills/create-project` →
the parent of `.claude`). New projects are created as subfolders there. Confirm the root with the user if ambiguous.

## 2. Name + slug
Ask for the project name. Derive a kebab-case `<slug>`. Verify `<root>/<slug>` does not already
exist, unless `--force` is given (overwrite existing files; default skips files that already
exist).

## 3. Adaptive interview
Follow [reference/interview.md](reference/interview.md). Cover purpose, key terms, known rules,
tech stack & structure, Python?, git? Ask only what helps; gauge depth from the answers.

## 4. Copy + substitute
Copy the entire `assets/template/` tree **recursively, including dotfiles** (`.claude/`,
`.gitkeep`) → `<root>/<slug>/`. Then in every copied file replace `{{PROJECT_NAME}}`, `{{SLUG}}`,
`{{DATE}}` (today, `YYYY-MM-DD`), and `{{PROJECT_ABS_PATH}}` (the absolute filesystem path of the
new project folder, `<root>/<slug>`, OS-native separators). See
[reference/md-conventions.md](reference/md-conventions.md) for link and frontmatter conventions.

> **Note:** `docs/episodes/_TEMPLATE.md` intentionally contains no `{{ }}` tokens — leave its
> `YYYY-MM-DD` / `<slug>` / `<session-name>` placeholders untouched for `new-task` to fill per task.

`.claude/settings.local.json` sets `autoMemoryDirectory` to `<PROJECT_ABS_PATH>/docs/memory/claude`
so the project's auto-memory stays local to the project instead of the global default. This must
be an absolute path.

Mirror every copied `.claude/skills/<name>/` directory as `.agents/skills/<name>` (a directory
junction on Windows via `mklink /J`, a symlink on POSIX) so a Codex-style agent discovers the same
skills without a second copy.

## 5. Pre-fill (adaptive)
Fill what the interview made clear — README overview, INDEX structure, additional `SEMANTICS.md`
terms, additional `PROCEDURES.md`/`GUARDRAILS.md` entries (same schema as the seed entries already
in the template). Any new `applicability` tag must first exist as an entry id in `SEMANTICS.md` —
add the term there before referencing it. Where something is unclear, leave a `TODO:` marker —
never invent specifics.

## 6. Conditionals
- **Python:** run `uv venv` in the project and create a `pyproject.toml` (project name +
  metadata).
- **Git:** if wanted, `git init` and write a `.gitignore` (include `.venv/`, `__pycache__/`,
  `.DS_Store`, editor cruft).

## 7. Register
Append an entry to `<root>/PROJECTS.md` — `- [{{PROJECT_NAME}}](<slug>/README.md) — <one-line
purpose> (created {{DATE}})`. Create `PROJECTS.md` (with frontmatter `tags: [registry]` and a
`# Projects` heading) if it does not exist.

## 8. Report
Summarize what was created, list outstanding `TODO:` markers, and suggest running `new-task` in
the new project to begin.

## Notes
- `.claude/skills/` is the canonical project-local skill source; `.agents/skills/` mirrors it
  (step 4) for platform-agnostic discovery.
- The template lives at `.claude/skills/create-project/assets/template/`.
- All `{{PROJECT_NAME}}`, `{{SLUG}}`, `{{DATE}}`, and `{{PROJECT_ABS_PATH}}` placeholders are
  replaced automatically.
