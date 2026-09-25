---
name: create-project
description: Create a new top-level project repository under your projects workspace root with the shared Claude/Codex docs, memory structure, and starter lifecycle skills.
argument-hint: "<repo-name> [one-line description]"
---

# create-project

Use this workspace-level skill when the user wants to create a new top-level project repository with the standard docs and memory structure.

## When to use

- User asks to create a new project, repo, or workspace
- User says "set up a new project", "bootstrap a project", or "create a repo"
- The target should be a direct child of your projects workspace root

Do not use this for repo-local tasks inside an existing project. Those project-specific skills live in each repo's own `.claude/skills/` directory and may intentionally drift toward that repo's workflow.

## What it does

Runs `scripts/bootstrap-top-level-repo.sh` to scaffold a new project directory under your projects workspace root with the standard file structure:

```
<repo-name>/
├── README.md                          # repo entry point
├── CLAUDE.md                          # Claude operating rules and working memory
├── AGENTS.md -> CLAUDE.md              # Codex operating rules symlink
├── .claude/
│   ├── settings.json              # permissions for skill scripts
│   └── skills/
│       ├── new-task/
│       │   ├── SKILL.md               # /new-task skill definition
│       │   └── scripts/
│       │       └── new-task.sh        # creates branch, episode file, updates NOTES
│       ├── code-review/
│       │   ├── SKILL.md               # /code-review skill definition
│       │   └── scripts/
│       │       └── code-review-commit.sh  # stages and commits after passing review
│       ├── closeout/
│       │   ├── SKILL.md               # /closeout skill definition
│       │   └── scripts/
│       │       └── closeout.sh        # merges branch, optional delete
│       ├── distill/
│       │   ├── SKILL.md               # /distill skill definition — promotes signals into memory + skills/tools
│       │   └── scripts/
│       │       └── tally-signals.sh   # greps episode signals into a promotion tally
│       └── drift-check/
│           ├── SKILL.md               # /drift-check skill definition — audits skills + prunes Lessons.md
│           └── scripts/
│               └── inventory.sh       # lists/diffs skills for Quick Scan vs Full Stocktake
├── .agents/
│   └── skills/
│       ├── new-task -> ../../.claude/skills/new-task
│       ├── code-review -> ../../.claude/skills/code-review
│       ├── closeout -> ../../.claude/skills/closeout
│       ├── distill -> ../../.claude/skills/distill
│       └── drift-check -> ../../.claude/skills/drift-check
└── docs/
    ├── ONBOARDING.md                  # agent onboarding procedures
    ├── TASK.md                        # task lifecycle workflow
    ├── NOTES.md                       # shared scratchpad (cleaned each session)
    ├── README.md                      # project description and state
    ├── ROADMAP.md                     # project priorities
    └── Memory/
        ├── Semantics.md               # stable facts and policies (heading + YAML entries)
        ├── Procedures.md              # refined workflow bodies, populated by /distill
        ├── Guardrails.md              # tiered enforcement registry, populated by /distill
        ├── Lessons.md                 # capped narrative lessons, populated by /distill
        ├── Archive.md                 # collapsed Procedures bodies (reference-only)
        └── Episodes/
            ├── README.md              # episode conventions + signal schema
            └── episode-template.md   # template for new episodes (includes signals: [])
```

## How to invoke

1. Ask the user for the repo name and a one-line project description if not already provided.
2. Run the bootstrap script:

Run from your projects workspace root:

```bash
bash .claude/skills/create-project/scripts/bootstrap-top-level-repo.sh "<repo-name>" "<one-line description>"
```

3. After scaffolding completes, open the new repo and prompt the user to fill in the placeholders in:
   - `docs/README.md` — project description and current state
   - `docs/ROADMAP.md` — priorities and active work
   - `CLAUDE.md` — shared Claude/Codex project-specific rules (under `## Project Rules`)
4. The bootstrap script automatically appends a stub entry to `INDEX.md` at your projects workspace root using the one-line description, creating `INDEX.md` first if it doesn't exist yet; revisit and expand the second sentence once the project has concrete state worth describing.

## Flags

- `--force` — overwrite existing files (default skips files that already exist)

## Documentation Formatting

- All docs use **Obsidian-compatible markdown** with YAML frontmatter (`tags`, `aliases`, `date`).
- Use standard markdown links `[text](relative-path.md)` for all cross-document links — **not** `[[wikilinks]]`. Standard links render on both GitHub and Obsidian graph view.
- Every entry in `Semantics.md` and `Procedures.md` must link to the episode files that support it.
- Episode files link back to promoted items and related docs via the `## Related` section.

## Notes

- The script initializes a git repo in the new directory if one does not already exist.
- `.claude/skills/` is the canonical project-local skill source for Claude.
- `.agents/skills/` contains symlinks to the same skill folders so Codex discovers the same source.
- `distill` and `drift-check` are copied into every new project but are invoked on demand only — never wired into `/new-task`, `/code-review`, or `/closeout`.
- `graduate-to-template` is a separate, projects-root-level skill (sibling to `create-project`, not copied into individual projects) — see `.claude/skills/graduate-to-template/SKILL.md` at your projects workspace root.
- `AGENTS.md` is a symlink to `CLAUDE.md` so Codex and Claude share the same repo-level operating rules.
- All `__REPO_NAME__`, `__PROJECT_DESCRIPTION__`, and `__DATE__` placeholders are replaced automatically.
- The template lives at `.claude/skills/create-project/template/top-level-repo/`.
- After scaffolding, the script appends a stub `### [<repo>](./<repo>/)` section to `INDEX.md` at your projects workspace root, creating the file first if it doesn't exist yet (skipped only if an entry for the repo is already present).
