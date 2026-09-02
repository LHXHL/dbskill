#!/usr/bin/env bash
set -euo pipefail

action=""
path=""
target=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -Action) action="$2"; shift 2 ;;
    -Path) path="$2"; shift 2 ;;
    -Target) target="$2"; shift 2 ;;
    *) shift ;;
  esac
done

marker_name=".dbs-test-junction-target"

case "$action" in
  create)
    [[ -n "$path" && -n "$target" && ! -e "$path" ]]
    mkdir "$path"
    printf '%s\n' "$target" > "$path/$marker_name"
    ;;
  target)
    [[ -f "$path/$marker_name" ]]
    sed -n '1p' "$path/$marker_name"
    ;;
  remove)
    [[ -f "$path/$marker_name" ]]
    rm "$path/$marker_name"
    rmdir "$path"
    ;;
  test)
    [[ -f "$path/$marker_name" ]]
    ;;
  list)
    [[ -d "$path" ]] || exit 0
    while IFS= read -r marker; do
      dirname "$marker"
    done < <(find "$path" -mindepth 2 -maxdepth 2 -name "$marker_name" -type f | sort)
    ;;
  *) exit 2 ;;
esac
