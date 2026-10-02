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
    function flush() {
      if (cur_kind != "" && cur_id != "") {
        print cur_kind "\t" cur_id "\t" cur_scope "\t" cur_severity "\t" file
      }
      cur_kind=""; cur_id=""; cur_scope="project"; cur_severity=""
    }
    /^signals:/ { insig=1; next }
    insig && /^---[ \t]*$/ { flush(); insig=0; next }
    insig && /^[A-Za-z_]+:/ && !/^[ \t]/ { flush(); insig=0 }
    insig && /^[ \t]*# / { next }
    insig && /^[ \t]*- kind:/ {
      flush()
      kind=$0
      sub(/.*- kind:[ \t]*/, "", kind)
      gsub(/[ \t]+$/, "", kind)
      cur_kind=kind
      cur_scope="project"
      next
    }
    insig && /^[ \t]*(- )?id:/ {
      id=$0
      sub(/.*id:[ \t]*/, "", id)
      gsub(/[ \t]+$/, "", id)
      cur_id=id
      next
    }
    insig && /^[ \t]*(- )?scope:/ {
      scope=$0
      sub(/.*scope:[ \t]*/, "", scope)
      gsub(/[ \t]+$/, "", scope)
      cur_scope=scope
      next
    }
    insig && /^[ \t]*(- )?severity:/ {
      sev=$0
      sub(/.*severity:[ \t]*/, "", sev)
      gsub(/[ \t]+$/, "", sev)
      cur_severity=sev
      next
    }
    END { flush() }
  ' "$f"
done | sort | awk -F'\t' '
  function sevrank(s) {
    if (s == "high") return 3
    if (s == "medium") return 2
    if (s == "low") return 1
    return 0
  }
  {
    key = $1 "\t" $2
    count[key]++
    if ($3 == "global") global[key] = 1
    if ($4 != "" && (!(key in severity) || sevrank($4) > sevrank(severity[key]))) {
      severity[key] = $4
    }
    episodes[key] = episodes[key] $5 ","
  }
  END {
    for (k in count) {
      scope_out = (k in global) ? "global" : "project"
      sev_out = (k in severity) ? severity[k] : ""
      print k "\t" count[k] "\t" scope_out "\t" sev_out "\t" episodes[k]
    }
  }
' | sort
