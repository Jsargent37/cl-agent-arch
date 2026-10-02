#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../lib/git-common.sh
source "$script_dir/../../lib/git-common.sh"

# Called after a passing /code-review to commit all changes.
# Usage: code-review-commit.sh "<commit-message>"
# The commit message should describe what was changed, not just that a review passed.

if [[ $# -lt 1 || -z "$1" ]]; then
  echo "Usage: code-review-commit.sh \"<commit-message>\"" >&2
  echo "  Provide a descriptive message summarizing what was changed." >&2
  exit 2
fi

commit_message="$1"

require_git_repo_or_exit "commit"

if ! has_uncommitted_changes; then
  echo "Nothing to commit — working tree is clean."
  exit 0
fi

git add -A
git commit -m "$commit_message"
echo "Committed: $commit_message"
