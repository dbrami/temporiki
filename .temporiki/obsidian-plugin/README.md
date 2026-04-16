# Temporiki Auto-Ingest (Obsidian plugin)

Tiny community plugin that keeps the Temporiki vault index fresh while Obsidian is open.

## What it does

- Listens to vault `create` and `modify` events
- Filters to paths under `raw/`
- Debounces bursts by 2s (so folder drops don't fire N times)
- Spawns `uv --project .temporiki run temporiki palace-event --root <vault>` via Node `child_process.execFile` with an explicit argv (no shell interpretation, no string interpolation)
- Surfaces status in the Obsidian status bar (`idle`, `pending`, `ingesting`, `ok`, `error`)

## Install

Bootstrap installs this automatically:

```bash
./.temporiki/hooks/obsidian-zero.sh
```

That symlinks `.temporiki/obsidian-plugin/` into `.obsidian/plugins/temporiki-autoingest/` and enables it in `.obsidian/community-plugins.json`.

The first time you open the vault after install, Obsidian will ask you to trust the plugin. Confirm once; it remembers.

## PATH requirement

On macOS and Linux, the plugin resolves `uv` via `bash -lc 'command -v uv'` at load time. If your login shell can find `uv`, the plugin can too. If the status bar shows `Temporiki: uv not found`, install `uv` per https://docs.astral.sh/uv/ and restart Obsidian.

On Windows, the plugin uses `uv` directly from PATH.

## Files

- `manifest.json` — plugin manifest read by Obsidian
- `main.js` — plugin source (plain CommonJS, no build step required)

## Editing

This is plain JavaScript. Edit `main.js` directly; Obsidian re-reads the plugin when the vault reloads (or disable/re-enable the plugin).

## Why no TypeScript / bundler

The plugin is ~100 lines and has one dependency (`obsidian`), which Obsidian injects at runtime. A TypeScript pipeline would add three tools and a build step for zero user-facing benefit. If it ever grows past ~300 lines, revisit.

## Relationship to the Python router's lazy-ingest guard

This plugin is the eager path — it fires when Obsidian notices a vault change. The Python CLI (`palace-search`, `palace-kg-query`) has its own lazy staleness check (see `.temporiki/temporiki_tools/stale.py`) that handles the case where files land in `raw/` while Obsidian is closed (Finder / CLI copy). Together they cover every realistic ingestion path with no OS-level processes.
