"""Tests for graduate_guardrail.py against the Markdown+YAML-block registry format."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from graduate_guardrail import (
    GuardrailError,
    ProposalInputs,
    ToolPaths,
    add_permission_rule,
    add_pretooluse_hook,
    apply_proposal,
    classify_mechanism,
    dump_entry_yaml,
    load_guardrail_entry,
    known_verbs_from_settings,
    load_known_cli_verbs,
    load_settings,
    propose,
    replace_entry_block,
    scaffold_hook_script,
    suggest_hook_matcher,
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
    proposal = propose(entry, ProposalInputs(mechanism, pattern, "deny"))
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
    proposal = propose(entry, ProposalInputs(mechanism, pattern, "deny"))
    apply_proposal(ToolPaths(tmp_path, settings_file, memory_dir), entry, proposal)

    updated_text = (memory_dir / "GUARDRAILS.md").read_text(encoding="utf-8")
    assert "status: promoted" in updated_text
    assert "tier: script" in updated_text
    # sibling entry survives untouched
    assert "A second entry whose id is a superstring" in updated_text
    settings = json.loads(settings_file.read_text(encoding="utf-8"))
    assert "Bash(pip install:*)" in settings["permissions"]["deny"]


def test_propose_with_severity_sets_severity_on_registry_update(tmp_path: Path):
    (tmp_path / "GUARDRAILS.md").write_text(SAMPLE_GUARDRAILS_MD, encoding="utf-8")
    entry = load_guardrail_entry(tmp_path, "no-global-python")
    mechanism, pattern = classify_mechanism(entry)
    proposal = propose(entry, ProposalInputs(mechanism, pattern, "deny", severity="high"))
    assert proposal["registry_update"]["severity"] == "high"


def test_propose_unknown_mechanism_raises():
    entry = {"id": "x", "content": ""}
    with pytest.raises(GuardrailError):
        propose(entry, ProposalInputs("not-a-real-mechanism", None, "deny"))


def test_propose_permission_rule_without_pattern_raises():
    entry = {"id": "x", "content": ""}
    with pytest.raises(GuardrailError):
        propose(entry, ProposalInputs("permission-rule", None, "deny"))


def test_validate_eligible_rejects_soft_enforceability():
    with pytest.raises(GuardrailError):
        validate_eligible({"id": "x", "enforceability": "soft", "status": "draft"})


def test_validate_eligible_rejects_already_promoted():
    with pytest.raises(GuardrailError):
        validate_eligible({"id": "x", "enforceability": "hard", "status": "promoted"})


def test_classify_mechanism_falls_back_to_hook_script_for_unknown_verb():
    entry = {"content": "Run `some-custom-tool do-thing` before committing."}
    mechanism, pattern = classify_mechanism(entry)
    assert mechanism == "hook-script"
    assert pattern is None


def test_load_settings_missing_file_raises(tmp_path: Path):
    with pytest.raises(GuardrailError):
        load_settings(tmp_path / "nope.json")


def test_load_known_cli_verbs_derives_from_settings_deny_and_ask_bash_and_powershell(tmp_path: Path):
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "permissions": {
                    "deny": ["Bash(pip install:*)"],
                    "ask": ["Bash(rm:*)", "Bash(git clean:*)", "PowerShell(Remove-Item:*)"],
                }
            }
        ),
        encoding="utf-8",
    )
    verbs = load_known_cli_verbs(settings_file)
    assert verbs == {"pip", "rm", "git", "Remove-Item"}


def test_load_known_cli_verbs_missing_file_returns_empty_set(tmp_path: Path):
    assert load_known_cli_verbs(tmp_path / "nope.json") == set()


def test_known_verbs_from_settings_ignores_a_rule_with_no_command_text():
    # A malformed/placeholder rule like "Bash( :*)" has a non-empty regex
    # capture group that is pure whitespace -- must not raise IndexError when
    # there's no first word to extract.
    settings = {"permissions": {"deny": [], "ask": ["Bash( :*)", "Bash(rm:*)"]}}
    assert known_verbs_from_settings(settings) == {"rm"}


def test_known_verbs_from_settings_matches_load_known_cli_verbs(tmp_path: Path):
    settings = {"permissions": {"deny": [], "ask": ["Bash(ssh:*)", "PowerShell(Invoke-WebRequest:*)"]}}
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps(settings), encoding="utf-8")
    assert known_verbs_from_settings(settings) == load_known_cli_verbs(settings_file)
    assert known_verbs_from_settings(settings) == {"ssh", "Invoke-WebRequest"}


def test_classify_mechanism_uses_verbs_derived_from_settings_json_not_hardcoded_list():
    # "rm" was never in the old hand-maintained KNOWN_CLI_VERBS set --
    # classify_mechanism must still recognize it via a settings.json-derived
    # verb set. Pass known_verbs explicitly so this test doesn't depend on the
    # real template settings.json's current contents.
    entry = {"content": "Always confirm scope before `rm -rf` on shared directories."}
    mechanism, pattern = classify_mechanism(entry, known_verbs={"rm"})
    assert mechanism == "permission-rule"
    assert pattern == "rm -rf"


def test_suggest_hook_matcher_scopes_to_bash_for_unknown_shell_command():
    content = "Run `some-custom-tool do-thing` before committing."
    assert suggest_hook_matcher(content) == "Bash"


def test_suggest_hook_matcher_falls_back_to_wildcard_for_non_shell_guardrail():
    content = "Always write commit messages in the past tense."
    assert suggest_hook_matcher(content) == "*"


def test_suggest_hook_matcher_does_not_mistake_a_bare_filename_for_a_command():
    # A single backtick-quoted token (a filename or identifier, not a command
    # invocation) must not be scoped to 'Bash' -- there's no actual shell
    # command here for a Bash-matched hook to ever see.
    content = "Always keep `CHANGELOG.md` up to date before releasing."
    assert suggest_hook_matcher(content) == "*"


def test_suggest_hook_matcher_recognizes_path_qualified_commands():
    # A command invoked by absolute/relative path is still a real command
    # invocation and must be scoped to 'Bash', not fall through to '*'.
    content = "Run `/usr/local/bin/mytool clean` before committing."
    assert suggest_hook_matcher(content) == "Bash"


def test_propose_hook_script_scopes_matcher_to_bash_not_wildcard():
    entry = {
        "id": "needs-hook",
        "content": "Run `some-custom-tool do-thing` before committing.",
    }
    proposal = propose(entry, ProposalInputs("hook-script", None, "deny"))
    assert proposal["matcher"] == "Bash"
    assert "matcher 'Bash'" in proposal["settings_change"]


def test_apply_proposal_hook_script_wires_bash_matcher_not_wildcard(tmp_path: Path):
    hook_script_md = """### needs-hook
```yaml
summary: A guardrail naming a shell command with an unrecognized verb
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Run `some-custom-tool do-thing` before committing.
enforceability: hard
tier: null
severity: null
hook: null
```
"""
    memory_dir = tmp_path / "docs" / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "GUARDRAILS.md").write_text(hook_script_md, encoding="utf-8")
    settings_file = tmp_path / ".claude" / "settings.json"
    settings_file.parent.mkdir(parents=True)
    settings_file.write_text(json.dumps({"hooks": {}}), encoding="utf-8")

    entry = load_guardrail_entry(memory_dir, "needs-hook")
    mechanism, pattern = classify_mechanism(entry)
    assert mechanism == "hook-script"
    proposal = propose(entry, ProposalInputs(mechanism, pattern, "deny"))
    apply_proposal(ToolPaths(tmp_path, settings_file, memory_dir), entry, proposal)

    settings = json.loads(settings_file.read_text(encoding="utf-8"))
    pretooluse = settings["hooks"]["PreToolUse"]
    assert pretooluse[0]["matcher"] == "Bash"


def test_add_permission_rule_is_idempotent_and_does_not_mutate_input():
    original = {"permissions": {"deny": ["Bash(pip install:*)"]}}
    updated, was_added = add_permission_rule(original, "deny", "Bash(pip install:*)")
    assert was_added is False
    assert updated == original
    assert original == {"permissions": {"deny": ["Bash(pip install:*)"]}}

    updated, was_added = add_permission_rule(original, "deny", "Bash(npm install:*)")
    assert was_added is True
    assert "Bash(npm install:*)" in updated["permissions"]["deny"]
    assert "Bash(npm install:*)" not in original["permissions"]["deny"]


def test_add_permission_rule_rejects_bad_rule_type():
    with pytest.raises(GuardrailError):
        add_permission_rule({}, "allow", "Bash(pip install:*)")


def test_scaffold_hook_script_writes_stub_and_is_idempotent(tmp_path: Path):
    script_path = scaffold_hook_script(tmp_path, "no-global-python")
    assert script_path == tmp_path / "no-global-python.py"
    first_contents = script_path.read_text(encoding="utf-8")
    assert "def main() -> int:" in first_contents
    assert "no-global-python" in first_contents

    # A second call must not overwrite an existing stub with fresh boilerplate.
    script_path.write_text(first_contents + "\n# hand-written enforcement logic\n", encoding="utf-8")
    scaffold_hook_script(tmp_path, "no-global-python")
    assert "hand-written enforcement logic" in script_path.read_text(encoding="utf-8")


def test_add_pretooluse_hook_is_idempotent_and_does_not_mutate_input():
    original = {"hooks": {"PreToolUse": []}}
    updated, was_added = add_pretooluse_hook(original, "*", "python docs/tools/guardrail_hooks/x.py")
    assert was_added is True
    assert updated["hooks"]["PreToolUse"][0]["matcher"] == "*"
    assert original == {"hooks": {"PreToolUse": []}}

    updated, was_added = add_pretooluse_hook(updated, "*", "python docs/tools/guardrail_hooks/x.py")
    assert was_added is False
    assert len(updated["hooks"]["PreToolUse"][0]["hooks"]) == 1


def test_apply_proposal_hook_script_mechanism_scaffolds_and_wires_hook(tmp_path: Path):
    hook_script_md = """### needs-manual-check
```yaml
summary: A guardrail with no known CLI verb to key a permission rule off of
applicability: [python-environment]
status: draft
promotion_type: null
promoted_to: null
promotion_count: 1
episodes: []
content: Review this by hand before merging.
enforceability: hard
tier: null
severity: null
hook: null
```
"""
    memory_dir = tmp_path / "docs" / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "GUARDRAILS.md").write_text(hook_script_md, encoding="utf-8")
    settings_file = tmp_path / ".claude" / "settings.json"
    settings_file.parent.mkdir(parents=True)
    settings_file.write_text(json.dumps({"hooks": {}}), encoding="utf-8")

    entry = load_guardrail_entry(memory_dir, "needs-manual-check")
    mechanism, pattern = classify_mechanism(entry)
    assert mechanism == "hook-script"
    proposal = propose(entry, ProposalInputs(mechanism, pattern, "deny"))
    apply_proposal(ToolPaths(tmp_path, settings_file, memory_dir), entry, proposal)

    stub_path = tmp_path / "docs" / "tools" / "guardrail_hooks" / "needs-manual-check.py"
    assert stub_path.exists()
    settings = json.loads(settings_file.read_text(encoding="utf-8"))
    pretooluse = settings["hooks"]["PreToolUse"]
    assert pretooluse[0]["matcher"] == "*"
    assert "guardrail_hooks/needs-manual-check.py" in pretooluse[0]["hooks"][0]["command"]
    updated_text = (memory_dir / "GUARDRAILS.md").read_text(encoding="utf-8")
    assert "promotion_type: hook" in updated_text
