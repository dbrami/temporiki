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

echo "[temporiki] starting background monitor..."
"$PROJECT_DIR/hooks/session-start.sh"

echo
echo "[temporiki] ready."
echo "1) Open this folder as your Obsidian vault."
echo "2) Start your LLM CLI in this repo and chat."
echo "   (Web Clipper attachment path is auto-set to raw/webclips.)"
