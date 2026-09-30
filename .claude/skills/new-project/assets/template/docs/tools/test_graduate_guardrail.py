"""Tests for graduate_guardrail.py against the Markdown+YAML-block registry format."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from graduate_guardrail import (
    GuardrailError,
    apply_proposal,
    classify_mechanism,
    dump_entry_yaml,
    load_guardrail_entry,
    propose,
    replace_entry_block,
    validate_eligible,
)

SAMPLE_GUARDRAILS_MD = """### no-global-python
```yaml
summary: Never install into or use a global/system Python
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: |
  Never install into or use a global/system Python. `pip install` is denied by settings.
enforceability: hard
tier: null
severity: null
hook: null
```
- Supported by: (none yet)

### no-global-python-v2
```yaml
summary: A second entry whose id is a superstring of the first, to catch anchoring bugs
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Placeholder second entry.
enforceability: soft
tier: null
severity: null
hook: null
```
- Supported by: (none yet)
"""


def test_load_guardrail_entry_finds_by_id(tmp_path: Path):
    (tmp_path / "GUARDRAILS.md").write_text(SAMPLE_GUARDRAILS_MD, encoding="utf-8")
    entry = load_guardrail_entry(tmp_path, "no-global-python")
    assert entry["summary"].startswith("Never install")


def test_load_guardrail_entry_missing_raises(tmp_path: Path):
    (tmp_path / "GUARDRAILS.md").write_text(SAMPLE_GUARDRAILS_MD, encoding="utf-8")
    with pytest.raises(GuardrailError):
        load_guardrail_entry(tmp_path, "does-not-exist")


def test_classify_mechanism_detects_pip():
    entry = {"content": "Never install into or use a global/system Python. `pip install` is denied by settings."}
    mechanism, pattern = classify_mechanism(entry)
    assert mechanism == "permission-rule"
    assert pattern == "pip install"


def test_dump_entry_yaml_preserves_multiline_literal_style():
    data = {"id": "x", "content": "line one\nline two"}
    out = dump_entry_yaml(data)
    assert "content: |" in out
    assert "line one" in out and "line two" in out


def test_replace_entry_block_anchors_on_full_heading_not_prefix():
    updated = replace_entry_block(
        SAMPLE_GUARDRAILS_MD, "no-global-python", {"summary": "CHANGED", "id": "no-global-python"}
    )
    assert "summary: CHANGED" in updated
    # the superstring-named sibling entry must be untouched
    assert "A second entry whose id is a superstring" in updated
    assert updated.count("CHANGED") == 1


def test_replace_entry_block_missing_id_raises():
    with pytest.raises(ValueError):
        replace_entry_block(SAMPLE_GUARDRAILS_MD, "does-not-exist", {"id": "does-not-exist"})


def test_propose_sets_tier_script_for_permission_rule(tmp_path: Path):
    (tmp_path / "GUARDRAILS.md").write_text(SAMPLE_GUARDRAILS_MD, encoding="utf-8")
    entry = load_guardrail_entry(tmp_path, "no-global-python")
    validate_eligible(entry)
    mechanism, pattern = classify_mechanism(entry)
    proposal = propose(entry, mechanism, pattern, "deny")
    assert proposal["registry_update"]["tier"] == "script"


def test_apply_proposal_writes_markdown_in_place(tmp_path: Path):
    memory_dir = tmp_path / "docs" / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "GUARDRAILS.md").write_text(SAMPLE_GUARDRAILS_MD, encoding="utf-8")
    settings_file = tmp_path / ".claude" / "settings.json"
    settings_file.parent.mkdir(parents=True)
    settings_file.write_text(json.dumps({"permissions": {"deny": []}}), encoding="utf-8")

    entry = load_guardrail_entry(memory_dir, "no-global-python")
    mechanism, pattern = classify_mechanism(entry)
    proposal = propose(entry, mechanism, pattern, "deny")
    apply_proposal(tmp_path, settings_file, memory_dir, entry, proposal)

    updated_text = (memory_dir / "GUARDRAILS.md").read_text(encoding="utf-8")
    assert "status: promoted" in updated_text
    assert "tier: script" in updated_text
    # sibling entry survives untouched
    assert "A second entry whose id is a superstring" in updated_text
    settings = json.loads(settings_file.read_text(encoding="utf-8"))
    assert "Bash(pip install:*)" in settings["permissions"]["deny"]
