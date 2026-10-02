#!/usr/bin/env python3
"""Registry relevance-check support tool: builds a compact index of the four
knowledge registries (no content bodies) and fetches full content for specific
entry ids.

Registries are Markdown files: one `### <id>` heading followed by a fenced
```yaml block per entry. Used by the registry-relevance-check step (via
--index) and by new-task (via --fetch).
Run: uv run --project docs/tools python docs/tools/registry_index.py --index
     uv run --project docs/tools python docs/tools/registry_index.py --fetch <id> [<id> ...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]  # workspace root
MEMORY_DIR = ROOT / "docs" / "memory"

REGISTRY_FILES = ["GUARDRAILS.md", "PROCEDURES.md", "LESSONS.md", "SEMANTICS.md"]
INDEX_FIELDS = ["id", "summary", "applicability", "status", "promotion_type"]

_ENTRY_HEADING_RE = re.compile(r"^### (\S+)\s*$", re.MULTILINE)
_YAML_BLOCK_RE = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


def parse_registry_markdown(text: str) -> list[dict[str, object]]:
    """Parse a registry Markdown file's text into a list of entry dicts.

    Each entry is `### <id>` followed by the first fenced ```yaml block after
    it (and before the next `### ` heading). The block's top-level YAML keys
    become dict fields; `id` is injected from the heading.
    """
    entries: list[dict[str, object]] = []
    headings = list(_ENTRY_HEADING_RE.finditer(text))
    for i, heading in enumerate(headings):
        entry_id = heading.group(1)
        start = heading.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block_text = text[start:end]
        yaml_match = _YAML_BLOCK_RE.search(block_text)
        if not yaml_match:
            continue
        data = yaml.safe_load(yaml_match.group(1)) or {}
        if not isinstance(data, dict):
            continue
        data["id"] = entry_id
        entries.append(data)
    return entries


def load_registry_list(path: Path) -> list[dict[str, object]]:
    """Load one registry Markdown file's entries. Missing file -> []."""
    if not path.exists():
        return []
    return parse_registry_markdown(path.read_text(encoding="utf-8-sig"))


def build_index(memory_dir: Path) -> dict[str, list[dict[str, object]]]:
    """Return {registry_filename: [compact entry, ...]} across all four registries.

    Each compact entry has only id/summary/applicability/status/promotion_type --
    never content or draft_ref.
    """
    index: dict[str, list[dict[str, object]]] = {}
    for filename in REGISTRY_FILES:
        entries = load_registry_list(memory_dir / filename)
        index[filename] = [
            {field: entry.get(field) for field in INDEX_FIELDS}
            for entry in entries
        ]
    return index


def format_index(index: dict[str, list[dict[str, object]]]) -> str:
    """Render the index as readable YAML, grouped by registry filename."""
    lines: list[str] = []
    for filename, entries in index.items():
        lines.append(f"# {filename}")
        lines.append(yaml.safe_dump(entries, sort_keys=False, allow_unicode=True).rstrip("\n"))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


class RegistryIndexError(ValueError):
    """Raised when a requested entry id cannot be found in any registry."""


def find_entry(memory_dir: Path, entry_id: str) -> tuple[str, dict[str, object]]:
    """Find entry_id across all four registries. Returns (filename, entry).

    Raises RegistryIndexError if not found in any registry.
    """
    for filename in REGISTRY_FILES:
        for entry in load_registry_list(memory_dir / filename):
            if entry.get("id") == entry_id:
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
        elif entry.get("distilled_into"):
            lines.append(f"distilled_into: {entry['distilled_into']}  # collapsed; see ARCHIVE.md / that id")
            if entry.get("promoted_to"):
                lines.append(f"promoted_to: {entry['promoted_to']}")
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
