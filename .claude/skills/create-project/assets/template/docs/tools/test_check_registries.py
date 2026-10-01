"""Tests for check_registries.py against the Markdown+YAML-block registry format."""
from __future__ import annotations

from pathlib import Path

from check_registries import run_registry_checks

SEMANTICS = """### code-standards
```yaml
summary: Tag for topics governed by docs/CODE_STANDARDS.md.
episodes: []
```

### python-environment
```yaml
summary: Tag for topics about this project's local uv virtual environment and Python dependency management.
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

VALID_PROCEDURE_NOT_DISTILLED = """### python-uv-workflow
```yaml
summary: Use a local uv virtual environment
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Use a local uv virtual environment.
distilled_into: null
```
"""

MISSING_DISTILLED_INTO_FIELD_PROCEDURE = """### old-format-procedure
```yaml
summary: A procedure written before distilled_into existed
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Placeholder.
```
"""

DISTILLED_PROCEDURE_WITH_ARCHIVE_ENTRY = """### collapsed-procedure
```yaml
summary: A procedure that graduated into a real skill
applicability: [python-environment]
status: promoted
promotion_type: skill
promoted_to: docs/tools/check_registries.py
promotion_count: 3
episodes: []
content: null
distilled_into: pm-example
```
"""

DISTILLED_PROCEDURE_MISSING_ARCHIVE_ENTRY = """### orphaned-collapse
```yaml
summary: Claims to be collapsed but has no matching ARCHIVE.md entry
applicability: [python-environment]
status: promoted
promotion_type: skill
promoted_to: docs/tools/check_registries.py
promotion_count: 3
episodes: []
content: null
distilled_into: pm-example
```
"""

DISTILLED_PROCEDURE_WITH_LEFTOVER_CONTENT = """### half-collapsed
```yaml
summary: distilled_into is set but content was never cleared
applicability: [python-environment]
status: promoted
promotion_type: skill
promoted_to: docs/tools/check_registries.py
promotion_count: 3
episodes: []
content: This should have been moved to ARCHIVE.md.
distilled_into: pm-example
```
"""

DISTILLED_PROCEDURE_WITH_DRAFT_STATUS = """### collapsed-procedure
```yaml
summary: distilled_into is set but status was never updated to promoted
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 3
episodes: []
content: null
distilled_into: pm-example
```
"""

MATCHING_ARCHIVE = """### collapsed-procedure
```yaml
collapsed_on: 2026-09-30
distilled_into: pm-example
original_promotions: 3
episodes: []
content: The full pre-collapse body, preserved for history.
```
"""


def _write(tmp_path: Path, guardrails_body: str = "", procedures_body: str = "", archive_body: str = "") -> Path:
    (tmp_path / "SEMANTICS.md").write_text(SEMANTICS, encoding="utf-8")
    (tmp_path / "GUARDRAILS.md").write_text(guardrails_body, encoding="utf-8")
    (tmp_path / "PROCEDURES.md").write_text(procedures_body, encoding="utf-8")
    (tmp_path / "LESSONS.md").write_text("", encoding="utf-8")
    (tmp_path / "ARCHIVE.md").write_text(archive_body, encoding="utf-8")
    return tmp_path


def test_valid_guardrail_with_tier_and_severity_passes(tmp_path: Path):
    _write(tmp_path, guardrails_body=VALID_GUARDRAIL)
    assert run_registry_checks(tmp_path) == []


def test_missing_tier_field_entirely_is_flagged(tmp_path: Path):
    _write(tmp_path, guardrails_body=MISSING_TIER_FIELD_GUARDRAIL)
    errors = run_registry_checks(tmp_path)
    assert any("tier" in e for e in errors)


def test_invalid_tier_value_is_flagged(tmp_path: Path):
    _write(tmp_path, guardrails_body=BAD_TIER_VALUE_GUARDRAIL)
    errors = run_registry_checks(tmp_path)
    assert any("tier" in e and "not-a-real-tier" in e for e in errors)


def test_duplicate_ids_flagged(tmp_path: Path):
    _write(tmp_path, guardrails_body=VALID_GUARDRAIL + "\n" + VALID_GUARDRAIL)
    errors = run_registry_checks(tmp_path)
    assert any("duplicate id" in e for e in errors)


def test_valid_procedure_with_null_distilled_into_passes(tmp_path: Path):
    _write(tmp_path, procedures_body=VALID_PROCEDURE_NOT_DISTILLED)
    assert run_registry_checks(tmp_path) == []


def test_missing_distilled_into_field_entirely_is_flagged(tmp_path: Path):
    _write(tmp_path, procedures_body=MISSING_DISTILLED_INTO_FIELD_PROCEDURE)
    errors = run_registry_checks(tmp_path)
    assert any("distilled_into" in e for e in errors)


def test_distilled_procedure_with_matching_archive_entry_passes(tmp_path: Path):
    _write(tmp_path, procedures_body=DISTILLED_PROCEDURE_WITH_ARCHIVE_ENTRY, archive_body=MATCHING_ARCHIVE)
    assert run_registry_checks(tmp_path) == []


def test_distilled_procedure_missing_archive_entry_is_flagged(tmp_path: Path):
    _write(tmp_path, procedures_body=DISTILLED_PROCEDURE_MISSING_ARCHIVE_ENTRY, archive_body="")
    errors = run_registry_checks(tmp_path)
    assert any("ARCHIVE.md" in e for e in errors)


def test_distilled_procedure_with_leftover_content_is_flagged(tmp_path: Path):
    _write(
        tmp_path,
        procedures_body=DISTILLED_PROCEDURE_WITH_LEFTOVER_CONTENT,
        archive_body=MATCHING_ARCHIVE,
    )
    errors = run_registry_checks(tmp_path)
    assert any("distilled_into" in e and "content" in e for e in errors)


def test_distilled_procedure_with_draft_status_is_flagged(tmp_path: Path):
    _write(
        tmp_path,
        procedures_body=DISTILLED_PROCEDURE_WITH_DRAFT_STATUS,
        archive_body=MATCHING_ARCHIVE,
    )
    errors = run_registry_checks(tmp_path)
    assert any("distilled_into" in e and "status" in e for e in errors)
