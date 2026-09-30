#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || -z "$1" ]]; then
  echo "Usage: branch-if-git.sh <branch-name>" >&2
  exit 2
fi
branch_name="$1"

if [[ ! -d ".git" ]]; then
  echo "not-a-git-repo: skipping branch creation"
  exit 0
fi

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

current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEAD")"
if [[ "$current_branch" != "$default_branch" && "$current_branch" != "HEAD" ]]; then
  echo "already-on-task-branch: currently on '$current_branch', not creating a new one"
  exit 0
fi

git checkout -b "$branch_name"
echo "created-branch: $branch_name"
