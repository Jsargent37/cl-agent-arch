#!/usr/bin/env python3
"""Guardrail hook-graduation tool: turns a `hard`-enforceability GUARDRAILS.md
entry into a settings.json enforcement mechanism (permission rule or PreToolUse
hook-script stub), tags it `tier: script`, and updates the registry entry to
match, editing the Markdown file in place.

Default mode proposes only (no writes); pass --apply to write.
Run: uv run --project docs/tools python docs/tools/graduate_guardrail.py <id> [--severity low|medium|high] [--apply]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from registry_index import load_registry_list

ROOT = Path(__file__).resolve().parents[2]  # workspace root
MEMORY_DIR = ROOT / "docs" / "memory"
SETTINGS_FILE = ROOT / ".claude" / "settings.json"

KNOWN_CLI_VERBS = {
    "pip", "pip3", "npm", "pnpm", "yarn", "brew", "apt", "apt-get", "choco",
    "winget", "pipx", "conda", "gem", "cargo", "go", "python", "python3",
}


class GuardrailError(ValueError):
    """Raised when a guardrail entry cannot be graduated."""


class _LiteralDumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_LiteralDumper.add_representer(str, _str_presenter)


def dump_entry_yaml(data: dict) -> str:
    """Dump an entry dict as YAML, using literal block style for multi-line strings.

    `id` is excluded — it lives in the `### <id>` heading, not the fenced block.
    """
    body = {k: v for k, v in data.items() if k != "id"}
    return yaml.dump(body, Dumper=_LiteralDumper, sort_keys=False, allow_unicode=True).rstrip("\n")


def replace_entry_block(text: str, entry_id: str, new_data: dict) -> str:
    """Replace entry_id's fenced ```yaml block in text with new_data's rendering.

    Anchors on the full `### <id>` heading line (word boundary via `\\s*$`) so an
    id that is a prefix of another id is never matched.
    """
    heading_re = re.compile(
        rf"(^### {re.escape(entry_id)}\s*\n```yaml\n)(.*?)(\n```)",
        re.DOTALL | re.MULTILINE,
    )
    new_yaml = dump_entry_yaml(new_data)
    new_text, count = heading_re.subn(lambda m: m.group(1) + new_yaml + m.group(3), text, count=1)
    if count == 0:
        raise ValueError(f"entry {entry_id!r} not found")
    return new_text


def load_guardrail_entry(memory_dir: Path, guardrail_id: str) -> dict:
    """Load one entry from GUARDRAILS.md by id. Raises GuardrailError if missing."""
    entries = load_registry_list(memory_dir / "GUARDRAILS.md")
    for entry in entries:
        if entry.get("id") == guardrail_id:
            return entry
    raise GuardrailError(f"no guardrail with id {guardrail_id!r} in {memory_dir / 'GUARDRAILS.md'}")


def validate_eligible(entry: dict) -> None:
    """Raise GuardrailError if entry is not eligible for hook graduation."""
    if entry.get("enforceability") != "hard":
        raise GuardrailError(
            f"{entry.get('id')!r} has enforceability {entry.get('enforceability')!r}, "
            "not 'hard' -- only hard guardrails graduate to hooks"
        )
    if entry.get("status") != "draft":
        raise GuardrailError(
            f"{entry.get('id')!r} has status {entry.get('status')!r}, "
            "not 'draft' -- already graduated or not eligible"
        )


def classify_mechanism(entry: dict) -> tuple[str, str | None]:
    """Propose 'permission-rule' (with a command pattern) or 'hook-script' (no pattern).

    Scans backtick-quoted spans in `content` for a known CLI verb as the first
    word (e.g. `pip install` -> pip). The first match wins. No match -> hook-script.
    """
    content = entry.get("content") or ""
    for span in re.findall(r"`([^`]+)`", content):
        stripped = span.strip()
        first_word = stripped.split()[0] if stripped else ""
        if first_word in KNOWN_CLI_VERBS:
            return "permission-rule", stripped
    return "hook-script", None


def build_registry_update(
    entry: dict, mechanism: str, target: str, severity: str | None = None
) -> dict:
    """Return a copy of entry with status/promotion_type/promoted_to/tier/severity set.

    Every mechanism this tool produces (permission-rule, hook-script) is `script`
    tier by construction -- this tool never proposes `review` or `judgment` tier.
    `severity` is proposed by the caller (distill's Graduate step); this tool never
    guesses it itself.
    """
    updated = dict(entry)
    updated["status"] = "promoted"
    updated["promotion_type"] = "hook"
    updated["promoted_to"] = target
    updated["tier"] = "script"
    if severity is not None:
        updated["severity"] = severity
    return updated


def permission_rule_string(pattern: str) -> str:
    """Format a command pattern as a Claude Code permission rule.

    e.g. 'pip install' -> 'Bash(pip install:*)'
    """
    return f"Bash({pattern}:*)"


def load_settings(path: Path) -> dict:
    if not path.exists():
        raise GuardrailError(f"{path} does not exist")
    return json.loads(path.read_text(encoding="utf-8"))


def add_permission_rule(settings: dict, rule_type: str, rule: str) -> tuple[dict, bool]:
    """Add `rule` to settings['permissions'][rule_type] if not already present.

    Returns (updated_settings, was_added); was_added is False on no-op.
    Does not mutate the input.
    """
    if rule_type not in ("deny", "ask"):
        raise GuardrailError(f"rule_type must be 'deny' or 'ask', got {rule_type!r}")
    updated = json.loads(json.dumps(settings))
    permissions = updated.setdefault("permissions", {})
    rules = permissions.setdefault(rule_type, [])
    if rule in rules:
        return updated, False
    rules.append(rule)
    return updated, True


def scaffold_hook_script(hook_scripts_dir: Path, guardrail_id: str) -> Path:
    """Write a stub PreToolUse hook script for guardrail_id if it doesn't already exist."""
    hook_scripts_dir.mkdir(parents=True, exist_ok=True)
    script_path = hook_scripts_dir / f"{guardrail_id}.py"
    if not script_path.exists():
        script_path.write_text(
            f'#!/usr/bin/env python3\n'
            f'"""PreToolUse hook stub for guardrail {guardrail_id!r}.\n\n'
            f'TODO: implement enforcement logic for {guardrail_id}\n'
            f'"""\n'
            f'import sys\n\n\n'
            f'def main() -> int:\n'
            f'    # TODO: implement enforcement logic for {guardrail_id}\n'
            f'    return 0\n\n\n'
            f'if __name__ == "__main__":\n'
            f'    raise SystemExit(main())\n',
            encoding="utf-8",
        )
    return script_path


def add_pretooluse_hook(settings: dict, matcher: str, command: str) -> tuple[dict, bool]:
    """Add a PreToolUse hook entry (matcher + command) if not already present.

    Returns (updated_settings, was_added). Does not mutate the input.
    """
    updated = json.loads(json.dumps(settings))
    hooks = updated.setdefault("hooks", {})
    pretooluse = hooks.setdefault("PreToolUse", [])
    for entry in pretooluse:
        if entry.get("matcher") == matcher:
            for h in entry.get("hooks", []):
                if h.get("command") == command:
                    return updated, False
            entry.setdefault("hooks", []).append({"type": "command", "command": command})
            return updated, True
    pretooluse.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})
    return updated, True


def propose(
    entry: dict,
    mechanism: str,
    pattern: str | None,
    rule_type: str,
    severity: str | None = None,
) -> dict:
    """Build the full proposal: mechanism, settings-change description, and registry update."""
    guardrail_id = entry["id"]
    if mechanism == "permission-rule":
        if not pattern:
            raise GuardrailError("permission-rule mechanism requires a pattern")
        rule = permission_rule_string(pattern)
        target = f".claude/settings.json#permissions.{rule_type}"
        settings_change = f"add {rule!r} to permissions.{rule_type}"
    elif mechanism == "hook-script":
        target = f"docs/tools/guardrail_hooks/{guardrail_id}.py"
        settings_change = (
            f"scaffold {target} (stub) and add a PreToolUse hook entry "
            f"matching this guardrail's tool(s)"
        )
    else:
        raise GuardrailError(f"unknown mechanism {mechanism!r}")

    return {
        "mechanism": mechanism,
        "pattern": pattern,
        "rule_type": rule_type,
        "settings_change": settings_change,
        "registry_update": build_registry_update(entry, mechanism, target, severity),
        "target": target,
    }


def apply_proposal(
    root: Path, settings_file: Path, memory_dir: Path, entry: dict, proposal: dict
) -> None:
    """Write the settings.json change, hook-script stub (if applicable), and the
    updated GUARDRAILS.md entry in place."""
    guardrail_id = entry["id"]

    if proposal["mechanism"] == "permission-rule":
        settings = load_settings(settings_file)
        rule = permission_rule_string(proposal["pattern"])
        updated_settings, _ = add_permission_rule(settings, proposal["rule_type"], rule)
        settings_file.write_text(json.dumps(updated_settings, indent=2) + "\n", encoding="utf-8")
    elif proposal["mechanism"] == "hook-script":
        hook_scripts_dir = root / "docs" / "tools" / "guardrail_hooks"
        script_path = scaffold_hook_script(hook_scripts_dir, guardrail_id)
        settings = load_settings(settings_file)
        command = f"python {script_path.relative_to(root).as_posix()}"
        updated_settings, _ = add_pretooluse_hook(settings, "*", command)
        settings_file.write_text(json.dumps(updated_settings, indent=2) + "\n", encoding="utf-8")

    guardrails_path = memory_dir / "GUARDRAILS.md"
    text = guardrails_path.read_text(encoding="utf-8-sig")
    updated_text = replace_entry_block(text, guardrail_id, proposal["registry_update"])
    guardrails_path.write_text(updated_text, encoding="utf-8")


def print_proposal(entry: dict, proposal: dict) -> None:
    print(f"Guardrail: {entry['id']}")
    print(f"  summary: {entry.get('summary')}")
    print(
        f"  current: status={entry.get('status')} "
        f"promotion_type={entry.get('promotion_type')} tier={entry.get('tier')} hook={entry.get('hook')}"
    )
    print()
    print(f"Proposed mechanism: {proposal['mechanism']}")
    print(f"  {proposal['settings_change']}")
    print()
    print("Proposed registry update:")
    ru = proposal["registry_update"]
    print(f"  status: {entry.get('status')} -> {ru['status']}")
    print(f"  promotion_type: {entry.get('promotion_type')} -> {ru['promotion_type']}")
    print(f"  promoted_to: {entry.get('promoted_to')} -> {ru['promoted_to']}")
    print(f"  tier: {entry.get('tier')} -> {ru['tier']}")
    if "severity" in ru:
        print(f"  severity: {entry.get('severity')} -> {ru['severity']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guardrail_id")
    parser.add_argument(
        "--mechanism", choices=["permission-rule", "hook-script"], default=None,
        help="Override the tool's proposed enforcement mechanism.",
    )
    parser.add_argument(
        "--pattern", default=None,
        help="Command pattern for permission-rule mechanism (e.g. 'pip install').",
    )
    parser.add_argument(
        "--rule-type", choices=["deny", "ask"], default="deny",
        help="Which permission list to add to for permission-rule mechanism (default: deny).",
    )
    parser.add_argument(
        "--severity", choices=["low", "medium", "high"], default=None,
        help="Severity to stamp on the graduated entry (proposed by the caller, e.g. distill).",
    )
    parser.add_argument("--apply", action="store_true", help="Write the changes (default: propose only).")
    args = parser.parse_args(argv)

    try:
        entry = load_guardrail_entry(MEMORY_DIR, args.guardrail_id)
        validate_eligible(entry)

        if args.mechanism:
            mechanism = args.mechanism
            pattern = args.pattern
        else:
            mechanism, pattern = classify_mechanism(entry)
            if args.pattern:
                pattern = args.pattern

        proposal = propose(entry, mechanism, pattern, args.rule_type, args.severity)
    except GuardrailError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print_proposal(entry, proposal)

    if args.apply:
        apply_proposal(ROOT, SETTINGS_FILE, MEMORY_DIR, entry, proposal)
        print("\nApplied.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
