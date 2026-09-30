"""Tests for check_registries.py against the Markdown+YAML-block registry format."""
from __future__ import annotations

from pathlib import Path

from check_registries import run_registry_checks

SEMANTICS = """### code-standards
```yaml
summary: Tag for topics governed by docs/CODE_STANDARDS.md.
episodes: []
```
"""

VALID_GUARDRAIL = """### follow-code-standards
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
"""

MISSING_TIER_FIELD_GUARDRAIL = """### no-tier-field
```yaml
summary: An old-format leftover with no tier/severity keys at all
applicability: [code-standards]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Placeholder.
enforceability: hard
hook: null
```
"""

BAD_TIER_VALUE_GUARDRAIL = """### bad-tier
```yaml
summary: A guardrail with an invalid tier value
applicability: [code-standards]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Placeholder.
enforceability: hard
tier: not-a-real-tier
severity: low
hook: null
```
"""


def _write(tmp_path: Path, guardrails_body: str) -> Path:
    (tmp_path / "SEMANTICS.md").write_text(SEMANTICS, encoding="utf-8")
    (tmp_path / "GUARDRAILS.md").write_text(guardrails_body, encoding="utf-8")
    (tmp_path / "PROCEDURES.md").write_text("", encoding="utf-8")
    (tmp_path / "LESSONS.md").write_text("", encoding="utf-8")
    return tmp_path


def test_valid_guardrail_with_tier_and_severity_passes(tmp_path: Path):
    _write(tmp_path, VALID_GUARDRAIL)
    assert run_registry_checks(tmp_path) == []


def test_missing_tier_field_entirely_is_flagged(tmp_path: Path):
    _write(tmp_path, MISSING_TIER_FIELD_GUARDRAIL)
    errors = run_registry_checks(tmp_path)
    assert any("tier" in e for e in errors)


def test_invalid_tier_value_is_flagged(tmp_path: Path):
    _write(tmp_path, BAD_TIER_VALUE_GUARDRAIL)
    errors = run_registry_checks(tmp_path)
    assert any("tier" in e and "not-a-real-tier" in e for e in errors)


def test_duplicate_ids_flagged(tmp_path: Path):
    _write(tmp_path, VALID_GUARDRAIL + "\n" + VALID_GUARDRAIL)
    errors = run_registry_checks(tmp_path)
    assert any("duplicate id" in e for e in errors)
