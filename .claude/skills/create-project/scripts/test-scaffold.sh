#!/usr/bin/env bash
# Smoke tests for scaffold.sh. Run directly: bash test-scaffold.sh
set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
scaffold="$script_dir/scaffold.sh"
failures=0

fail() {
  echo "FAIL: $1" >&2
  failures=$((failures + 1))
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/.claude/skills/create-project/scripts"
cp "$scaffold" "$tmp/.claude/skills/create-project/scripts/scaffold.sh"
ln -s "$script_dir/../assets" "$tmp/.claude/skills/create-project/assets"
run="$tmp/.claude/skills/create-project/scripts/scaffold.sh"

# A project name containing regex metacharacters must be scaffolded, deduped,
# and never regex-escaped incorrectly (regression test for a bug where
# escape_regex() turned literal ()/{}/+/?/| into BRE operators, breaking the
# PROJECTS.md dedup check for exactly the names it was meant to protect).
name='My.App (v2)'
bash "$run" --git "paren-app" "$name" "$tmp/paren-app" >/dev/null 2>&1

entry_count="$(grep -cF -- "- [$name](" "$tmp/PROJECTS.md")"
if [[ "$entry_count" != "1" ]]; then
  fail "expected exactly 1 entry for '$name', found $entry_count"
fi

# A project name containing a literal backslash must also dedupe correctly
# (regression test for a bug where `awk -v` interpreted backslash-escape
# sequences in the assigned value, corrupting the name before comparison and
# causing a duplicate PROJECTS.md entry on re-scaffold).
backslash_name='Weird"Name\Here'
bash "$run" "backslash-app" "$backslash_name" "$tmp/backslash-app" >/dev/null 2>&1
bash "$run" "backslash-app" "$backslash_name" "$tmp/backslash-app" >/dev/null 2>&1
entry_count="$(grep -cF -- "- [$backslash_name](" "$tmp/PROJECTS.md")"
if [[ "$entry_count" != "1" ]]; then
  fail "expected exactly 1 entry for '$backslash_name' after two scaffold runs, found $entry_count"
fi

# Re-running scaffold (idempotent conditional re-run, e.g. --python/--git
# added later) must skip re-appending, not duplicate the entry.
bash "$run" "paren-app" "$name" "$tmp/paren-app" >/dev/null 2>&1
entry_count="$(grep -cF -- "- [$name](" "$tmp/PROJECTS.md")"
if [[ "$entry_count" != "1" ]]; then
  fail "expected still exactly 1 entry for '$name' after re-run, found $entry_count"
fi

# A second project whose name is a superstring of the first must not be
# treated as already-present (anchored-start matching, not substring anywhere).
name2='My.App (v2) Extended'
bash "$run" "paren-app2" "$name2" "$tmp/paren-app2" >/dev/null 2>&1
entry_count="$(grep -cF -- "- [$name2](" "$tmp/PROJECTS.md")"
if [[ "$entry_count" != "1" ]]; then
  fail "expected exactly 1 distinct entry for '$name2', found $entry_count"
fi

# A PROJECTS.md whose last line has no trailing newline must still have that
# last line checked (regression test for a bug where `while read -r line`
# silently skips the body for an unterminated final line, since `read`
# returns non-zero for it -- the fix adds `|| [[ -n "$line" ]]` to the loop).
printf -- '%s' "$(cat "$tmp/PROJECTS.md")" > "$tmp/PROJECTS.md"
unterminated_name='My.App (v2) Extended'
bash "$run" "paren-app2" "$unterminated_name" "$tmp/paren-app2" >/dev/null 2>&1
entry_count="$(grep -cF -- "- [$unterminated_name](" "$tmp/PROJECTS.md")"
if [[ "$entry_count" != "1" ]]; then
  fail "expected still exactly 1 entry for '$unterminated_name' when PROJECTS.md's last line had no trailing newline, found $entry_count"
fi

# Scaffolding into an existing, non-empty, unrelated directory without
# --force must refuse (regression test for the scaffold-marker guard).
mkdir -p "$tmp/unrelated" && echo x > "$tmp/unrelated/f.txt"
if bash "$run" "unrelated" "Unrelated" "$tmp/unrelated" >/dev/null 2>&1; then
  fail "scaffold should refuse to scaffold into an existing non-empty unrelated directory without --force"
fi

if [[ "$failures" -gt 0 ]]; then
  echo "$failures assertion(s) failed" >&2
  exit 1
fi
echo "All scaffold.sh tests passed."
