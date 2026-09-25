# cl-agent-arch

A self-contained Claude Code toolkit for scaffolding and maintaining a
workspace of independent project repos, each with a shared memory and
lifecycle architecture — episodes that promote into procedures,
guardrails, and lessons, with on-demand extraction into skills and tools
once a pattern proves itself.

This repo *is* your projects workspace root: clone it, and `.claude/` —
the toolkit itself — is already in place at the top level. Every
subdirectory you create alongside it (each an independent project) is
automatically excluded from this repo's own git history; nothing you
build in them ever needs any git configuration of its own to stay out of
this repo.

## What's included

- **`.claude/skills/create-project/`** — scaffolds a new top-level project
  repo with the shared `docs/`, `CLAUDE.md`, and memory-lifecycle
  structure (`new-task`, `code-review`, `closeout`, `distill`,
  `drift-check`).
- **`.claude/skills/graduate-to-template/`** — promotes a skill, tool,
  agent, or guardrail that's proven itself across multiple of your
  projects up into the shared template, so every future project inherits
  it.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- The [`superpowers`](https://github.com/obra/superpowers) Claude Code
  plugin, installed from its marketplace — projects scaffolded by
  `create-project` assume its skills (`brainstorming`, `writing-plans`,
  `executing-plans`, etc.) are available.

## Setup

1. `git clone <this-repo-url> <your-projects-root>` — the clone becomes
   your projects workspace root; `.claude/` is already at its top level.
2. Install the `superpowers` plugin from its marketplace.
3. Run `/create-project` (or
   `bash .claude/skills/create-project/scripts/bootstrap-top-level-repo.sh <repo-name> "<description>"`,
   from your projects workspace root) to scaffold your first project.
4. `create-project` requires an `INDEX.md` file at your projects root — a
   short per-project index it appends a stub entry to on every new
   project. If one doesn't exist yet, it's created automatically on
   first use.

## Keeping your own projects private

Every subdirectory besides `.claude/` is excluded from this repo by
`.gitignore`'s blanket-deny pattern (`/*` at the top, with only
`.claude/`, `.gitignore`, `README.md`, and `LICENSE` allowed back in) —
so your own projects, however many you create, never need any git
configuration of their own to stay out of this repo's history.

## License

MIT — see [LICENSE](LICENSE).
