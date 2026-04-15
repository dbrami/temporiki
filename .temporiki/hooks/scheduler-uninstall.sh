#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

hash_path() {
  if command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$1" | sha256sum | awk '{print $1}'
  else
    printf '%s' "$1" | tr '/:' '__'
  fi
}

UNAME_S="$(uname -s)"
ROOT_HASH="$(hash_path "$ROOT_DIR")"
SHORT_HASH="${ROOT_HASH:0:12}"

if [[ "$UNAME_S" == "Darwin" ]]; then
  LABEL="com.temporiki.autorun.$SHORT_HASH"
  PLIST_PATH="$HOME/Library/LaunchAgents/$LABEL.plist"
  launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
  rm -f "$PLIST_PATH"
  echo "[temporiki] launchd scheduler removed: $LABEL"
  exit 0
fi

if [[ "$UNAME_S" == "Linux" ]]; then
  SERVICE="temporiki-auto-$SHORT_HASH.service"
  PATH_UNIT="temporiki-auto-$SHORT_HASH.path"
  TIMER_UNIT="temporiki-auto-$SHORT_HASH.timer"
  UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
  systemctl --user disable --now "$PATH_UNIT" >/dev/null 2>&1 || true
  systemctl --user disable --now "$TIMER_UNIT" >/dev/null 2>&1 || true
  rm -f "$UNIT_DIR/$PATH_UNIT" "$UNIT_DIR/$TIMER_UNIT" "$UNIT_DIR/$SERVICE"
  systemctl --user daemon-reload
  echo "[temporiki] systemd user scheduler removed: $PATH_UNIT, $TIMER_UNIT"
  exit 0
fi

case "$UNAME_S" in
  MINGW*|MSYS*|CYGWIN*)
    if ! command -v schtasks.exe >/dev/null 2>&1; then
      echo "[temporiki] schtasks.exe not found; cannot remove Windows scheduler" >&2
      exit 1
    fi
    TASK_NAME="TemporikiAuto-$SHORT_HASH"
    schtasks.exe /Delete /TN "$TASK_NAME" /F >/dev/null 2>&1 || true
    echo "[temporiki] Windows scheduler removed: $TASK_NAME"
    exit 0
    ;;
esac

echo "[temporiki] unsupported OS for scheduler uninstall: $UNAME_S" >&2
exit 1
