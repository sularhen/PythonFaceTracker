#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -x "$ROOT/.venv/bin/python" ]; then
  echo "[FaceTrail] Creating local virtual environment..."
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv "$ROOT/.venv"
  else
    python -m venv "$ROOT/.venv"
  fi
fi

echo "[FaceTrail] Ensuring dependencies are installed..."
"$ROOT/.venv/bin/python" -m pip install -e "$ROOT"

echo "[FaceTrail] Launching GUI..."
exec "$ROOT/.venv/bin/facetrail" "$@"
