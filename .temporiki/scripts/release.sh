#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 0.1.1"
  exit 1
fi

VERSION="$1"
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must be SemVer (X.Y.Z)"
  exit 1
fi

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJECT_DIR="$ROOT_DIR/.temporiki"
cd "$ROOT_DIR"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree must be clean before cutting a release."
  exit 1
fi

if git rev-parse "v$VERSION" >/dev/null 2>&1; then
  echo "Tag v$VERSION already exists."
  exit 1
fi

perl -0pi -e "s/version = \"[0-9]+\\.[0-9]+\\.[0-9]+\"/version = \"$VERSION\"/" "$PROJECT_DIR/pyproject.toml"

TODAY="$(date +%F)"
perl -0pi -e "s/## \\[Unreleased\\]\\n/## [Unreleased]\\n\\n## [$VERSION] - $TODAY\\n/" "$PROJECT_DIR/CHANGELOG.md"

git add "$PROJECT_DIR/pyproject.toml" "$PROJECT_DIR/CHANGELOG.md"
git commit -m "Release v$VERSION"
git tag "v$VERSION"

echo "Created commit + tag v$VERSION."
echo "Run: git push origin main --follow-tags"
