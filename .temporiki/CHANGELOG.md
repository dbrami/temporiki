# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

## [0.1.4] - 2026-04-14
### Changed
- `obsidian-zero.sh` output is now quieter: onboarding JSON is suppressed during bootstrap.
- Non-actionable Docker skip warnings are hidden by default when Chroma autostart cannot run (set `TEMPORIKI_BOOTSTRAP_DEBUG=1` to show them).
- Bootstrap completion text now reflects automatic `raw/webclips` attachment-path configuration (no manual setting step).

## [0.1.3] - 2026-04-14
### Added
- Hidden system layout (`.temporiki/`) so Obsidian root view stays focused on knowledge folders (`raw/`, `wiki/`).
- Automatic Obsidian Files & Links default for `attachmentFolderPath = raw/webclips` during onboarding/bootstrap.

### Changed
- Hooks, scripts, CI workflows, and docs now operate via `uv --project .temporiki ...`.
- Zero-command bootstrap now applies full onboarding defaults (templates + vault config) rather than templates alone.

## [0.1.2] - 2026-04-14
### Added
- `uv run temporiki onboard` guided setup command that bootstraps folder structure, templates, and setup checklist output.
- `temporiki_tools.onboarding` module + onboarding tests.

### Changed
- README now documents the optional guided onboarding flow and explicitly references `NicholasSpisak/second-brain` as an upstream idea source.

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
