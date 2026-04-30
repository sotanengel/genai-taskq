#!/usr/bin/env bash
set -euo pipefail

PORT="${GTQ_API_PORT:-18000}"

if ! command -v lsof >/dev/null 2>&1; then
  echo "preflight: lsof command not found; cannot verify port usage." >&2
  exit 1
fi

if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "preflight: port ${PORT} is already in use. Set GTQ_API_PORT to another value." >&2
  exit 1
fi

echo "preflight: port ${PORT} is available."
