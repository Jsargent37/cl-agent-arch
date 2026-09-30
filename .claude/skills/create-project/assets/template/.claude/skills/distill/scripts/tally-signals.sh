#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || -z "$1" ]]; then
  echo "Usage: tally-signals.sh <episodes-dir>" >&2
  exit 2
fi
episodes_dir="$1"

if [[ ! -d "$episodes_dir" ]]; then
  echo "Error: $episodes_dir not found." >&2
  exit 1
fi

for f in "$episodes_dir"/*.md; do
  [[ -f "$f" ]] || continue
  base="$(basename "$f")"
  [[ "$base" == "_TEMPLATE.md" ]] && continue
  awk -v file="$base" '
    /^signals:/ { insig=1; next }
    insig && /^---[ \t]*$/ { insig=0; next }
    insig && /^[A-Za-z_]+:/ && !/^[ \t]/ { insig=0 }
    insig && /^# / { next }
    insig && /- kind:/ {
      kind=$0
      sub(/.*- kind:[ \t]*/, "", kind)
      gsub(/[ \t]+$/, "", kind)
      cur_kind=kind
      cur_scope="project"
      next
    }
    insig && /id:/ {
      id=$0
      sub(/.*id:[ \t]*/, "", id)
      gsub(/[ \t]+$/, "", id)
      cur_id=id
      next
    }
    insig && /scope:/ {
      scope=$0
      sub(/.*scope:[ \t]*/, "", scope)
      gsub(/[ \t]+$/, "", scope)
      cur_scope=scope
      print cur_kind "\t" cur_id "\t" cur_scope "\t" file
    }
  ' "$f"
done | sort | awk -F'\t' '
  {
    key = $1 "\t" $2
    count[key]++
    if ($3 == "global") global[key] = 1
    episodes[key] = episodes[key] $4 ","
  }
  END {
    for (k in count) {
      scope_out = (k in global) ? "global" : "project"
      print k "\t" count[k] "\t" scope_out "\t" episodes[k]
    }
  }
' | sort
