#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
  -aw|-au) printf '%s\n' "$2" ;;
  *) exit 2 ;;
esac
