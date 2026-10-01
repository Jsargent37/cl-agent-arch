"""Tests for registry_index.py's Markdown+YAML-block parser and CLI helpers."""
from __future__ import annotations

from pathlib import Path

import pytest

from registry_index import (
    build_index,
    find_entry,
    format_fetch,
    format_index,
    load_registry_list,
    parse_registry_markdown,
    RegistryIndexError,
)

SAMPLE_MD = """---
tags: [memory, memory/guardrail]
---

# Guardrails

## Entries

### follow-code-standards
```yaml
summary: Follow CODE_STANDARDS.md for all code
applicability: [code-standards]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Follow CODE_STANDARDS.md for all code.
enforceability: hard
tier: null
severity: null
hook: null
```
- Supported by: (none yet)

### python-uv-workflow
```yaml
summary: Use a local uv virtual environment
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: |
  Line one of a multi-line explanation.
  ### This looks like a heading but is inside the fenced block.
  Line three.
enforceability: soft
tier: null
severity: null
hook: null
```
- Supported by: (none yet)

## Update Rule

Not an entry.
"""


def test_parse_registry_markdown_extracts_two_entries():
    entries = parse_registry_markdown(SAMPLE_MD)
    ids = [e["id"] for e in entries]
    assert ids == ["follow-code-standards", "python-uv-workflow"]


def test_parse_registry_markdown_preserves_multiline_content_with_embedded_heading_lookalike():
    entries = parse_registry_markdown(SAMPLE_MD)
    content = entries[1]["content"]
    assert "### This looks like a heading" in content
    assert content.count("\n") >= 2


def test_parse_registry_markdown_reads_scalar_fields():
    entries = parse_registry_markdown(SAMPLE_MD)
    assert entries[0]["enforceability"] == "hard"
    assert entries[0]["tier"] is None
    assert entries[0]["severity"] is None


def test_load_registry_list_missing_file_returns_empty(tmp_path: Path):
    assert load_registry_list(tmp_path / "NOPE.md") == []


def test_load_registry_list_round_trips_from_disk(tmp_path: Path):
    p = tmp_path / "GUARDRAILS.md"
    p.write_text(SAMPLE_MD, encoding="utf-8")
    entries = load_registry_list(p)
    assert len(entries) == 2


def test_build_index_excludes_content(tmp_path: Path):
    (tmp_path / "GUARDRAILS.md").write_text(SAMPLE_MD, encoding="utf-8")
    (tmp_path / "PROCEDURES.md").write_text("", encoding="utf-8")
    (tmp_path / "LESSONS.md").write_text("", encoding="utf-8")
    (tmp_path / "SEMANTICS.md").write_text("", encoding="utf-8")
    index = build_index(tmp_path)
    entry = index["GUARDRAILS.md"][0]
    assert "content" not in entry
    assert entry["id"] == "follow-code-standards"


def test_find_entry_missing_id_raises(tmp_path: Path):
    for name in ("GUARDRAILS.md", "PROCEDURES.md", "LESSONS.md", "SEMANTICS.md"):
        (tmp_path / name).write_text("", encoding="utf-8")
    with pytest.raises(RegistryIndexError):
        find_entry(tmp_path, "does-not-exist")


def test_format_fetch_inlines_content(tmp_path: Path):
    (tmp_path / "GUARDRAILS.md").write_text(SAMPLE_MD, encoding="utf-8")
    for name in ("PROCEDURES.md", "LESSONS.md", "SEMANTICS.md"):
        (tmp_path / name).write_text("", encoding="utf-8")
    out = format_fetch(tmp_path, ["follow-code-standards"])
    assert "content: Follow CODE_STANDARDS.md for all code." in out


DRAFT_REF_MD = """### long-procedure
```yaml
summary: A procedure too long to inline
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
draft_ref: docs/memory/promotion-drafts/long-procedure.md
distilled_into: null
```
"""

DISTILLED_INTO_MD = """### collapsed-procedure
```yaml
summary: A procedure that graduated into a real skill
applicability: [python-environment]
status: promoted
promotion_type: skill
promoted_to: .claude/skills/example/SKILL.md
promotion_count: 3
episodes: []
content: null
distilled_into: pm-example
```
"""


def test_format_fetch_points_to_draft_ref_file(tmp_path: Path):
    (tmp_path / "PROCEDURES.md").write_text(DRAFT_REF_MD, encoding="utf-8")
    for name in ("GUARDRAILS.md", "LESSONS.md", "SEMANTICS.md"):
        (tmp_path / name).write_text("", encoding="utf-8")
    out = format_fetch(tmp_path, ["long-procedure"])
    assert "draft_ref: docs/memory/promotion-drafts/long-procedure.md" in out
    assert "read this file directly" in out


def test_format_fetch_points_to_distilled_into_and_promoted_to(tmp_path: Path):
    (tmp_path / "PROCEDURES.md").write_text(DISTILLED_INTO_MD, encoding="utf-8")
    for name in ("GUARDRAILS.md", "LESSONS.md", "SEMANTICS.md"):
        (tmp_path / name).write_text("", encoding="utf-8")
    out = format_fetch(tmp_path, ["collapsed-procedure"])
    assert "distilled_into: pm-example" in out
    assert "promoted_to: .claude/skills/example/SKILL.md" in out


def test_format_index_groups_by_registry_filename(tmp_path: Path):
    (tmp_path / "GUARDRAILS.md").write_text(SAMPLE_MD, encoding="utf-8")
    for name in ("PROCEDURES.md", "LESSONS.md", "SEMANTICS.md"):
        (tmp_path / name).write_text("", encoding="utf-8")
    out = format_index(build_index(tmp_path))
    assert "# GUARDRAILS.md" in out
    assert "follow-code-standards" in out
    assert "content" not in out
