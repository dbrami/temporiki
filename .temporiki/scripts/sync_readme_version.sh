#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJECT_DIR="$ROOT_DIR/.temporiki"
README_PATH="$ROOT_DIR/README.md"
PYPROJECT_PATH="$PROJECT_DIR/pyproject.toml"

if [[ ! -f "$PYPROJECT_PATH" ]]; then
  echo "Missing $PYPROJECT_PATH"
  exit 1
fi

if [[ ! -f "$README_PATH" ]]; then
  echo "Missing $README_PATH"
  exit 1
fi

VERSION="$(
  sed -nE 's/^version = \"([0-9]+\.[0-9]+\.[0-9]+)\"/\1/p' "$PYPROJECT_PATH" \
    | head -n1
)"

if [[ -z "$VERSION" ]]; then
  echo "Could not parse version from $PYPROJECT_PATH"
  exit 1
fi

perl -0pi -e "s#(https://img\\.shields\\.io/badge/version-)[0-9]+\\.[0-9]+\\.[0-9]+(-informational)#\${1}$VERSION\${2}#g" "$README_PATH"

echo "Synced README version badge to $VERSION"
