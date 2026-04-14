# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

## [0.1.1] - 2026-04-13
### Added
- Version Guard CI workflow to enforce version bump + changelog updates for impactful runtime changes.
- `scripts/check_version_guard.sh` for local/CI enforcement between base and head commits.
- `scripts/bump_version.sh` helper for SemVer patch/minor/major bumps.

### Changed
- README now documents required versioning cadence and bump commands.

## [0.1.0] - 2026-04-14
### Added
- Zero-command Obsidian bootstrap (`hooks/obsidian-zero.sh`).
- Automatic session startup/monitor flow (`hooks/session-start.sh` + `hooks/session-launch.sh`).
- Hybrid retrieval router (SQLite FTS5 + Chroma HTTP when available).
- Obsidian UX pack dashboards and templates.
- Web Clipper inbox defaults (`raw/webclips/`, `raw/assets/`).
