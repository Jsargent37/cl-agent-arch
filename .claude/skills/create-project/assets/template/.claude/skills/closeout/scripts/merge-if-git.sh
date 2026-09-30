#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d ".git" ]]; then
  echo "not-a-git-repo: skipping branch merge"
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
