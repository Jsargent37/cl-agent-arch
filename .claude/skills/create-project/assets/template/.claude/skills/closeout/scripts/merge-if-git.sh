#!/usr/bin/env bash
set -euo pipefail

# Usage: merge-if-git.sh [<recorded-branch-name>]
# <recorded-branch-name> is the active episode's `branch:` frontmatter value (the
# {date}-{slug} branch new-task's branch-if-git.sh created for this task). Only
# merges+deletes when the CURRENT branch matches it exactly -- refuses otherwise.
recorded_branch="${1:-}"

if [[ ! -d ".git" ]]; then
  echo "not-a-git-repo: skipping branch merge"
  exit 0
fi

if ! git symbolic-ref -q HEAD >/dev/null; then
  echo "detached-head-skip-merge: HEAD is detached, refusing to merge/delete"
  exit 0
fi

current_branch="$(git rev-parse --abbrev-ref HEAD)"

default_branch="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || true)"
if [[ -z "$default_branch" ]]; then
  if git show-ref --verify --quiet refs/heads/main 2>/dev/null; then
    default_branch="main"
  elif git show-ref --verify --quiet refs/heads/master 2>/dev/null; then
    default_branch="master"
  else
    default_branch="main"
  fi
fi

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

if ! git diff --quiet || ! git diff --cached --quiet || git ls-files --others --exclude-standard | grep -q .; then
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

git branch "$branch_delete_flag" "$current_branch"
echo "merged-and-deleted: $current_branch -> $default_branch"
