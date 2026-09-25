#!/usr/bin/env bash
set -euo pipefail

# --- argument validation ---
if [[ $# -lt 1 || -z "$1" ]]; then
  echo "Usage: new-task.sh <task-name>" >&2
  exit 2
fi
task_name="$1"

# --- repo root validation ---
if [[ ! -d ".git" || ! -d "docs" ]]; then
  echo "Error: must be run from the repo root (.git/ and docs/ must exist)." >&2
  exit 1
fi

# --- default branch detection ---
default_branch="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || true)"
if [[ -z "$default_branch" ]]; then
  if git show-ref --verify --quiet refs/heads/main 2>/dev/null; then
    default_branch="main"
  elif git show-ref --verify --quiet refs/heads/master 2>/dev/null; then
    default_branch="master"
  else
    # Brand-new repo with no commits: HEAD is the initial ref name.
    default_branch="main"
  fi
fi

# --- current branch check ---
# "HEAD" is returned by git on a new repo before the first commit — allow it.
current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEAD")"
if [[ "$current_branch" != "$default_branch" && "$current_branch" != "HEAD" ]]; then
  echo "Error: currently on branch '$current_branch'." >&2
  echo "Switch to '$default_branch' before starting a new task." >&2
  exit 1
fi

# --- build branch name ---
today="$(date +%Y-%m-%d)"
# Lowercase, replace spaces with hyphens, strip non-alphanumeric-hyphen chars,
# collapse consecutive hyphens, strip leading/trailing hyphens.
kebab_name="$(printf '%s' "$task_name" \
  | tr '[:upper:]' '[:lower:]' \
  | tr ' ' '-' \
  | tr -cd 'a-z0-9-' \
  | sed 's/-\{2,\}/-/g' \
  | sed 's/^-//;s/-$//')"

if [[ -z "$kebab_name" ]]; then
  echo "Error: task name '$task_name' produced an empty branch slug." >&2
  exit 2
fi

branch_name="${today}-${kebab_name}"

# --- create branch ---
git checkout -b "$branch_name"
echo "Created branch: $branch_name"

# --- copy episode template ---
template_file="docs/Memory/Episodes/episode-template.md"
episode_file="docs/Memory/Episodes/${branch_name}.md"
if [[ -f "$template_file" ]]; then
  cp "$template_file" "$episode_file"
  echo "Created episode file: $episode_file"
else
  echo "Warning: episode template not found at $template_file. Skipping episode creation." >&2
fi

# --- update NOTES.md active branch line ---
# Replaces the first non-blank line after the "## Active Branch" heading.
# Tolerates a blank line between the heading and the placeholder, and updates
# the line whether it is the "-" placeholder or an already-set branch name.
notes_file="docs/NOTES.md"
if [[ -f "$notes_file" ]]; then
  tmp=$(mktemp) || exit 1
  trap "rm -f '$tmp'" EXIT
  awk -v b="$branch_name" '
    /^## Active Branch/ { print; found=1; next }
    found && !done && NF > 0 { print "- " b; done=1; next }
    { print }
  ' "$notes_file" > "$tmp" && mv "$tmp" "$notes_file"
  echo "Updated Active Branch in $notes_file"
else
  echo "Warning: $notes_file not found. Skipping Active Branch update." >&2
fi

# --- print checklist ---
cat <<EOF

Branch ready: $branch_name

Required read order before coding:
  [ ] docs/ONBOARDING.md
  [ ] docs/TASK.md
  [ ] docs/README.md
  [ ] docs/ROADMAP.md
  [ ] docs/Memory/Semantics.md
  [ ] docs/Memory/Procedures.md
  [ ] recent files in docs/Memory/Episodes/

Next steps:
  1. Set ## Current Work and ## Next in docs/NOTES.md.
  2. Write the initial implementation plan in $episode_file before coding begins.
EOF
