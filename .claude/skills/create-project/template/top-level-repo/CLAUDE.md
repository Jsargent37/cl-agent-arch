# __REPO_NAME__ — Claude

Last updated: __DATE__

## Operating Rules

- Read [Onboarding](docs/ONBOARDING.md), [Task Workflow](docs/TASK.md), and [Project README](docs/README.md) before making any substantive changes.
- Every task starts on a new branch. Never implement directly on the default branch.
- Record the implementation plan in the episode file **before** coding begins.
- Code review happens before testing. Testing happens before user review.
- Present changes to the user for approval before starting closeout.
- Use [Notes](docs/NOTES.md) as the shared scratchpad during active work.
- At session end: write or update the episode, promote durable learnings only if supported by two or more episodes, and clean [Notes](docs/NOTES.md).

## Task Lifecycle (summary)

1. Read required docs in order ([Onboarding](docs/ONBOARDING.md) → [Task Workflow](docs/TASK.md) → [Project README](docs/README.md) → [Roadmap](docs/ROADMAP.md) → [Semantics](docs/Memory/Semantics.md) → [Procedures](docs/Memory/Procedures.md) → recent [Episodes](docs/Memory/Episodes/README.md)).
2. Create a branch. Write the implementation plan to the episode and [Notes](docs/NOTES.md).
3. Implement → review → test → present to user.
4. On approval: write episode, consider memory promotion, clean [Notes](docs/NOTES.md), merge.

Full details: [Onboarding](docs/ONBOARDING.md) and [Task Workflow](docs/TASK.md).

## Memory Promotion Rule

- [Semantics](docs/Memory/Semantics.md) — stable facts, updated only when supported by at least two episode files. Promoted directly during `/closeout`.
- [Procedures](docs/Memory/Procedures.md) — repeatable workflows, updated only when supported by at least two episode files. Populated by running `/distill` **on demand** — never automatically during `/closeout`.
- [Guardrails](docs/Memory/Guardrails.md) — hard must/must-not rules, routed to a script/review/judgment enforcement tier. Promotion is a judgment call (severity/friction), not a fixed count. Populated by `/distill`, on demand.
- [Lessons](docs/Memory/Lessons.md) — what worked/failed, capped at 5 lines per entry, updated only when supported by at least two episode files. Populated by `/distill`, on demand.
- Single-episode learnings stay in the episode history until corroborated, except judgment-gated guardrails — see [Guardrails](docs/Memory/Guardrails.md).
- **Every promoted entry must include links to the supporting episode files.**
- `/distill` and `/graduate-to-template` are invoked deliberately by the user or agent — they are never part of `/closeout`'s mandatory sequence and never run on a schedule.

## Obsidian Formatting

- All documentation uses Obsidian-compatible markdown formatting.
- Use standard markdown links `[text](relative-path.md)` for cross-document links (renders on both GitHub and Obsidian graph view).
- Use YAML frontmatter with `tags`, `aliases`, and `date` properties on every doc.
- Use `#tag` and `#tag/subtag` in frontmatter for categorization.
- The `docs/` folder is structured as an Obsidian vault — the graph view should show connected documents.

## Git Workflow

- NEVER work on main. Always create a feature branch first.
- Follow: create branch → make changes → commit → merge to main.

## Deployment

- Always use `--build` when deploying Docker containers. Never use `--no-build` unless explicitly told.
- Do NOT use invalid or unverified CLI flags. Verify flag validity before running.
- When deploying to headless/remote servers, never run interactive commands over non-interactive SSH.

## Shell Scripts

- Avoid `set -e` with `&&` patterns — failures become silent.
- Failing to push to a nonexistent remote is acceptable. Check before pushing and handle gracefully — do not error out.
- Never use interactive `read` prompts in scripts that may run non-interactively. Use timeouts or defaults.

## Testing

- After writing or editing any shell script, immediately run it with a simple test case and fix errors before moving on.
- For Python files, run `pytest`. Do not proceed to the next step until the current file works.

## Project Rules

- Add project-specific rules here.
- Add any global rules that apply in this repo.

## Before Compact

- Dump key context, decisions, failed attempts, and open questions into [Notes](docs/NOTES.md) before running `/compact`.
