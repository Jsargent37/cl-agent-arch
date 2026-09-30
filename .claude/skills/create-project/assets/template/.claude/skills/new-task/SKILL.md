---
name: new-task
description: Get up to speed on this project and start a new task. Runs a brief goal/scope interview, reads the curated docs (AGENTS, CODE_STANDARDS, README, INDEX), dispatches the registry-relevance-check agent to load only applicable knowledge-registry entries, then creates a dated episode file capturing the task goal and plan. Use at the start of any new task or work session in this project.
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

Then load relevant registry entries using whichever path is available:

**If `docs/tools/registry_index.py` exists (fast path):**
- Run `uv run --project docs/tools python docs/tools/registry_index.py --index`.
- Dispatch the `registry-relevance-check` agent with the task's brief goal/scope (from step 1) and
  the index output.
- If it returns any entry ids, run
  `uv run --project docs/tools python docs/tools/registry_index.py --fetch <id> [<id> ...]` and read
  the result — for any entry whose output shows a `draft_ref` path (instead of inline content), open
  that `docs/memory/promotion-drafts/<slug>.md` file directly. Only these matched entries' full
  content loads into context.
- A relevance pass returning zero matches is normal (new project, novel task) — proceed with no
  loaded registry content.

**If `docs/tools/registry_index.py` does not exist (fallback):**
- Read all four registries in full: `docs/memory/GUARDRAILS.yaml`, `docs/memory/PROCEDURES.yaml`,
  `docs/memory/LESSONS.yaml`, `docs/memory/SEMANTICS.yaml`.
- Mention to the user that the registry tools are not installed. The tools are not bundled in this
  template — they can be obtained from the `new-project` skill source or added manually. Offer to
  proceed with the full-read fallback, which is functionally equivalent for most projects.

## 3. Recap
Give the user a short "here's what I understand about this project and your task" recap to confirm
onboarding worked — mention any matched registry entries from step 2.

## 4. Capture the task
Interview fully for Goal/Scope and an initial Plan (expanding on step 1's brief version).
- **Big task** (multi-step, multi-file, design open): run a dedicated brainstorming pass, then
  write a plan document and link it in the episode's `## Plan`.
- **Small task:** write the Plan inline in the episode.

## 5. Open the episode
- Determine today's date (`YYYY-MM-DD`) and a short kebab-case `<slug>`.
- Copy `docs/episodes/_TEMPLATE.md` to `docs/episodes/{date}-{slug}.md` (if it exists, append `-2`,
  `-3`, …).
- Fill the frontmatter (`date`, `session`, `status: active`) and the `## Goal / Scope` and `## Plan`
  sections.

## 6. Work
As you work, keep these episode sections current: `## Log` (key decisions), `## Files touched`
(every file you create/edit), and `## Promotion candidates` (terms/rules worth promoting). Finish
with the `closeout` skill.
