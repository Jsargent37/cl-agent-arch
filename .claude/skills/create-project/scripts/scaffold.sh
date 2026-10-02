#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scaffold.sh [--force] [--git] [--python] <slug> "<project-name>" "<project-abs-path>"

Copies assets/template/ into <project-abs-path>, substituting {{PROJECT_NAME}},
{{SLUG}}, {{DATE}}, and {{PROJECT_ABS_PATH}} in every copied file (except
docs/episodes/_TEMPLATE.md, which new-task fills per task), mirrors every
.claude/skills/<name>/ as .agents/skills/<name>, registers the project in
PROJECTS.md, and (with --git) runs git init + writes a .gitignore + an
initial commit. Never invents adaptive content -- the adaptive interview and
pre-fill pass are the calling skill's job, done after this script returns.

Examples:
  ./scaffold.sh my-app "My App" "/c/Users/me/Documents/projects/my-app"
  ./scaffold.sh --force --git --python my-app "My App" "/c/Users/me/Documents/projects/my-app"
EOF
}

force=0
do_git=0
do_python=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) force=1; shift ;;
    --git) do_git=1; shift ;;
    --python) do_python=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done

if [[ $# -lt 3 ]]; then
  usage >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(dirname "$script_dir")"
template_dir="$skill_dir/assets/template"
projects_dir="$(cd "$skill_dir/../../.." && pwd)"

slug="$1"
project_name="$2"
project_abs_path="$3"
today="$(date +%Y-%m-%d)"

if [[ "$slug" == *"/"* ]] || [[ "$slug" == "." ]] || [[ "$slug" == ".." ]]; then
  echo "Slug must be a direct child directory name under $projects_dir" >&2
  exit 2
fi

if [[ ! -d "$template_dir" ]]; then
  echo "Template directory not found: $template_dir" >&2
  exit 1
fi

escape_sed() {
  printf '%s' "$1" | sed -e 's/[\/&\\]/\\&/g'
}

name_escaped="$(escape_sed "$project_name")"
slug_escaped="$(escape_sed "$slug")"
date_escaped="$(escape_sed "$today")"
path_escaped="$(escape_sed "$project_abs_path")"

scaffold_marker="$project_abs_path/.claude/.scaffolded-by-create-project"
if [[ -n "$(ls -A "$project_abs_path" 2>/dev/null)" ]] \
  && [[ ! -f "$scaffold_marker" ]] && [[ "$force" -ne 1 ]]; then
  echo "Refusing to scaffold into existing non-empty directory without --force: $project_abs_path" >&2
  echo "(pass --force to scaffold into it anyway)" >&2
  exit 2
fi

mkdir -p "$project_abs_path"
mkdir -p "$(dirname "$scaffold_marker")"
touch "$scaffold_marker"

list_template_files() {
  if git -C "$template_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$template_dir" ls-files -z --cached --others --exclude-standard
  else
    ( cd "$template_dir" && find . -type f \
      -not -path '*/.venv/*' \
      -not -path '*/__pycache__/*' \
      -not -path '*/.pytest_cache/*' \
      -not -name '*.pyc' \
      -not -name '*.pyo' \
      -not -name 'uv.lock' \
      -print0 ) | sed -z 's|^\./||'
  fi
}

while IFS= read -r -d '' rel; do
  src="$template_dir/$rel"

  if [[ "$rel" == "docs/episodes/_TEMPLATE.md" ]]; then
    dest="$project_abs_path/$rel"
    if [[ -e "$dest" && "$force" -ne 1 ]]; then
      echo "skip  $rel"
    else
      mkdir -p "$(dirname "$dest")"
      cp "$src" "$dest"
      echo "write $rel (unsubstituted, per-task template)"
    fi
    continue
  fi

  dest="$project_abs_path/$rel"
  if [[ -e "$dest" && "$force" -ne 1 ]]; then
    echo "skip  $rel"
    continue
  fi
  mkdir -p "$(dirname "$dest")"
  sed \
    -e "s/{{PROJECT_NAME}}/$name_escaped/g" \
    -e "s/{{SLUG}}/$slug_escaped/g" \
    -e "s/{{DATE}}/$date_escaped/g" \
    -e "s/{{PROJECT_ABS_PATH}}/$path_escaped/g" \
    "$src" >"$dest"
  case "$dest" in
    *.sh) chmod +x "$dest" ;;
  esac
  echo "write $rel"
done < <(list_template_files)

if [[ -d "$project_abs_path/.claude/skills" ]]; then
  for skill_path in "$project_abs_path"/.claude/skills/*/; do
    [[ -f "$skill_path/SKILL.md" ]] || continue
    name="$(basename "$skill_path")"
    dest="$project_abs_path/.agents/skills/$name"
    mkdir -p "$(dirname "$dest")"
    if [[ -e "$dest" ]]; then
      if [[ "$force" -ne 1 ]]; then
        echo "skip  .agents/skills/$name"
        continue
      fi
      rm -rf "$dest"
    fi
    if [[ "${OS:-}" == "Windows_NT" ]]; then
      src_path="$project_abs_path/.claude/skills/$name"
      if command -v cygpath >/dev/null 2>&1; then
        dest_win="$(cygpath -w "$dest")"
        src_win="$(cygpath -w "$src_path")"
        cmd //c mklink //J "$dest_win" "$src_win" >/dev/null
      else
        cmd //c mklink //J "$dest" "$src_path" >/dev/null
      fi
      echo "junction .agents/skills/$name -> .claude/skills/$name"
    else
      ln -s "../../.claude/skills/$name" "$dest"
      echo "link  .agents/skills/$name -> .claude/skills/$name"
    fi
  done
fi

if [[ "$do_python" -eq 1 ]]; then
  ( cd "$project_abs_path" && uv venv >/dev/null 2>&1 || true )
  echo "python: uv venv initialized (pyproject.toml expected from the copied template)"
fi

if [[ "$do_git" -eq 1 ]]; then
  gitignore="$project_abs_path/.gitignore"
  if [[ ! -e "$gitignore" || "$force" -eq 1 ]]; then
    cat > "$gitignore" <<'GITIGNORE'
.venv/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
*.swp
.agents/
.claude/skills/.drift-check-cache
.claude/.scaffolded-by-create-project
GITIGNORE
    echo "write .gitignore"
  fi
  if [[ ! -d "$project_abs_path/.git" ]]; then
    git -C "$project_abs_path" init >/dev/null
    echo "Initialized git repo in $project_abs_path"
  fi
  git -C "$project_abs_path" add -A
  git -C "$project_abs_path" commit -m "chore: initial project scaffold for $project_name" >/dev/null
  echo "Initial commit created on $(git -C "$project_abs_path" rev-parse --abbrev-ref HEAD)"
fi

projects_index="$projects_dir/PROJECTS.md"
if [[ ! -f "$projects_index" ]]; then
  {
    printf -- '---\ntags: [registry]\n---\n\n'
    printf '# Projects\n'
  } >"$projects_index"
  echo "write PROJECTS.md (created)"
fi

# Pure-bash literal-prefix match -- a quoted variable in `[[ ]]` is never
# regex/escape-processed, unlike the grep- and awk-based checks this replaced.
already_registered=0
while IFS= read -r line || [[ -n "$line" ]]; do
  if [[ "$line" == "- [$project_name]("* ]]; then
    already_registered=1
    break
  fi
done <"$projects_index"

if [[ "$already_registered" -eq 1 ]]; then
  echo "skip  PROJECTS.md (entry for $project_name already present)"
else
  printf -- '- [%s](%s/README.md) — TODO: one-line purpose (created %s)\n' \
    "$project_name" "$slug" "$today" >>"$projects_index"
  echo "write PROJECTS.md (appended entry for $project_name)"
fi

cat <<EOF

Scaffold complete for $project_name at $project_abs_path

Next: continue the adaptive pre-fill (README overview, INDEX structure, any
additional SEMANTICS/PROCEDURES/GUARDRAILS entries the interview surfaced),
then replace PROJECTS.md's TODO purpose line with a real one.
EOF
