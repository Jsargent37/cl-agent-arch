from pathlib import Path

import check_registries as cr


def test_load_yaml_list_missing_file_returns_empty(tmp_path):
    assert cr.load_yaml_list(tmp_path / "nope.yaml") == []


def test_load_yaml_list_reads_entries(tmp_path):
    path = tmp_path / "REGISTRY.yaml"
    path.write_text(
        "- id: example-one\n  summary: does a thing\n"
        "- id: example-two\n  summary: does another thing\n",
        encoding="utf-8",
    )
    entries = cr.load_yaml_list(path)
    assert [e["id"] for e in entries] == ["example-one", "example-two"]


def test_load_yaml_list_rejects_non_list_top_level(tmp_path):
    path = tmp_path / "REGISTRY.yaml"
    path.write_text("id: not-a-list\n", encoding="utf-8")
    try:
        cr.load_yaml_list(path)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "top-level YAML list" in str(e)


def test_load_semantics_ids_collects_ids(tmp_path):
    path = tmp_path / "SEMANTICS.yaml"
    path.write_text(
        "- id: streamlit\n  summary: the dashboard UI framework\n"
        "- id: dashboard-ui\n  summary: the friction dashboard\n",
        encoding="utf-8",
    )
    assert cr.load_semantics_ids(path) == {"streamlit", "dashboard-ui"}


def test_validate_entry_flags_missing_fields():
    errors = []
    cr.validate_entry(
        {"id": "x", "summary": "s"},
        "PROCEDURES.yaml", 0, is_guardrail=False, semantics_ids=set(), errors=errors,
    )
    assert any("missing field(s)" in e for e in errors)


def test_validate_entry_flags_bad_status():
    entry = _minimal_entry(status="not-a-status")
    errors = []
    cr.validate_entry(entry, "PROCEDURES.yaml", 0, False, {"tag-a"}, errors)
    assert any("status" in e for e in errors)


def test_validate_entry_flags_bad_promotion_type():
    entry = _minimal_entry(promotion_type="not-a-type")
    errors = []
    cr.validate_entry(entry, "PROCEDURES.yaml", 0, False, {"tag-a"}, errors)
    assert any("promotion_type" in e for e in errors)


def test_validate_entry_guardrail_requires_enforceability():
    entry = _minimal_entry()
    errors = []
    cr.validate_entry(entry, "GUARDRAILS.yaml", 0, True, {"tag-a"}, errors)
    assert any("enforceability" in e for e in errors)


def test_validate_entry_accepts_well_formed_procedure(tmp_path):
    draft = tmp_path / "draft.md"
    draft.write_text("# draft\n", encoding="utf-8")
    entry = _minimal_entry(content=None, draft_ref=str(draft))
    errors = []
    cr.validate_entry(entry, "PROCEDURES.yaml", 0, False, {"tag-a"}, errors)
    assert errors == []


def test_run_registry_checks_clean_on_empty_registries(tmp_path):
    (tmp_path / "SEMANTICS.yaml").write_text("[]\n", encoding="utf-8")
    assert cr.run_registry_checks(tmp_path) == []


def test_run_registry_checks_flags_duplicate_ids(tmp_path):
    (tmp_path / "SEMANTICS.yaml").write_text(
        "- id: tag-a\n  summary: a tag\n", encoding="utf-8"
    )
    (tmp_path / "PROCEDURES.yaml").write_text(
        "- id: dup\n  summary: one\n  applicability: [tag-a]\n  status: draft\n"
        "  promotion_type: null\n  promoted_to: null\n  promotion_count: 1\n"
        "  episodes: [ep1]\n  content: a\n"
        "- id: dup\n  summary: two\n  applicability: [tag-a]\n  status: draft\n"
        "  promotion_type: null\n  promoted_to: null\n  promotion_count: 1\n"
        "  episodes: [ep2]\n  content: b\n",
        encoding="utf-8",
    )
    errors = cr.run_registry_checks(tmp_path)
    assert any("duplicate id" in e for e in errors)


def test_main_exits_nonzero_on_errors(tmp_path, monkeypatch):
    (tmp_path / "SEMANTICS.yaml").write_text("[]\n", encoding="utf-8")
    (tmp_path / "GUARDRAILS.yaml").write_text(
        "- id: bad\n  summary: missing fields\n", encoding="utf-8"
    )
    monkeypatch.setattr(cr, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(cr, "SEMANTICS_FILE", tmp_path / "SEMANTICS.yaml")
    assert cr.main() == 1


def _minimal_entry(**overrides):
    entry = {
        "id": "example-procedure",
        "summary": "does a thing",
        "applicability": ["tag-a"],
        "status": "draft",
        "promotion_type": None,
        "promoted_to": None,
        "promotion_count": 1,
        "episodes": ["2026-07-10-example"],
        "content": "step one\nstep two\n",
    }
    entry.update(overrides)
    if overrides.get("content") is None and "draft_ref" not in overrides:
        entry.pop("content", None)
    return entry


def test_promoted_to_with_settings_fragment_is_valid(tmp_path, monkeypatch):
    """A guardrail's promoted_to pointing at .claude/settings.json#permissions.deny should
    validate against the real file (.claude/settings.json), ignoring the #fragment."""
    import check_registries as cr

    monkeypatch.setattr(cr, "ROOT", tmp_path)
    monkeypatch.setattr(cr, "MEMORY_DIR", tmp_path / "docs" / "memory")
    (tmp_path / ".claude").mkdir(parents=True)
    (tmp_path / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
    memory_dir = tmp_path / "docs" / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "SEMANTICS.yaml").write_text("- id: t1\n", encoding="utf-8")
    entry = {
        "id": "g1",
        "summary": "s",
        "applicability": ["t1"],
        "status": "promoted",
        "promotion_type": "hook",
        "promoted_to": ".claude/settings.json#permissions.deny",
        "promotion_count": 1,
        "episodes": [],
        "content": "c",
        "enforceability": "hard",
        "hook": None,
    }
    errors: list = []
    cr.validate_entry(entry, "docs/memory/GUARDRAILS.yaml", 0, True, {"t1"}, errors)
    assert errors == []
