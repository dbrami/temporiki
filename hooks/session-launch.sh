#!/usr/bin/env bash
set -euo pipefail

# Starts local Chroma server for Temporiki if Docker is available.
# Safe to run repeatedly.

if [[ "${TEMPORIKI_DISABLE_CHROMA_AUTOSTART:-${MEMORIKI_DISABLE_CHROMA_AUTOSTART:-0}}" == "1" ]]; then
  exit 0
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[temporiki] docker not found; skipping chroma autostart" >&2
  exit 0
fi

if ! docker info >/dev/null 2>&1; then
  echo "[temporiki] docker daemon not running; skipping chroma autostart" >&2
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHROMA_DATA_DIR="${TEMPORIKI_CHROMA_DATA_DIR:-${MEMORIKI_CHROMA_DATA_DIR:-$ROOT_DIR/.chroma-data}}"
CHROMA_CONTAINER="${TEMPORIKI_CHROMA_CONTAINER:-${MEMORIKI_CHROMA_CONTAINER:-temporiki-chroma}}"
CHROMA_PORT="${TEMPORIKI_CHROMA_PORT:-${MEMORIKI_CHROMA_PORT:-8000}}"
CHROMA_IMAGE="${TEMPORIKI_CHROMA_IMAGE:-${MEMORIKI_CHROMA_IMAGE:-chromadb/chroma:latest}}"

mkdir -p "$CHROMA_DATA_DIR"

# Create/start container if needed.
if ! docker ps -a --format '{{.Names}}' | grep -qx "$CHROMA_CONTAINER"; then
  docker run -d \
    --name "$CHROMA_CONTAINER" \
    -p "$CHROMA_PORT:8000" \
    -v "$CHROMA_DATA_DIR:/chroma/chroma" \
    "$CHROMA_IMAGE" >/dev/null
else
  if ! docker ps --format '{{.Names}}' | grep -qx "$CHROMA_CONTAINER"; then
    docker start "$CHROMA_CONTAINER" >/dev/null
  fi
fi

# Export convenience var for this shell when sourced; harmless when executed.
export TEMPORIKI_CHROMA_URL="${TEMPORIKI_CHROMA_URL:-${MEMORIKI_CHROMA_URL:-http://127.0.0.1:$CHROMA_PORT}}"
export MEMORIKI_CHROMA_URL="${TEMPORIKI_CHROMA_URL}"

echo "[temporiki] chroma ready at ${TEMPORIKI_CHROMA_URL} (container: $CHROMA_CONTAINER)"
