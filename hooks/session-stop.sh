#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/.memplite/auto.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "[memoriki] no auto monitor pid file"
  exit 0
fi

PID="$(cat "$PID_FILE" 2>/dev/null || true)"
if [[ -n "$PID" ]] && ps -p "$PID" >/dev/null 2>&1; then
  kill "$PID" || true
  echo "[memoriki] auto monitor stopped (pid=$PID)"
else
  echo "[memoriki] auto monitor was not running"
fi

rm -f "$PID_FILE"
