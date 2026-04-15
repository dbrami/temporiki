#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Exit quietly when the project root is gone or incomplete.
if [[ ! -d "$ROOT_DIR" ]] || [[ ! -f "$ROOT_DIR/.temporiki/pyproject.toml" ]]; then
  exit 0
fi

STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
LOCK_HOME="$STATE_HOME/temporiki/locks"
mkdir -p "$LOCK_HOME"

if command -v shasum >/dev/null 2>&1; then
  LOCK_KEY="$(printf '%s' "$ROOT_DIR" | shasum -a 256 | awk '{print $1}')"
elif command -v sha256sum >/dev/null 2>&1; then
  LOCK_KEY="$(printf '%s' "$ROOT_DIR" | sha256sum | awk '{print $1}')"
else
  LOCK_KEY="$(printf '%s' "$ROOT_DIR" | tr '/:' '__')"
fi

LOCK_DIR="$LOCK_HOME/$LOCK_KEY.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  # Another run is already in progress; skip.
  exit 0
fi
trap 'rmdir "$LOCK_DIR" >/dev/null 2>&1 || true' EXIT

cd "$ROOT_DIR"
uv --project "$ROOT_DIR/.temporiki" run temporiki palace-event --root "$ROOT_DIR"
