from pathlib import Path

import graduate_guardrail as gg


def _write_guardrails(tmp_path: Path, entries_yaml: str) -> Path:
    path = tmp_path / "GUARDRAILS.yaml"
    path.write_text(entries_yaml, encoding="utf-8")
    return path


HARD_DRAFT_ENTRY_YAML = """\
- id: no-global-python
  summary: Never use a global Python
  applicability: [python-environment]
  status: draft
  promotion_type: null
  promoted_to: null
  promotion_count: 1
  episodes: []
  content: "Use a local `uv` venv. Add deps with `uv add`. Never use global Python -- `pip install` is denied by settings."
  enforceability: hard
  hook: null
"""

SOFT_DRAFT_ENTRY_YAML = """\
- id: keep-episode-current
  summary: Keep episode current
  applicability: [episode]
  status: draft
  promotion_type: null
  promoted_to: null
  promotion_count: 1
  episodes: []
  content: Keep the episode current.
  enforceability: soft
  hook: null
"""

HARD_PROMOTED_ENTRY_YAML = """\
- id: already-done
  summary: Already graduated
  applicability: [x]
  status: promoted
  promotion_type: hook
  promoted_to: .claude/settings.json#permissions.deny
  promotion_count: 1
  episodes: []
  content: "Some `rm -rf` ban."
  enforceability: hard
  hook: .claude/settings.json#permissions.deny
"""

NO_COMMAND_LITERAL_ENTRY_YAML = """\
- id: nas-bridge-only
  summary: Real data only via the NAS bridge
  applicability: [nas-bridge]
  status: draft
  promotion_type: null
  promoted_to: null
  promotion_count: 1
  episodes: []
  content: Real data in the PCI environment can only be accessed via the NAS bridge.
  enforceability: hard
  hook: null
"""


def test_load_guardrail_entry_found(tmp_path):
    _write_guardrails(tmp_path, HARD_DRAFT_ENTRY_YAML)
    entry = gg.load_guardrail_entry(tmp_path, "no-global-python")
    assert entry["id"] == "no-global-python"
    assert entry["enforceability"] == "hard"


def test_load_guardrail_entry_missing_id_raises(tmp_path):
    _write_guardrails(tmp_path, HARD_DRAFT_ENTRY_YAML)
    try:
        gg.load_guardrail_entry(tmp_path, "does-not-exist")
        assert False, "expected GuardrailError"
    except gg.GuardrailError as e:
        assert "does-not-exist" in str(e)


def test_load_guardrail_entry_missing_file_raises(tmp_path):
    try:
        gg.load_guardrail_entry(tmp_path, "anything")
        assert False, "expected GuardrailError"
    except gg.GuardrailError as e:
        assert "does not exist" in str(e)


def test_validate_eligible_accepts_hard_draft(tmp_path):
    _write_guardrails(tmp_path, HARD_DRAFT_ENTRY_YAML)
    entry = gg.load_guardrail_entry(tmp_path, "no-global-python")
    gg.validate_eligible(entry)  # must not raise


def test_validate_eligible_rejects_soft(tmp_path):
    _write_guardrails(tmp_path, SOFT_DRAFT_ENTRY_YAML)
    entry = gg.load_guardrail_entry(tmp_path, "keep-episode-current")
    try:
        gg.validate_eligible(entry)
        assert False, "expected GuardrailError"
    except gg.GuardrailError as e:
        assert "not 'hard'" in str(e)


def test_validate_eligible_rejects_already_promoted(tmp_path):
    _write_guardrails(tmp_path, HARD_PROMOTED_ENTRY_YAML)
    entry = gg.load_guardrail_entry(tmp_path, "already-done")
    try:
        gg.validate_eligible(entry)
        assert False, "expected GuardrailError"
    except gg.GuardrailError as e:
        assert "not 'draft'" in str(e)


def test_classify_mechanism_permission_rule_from_pip_install(tmp_path):
    _write_guardrails(tmp_path, HARD_DRAFT_ENTRY_YAML)
    entry = gg.load_guardrail_entry(tmp_path, "no-global-python")
    mechanism, pattern = gg.classify_mechanism(entry)
    assert mechanism == "permission-rule"
    assert pattern == "pip install"


def test_classify_mechanism_hook_script_when_no_command_literal(tmp_path):
    _write_guardrails(tmp_path, NO_COMMAND_LITERAL_ENTRY_YAML)
    entry = gg.load_guardrail_entry(tmp_path, "nas-bridge-only")
    mechanism, pattern = gg.classify_mechanism(entry)
    assert mechanism == "hook-script"
    assert pattern is None


def test_build_registry_update_sets_fields_permission_rule():
    entry = {"id": "x", "status": "draft", "promotion_type": None, "promoted_to": None}
    updated = gg.build_registry_update(
        entry, "permission-rule", ".claude/settings.json#permissions.deny"
    )
    assert updated["status"] == "promoted"
    assert updated["promotion_type"] == "hook"
    assert updated["promoted_to"] == ".claude/settings.json#permissions.deny"
    assert entry["status"] == "draft", "must not mutate the input entry"


def test_build_registry_update_sets_fields_hook_script():
    entry = {"id": "y", "status": "draft", "promotion_type": None, "promoted_to": None}
    updated = gg.build_registry_update(
        entry, "hook-script", "docs/tools/guardrail_hooks/y.py"
    )
    assert updated["promoted_to"] == "docs/tools/guardrail_hooks/y.py"


import json

import yaml


def test_permission_rule_string_format():
    assert gg.permission_rule_string("pip install") == "Bash(pip install:*)"


def test_load_settings_missing_file_raises(tmp_path):
    try:
        gg.load_settings(tmp_path / "nope.json")
        assert False, "expected GuardrailError"
    except gg.GuardrailError as e:
        assert "does not exist" in str(e)


def test_load_settings_reads_json(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"permissions": {"deny": ["Bash(x:*)"]}}', encoding="utf-8")
    settings = gg.load_settings(path)
    assert settings["permissions"]["deny"] == ["Bash(x:*)"]


def test_add_permission_rule_appends_new():
    settings = {"permissions": {"deny": ["Bash(x:*)"]}}
    updated, added = gg.add_permission_rule(settings, "deny", "Bash(pip install:*)")
    assert added is True
    assert updated["permissions"]["deny"] == ["Bash(x:*)", "Bash(pip install:*)"]
    assert settings["permissions"]["deny"] == ["Bash(x:*)"], "must not mutate input"


def test_add_permission_rule_noop_when_present():
    settings = {"permissions": {"deny": ["Bash(pip install:*)"]}}
    updated, added = gg.add_permission_rule(settings, "deny", "Bash(pip install:*)")
    assert added is False
    assert updated["permissions"]["deny"] == ["Bash(pip install:*)"]


def test_add_permission_rule_creates_missing_lists():
    settings = {}
    updated, added = gg.add_permission_rule(settings, "ask", "Bash(rm:*)")
    assert added is True
    assert updated["permissions"]["ask"] == ["Bash(rm:*)"]


def test_add_permission_rule_rejects_bad_rule_type():
    try:
        gg.add_permission_rule({}, "allow", "x")
        assert False, "expected GuardrailError"
    except gg.GuardrailError as e:
        assert "rule_type" in str(e)


def test_scaffold_hook_script_creates_stub(tmp_path):
    hook_dir = tmp_path / "guardrail_hooks"
    path = gg.scaffold_hook_script(hook_dir, "nas-bridge-only")
    assert path == hook_dir / "nas-bridge-only.py"
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "TODO: implement enforcement logic for nas-bridge-only" in content


def test_scaffold_hook_script_idempotent_no_overwrite(tmp_path):
    hook_dir = tmp_path / "guardrail_hooks"
    path = gg.scaffold_hook_script(hook_dir, "nas-bridge-only")
    path.write_text("# hand-edited\n", encoding="utf-8")
    path2 = gg.scaffold_hook_script(hook_dir, "nas-bridge-only")
    assert path2.read_text(encoding="utf-8") == "# hand-edited\n"


def test_add_pretooluse_hook_appends_new():
    settings = {}
    updated, added = gg.add_pretooluse_hook(settings, "Bash", "python docs/tools/guardrail_hooks/x.py")
    assert added is True
    assert updated["hooks"]["PreToolUse"] == [
        {"matcher": "Bash", "hooks": [{"type": "command", "command": "python docs/tools/guardrail_hooks/x.py"}]}
    ]


def test_add_pretooluse_hook_noop_when_present():
    settings = {
        "hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "python x.py"}]}
        ]}
    }
    updated, added = gg.add_pretooluse_hook(settings, "Bash", "python x.py")
    assert added is False
    assert len(updated["hooks"]["PreToolUse"][0]["hooks"]) == 1


def test_add_pretooluse_hook_extends_existing_matcher():
    settings = {
        "hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "python x.py"}]}
        ]}
    }
    updated, added = gg.add_pretooluse_hook(settings, "Bash", "python y.py")
    assert added is True
    assert len(updated["hooks"]["PreToolUse"][0]["hooks"]) == 2


def test_propose_permission_rule_builds_target_and_change_description():
    entry = {"id": "no-global-python", "status": "draft", "promotion_type": None, "promoted_to": None}
    proposal = gg.propose(entry, "permission-rule", "pip install", "deny")
    assert proposal["mechanism"] == "permission-rule"
    assert proposal["target"] == ".claude/settings.json#permissions.deny"
    assert "Bash(pip install:*)" in proposal["settings_change"]
    assert proposal["registry_update"]["promoted_to"] == ".claude/settings.json#permissions.deny"


def test_propose_hook_script_builds_target_and_change_description():
    entry = {"id": "nas-bridge-only", "status": "draft", "promotion_type": None, "promoted_to": None}
    proposal = gg.propose(entry, "hook-script", None, "deny")
    assert proposal["mechanism"] == "hook-script"
    assert proposal["target"] == "docs/tools/guardrail_hooks/nas-bridge-only.py"
    assert proposal["registry_update"]["promoted_to"] == "docs/tools/guardrail_hooks/nas-bridge-only.py"


def test_propose_permission_rule_without_pattern_raises():
    entry = {"id": "x", "status": "draft", "promotion_type": None, "promoted_to": None}
    try:
        gg.propose(entry, "permission-rule", None, "deny")
        assert False, "expected GuardrailError"
    except gg.GuardrailError as e:
        assert "pattern" in str(e)


def test_apply_proposal_permission_rule_writes_settings_and_registry(tmp_path):
    _write_guardrails(tmp_path, HARD_DRAFT_ENTRY_YAML)
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"permissions": {"deny": []}}', encoding="utf-8")
    entry = gg.load_guardrail_entry(tmp_path, "no-global-python")
    mechanism, pattern = gg.classify_mechanism(entry)
    proposal = gg.propose(entry, mechanism, pattern, "deny")

    gg.apply_proposal(tmp_path, settings_file, tmp_path, entry, proposal)

    written_settings = json.loads(settings_file.read_text(encoding="utf-8"))
    assert "Bash(pip install:*)" in written_settings["permissions"]["deny"]

    updated_entries = yaml.safe_load((tmp_path / "GUARDRAILS.yaml").read_text(encoding="utf-8"))
    updated = next(e for e in updated_entries if e["id"] == "no-global-python")
    assert updated["status"] == "promoted"
    assert updated["promotion_type"] == "hook"
    assert updated["promoted_to"] == ".claude/settings.json#permissions.deny"


def test_apply_proposal_hook_script_writes_stub_settings_and_registry(tmp_path):
    _write_guardrails(tmp_path, NO_COMMAND_LITERAL_ENTRY_YAML)
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("{}", encoding="utf-8")
    entry = gg.load_guardrail_entry(tmp_path, "nas-bridge-only")
    mechanism, pattern = gg.classify_mechanism(entry)
    proposal = gg.propose(entry, mechanism, pattern, "deny")

    gg.apply_proposal(tmp_path, settings_file, tmp_path, entry, proposal)

    script_path = tmp_path / "docs" / "tools" / "guardrail_hooks" / "nas-bridge-only.py"
    assert script_path.exists()

    written_settings = json.loads(settings_file.read_text(encoding="utf-8"))
    assert written_settings["hooks"]["PreToolUse"][0]["matcher"] == "*"

    updated_entries = yaml.safe_load((tmp_path / "GUARDRAILS.yaml").read_text(encoding="utf-8"))
    updated = next(e for e in updated_entries if e["id"] == "nas-bridge-only")
    assert updated["status"] == "promoted"
    assert updated["promoted_to"] == "docs/tools/guardrail_hooks/nas-bridge-only.py"


def test_main_propose_mode_makes_no_writes(tmp_path, monkeypatch, capsys):
    _write_guardrails(tmp_path, HARD_DRAFT_ENTRY_YAML)
    settings_file = tmp_path / "settings.json"
    settings_before = '{"permissions": {"deny": []}}'
    settings_file.write_text(settings_before, encoding="utf-8")
    monkeypatch.setattr(gg, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(gg, "SETTINGS_FILE", settings_file)
    monkeypatch.setattr(gg, "ROOT", tmp_path)

    exit_code = gg.main(["no-global-python"])

    assert exit_code == 0
    assert settings_file.read_text(encoding="utf-8") == settings_before
    entries = yaml.safe_load((tmp_path / "GUARDRAILS.yaml").read_text(encoding="utf-8"))
    assert entries[0]["status"] == "draft"
    out = capsys.readouterr().out
    assert "permission-rule" in out


def test_main_propose_hook_script_mode_makes_no_writes(tmp_path, monkeypatch, capsys):
    _write_guardrails(tmp_path, NO_COMMAND_LITERAL_ENTRY_YAML)
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gg, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(gg, "SETTINGS_FILE", settings_file)
    monkeypatch.setattr(gg, "ROOT", tmp_path)

    exit_code = gg.main(["nas-bridge-only"])

    assert exit_code == 0
    assert settings_file.read_text(encoding="utf-8") == "{}"
    assert not (tmp_path / "docs" / "tools" / "guardrail_hooks" / "nas-bridge-only.py").exists()
    entries = yaml.safe_load((tmp_path / "GUARDRAILS.yaml").read_text(encoding="utf-8"))
    assert entries[0]["status"] == "draft"
    out = capsys.readouterr().out
    assert "hook-script" in out


def test_main_apply_mode_writes_changes(tmp_path, monkeypatch):
    _write_guardrails(tmp_path, HARD_DRAFT_ENTRY_YAML)
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"permissions": {"deny": []}}', encoding="utf-8")
    monkeypatch.setattr(gg, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(gg, "SETTINGS_FILE", settings_file)
    monkeypatch.setattr(gg, "ROOT", tmp_path)

    exit_code = gg.main(["no-global-python", "--apply"])

    assert exit_code == 0
    written_settings = json.loads(settings_file.read_text(encoding="utf-8"))
    assert "Bash(pip install:*)" in written_settings["permissions"]["deny"]
    entries = yaml.safe_load((tmp_path / "GUARDRAILS.yaml").read_text(encoding="utf-8"))
    assert entries[0]["status"] == "promoted"


def test_main_rejects_soft_guardrail_returns_1(tmp_path, monkeypatch):
    _write_guardrails(tmp_path, SOFT_DRAFT_ENTRY_YAML)
    monkeypatch.setattr(gg, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(gg, "SETTINGS_FILE", tmp_path / "settings.json")
    monkeypatch.setattr(gg, "ROOT", tmp_path)

    exit_code = gg.main(["keep-episode-current"])

    assert exit_code == 1


def test_main_mechanism_override(tmp_path, monkeypatch):
    _write_guardrails(tmp_path, HARD_DRAFT_ENTRY_YAML)  # classifies as permission-rule by default
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gg, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(gg, "SETTINGS_FILE", settings_file)
    monkeypatch.setattr(gg, "ROOT", tmp_path)

    exit_code = gg.main(["no-global-python", "--mechanism", "hook-script", "--apply"])

    assert exit_code == 0
    script_path = tmp_path / "docs" / "tools" / "guardrail_hooks" / "no-global-python.py"
    assert script_path.exists()
