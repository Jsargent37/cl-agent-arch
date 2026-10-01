#!/usr/bin/env bash
set -euo pipefail

quick=0
if [[ "${1:-}" == "--quick" ]]; then
  quick=1
fi

skills_root=".claude/skills"
if [[ ! -d "$skills_root" ]]; then
  echo "Error: $skills_root not found. Run from repo root." >&2
  exit 1
fi

cache_file="$skills_root/.drift-check-cache"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

for f in "$skills_root"/*/SKILL.md; do
  [[ -f "$f" ]] || continue
  name="$(basename "$(dirname "$f")")"
  mtime="$(stat -c '%Y' "$f" 2>/dev/null || stat -f '%m' "$f" 2>/dev/null)"
  desc="$(awk -F': ' '/^description:/ { sub(/^description: */, ""); print; exit }' "$f")"
  printf '%s\t%s\t%s\n' "$name" "$mtime" "$desc"
done | sort > "$tmp"

if [[ "$quick" -eq 1 && -f "$cache_file" ]]; then
  echo "Changed skills since last run:"
  comm -13 <(sort "$cache_file") <(sort "$tmp") | cut -f1
else
  echo "Full skill inventory:"
  cat "$tmp"
fi

cp "$tmp" "$cache_file"
