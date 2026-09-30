#!/usr/bin/env bash
set -euo pipefail

# Called after a passing /code-review to commit all changes.
# Usage: code-review-commit.sh "<commit-message>"
# The commit message should describe what was changed, not just that a review passed.

if [[ $# -lt 1 || -z "$1" ]]; then
  echo "Usage: code-review-commit.sh \"<commit-message>\"" >&2
  echo "  Provide a descriptive message summarizing what was changed." >&2
  exit 2
fi

commit_message="$1"

if [[ ! -d ".git" ]]; then
  echo "not-a-git-repo: skipping commit"
  exit 0
fi

if git diff --quiet && git diff --cached --quiet && ! git ls-files --others --exclude-standard | grep -q .; then
  echo "Nothing to commit — working tree is clean."
  exit 0
fi

git add -A
git commit -m "$commit_message"
echo "Committed: $commit_message"
