#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="$ROOT_DIR/.temporiki"
cd "$ROOT_DIR"

# 0) Ensure expected vault folders exist (idempotent).
mkdir -p "$ROOT_DIR/raw/webclips" "$ROOT_DIR/raw/assets" "$ROOT_DIR/wiki/queries" "$ROOT_DIR/wiki/meta" "$ROOT_DIR/wiki/_templates"

# 0.5) Ensure runtime deps exist (lightweight + chroma client only).
if ! uv sync --project "$PROJECT_DIR" --extra chroma-client >/dev/null 2>&1; then
  echo "[temporiki] uv sync failed; continuing with existing environment" >&2
fi

# 0.6) Ensure onboarding defaults (folders, templates, Obsidian files/links config).
uv --project "$PROJECT_DIR" run temporiki onboard >/dev/null 2>&1 || true

# 1) Bring up Chroma if possible (no-op if Docker unavailable).
"$PROJECT_DIR/hooks/session-launch.sh" || true

# 2) Ensure runtime state dir exists.
mkdir -p "$ROOT_DIR/.memplite"

cat <<'MSG'
[temporiki] session ready.
[temporiki] automation is event-driven (no always-on daemon).
[temporiki] if this repo was not bootstrapped with obsidian-zero:
  ./.temporiki/hooks/scheduler-install.sh
MSG
