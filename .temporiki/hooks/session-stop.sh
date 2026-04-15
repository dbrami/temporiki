#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PID_FILE="$ROOT_DIR/.memplite/auto.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "[temporiki] no legacy daemon pid file"
else
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$PID" ]] && ps -p "$PID" >/dev/null 2>&1; then
    kill "$PID" || true
    echo "[temporiki] legacy auto monitor stopped (pid=$PID)"
  else
    echo "[temporiki] legacy auto monitor was not running"
  fi
  rm -f "$PID_FILE"
fi

if [[ "${TEMPORIKI_UNINSTALL_SCHEDULER_ON_STOP:-0}" == "1" ]]; then
  "$ROOT_DIR/.temporiki/hooks/scheduler-uninstall.sh" || true
fi
