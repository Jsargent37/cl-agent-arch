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
  [[ "$base" == "episode-template.md" || "$base" == "README.md" ]] && continue
  awk -v file="$base" '
    /^signals:/ { insig=1; next }
    insig && /^---[ \t]*$/ { insig=0; next }
    insig && /^[A-Za-z_]+:/ && !/^[ \t]/ { insig=0 }
    insig && /- kind:/ {
      kind=$0
      sub(/.*- kind:[ \t]*/, "", kind)
      gsub(/[ \t]+$/, "", kind)
      cur_kind=kind
      next
    }
    insig && /id:/ {
      id=$0
      sub(/.*id:[ \t]*/, "", id)
      gsub(/[ \t]+$/, "", id)
      print cur_kind "\t" id "\t" file
    }
  ' "$f"
done | sort | awk -F'\t' '
  {
    key = $1 "\t" $2
    count[key]++
    episodes[key] = episodes[key] $3 ","
  }
  END {
    for (k in count) {
      print k "\t" count[k] "\t" episodes[k]
    }
  }
' | sort
