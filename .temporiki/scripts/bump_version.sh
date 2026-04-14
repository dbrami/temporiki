#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <patch|minor|major>"
  exit 1
fi

KIND="$1"
if [[ "$KIND" != "patch" && "$KIND" != "minor" && "$KIND" != "major" ]]; then
  echo "Expected one of: patch, minor, major"
  exit 1
fi

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJECT_DIR="$ROOT_DIR/.temporiki"
cd "$ROOT_DIR"

CURRENT="$(
  sed -nE 's/^version = \"([0-9]+\.[0-9]+\.[0-9]+)\"/\1/p' "$PROJECT_DIR/pyproject.toml" \
    | head -n1
)"
if [[ -z "$CURRENT" ]]; then
  echo "Could not parse current version from pyproject.toml"
  exit 1
fi

IFS='.' read -r MAJOR MINOR PATCH <<<"$CURRENT"
case "$KIND" in
  patch) PATCH=$((PATCH + 1)) ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
esac

NEXT="${MAJOR}.${MINOR}.${PATCH}"
TODAY="$(date +%F)"

perl -0pi -e "s/version = \"[0-9]+\\.[0-9]+\\.[0-9]+\"/version = \"$NEXT\"/" "$PROJECT_DIR/pyproject.toml"
perl -0pi -e "s/## \\[Unreleased\\]\\n/## [Unreleased]\\n\\n## [$NEXT] - $TODAY\\n/" "$PROJECT_DIR/CHANGELOG.md"

echo "Version bumped: $CURRENT -> $NEXT"
echo "Next: fill changelog notes for $NEXT, then commit."
