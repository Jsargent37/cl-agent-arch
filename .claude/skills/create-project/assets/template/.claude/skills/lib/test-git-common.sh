#!/usr/bin/env bash
# Smoke tests for git-common.sh's shared helpers. Run directly: bash test-git-common.sh
set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
failures=0

assert_eq() {
  local expected="$1" actual="$2" msg="$3"
  if [[ "$expected" != "$actual" ]]; then
    echo "FAIL: $msg (expected '$expected', got '$actual')" >&2
    failures=$((failures + 1))
  fi
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# require_git_repo_or_exit: non-git dir prints the message then exits before
# any later code in the sourcing script runs.
out="$(cd "$tmp" && source "$script_dir/git-common.sh" && require_git_repo_or_exit "testing"; echo "UNREACHABLE")"
assert_eq "not-a-git-repo: skipping testing" "$out" "require_git_repo_or_exit message/early-exit in a non-git dir"

# require_git_repo_or_exit: inside a git repo, does not exit.
repo="$tmp/repo"
mkdir -p "$repo"
(cd "$repo" && git init -q && git config user.email t@t.com && git config user.name t)
out="$(cd "$repo" && source "$script_dir/git-common.sh" && require_git_repo_or_exit "testing"; echo "REACHED")"
assert_eq "REACHED" "$out" "require_git_repo_or_exit should not exit inside a git repo"

# resolve_default_branch: detects a local 'main' branch.
(cd "$repo" && echo x > f.txt && git add -A && git commit -q -m init && git branch -m main)
out="$(cd "$repo" && source "$script_dir/git-common.sh" && resolve_default_branch)"
assert_eq "main" "$out" "resolve_default_branch should detect local 'main'"

# resolve_default_branch: falls back to 'main' when neither main nor master exists.
(cd "$repo" && git branch -m trunk)
out="$(cd "$repo" && source "$script_dir/git-common.sh" && resolve_default_branch)"
assert_eq "main" "$out" "resolve_default_branch should default to 'main' with no main/master"
(cd "$repo" && git branch -m main)

# has_uncommitted_changes: clean tree -> false (non-zero exit).
if (cd "$repo" && source "$script_dir/git-common.sh" && has_uncommitted_changes); then
  echo "FAIL: has_uncommitted_changes should be false on a clean tree" >&2
  failures=$((failures + 1))
fi

# has_uncommitted_changes: untracked file -> true (zero exit).
(cd "$repo" && echo y > untracked.txt)
if ! (cd "$repo" && source "$script_dir/git-common.sh" && has_uncommitted_changes); then
  echo "FAIL: has_uncommitted_changes should be true with an untracked file" >&2
  failures=$((failures + 1))
fi

if [[ "$failures" -gt 0 ]]; then
  echo "$failures assertion(s) failed" >&2
  exit 1
fi
echo "All git-common.sh tests passed."
