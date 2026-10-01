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
The projects root is three levels up from this skill folder (`…/.claude/skills/create-project` →
the parent of `.claude`). New projects are created as subfolders there. Confirm the root with the
user if ambiguous.

## 2. Name + slug
Ask for the project name. Derive a kebab-case `<slug>`. Verify `<root>/<slug>` does not already
exist, unless `--force` is given (overwrite existing files; default skips files that already
exist).

## 3. Adaptive interview
Follow [reference/interview.md](reference/interview.md). Cover purpose, key terms, known rules,
tech stack & structure, Python?, git? Ask only what helps; gauge depth from the answers.

## 4. Copy + substitute
Run `.claude/skills/create-project/scripts/scaffold.sh <slug> "<project-name>" "<project-abs-path>"`
(add `--force` to overwrite
existing files, `--python`/`--git` per step 6's conditionals). It copies `assets/template/`
**recursively, including dotfiles** into `<project-abs-path>`, substitutes `{{PROJECT_NAME}}`,
`{{SLUG}}`, `{{DATE}}`, and `{{PROJECT_ABS_PATH}}` in every file except
`docs/episodes/_TEMPLATE.md` (left untouched for `new-task` to fill per task — see
[reference/md-conventions.md](reference/md-conventions.md) for link and frontmatter conventions),
and mirrors every `.claude/skills/<name>/` as `.agents/skills/<name>` (a directory junction on
Windows, a symlink on POSIX) so a Codex-style agent discovers the same skills without a second
copy.

`.claude/settings.local.json` sets `autoMemoryDirectory` to `<PROJECT_ABS_PATH>/docs/memory/claude`
so the project's auto-memory stays local to the project instead of the global default. This must
be an absolute path — the script's `{{PROJECT_ABS_PATH}}` substitution handles it automatically.

## 5. Pre-fill (adaptive)
Fill what the interview made clear — README overview, INDEX structure, additional `SEMANTICS.md`
terms, additional `PROCEDURES.md`/`GUARDRAILS.md` entries (same schema as the seed entries already
in the template, including `distilled_into: null` on any new `PROCEDURES.md` entry). Any new
`applicability` tag must first exist as an entry id in `SEMANTICS.md` — add the term there before
referencing it. Where something is unclear, leave a `TODO:` marker — never invent specifics. The
script never does this step — it only copies and substitutes; this pass is agent judgment.

## 6. Conditionals
Re-run step 4's `scaffold.sh` invocation with `--python` and/or `--git` added, or run it once
up front with both flags if the interview already answered these — the script is idempotent
(skips existing files unless `--force`). `--python` runs `uv venv`; `--git` runs `git init`, writes
a `.gitignore`, and makes an initial commit. Never run `--git` unless the user wants this project
git-tracked — nothing else in this template requires it.

## 7. Register
`scaffold.sh` already appended a stub entry to `<root>/PROJECTS.md` during step 4 — replace its
`TODO: one-line purpose` with a real one now that the interview/pre-fill passes are done.

## 8. Report
Summarize what was created, list outstanding `TODO:` markers, and suggest running `new-task` in
the new project to begin.

## Notes
- `.claude/skills/` is the canonical project-local skill source; `.agents/skills/` mirrors it
  (step 4, via the script) for platform-agnostic discovery.
- The template lives at `.claude/skills/create-project/assets/template/`; the scaffolding mechanics
  live at `.claude/skills/create-project/scripts/scaffold.sh` — modify the script for mechanical
  changes (new placeholder tokens, registration format), modify this SKILL.md for judgment-driven
  steps (interview, pre-fill).
- All `{{PROJECT_NAME}}`, `{{SLUG}}`, `{{DATE}}`, and `{{PROJECT_ABS_PATH}}` placeholders are
  replaced automatically by the script.
