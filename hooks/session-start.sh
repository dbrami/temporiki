#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# 0) Ensure expected vault folders exist (idempotent).
mkdir -p "$ROOT_DIR/raw/webclips" "$ROOT_DIR/raw/assets" "$ROOT_DIR/wiki/queries" "$ROOT_DIR/wiki/meta" "$ROOT_DIR/wiki/_templates"

# 0.5) Ensure runtime deps exist (lightweight + chroma client only).
if ! uv sync --extra chroma-client >/dev/null 2>&1; then
  echo "[temporiki] uv sync failed; continuing with existing environment" >&2
fi

# 0.6) Ensure Obsidian dashboards/templates are present.
uv run temporiki obsidian-ux-pack >/dev/null 2>&1 || true

# 1) Bring up Chroma if possible (no-op if Docker unavailable).
"$ROOT_DIR/hooks/session-launch.sh" || true

# 2) Start auto monitor daemon if not already running.
mkdir -p "$ROOT_DIR/.memplite"
PID_FILE="$ROOT_DIR/.memplite/auto.pid"
LOG_FILE="$ROOT_DIR/.memplite/auto.log"

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$PID" ]] && ps -p "$PID" >/dev/null 2>&1; then
    echo "[temporiki] auto monitor already running (pid=$PID)"
    exit 0
  fi
fi

nohup uv run temporiki palace-auto >"$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

echo "[temporiki] auto monitor started (pid=$NEW_PID, log=$LOG_FILE)"
