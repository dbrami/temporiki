#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <base_sha> [head_sha]"
  exit 1
fi

BASE="$1"
HEAD="${2:-HEAD}"
PROJECT_DIR=".temporiki"
README_PATH="README.md"

if [[ "$BASE" =~ ^0+$ ]]; then
  echo "[version-guard] initial push detected; skipping guard"
  exit 0
fi

pyproject_version="$(
  sed -nE 's/^version = \"([0-9]+\.[0-9]+\.[0-9]+)\"/\1/p' "$PROJECT_DIR/pyproject.toml" \
    | head -n1
)"
readme_version="$(
  sed -nE 's#^!\[Version\]\(https://img\.shields\.io/badge/version-([0-9]+\.[0-9]+\.[0-9]+)-informational\)$#\1#p' "$README_PATH" \
    | head -n1
)"

if [[ -z "$pyproject_version" || -z "$readme_version" ]]; then
  echo "[version-guard] could not parse version from $PROJECT_DIR/pyproject.toml or $README_PATH"
  exit 1
fi

if [[ "$pyproject_version" != "$readme_version" ]]; then
  echo "[version-guard] README version badge ($readme_version) does not match pyproject ($pyproject_version)"
  exit 1
fi

if ! git cat-file -e "$BASE^{commit}" 2>/dev/null; then
  echo "[version-guard] base commit not found; skipping guard"
  exit 0
fi

CHANGED="$(git diff --name-only "$BASE" "$HEAD" || true)"
if [[ -z "$CHANGED" ]]; then
  echo "[version-guard] no changes"
  exit 0
fi

IMPACTFUL="$(echo "$CHANGED" | rg -N '^(\.temporiki/temporiki_tools/|\.temporiki/hooks/|\.temporiki/mempalace.yaml|\.temporiki/Makefile|\.temporiki/scripts/)' || true)"
if [[ -z "$IMPACTFUL" ]]; then
  echo "[version-guard] no impactful runtime changes"
  exit 0
fi

if ! echo "$CHANGED" | rg -q '^\.temporiki/pyproject\.toml$'; then
  echo "[version-guard] impactful changes require .temporiki/pyproject.toml version bump"
  echo "$IMPACTFUL"
  exit 1
fi

if ! echo "$CHANGED" | rg -q '^\.temporiki/CHANGELOG\.md$'; then
  echo "[version-guard] impactful changes require .temporiki/CHANGELOG.md update"
  echo "$IMPACTFUL"
  exit 1
fi

old_version="$(
  git show "$BASE:$PROJECT_DIR/pyproject.toml" 2>/dev/null \
    | sed -nE 's/^version = \"([0-9]+\.[0-9]+\.[0-9]+)\"/\1/p' \
    | head -n1
)"
new_version="$(
  sed -nE 's/^version = \"([0-9]+\.[0-9]+\.[0-9]+)\"/\1/p' "$PROJECT_DIR/pyproject.toml" \
    | head -n1
)"

if [[ -z "$old_version" || -z "$new_version" ]]; then
  echo "[version-guard] could not parse versions"
  exit 1
fi

if [[ "$old_version" == "$new_version" ]]; then
  echo "[version-guard] version unchanged ($new_version) despite impactful changes"
  echo "$IMPACTFUL"
  exit 1
fi

echo "[version-guard] ok: $old_version -> $new_version"
