#!/usr/bin/env python3
"""Registry linter: validates docs/memory/{GUARDRAILS,PROCEDURES,LESSONS,SEMANTICS}.md.

Registries are Markdown files, one `### <id>` heading + fenced ```yaml block
per entry (see registry_index.py for the shared parser). `ARCHIVE.md` is NOT a
fifth registry validated the same way as the other four: only its id set is
read (via load_archive_ids), to cross-reference `distilled_into` targets on the
real registries. ARCHIVE.md's own field schema (`collapsed_on`,
`original_promotions`, etc.) is not separately validated by this script.
ARCHIVE.md is intentionally NOT in registry_index.py's REGISTRY_FILES -- it
stays out of the relevance-check index and every required-read list.
Exit 0 = clean, 1 = violations found.
Run: uv run --project docs/tools python docs/tools/check_registries.py
"""
from __future__ import annotations

from pathlib import Path

from registry_index import load_registry_list

ROOT = Path(__file__).resolve().parents[2]  # workspace root
MEMORY_DIR = ROOT / "docs" / "memory"

# filename -> {"is_guardrail": bool, "is_procedure": bool}. SEMANTICS.md is handled
# separately (it's the tag vocabulary source, not a content registry with the
# common schema). ARCHIVE.md is handled separately too (read on demand to validate
# distilled_into references, never iterated as a content registry of its own).
CONTENT_REGISTRIES: dict[str, dict] = {
    "GUARDRAILS.md": {"is_guardrail": True, "is_procedure": False},
    "PROCEDURES.md": {"is_guardrail": False, "is_procedure": True},
    "LESSONS.md": {"is_guardrail": False, "is_procedure": False},
}

COMMON_FIELDS = {
    "id", "summary", "applicability", "status", "promotion_type",
    "promoted_to", "promotion_count", "episodes",
}
GUARDRAIL_FIELDS = COMMON_FIELDS | {"enforceability", "hook", "tier", "severity"}
PROCEDURE_FIELDS = COMMON_FIELDS | {"distilled_into"}

STATUS_VALUES = {"draft", "promoted"}
PROMOTION_TYPE_VALUES = {"skill", "hook", "agent", None}
ENFORCEABILITY_VALUES = {"hard", "soft"}
TIER_VALUES = {"script", "review", "judgment", None}
SEVERITY_VALUES = {"low", "medium", "high", None}


def load_semantics_ids(path: Path) -> set[str]:
    return {entry["id"] for entry in load_registry_list(path) if "id" in entry}


def load_archive_ids(path: Path) -> set[str]:
    return {entry["id"] for entry in load_registry_list(path) if "id" in entry}


def validate_entry(
    entry: dict,
    rel: str,
    index: int,
    is_guardrail: bool,
    is_procedure: bool,
    semantics_ids: set,
    archive_ids: set,
    errors: list,
) -> None:
    loc = f"{rel}[{index}]"
    entry_id = entry.get("id")
    label = f"{loc} ({entry_id!r})"

    if is_guardrail:
        required = GUARDRAIL_FIELDS
    elif is_procedure:
        required = PROCEDURE_FIELDS
    else:
        required = COMMON_FIELDS
    missing = required - entry.keys()
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
                errors.append(f"{label}: applicability tag {tag!r} not in SEMANTICS.md")

    distilled_into = entry.get("distilled_into") if is_procedure else None
    content = entry.get("content")
    draft_ref = entry.get("draft_ref")
    if not distilled_into and bool(content) == bool(draft_ref):
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
        if "tier" not in entry:
            errors.append(f"{label}: missing field(s) ['tier']")
        elif entry.get("tier") not in TIER_VALUES:
            errors.append(f"{label}: tier {entry.get('tier')!r} not in {sorted(str(v) for v in TIER_VALUES)}")
        if "severity" not in entry:
            errors.append(f"{label}: missing field(s) ['severity']")
        elif entry.get("severity") not in SEVERITY_VALUES:
            errors.append(f"{label}: severity {entry.get('severity')!r} not in {sorted(str(v) for v in SEVERITY_VALUES)}")

    if is_procedure:
        if "distilled_into" not in entry:
            errors.append(f"{label}: missing field(s) ['distilled_into']")
        elif distilled_into is not None:
            if not isinstance(distilled_into, str) or not distilled_into:
                errors.append(f"{label}: distilled_into must be a non-empty string or null")
            if content:
                errors.append(
                    f"{label}: distilled_into is set but content is not empty -- "
                    "collapse the full body into ARCHIVE.md and clear content"
                )
            if entry_id not in archive_ids:
                errors.append(
                    f"{label}: distilled_into is set but no ARCHIVE.md entry with id "
                    f"{entry_id!r} exists"
                )
            if entry.get("status") != "promoted":
                errors.append(
                    f"{label}: distilled_into is set but status is "
                    f"{entry.get('status')!r}, not 'promoted' -- a collapsed entry must be "
                    "marked promoted so it is not re-collected/re-graduated"
                )


def run_registry_checks(memory_dir: Path) -> list[str]:
    errors: list = []
    semantics_ids = load_semantics_ids(memory_dir / "SEMANTICS.md")
    archive_ids = load_archive_ids(memory_dir / "ARCHIVE.md")

    for filename, opts in CONTENT_REGISTRIES.items():
        path = memory_dir / filename
        rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        entries = load_registry_list(path)
        seen_ids: set = set()
        for i, entry in enumerate(entries):
            validate_entry(
                entry, rel, i, opts["is_guardrail"], opts["is_procedure"],
                semantics_ids, archive_ids, errors,
            )
            entry_id = entry.get("id")
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
