#!/usr/bin/env python3
"""Registry linter: validates docs/memory/{GUARDRAILS,PROCEDURES,LESSONS,SEMANTICS}.yaml.

Enforces the schema in
docs/superpowers/specs/2026-07-10-knowledge-registry-taxonomy-design.md.
Exit 0 = clean, 1 = violations found.
Run: uv run --project docs/tools python docs/tools/check_registries.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]  # workspace root
MEMORY_DIR = ROOT / "docs" / "memory"
SEMANTICS_FILE = MEMORY_DIR / "SEMANTICS.yaml"

# filename -> {"is_guardrail": bool}. SEMANTICS.yaml is handled separately (it's
# the tag vocabulary source, not a content registry with the common schema).
CONTENT_REGISTRIES: dict[str, dict] = {
    "GUARDRAILS.yaml": {"is_guardrail": True},
    "PROCEDURES.yaml": {"is_guardrail": False},
    "LESSONS.yaml": {"is_guardrail": False},
}


def load_yaml_list(path: Path) -> list:
    """Load a registry file's top-level list. Missing file -> []."""
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or []
    if not isinstance(data, list):
        raise ValueError(
            f"{path}: expected a top-level YAML list, got {type(data).__name__}"
        )
    return data


def load_semantics_ids(path: Path) -> set[str]:
    return {
        entry["id"]
        for entry in load_yaml_list(path)
        if isinstance(entry, dict) and "id" in entry
    }


COMMON_FIELDS = {
    "id", "summary", "applicability", "status", "promotion_type",
    "promoted_to", "promotion_count", "episodes",
}
GUARDRAIL_FIELDS = COMMON_FIELDS | {"enforceability", "hook"}

STATUS_VALUES = {"draft", "promoted"}
PROMOTION_TYPE_VALUES = {"skill", "hook", "agent", None}
ENFORCEABILITY_VALUES = {"hard", "soft"}


def validate_entry(
    entry, rel: str, index: int, is_guardrail: bool, semantics_ids: set, errors: list
) -> None:
    loc = f"{rel}[{index}]"
    if not isinstance(entry, dict):
        errors.append(f"{loc}: entry is not a mapping")
        return

    entry_id = entry.get("id")
    label = f"{loc} ({entry_id!r})"

    required = GUARDRAIL_FIELDS if is_guardrail else COMMON_FIELDS
    missing = required - entry.keys()
    # content/draft_ref are validated separately (exactly-one-of), not via `required`.
    missing -= set()
    if missing:
        errors.append(f"{label}: missing field(s) {sorted(missing)}")

    if not entry_id or not isinstance(entry_id, str):
        errors.append(f"{loc}: 'id' must be a non-empty string")

    status = entry.get("status")
    if status not in STATUS_VALUES:
        errors.append(f"{label}: status {status!r} not in {sorted(STATUS_VALUES)}")

    promotion_type = entry.get("promotion_type")
    if promotion_type not in PROMOTION_TYPE_VALUES:
        errors.append(
            f"{label}: promotion_type {promotion_type!r} not in "
            f"{sorted(str(v) for v in PROMOTION_TYPE_VALUES)}"
        )

    if promotion_type is not None and status == "promoted" and not entry.get("promoted_to"):
        errors.append(f"{label}: status is 'promoted' but promoted_to is not set")

    applicability = entry.get("applicability") or []
    if not isinstance(applicability, list):
        errors.append(f"{label}: applicability must be a list")
    else:
        for tag in applicability:
            if tag not in semantics_ids:
                errors.append(f"{label}: applicability tag {tag!r} not in SEMANTICS.yaml")

    content = entry.get("content")
    draft_ref = entry.get("draft_ref")
    if bool(content) == bool(draft_ref):
        errors.append(f"{label}: exactly one of 'content' or 'draft_ref' must be set")
    if draft_ref and not (ROOT / draft_ref).exists():
        errors.append(f"{label}: draft_ref {draft_ref!r} does not resolve to a file")

    promoted_to = entry.get("promoted_to")
    if promoted_to:
        promoted_to_path = promoted_to.split("#", 1)[0]
        if not (ROOT / promoted_to_path).exists():
            errors.append(f"{label}: promoted_to {promoted_to!r} does not resolve to a file")

    if is_guardrail:
        enforceability = entry.get("enforceability")
        if enforceability not in ENFORCEABILITY_VALUES:
            errors.append(
                f"{label}: enforceability {enforceability!r} not in "
                f"{sorted(ENFORCEABILITY_VALUES)}"
            )
        hook = entry.get("hook")
        if hook is not None and not isinstance(hook, str):
            errors.append(f"{label}: hook must be a string or null")


def run_registry_checks(memory_dir: Path) -> list[str]:
    errors: list = []
    semantics_ids = load_semantics_ids(memory_dir / "SEMANTICS.yaml")

    for filename, opts in CONTENT_REGISTRIES.items():
        path = memory_dir / filename
        rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        entries = load_yaml_list(path)
        seen_ids: set = set()
        for i, entry in enumerate(entries):
            validate_entry(entry, rel, i, opts["is_guardrail"], semantics_ids, errors)
            entry_id = entry.get("id") if isinstance(entry, dict) else None
            if entry_id:
                if entry_id in seen_ids:
                    errors.append(f"{rel}[{i}]: duplicate id {entry_id!r}")
                seen_ids.add(entry_id)

    return errors


def main() -> int:
    errors = run_registry_checks(MEMORY_DIR)
    if errors:
        print(f"\n{len(errors)} registry issue(s):\n")
        for e in sorted(errors):
            print("  " + e)
        return 1
    print(f"OK — {len(CONTENT_REGISTRIES)} registries pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
