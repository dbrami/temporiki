#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="$ROOT_DIR/.temporiki"
cd "$ROOT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "[temporiki] uv is required: https://docs.astral.sh/uv/" >&2
  exit 1
fi

mkdir -p raw/webclips raw/assets wiki/queries wiki/meta wiki/_templates
touch raw/webclips/.gitkeep raw/assets/.gitkeep

echo "[temporiki] syncing lightweight runtime..."
uv sync --project "$PROJECT_DIR" --extra chroma-client

echo "[temporiki] applying vault onboarding defaults..."
uv --project "$PROJECT_DIR" run temporiki onboard >/dev/null

# One-shot migration: clean up any residual OS scheduler state from pre-plugin installs.
# TODO: remove this block after a release or two once known clones have migrated.
case "$(uname -s)" in
  Darwin)
    for plist in "$HOME/Library/LaunchAgents"/com.temporiki.autorun.*.plist; do
      [[ -e "$plist" ]] || continue
      launchctl unload "$plist" >/dev/null 2>&1 || true
      rm -f "$plist"
      echo "[temporiki] migration: removed legacy launchd agent $(basename "$plist" .plist)"
    done
    ;;
  Linux)
    UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
    if [[ -d "$UNIT_DIR" ]]; then
      migration_changed=0
      for unit in \
        "$UNIT_DIR"/temporiki-auto-*.path \
        "$UNIT_DIR"/temporiki-auto-*.timer \
        "$UNIT_DIR"/temporiki-auto-*.service; do
        [[ -e "$unit" ]] || continue
        unit_name="$(basename "$unit")"
        systemctl --user disable --now "$unit_name" >/dev/null 2>&1 || true
        rm -f "$unit"
        echo "[temporiki] migration: removed legacy systemd unit $unit_name"
        migration_changed=1
      done
      if [[ "$migration_changed" == "1" ]]; then
        systemctl --user daemon-reload >/dev/null 2>&1 || true
      fi
    fi
    ;;
  MINGW*|MSYS*|CYGWIN*)
    if command -v schtasks.exe >/dev/null 2>&1; then
      schtasks.exe /Query /FO CSV /NH 2>/dev/null \
        | awk -F',' '{ gsub(/"/, ""); print $1 }' \
        | grep -i '^TemporikiAuto-' \
        | while IFS= read -r task; do
            schtasks.exe /Delete /TN "$task" /F >/dev/null 2>&1 || true
            echo "[temporiki] migration: removed legacy scheduled task $task"
          done
    fi
    ;;
esac

# Symlink the Obsidian auto-ingest plugin into the vault's plugins folder.
PLUGIN_SRC="$PROJECT_DIR/obsidian-plugin"
PLUGIN_DST="$ROOT_DIR/.obsidian/plugins/temporiki-autoingest"
mkdir -p "$(dirname "$PLUGIN_DST")"
if [[ ! -e "$PLUGIN_DST" ]] || [[ -L "$PLUGIN_DST" ]]; then
  ln -snf "$PLUGIN_SRC" "$PLUGIN_DST"
  echo "[temporiki] Obsidian plugin symlinked: $PLUGIN_DST -> $PLUGIN_SRC"
else
  echo "[temporiki] WARNING: $PLUGIN_DST exists and is not a symlink; skipping plugin install" >&2
fi

echo "[temporiki] running session setup..."
"$PROJECT_DIR/hooks/session-start.sh" >/dev/null

echo
echo "[temporiki] ready."
echo "1) Open this folder as your Obsidian vault."
echo "2) When prompted, trust the 'Temporiki Auto-Ingest' community plugin."
echo "3) Start your LLM CLI in this repo and chat."
echo "   (Web Clipper attachment path is auto-set to raw/webclips.)"
