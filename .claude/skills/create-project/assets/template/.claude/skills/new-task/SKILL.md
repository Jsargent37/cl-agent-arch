---
name: new-task
description: Start a new task in this project. Confirms the goal/scope, reads the required onboarding docs, runs a registry relevance check to load only applicable knowledge-registry entries, creates a task branch when the project is a git repo, then opens a dated episode file capturing the task's goal and plan. Use at the start of any new task or work session in this project.
---

# new-task

## 1. Brief interview
Ask just enough to state the task's goal/scope in a sentence or two — not the full interview
(that's step 4). This drives the registry relevance check in step 2.

## 2. Onboard (curated layer + relevant registry entries)
Read, in order: `AGENTS.md`, `docs/CODE_STANDARDS.md`, `README.md`, `docs/INDEX.md`; skim
`docs/BACKLOG.md`. Do NOT read every episode — durable knowledge has been promoted into the
registries. Pull a specific episode from `docs/episodes/` only if it is clearly relevant to this
task.

Then run the registry relevance check instead of reading all four registries in full:
- Run `uv run --project docs/tools python docs/tools/registry_index.py --index`.
- Dispatch a subagent (or perform the check yourself if no subagent mechanism is available) with
  the task's brief goal/scope (from step 1) and the index output, asking it to name only the
  entry ids relevant to this task.
- If it returns any entry ids, run
  `uv run --project docs/tools python docs/tools/registry_index.py --fetch <id> [<id> ...]` and read
  the result — for any entry whose output shows a `draft_ref` path (instead of inline content), open
  that `docs/memory/promotion-drafts/<slug>.md` file directly. Only these matched entries' full
  content loads into context.
- A relevance pass returning zero matches is normal (new project, novel task) — proceed with no
  loaded registry content, no special-casing.

## 3. Recap
Give the user a short "here's what I understand about this project and your task" recap to confirm
onboarding worked — mention any matched registry entries from step 2.

## 4. Capture the task
Interview fully for Goal/Scope and an initial Plan (expanding on step 1's brief version).
- **Big task** (multi-step, multi-file, design open): run a structured design/brainstorming pass
  before writing the plan, then produce a written implementation plan — link the resulting plan
  file in the episode's `## Plan`.
- **Small task:** write the Plan inline in the episode.

## 5. Open the episode
- Determine today's date (`YYYY-MM-DD`) and a short kebab-case `<slug>`.
- Copy `docs/episodes/_TEMPLATE.md` to `docs/episodes/{date}-{slug}.md` (if it exists, append `-2`,
  `-3`, …).
- Fill the frontmatter (`date`, `session`, `status: active`, `branch: null`, `signals: []`) and the
  `## Goal / Scope` and `## Plan` sections.

## 6. Branch (conditional)
Run `.claude/skills/new-task/scripts/branch-if-git.sh {date}-{slug}` (the same `{date}-{slug}` from
step 5, so the branch name and episode filename always match). It reports one of: `not-a-git-repo`
(this project isn't git-tracked — proceed with no branch, exactly as today), `already-on-task-branch`
(a task branch is already checked out — don't nest a second one), or `created-branch` (the new
branch is now checked out). Never run `git init` yourself to force this step to apply — an ungated
project simply skips it. If (and only if) it reports `created-branch`, set the episode's `branch:`
frontmatter field to `{date}-{slug}` — this is what lets `closeout` later verify it's merging the
right branch.

## 7. Work
As you work, keep these episode sections current: `## Log` (key decisions), `## Files touched`
(every file you create/edit), `## Promotion candidates` (terms/rules worth promoting), and
`signals:` (one entry per reusable pattern, per the schema comment in `_TEMPLATE.md` — most tasks
add none). Finish with the `closeout` skill.
