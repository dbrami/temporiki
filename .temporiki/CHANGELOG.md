# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

## [0.2.0] - 2026-04-15
### Added
- In-vault Obsidian plugin (`.temporiki/obsidian-plugin/`) that listens to `vault.on('create'|'modify')` under `raw/`, debounces 2s, and spawns `temporiki palace-event` via a safe argv-based process launch — no OS-level watcher, no resident daemon.
- Router-lazy ingest guard `temporiki_tools/stale.py` (`should_run_ingest(root)`). `palace-search` and `palace-kg-query` now run `run_event_cycle(root)` before answering if any `raw/` file is newer than `.manifest.json:updated_at`, so Finder/CLI drops while Obsidian is closed still produce correct results.
- `run_event_cycle()` in `temporiki_tools/automation.py` — single entry point reused by the plugin (eager path) and the lazy-router guard.
- One-shot migration cleanup in `obsidian-zero.sh` that unloads/removes any residual pre-plugin launchd plists (macOS), systemd path+timer units (Linux), or Task Scheduler entries (Windows).
- Onboarding now enables the `temporiki-autoingest` community plugin in `.obsidian/community-plugins.json` and symlinks `.temporiki/obsidian-plugin/` into `.obsidian/plugins/temporiki-autoingest/`.

### Removed
- `scheduler-install.sh`, `scheduler-uninstall.sh`, `auto-run-once.sh`, and `hooks/windows/temporiki-auto-once.ps1`. Ingestion is now triggered entirely from inside the repo (plugin + router guard). Prior installs are cleaned up automatically on next `obsidian-zero.sh` run.

## [0.1.6] - 2026-04-14
### Added
- Auto-save for high-confidence `palace-search` results into `wiki/queries/` (compounding query knowledge by default).
- Lint check `missing_from_index` for wiki pages not represented in `wiki/index.md`.
- Lint check `decision_conflicts` for overlapping active decisions on the same topic.

### Changed
- `palace-search` output now includes `auto_saved` state and optional `saved_query_path` / `auto_save_reason`.

## [0.1.5] - 2026-04-14
### Added
- `wiki/meta/webclips-activity.md` dashboard (Dataview): shows ingress inbox files and recent archived clips.

### Changed
- Webclips are now archived automatically after ingest detection and before mining to keep `raw/webclips/` clean.
- Archive flow rewrites wiki `sources:` frontmatter paths and updates manifest entries so provenance remains valid after moves.

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
