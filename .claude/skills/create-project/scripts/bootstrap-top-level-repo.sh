#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./bootstrap-top-level-repo.sh [--force] <repo-name> [one-line description]

Examples:
  ./bootstrap-top-level-repo.sh sample-repo "Short description"
  ./bootstrap-top-level-repo.sh --force sample-repo "Short description"
EOF
}

force=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      force=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(dirname "$script_dir")"
projects_dir="$(cd "$skill_dir/../../.." && pwd)"
template_dir="$skill_dir/template/top-level-repo"
repo_name="$1"
shift
project_description="${*:-TODO: replace with a one-line project description.}"
repo_dir="$projects_dir/$repo_name"
today="$(date +%Y-%m-%d)"

if [[ "$repo_name" == *"/"* ]] || [[ "$repo_name" == "." ]] || [[ "$repo_name" == ".." ]]; then
  echo "Repo name must be a direct child name under $projects_dir" >&2
  exit 2
fi

if [[ ! -d "$template_dir" ]]; then
  echo "Template directory not found: $template_dir" >&2
  exit 1
fi

mkdir -p "$repo_dir"

if [[ ! -d "$repo_dir/.git" ]]; then
  git -C "$repo_dir" init >/dev/null
  echo "Initialized git repo in $repo_dir"
fi

escape_sed() {
  printf '%s' "$1" | sed -e 's/[\/&\\]/\\&/g'
}

render_template() {
  local src="$1"
  local dest="$2"
  local repo_escaped description_escaped date_escaped

  if [[ -e "$dest" && "$force" -ne 1 ]]; then
    echo "skip  ${dest#$projects_dir/}"
    return
  fi

  mkdir -p "$(dirname "$dest")"
  repo_escaped="$(escape_sed "$repo_name")"
  description_escaped="$(escape_sed "$project_description")"
  date_escaped="$(escape_sed "$today")"

  sed \
    -e "s/__REPO_NAME__/$repo_escaped/g" \
    -e "s/__PROJECT_DESCRIPTION__/$description_escaped/g" \
    -e "s/__DATE__/$date_escaped/g" \
    "$src" >"$dest"

  echo "write ${dest#$projects_dir/}"
}

render_executable() {
  render_template "$1" "$2"
  chmod +x "$2"
}

link_codex_skill() {
  local skill_name="$1"
  local dest="$repo_dir/.agents/skills/$skill_name"
  local target="../../.claude/skills/$skill_name"

  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$force" -ne 1 ]]; then
      echo "skip  ${dest#$projects_dir/}"
      return
    fi
    rm -rf "$dest"
  fi

  mkdir -p "$(dirname "$dest")"
  ln -s "$target" "$dest"
  echo "link  ${dest#$projects_dir/} -> $target"
}

link_agents_md() {
  local dest="$repo_dir/AGENTS.md"
  local target="CLAUDE.md"

  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$force" -ne 1 ]]; then
      echo "skip  ${dest#$projects_dir/}"
      return
    fi
    rm -f "$dest"
  fi

  ln -s "$target" "$dest"
  echo "link  ${dest#$projects_dir/} -> $target"
}

render_template "$template_dir/README.md"                                                   "$repo_dir/README.md"
render_template "$template_dir/CLAUDE.md"                                                   "$repo_dir/CLAUDE.md"
link_agents_md
render_template "$template_dir/docs/README.md"                                     "$repo_dir/docs/README.md"
render_template "$template_dir/docs/ONBOARDING.md"                                 "$repo_dir/docs/ONBOARDING.md"
render_template "$template_dir/docs/TASK.md"                                       "$repo_dir/docs/TASK.md"
render_template "$template_dir/docs/NOTES.md"                                      "$repo_dir/docs/NOTES.md"
render_template "$template_dir/docs/ROADMAP.md"                                    "$repo_dir/docs/ROADMAP.md"
render_template "$template_dir/docs/Memory/Semantics.md"                           "$repo_dir/docs/Memory/Semantics.md"
render_template "$template_dir/docs/Memory/Procedures.md"                          "$repo_dir/docs/Memory/Procedures.md"
render_template "$template_dir/docs/Memory/Guardrails.md"                         "$repo_dir/docs/Memory/Guardrails.md"
render_template "$template_dir/docs/Memory/Lessons.md"                            "$repo_dir/docs/Memory/Lessons.md"
render_template "$template_dir/docs/Memory/Archive.md"                            "$repo_dir/docs/Memory/Archive.md"
render_template "$template_dir/docs/Memory/Episodes/README.md"                     "$repo_dir/docs/Memory/Episodes/README.md"
render_template "$template_dir/docs/Memory/Episodes/episode-template.md"           "$repo_dir/docs/Memory/Episodes/episode-template.md"

render_template   "$template_dir/.claude/settings.json"                                      "$repo_dir/.claude/settings.json"
render_template   "$template_dir/.claude/skills/new-task/SKILL.md"                          "$repo_dir/.claude/skills/new-task/SKILL.md"
render_executable "$template_dir/.claude/skills/new-task/scripts/new-task.sh"               "$repo_dir/.claude/skills/new-task/scripts/new-task.sh"
render_template   "$template_dir/.claude/skills/code-review/SKILL.md"                       "$repo_dir/.claude/skills/code-review/SKILL.md"
render_executable "$template_dir/.claude/skills/code-review/scripts/code-review-commit.sh"  "$repo_dir/.claude/skills/code-review/scripts/code-review-commit.sh"
render_template   "$template_dir/.claude/skills/closeout/SKILL.md"                          "$repo_dir/.claude/skills/closeout/SKILL.md"
render_executable "$template_dir/.claude/skills/closeout/scripts/closeout.sh"               "$repo_dir/.claude/skills/closeout/scripts/closeout.sh"
render_template   "$template_dir/.claude/skills/distill/SKILL.md"                           "$repo_dir/.claude/skills/distill/SKILL.md"
render_executable "$template_dir/.claude/skills/distill/scripts/tally-signals.sh"            "$repo_dir/.claude/skills/distill/scripts/tally-signals.sh"
render_template   "$template_dir/.claude/skills/drift-check/SKILL.md"                    "$repo_dir/.claude/skills/drift-check/SKILL.md"
render_executable "$template_dir/.claude/skills/drift-check/scripts/inventory.sh"        "$repo_dir/.claude/skills/drift-check/scripts/inventory.sh"

link_codex_skill "new-task"
link_codex_skill "code-review"
link_codex_skill "closeout"
link_codex_skill "distill"
link_codex_skill "drift-check"

# --- register in workspace INDEX.md ---
index_file="$projects_dir/INDEX.md"
if [[ ! -f "$index_file" ]]; then
  {
    printf '# Projects Index\n\n'
    printf 'A short index of every top-level project under this workspace, with a two-sentence description of each.\n\n'
    printf '## Projects\n'
  } >"$index_file"
  echo "write INDEX.md (created)"
fi

if grep -q "^### \[$repo_name\](" "$index_file"; then
  echo "skip  INDEX.md (entry for $repo_name already present)"
else
  {
    printf '\n### [%s](./%s/)\n' "$repo_name" "$repo_name"
    printf '%s TODO: add a second sentence with more context once the project takes shape.\n' "$project_description"
  } >>"$index_file"
  echo "write INDEX.md (appended entry for $repo_name)"
fi

# --- initial commit ---
git -C "$repo_dir" add .
git -C "$repo_dir" commit -m "chore: initial project scaffold for $repo_name" >/dev/null
echo "Initial commit created on $(git -C "$repo_dir" rev-parse --abbrev-ref HEAD)"

cat <<EOF

Bootstrap complete for $repo_name

Next steps:
1. Fill in the placeholders in docs/README.md, docs/ROADMAP.md, and CLAUDE.md (Project Rules section).
2. Attach the repo remote if needed.
3. Expand the stub entry in $projects_dir/INDEX.md with a real second sentence once the project takes shape.
EOF
