#!/usr/bin/env bash
set -euo pipefail

input="${2:-}"
parent="$(dirname "$input")"
if [[ -d "$parent" ]]; then
  input="$(cd "$parent" && pwd -P)/$(basename "$input")"
fi

case "${1:-}" in
  -aw|-au) printf '%s\n' "$input" ;;
  *) exit 2 ;;
esac
