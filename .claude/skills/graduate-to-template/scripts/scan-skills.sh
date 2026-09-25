#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(dirname "$script_dir")"
projects_root="$(cd "$skill_dir/../../.." && pwd)"
template_skills="$projects_root/.claude/skills/create-project/template/top-level-repo/.claude/skills"

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

for skill_md in "$projects_root"/*/.claude/skills/*/SKILL.md; do
  [[ -f "$skill_md" ]] || continue
  project_dir="$(dirname "$(dirname "$(dirname "$(dirname "$skill_md")")")")"
  project="$(basename "$project_dir")"
  skill_name="$(basename "$(dirname "$skill_md")")"
  printf '%s\t%s\n' "$skill_name" "$project" >> "$tmp"
done

echo "Skill occurrence report (name, project count, projects):"
sort -u "$tmp" | awk -F'\t' '
  { count[$1]++; list[$1] = list[$1] $2 "," }
  END { for (n in count) print n "\t" count[n] "\t" list[n] }
' | sort

echo ""
echo "Drift vs template (project copy differs from template original):"
while IFS=$'\t' read -r skill_name project; do
  skill_md="$projects_root/$project/.claude/skills/$skill_name/SKILL.md"
  template_md="$template_skills/$skill_name/SKILL.md"
  if [[ -f "$template_md" ]] && ! diff -q "$skill_md" "$template_md" >/dev/null 2>&1; then
    echo "DIFF: $project/$skill_name vs template"
  fi
done < <(sort -u "$tmp")
