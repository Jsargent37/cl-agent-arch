#!/usr/bin/env python3
# screen-intelligence-research/docs/tools/registry_index.py
"""Registry relevance-check support tool: builds a compact index of the four
knowledge registries (no content bodies) and fetches full content for specific
entry ids.

Used by the `registry-relevance-check` agent (via --index) and by `new-task`
(via --fetch), per
docs/superpowers/specs/2026-07-10-registry-relevance-check-design.md.
Run: uv run --project docs/tools python docs/tools/registry_index.py --index
     uv run --project docs/tools python docs/tools/registry_index.py --fetch <id> [<id> ...]
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]  # workspace root
MEMORY_DIR = ROOT / "docs" / "memory"

REGISTRY_FILES = ["GUARDRAILS.yaml", "PROCEDURES.yaml", "LESSONS.yaml", "SEMANTICS.yaml"]
INDEX_FIELDS = ["id", "summary", "applicability", "status", "promotion_type"]


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


def build_index(memory_dir: Path) -> dict[str, list[dict]]:
    """Return {registry_filename: [compact entry, ...]} across all four registries.

    Each compact entry has only id/summary/applicability/status/promotion_type --
    never content or draft_ref.
    """
    index: dict[str, list[dict]] = {}
    for filename in REGISTRY_FILES:
        entries = load_yaml_list(memory_dir / filename)
        index[filename] = [
            {field: entry.get(field) for field in INDEX_FIELDS}
            for entry in entries
            if isinstance(entry, dict)
        ]
    return index


def format_index(index: dict[str, list[dict]]) -> str:
    """Render the index as readable YAML, grouped by registry filename."""
    lines: list[str] = []
    for filename, entries in index.items():
        lines.append(f"# {filename}")
        lines.append(yaml.safe_dump(entries, sort_keys=False, allow_unicode=True).rstrip("\n"))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


import argparse
import sys


class RegistryIndexError(ValueError):
    """Raised when a requested entry id cannot be found in any registry."""


def find_entry(memory_dir: Path, entry_id: str) -> tuple[str, dict]:
    """Find entry_id across all four registries. Returns (filename, entry).

    Raises RegistryIndexError if not found in any registry.
    """
    for filename in REGISTRY_FILES:
        for entry in load_yaml_list(memory_dir / filename):
            if isinstance(entry, dict) and entry.get("id") == entry_id:
                return filename, entry
    raise RegistryIndexError(f"no entry with id {entry_id!r} in any registry")


def format_fetch(memory_dir: Path, entry_ids: list[str]) -> str:
    """Render full content for each requested id, in the order given.

    Entries with inline `content` print it directly; entries with `draft_ref`
    print the file path instead of inlining it, so the caller reads that file
    directly. Raises RegistryIndexError (via find_entry) if any id is missing.
    """
    lines: list[str] = []
    for entry_id in entry_ids:
        filename, entry = find_entry(memory_dir, entry_id)
        lines.append(f"# {entry_id} ({filename})")
        lines.append(f"summary: {entry.get('summary')}")
        if entry.get("content"):
            lines.append(f"content: {entry['content']}")
        elif entry.get("draft_ref"):
            lines.append(f"draft_ref: {entry['draft_ref']}  # read this file directly")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--index", action="store_true", help="Print the compact index (no content bodies)."
    )
    group.add_argument(
        "--fetch", nargs="+", metavar="ID", help="Print full content for one or more entry ids."
    )
    args = parser.parse_args(argv)

    if args.index:
        print(format_index(build_index(MEMORY_DIR)), end="")
        return 0

    try:
        print(format_fetch(MEMORY_DIR, args.fetch), end="")
    except RegistryIndexError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
