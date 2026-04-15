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
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST_PATH="$PLIST_DIR/$LABEL.plist"
  mkdir -p "$PLIST_DIR"

  cat >"$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
      <string>$ROOT_DIR/.temporiki/hooks/auto-run-once.sh</string>
    </array>
    <key>WatchPaths</key>
    <array>
      <string>$ROOT_DIR/raw</string>
    </array>
    <key>StandardOutPath</key>
    <string>$ROOT_DIR/.memplite/scheduler.log</string>
    <key>StandardErrorPath</key>
    <string>$ROOT_DIR/.memplite/scheduler.log</string>
  </dict>
</plist>
EOF

  launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
  launchctl load "$PLIST_PATH"
  echo "[temporiki] launchd scheduler installed: $LABEL"
  exit 0
fi

if [[ "$UNAME_S" == "Linux" ]]; then
  UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
  SERVICE="temporiki-auto-$SHORT_HASH.service"
  PATH_UNIT="temporiki-auto-$SHORT_HASH.path"
  mkdir -p "$UNIT_DIR"
  mkdir -p "$ROOT_DIR/.memplite"

  cat >"$UNIT_DIR/$SERVICE" <<EOF
[Unit]
Description=Temporiki one-shot auto ingest ($SHORT_HASH)

[Service]
Type=oneshot
WorkingDirectory=$ROOT_DIR
ExecStart=$ROOT_DIR/.temporiki/hooks/auto-run-once.sh
EOF

  cat >"$UNIT_DIR/$PATH_UNIT" <<EOF
[Unit]
Description=Watch Temporiki raw/ for changes ($SHORT_HASH)

[Path]
PathExists=$ROOT_DIR/raw
PathModified=$ROOT_DIR/raw
Unit=$SERVICE

[Install]
WantedBy=default.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable --now "$PATH_UNIT"
  echo "[temporiki] systemd user path scheduler installed: $PATH_UNIT"
  exit 0
fi

case "$UNAME_S" in
  MINGW*|MSYS*|CYGWIN*)
    if ! command -v schtasks.exe >/dev/null 2>&1; then
      echo "[temporiki] schtasks.exe not found; cannot install Windows scheduler" >&2
      exit 1
    fi
    TASK_NAME="TemporikiAuto-$SHORT_HASH"
    WIN_ROOT="$(cygpath -w "$ROOT_DIR")"
    WIN_PS1="$(cygpath -w "$ROOT_DIR/.temporiki/hooks/windows/temporiki-auto-once.ps1")"
    schtasks.exe /Delete /TN "$TASK_NAME" /F >/dev/null 2>&1 || true
    schtasks.exe /Create /TN "$TASK_NAME" /SC MINUTE /MO 2 /F /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$WIN_PS1\" -RootDir \"$WIN_ROOT\""
    echo "[temporiki] Windows scheduler installed (2-min polling): $TASK_NAME"
    exit 0
    ;;
esac

echo "[temporiki] unsupported OS for scheduler install: $UNAME_S" >&2
exit 1
