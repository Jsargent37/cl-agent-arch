from pathlib import Path

import registry_index as ri


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_load_yaml_list_missing_file_returns_empty(tmp_path):
    assert ri.load_yaml_list(tmp_path / "nope.yaml") == []


def test_load_yaml_list_reads_entries(tmp_path):
    path = _write(
        tmp_path / "REGISTRY.yaml",
        "- id: example-one\n  summary: does a thing\n"
        "- id: example-two\n  summary: does another thing\n",
    )
    entries = ri.load_yaml_list(path)
    assert [e["id"] for e in entries] == ["example-one", "example-two"]


def test_build_index_strips_content_and_draft_ref(tmp_path):
    _write(
        tmp_path / "GUARDRAILS.yaml",
        "- id: no-global-python\n"
        "  summary: Never use a global Python\n"
        "  applicability: [python-environment]\n"
        "  status: draft\n"
        "  promotion_type: null\n"
        "  promoted_to: null\n"
        "  promotion_count: 1\n"
        "  episodes: []\n"
        "  content: Use a local uv venv.\n"
        "  enforceability: hard\n"
        "  hook: null\n",
    )
    for name in ("PROCEDURES.yaml", "LESSONS.yaml", "SEMANTICS.yaml"):
        _write(tmp_path / name, "")

    index = ri.build_index(tmp_path)
    entry = index["GUARDRAILS.yaml"][0]
    assert entry == {
        "id": "no-global-python",
        "summary": "Never use a global Python",
        "applicability": ["python-environment"],
        "status": "draft",
        "promotion_type": None,
    }
    assert "content" not in entry
    assert "draft_ref" not in entry


def test_build_index_covers_all_four_registries(tmp_path):
    for name in ri.REGISTRY_FILES:
        _write(tmp_path / name, "")
    index = ri.build_index(tmp_path)
    assert set(index.keys()) == {
        "GUARDRAILS.yaml", "PROCEDURES.yaml", "LESSONS.yaml", "SEMANTICS.yaml",
    }


def test_build_index_missing_registry_file_yields_empty_list(tmp_path):
    index = ri.build_index(tmp_path)
    assert index["GUARDRAILS.yaml"] == []


def test_format_index_lists_each_registry_and_entry(tmp_path):
    for name in ri.REGISTRY_FILES:
        _write(tmp_path / name, "")
    _write(
        tmp_path / "SEMANTICS.yaml",
        "- id: streamlit\n  summary: dashboard UI framework\n  applicability: []\n"
        "  status: promoted\n  promotion_type: null\n",
    )
    text = ri.format_index(ri.build_index(tmp_path))
    assert "SEMANTICS.yaml" in text
    assert "streamlit" in text
    assert "dashboard UI framework" in text


import pytest


def _guardrails_with_draft_ref(tmp_path, draft_dir):
    draft_dir.mkdir(parents=True, exist_ok=True)
    draft_path = draft_dir / "long-thing.md"
    draft_path.write_text("# long thing\nsteps...\n", encoding="utf-8")
    _write(
        tmp_path / "PROCEDURES.yaml",
        "- id: long-thing\n"
        "  summary: A long procedure\n"
        "  applicability: []\n"
        "  status: draft\n"
        "  promotion_type: null\n"
        "  promoted_to: null\n"
        "  promotion_count: 1\n"
        "  episodes: []\n"
        f"  draft_ref: {draft_path.as_posix()}\n",
    )
    _write(
        tmp_path / "GUARDRAILS.yaml",
        "- id: no-global-python\n"
        "  summary: Never use a global Python\n"
        "  applicability: [python-environment]\n"
        "  status: draft\n"
        "  promotion_type: null\n"
        "  promoted_to: null\n"
        "  promotion_count: 1\n"
        "  episodes: []\n"
        "  content: Use a local uv venv.\n"
        "  enforceability: hard\n"
        "  hook: null\n",
    )
    for name in ("LESSONS.yaml", "SEMANTICS.yaml"):
        _write(tmp_path / name, "")
    return draft_path


def test_find_entry_locates_by_id_across_registries(tmp_path):
    _guardrails_with_draft_ref(tmp_path, tmp_path / "promotion-drafts")
    filename, entry = ri.find_entry(tmp_path, "no-global-python")
    assert filename == "GUARDRAILS.yaml"
    assert entry["summary"] == "Never use a global Python"


def test_find_entry_raises_for_unknown_id(tmp_path):
    for name in ri.REGISTRY_FILES:
        _write(tmp_path / name, "")
    with pytest.raises(ri.RegistryIndexError, match="unknown-id"):
        ri.find_entry(tmp_path, "unknown-id")


def test_format_fetch_prints_inline_content(tmp_path):
    _guardrails_with_draft_ref(tmp_path, tmp_path / "promotion-drafts")
    text = ri.format_fetch(tmp_path, ["no-global-python"])
    assert "Use a local uv venv." in text


def test_format_fetch_prints_draft_ref_path_not_inlined(tmp_path):
    draft_path = _guardrails_with_draft_ref(tmp_path, tmp_path / "promotion-drafts")
    text = ri.format_fetch(tmp_path, ["long-thing"])
    assert draft_path.as_posix() in text
    assert "steps..." not in text


def test_format_fetch_handles_multiple_ids_in_order(tmp_path):
    _guardrails_with_draft_ref(tmp_path, tmp_path / "promotion-drafts")
    text = ri.format_fetch(tmp_path, ["no-global-python", "long-thing"])
    assert text.index("no-global-python") < text.index("long-thing")


def test_main_index_prints_and_returns_zero(tmp_path, monkeypatch, capsys):
    for name in ri.REGISTRY_FILES:
        _write(tmp_path / name, "")
    monkeypatch.setattr(ri, "MEMORY_DIR", tmp_path)
    rc = ri.main(["--index"])
    assert rc == 0
    assert "GUARDRAILS.yaml" in capsys.readouterr().out


def test_main_fetch_unknown_id_prints_error_and_returns_one(tmp_path, monkeypatch, capsys):
    for name in ri.REGISTRY_FILES:
        _write(tmp_path / name, "")
    monkeypatch.setattr(ri, "MEMORY_DIR", tmp_path)
    rc = ri.main(["--fetch", "unknown-id"])
    assert rc == 1
    assert "unknown-id" in capsys.readouterr().err


def test_main_requires_index_or_fetch(tmp_path, monkeypatch):
    monkeypatch.setattr(ri, "MEMORY_DIR", tmp_path)
    with pytest.raises(SystemExit):
        ri.main([])
