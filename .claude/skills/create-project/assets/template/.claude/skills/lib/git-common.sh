#!/usr/bin/env bash
# Shared git helpers sourced by new-task/closeout/code-review's scripts.
# Not meant to be executed directly.

# require_git_repo_or_exit <action-description>
# Exits 0 with a "not-a-git-repo: skipping <action>" message if the current
# directory isn't a git repo (checked via .git/).
require_git_repo_or_exit() {
  if [[ ! -d ".git" ]]; then
    echo "not-a-git-repo: skipping $1"
    exit 0
  fi
}

# resolve_default_branch
# Echoes the repo's default branch: origin/HEAD's target if set, else the
# first of main/master that exists locally, else "main" (brand-new repo).
resolve_default_branch() {
  local default_branch
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
  echo "$default_branch"
}

# has_uncommitted_changes
# Returns success (0) if there are any staged, unstaged, or untracked changes.
has_uncommitted_changes() {
  ! git diff --quiet || ! git diff --cached --quiet || [[ -n "$(git ls-files --others --exclude-standard)" ]]
}
