---
tags: [memory, memory/procedure]
---

# Procedures

Repeatable multi-step workflows, populated by `distill` once a workflow recurs across at least
two episodes (or immediately for anything genuinely universal).

## Entries

### python-uv-workflow
```yaml
summary: Use a local uv virtual environment and pyproject.toml for Python work
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: |
  Use a local `uv` virtual environment (`.venv`) and maintain `pyproject.toml`. Manage dependencies
  with `uv add`; run code with `uv run`.
distilled_into: null
```
- Supported by: (none yet)

## Update Rule

- Update this file only when a workflow is supported by at least two episode files
  (`promotion_count >= 2`), or immediately for anything genuinely universal.
- Every entry's YAML block must include an `episodes` field; when non-empty, add matching links
  to the "Supported by" line.
- Every entry's YAML block must include a `distilled_into` field. It stays `null` until the
  procedure graduates into its own skill/tool file, at which point `distill`'s Graduate step sets
  it to that skill/tool's id, moves the full `content` into a matching-id entry in
  [Archive](ARCHIVE.md), and clears `content` here to `null`.

---

See also: [Guardrails](GUARDRAILS.md) | [Lessons](LESSONS.md) | [Semantics](SEMANTICS.md) |
[Archive](ARCHIVE.md)
