---
tags: [standards]
---

# Code Standards — {{PROJECT_NAME}}

Canonical, universal engineering standards. All review skills review against these, and follow them while writing code. (Referenced from AGENTS.md.)

## Principles
DRY, SOLID, KISS, OOP.

## Functions & classes
- Use clear, single-purpose helper functions.
- No function or class exceeds ~50 lines of code without a significant, stated reason.

## Naming
Names are clear and concise so the code reads itself and comments stay minimal.

## Comments
- Use comments only when appropriate.
- Inline comments are ≤ 2 lines, and only when a name cannot carry the meaning.
- Docstrings only on public classes/functions; review them hard for accuracy and staleness.

## Dead code & redundancy
Hunt orphaned code. Remove redundancy; consolidate duplication under uniform classes/helpers.

## Logging & error handling
Verbose, consistent logging and error handling throughout, with appropriate log levels and error types. More information out is better, especially for debugging.

## Testing
Maintain an appropriate amount of unit, integration, and e2e testing.

## Documentation
- Keep documentation current, especially when new run/entrypoint/shell-script/API surfaces are created.
- **Every Markdown link points to a specific openable file** — a relative `[text](path.md)` resolved from the linking file's location. Never link a bare folder (link its `README.md`/`INDEX.md`, or use inline code for the path), and never use `[[wikilinks]]` in body text (only the `related:` frontmatter property may). See [ONBOARDING.md](ONBOARDING.md) → "Markdown conventions".
