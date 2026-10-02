#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../lib/git-common.sh
source "$script_dir/../../lib/git-common.sh"

if [[ $# -lt 1 || -z "$1" ]]; then
  echo "Usage: branch-if-git.sh <branch-name>" >&2
  exit 2
fi
branch_name="$1"

require_git_repo_or_exit "branch creation"

if [[ ! -d "docs" ]]; then
  echo "error: must be run from the repo root (docs/ must exist)" >&2
  exit 1
fi

default_branch="$(resolve_default_branch)"

current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEAD")"
if [[ "$current_branch" != "$default_branch" && "$current_branch" != "HEAD" ]]; then
  echo "already-on-task-branch: currently on '$current_branch', not creating a new one"
  exit 0
fi

git checkout -b "$branch_name"
echo "created-branch: $branch_name"
