#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../lib/git-common.sh
source "$script_dir/../../lib/git-common.sh"

# Usage: merge-if-git.sh [--no-delete] [<recorded-branch-name>]
# <recorded-branch-name> is the active episode's `branch:` frontmatter value (the
# {date}-{slug} branch new-task's branch-if-git.sh created for this task). Only
# merges+deletes when the CURRENT branch matches it exactly -- refuses otherwise.
# --no-delete merges but keeps the task branch instead of deleting it.
no_delete=0
recorded_branch=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-delete) no_delete=1; shift ;;
    *)
      # Only the first positional arg counts, matching the old ${1:-} behavior.
      if [[ -z "$recorded_branch" ]]; then
        recorded_branch="$1"
      fi
      shift
      ;;
  esac
done

require_git_repo_or_exit "branch merge"

if ! git symbolic-ref -q HEAD >/dev/null; then
  echo "detached-head-skip-merge: HEAD is detached, refusing to merge/delete"
  exit 0
fi

current_branch="$(git rev-parse --abbrev-ref HEAD)"

default_branch="$(resolve_default_branch)"

if [[ "$current_branch" == "$default_branch" ]]; then
  echo "already-on-default-branch: skipping merge/cleanup"
  exit 0
fi

if [[ -z "$recorded_branch" || "$recorded_branch" == "null" ]]; then
  echo "no-recorded-branch-skip-merge: episode has no recorded branch, refusing to merge/delete '$current_branch'"
  exit 0
fi

if [[ "$current_branch" != "$recorded_branch" ]]; then
  echo "current-branch-mismatch-skip-merge: current branch '$current_branch' != episode's recorded branch '$recorded_branch', refusing to merge/delete"
  exit 0
fi

episode_file="docs/episodes/${current_branch}.md"
if [[ ! -f "$episode_file" ]]; then
  echo "warning: episode file not found: $episode_file (closeout step 3 should create it before merging)" >&2
else
  # Episode status is only ever 'active' (template default) or 'closed' (set
  # by closeout step 3) -- see docs/episodes/_TEMPLATE.md.
  if grep -q '^status: active' "$episode_file"; then
    echo "warning: $episode_file has not been finalized (status is not 'closed') -- closeout step 3 should finalize it before merging" >&2
  fi
  if grep -q 'TODO:' "$episode_file"; then
    echo "warning: $episode_file still has unresolved TODO: markers -- closeout step 7 should resolve them before merging" >&2
  fi
fi

if has_uncommitted_changes; then
  git add -A
  git commit -m "chore: closeout - commit remaining changes on $current_branch"
  echo "committed-remaining-changes"
fi

if git show-ref --verify --quiet "refs/heads/$default_branch"; then
  git checkout "$default_branch"
  git merge --no-ff "$current_branch" -m "Merge branch '$current_branch'"
  branch_delete_flag="-d"
else
  git branch "$default_branch"
  git checkout "$default_branch"
  branch_delete_flag="-D"
fi

if [[ "$no_delete" -eq 1 ]]; then
  echo "merged-and-kept: $current_branch -> $default_branch"
else
  git branch "$branch_delete_flag" "$current_branch"
  echo "merged-and-deleted: $current_branch -> $default_branch"
fi
