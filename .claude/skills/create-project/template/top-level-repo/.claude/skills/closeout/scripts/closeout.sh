#!/usr/bin/env bash
set -euo pipefail

# --- flags ---
no_delete=0
auto_yes=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-delete)
      no_delete=1
      shift
      ;;
    -y|--yes)
      auto_yes=1
      shift
      ;;
    -h|--help)
      echo "Usage: closeout.sh [--no-delete] [-y|--yes]" >&2
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: closeout.sh [--no-delete] [-y|--yes]" >&2
      exit 2
      ;;
  esac
done

# --- repo root validation ---
if [[ ! -d ".git" ]]; then
  echo "Error: must be run from the repo root (.git/ must exist)." >&2
  exit 1
fi

# --- detect current branch ---
current_branch="$(git rev-parse --abbrev-ref HEAD)"

# --- detect default branch ---
default_branch="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || true)"
if [[ -z "$default_branch" ]]; then
  if git show-ref --verify --quiet refs/heads/main 2>/dev/null; then
    default_branch="main"
  elif git show-ref --verify --quiet refs/heads/master 2>/dev/null; then
    default_branch="master"
  else
    # Brand-new repo: default branch has no commits yet; assume "main".
    default_branch="main"
  fi
fi

# --- abort if already on default branch ---
if [[ "$current_branch" == "$default_branch" ]]; then
  echo "Error: currently on '$default_branch'. Switch to the task branch before running closeout." >&2
  exit 1
fi

# --- warn if episode file is missing ---
episode_file="docs/Memory/Episodes/${current_branch}.md"
if [[ ! -f "$episode_file" ]]; then
  echo "Warning: episode file not found: $episode_file"
  echo "  Run /closeout steps 3–4 to create it before merging."
fi

# --- warn if NOTES.md has non-placeholder content ---
notes_file="docs/NOTES.md"
if [[ -f "$notes_file" ]]; then
  # Flag lines that are not: blank, headings, standard header prose, or dash-only placeholders
  non_placeholder="$(grep -Ev '^(#|$|Last updated:|Shared scratchpad|Scratch notes here|## |-$)' "$notes_file" || true)"
  if [[ -n "$non_placeholder" ]]; then
    echo "Warning: $notes_file appears to have non-placeholder content."
    echo "  Run /closeout step 7 to clean it before merging."
  fi
fi

# --- confirmation prompt ---
echo ""
echo "About to close out branch: $current_branch"
echo "  Merge into:  $default_branch"
if [[ "$no_delete" -eq 0 ]]; then
  echo "  After merge: delete $current_branch"
else
  echo "  After merge: keep $current_branch (--no-delete)"
fi
echo ""
if [[ "$auto_yes" -eq 1 ]]; then
  echo "(--yes flag: skipping confirmation)"
else
  read -r -t 30 -p "Confirm? [y/N] " confirm || { echo "Timeout or no input — aborting."; exit 1; }
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
  fi
fi

# --- commit any remaining changes ---
if ! git diff --quiet || ! git diff --cached --quiet || git ls-files --others --exclude-standard | grep -q .; then
  git add -A
  git commit -m "chore: closeout – commit remaining changes on $current_branch"
  echo "Committed remaining changes on $current_branch"
fi

# --- git operations ---
if git show-ref --verify --quiet "refs/heads/$default_branch"; then
  git checkout "$default_branch"
  git merge --no-ff "$current_branch" -m "Merge branch '$current_branch'"
  branch_delete_flag="-d"
else
  # Brand-new repo: default branch has no commits yet.
  # Create it at the task branch's current HEAD instead of merging.
  git branch "$default_branch"
  git checkout "$default_branch"
  branch_delete_flag="-D"
fi

if [[ "$no_delete" -eq 0 ]]; then
  git branch "$branch_delete_flag" "$current_branch"
  echo "Deleted branch: $current_branch"
fi

# --- summary ---
echo ""
echo "Closeout complete."
echo "  Merged: $current_branch → $default_branch"
if [[ "$no_delete" -eq 0 ]]; then
  echo "  Branch deleted: $current_branch"
else
  echo "  Branch kept: $current_branch"
fi
