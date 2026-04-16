# Temporiki Agent Schema

## Overview
This repository follows Karpathy's LLM Wiki pattern with automatic dual-store retrieval:
- local `mempalace-lite` (SQLite FTS5) always available
- Chroma HTTP retrieval when healthy
The agent maintains a persistent wiki in `wiki/` from immutable sources in `raw/`.

## Directory Structure
```
temporiki/
  .temporiki/AGENTS.md   # Agent schema (Codex/OpenCode/Cursor)
  .temporiki/CLAUDE.md   # Compatibility mirror for Claude Code
  .temporiki/idea-file.md # Karpathy's original idea
  raw/                   # Immutable source material
  wiki/
    index.md             # Master index (always current)
    log.md               # Append-only operation log
    entities/
    concepts/
    sources/
    synthesis/
    decisions/           # Time-scoped decision records
    queries/             # Saved high-value query outputs
```

## Core Rules
0. One-time setup after clone: run `./.temporiki/hooks/obsidian-zero.sh`. No recurring startup command is required.
1. Never modify files in `raw/`.
2. Every wiki page must have YAML frontmatter.
3. Always update `wiki/index.md` and `wiki/log.md` after ingest/query/lint writes.
4. Use `[[wiki-links]]` for cross-references.
5. Preserve provenance: clearly separate extracted facts from inferred claims.

## Required Frontmatter
```yaml
---
title: Page Title
type: entity|concept|source|synthesis|decision|query
sources: [raw/file.md]
related: [[linked-page]]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Context Graph Mode (Temporal Decision Capture)
When ingesting any source, extract explicit decisions and rationale.

Decision pages go in `wiki/decisions/` with this schema:
```yaml
---
title: Decision on [Topic]
date: YYYY-MM-DD
validity_until: YYYY-MM-DD or "indefinite"
context: "..."
alternatives_considered: ["..."]
precedent_references: [[page-a]], [[page-b]]
why_this_choice: "..."
event_clock: "What changed and why at this timestamp"
sources: [raw/source.md]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Operation Flows
### Ingest
1. Run `uv --project .temporiki run temporiki ingest` to identify only new/changed sources (delta ingest).
   - default user inbox from Obsidian Web Clipper: `raw/webclips/`
   - webclips are auto-archived post-ingest to `raw/webclips/_archive/YYYY-MM/` and wiki `sources:` paths are rewritten automatically.
2. Run `uv --project .temporiki run temporiki palace-mine` to index `raw/`:
   - always into `.memplite/palace.sqlite3`
   - into Chroma too when Chroma is available
3. Read changed sources from `raw/` and `raw/webclips/_archive/`.
4. Update `wiki/sources/`, `wiki/entities/`, `wiki/concepts/`, and `wiki/decisions/` as needed.
5. Update `wiki/index.md`.
6. Append log entry in `wiki/log.md`.

### Query
Default query flow for non-trivial questions:
1. `uv --project .temporiki run temporiki palace-search "<query>" --as-of YYYY-MM-DD`
2. Router strategy (automatic, no manual switch):
   - decision intent -> `wiki/decisions` temporal KG query
   - otherwise hybrid rerank of Chroma + SQLite if Chroma is healthy
   - otherwise SQLite FTS5 fallback
3. Return currently valid precedents plus `why` traces
4. `palace-search` auto-saves high-confidence answers to `wiki/queries/` by default.
5. For manual/curated save-back, use `uv --project .temporiki run temporiki query ...`.

### Session Hooks
All hooks live in `.temporiki/hooks/` and are idempotent.

**First-time bootstrap (one-time):** `./.temporiki/hooks/obsidian-zero.sh`
1. Scaffolds `raw/webclips`, `raw/assets`, `wiki/queries`, `wiki/meta`, `wiki/_templates`.
2. Runs `uv sync --project .temporiki --extra chroma-client`.
3. Applies `temporiki onboard` defaults (Obsidian Web Clipper attachment path, enables the `temporiki-autoingest` community plugin).
4. Symlinks `.temporiki/obsidian-plugin/` into `.obsidian/plugins/temporiki-autoingest/`.
5. One-shot migration cleanup: removes any residual launchd plists / systemd units / Windows scheduled tasks from pre-plugin installs.
6. Runs initial runtime setup (`session-start.sh`) with optional Chroma autostart.

**Ingest triggering (no resident daemon, no OS scheduler):**
1. **Eager path (Obsidian open)** — the in-vault plugin listens to `vault.on('create'|'modify')` under `raw/`, debounces 2s, and spawns `temporiki palace-event --root <vault>` via Node's safe argv-based process launch (no shell interpolation).
2. **Lazy path (Obsidian closed)** — `palace-search` and `palace-kg-query` call `stale.should_run_ingest(root)` before querying; if any `raw/` file has mtime newer than `.manifest.json:updated_at`, they run `run_event_cycle(root)` first so the answer is correct.
3. Lint/health cadence state is persisted in `.memplite/event-state.json` regardless of which path fired.
4. Webclips are auto-archived post-ingest to `raw/webclips/_archive/YYYY-MM/`.

**Chroma-only launch:** `./.temporiki/hooks/session-launch.sh`
Starts/reuses the `temporiki-chroma` Docker container on `${TEMPORIKI_CHROMA_PORT:-8000}` with data at `.chroma-data/`. No-op when Docker is unavailable.

**Session stop:** `./.temporiki/hooks/session-stop.sh`
Cleans up any legacy daemon pid file. (OS scheduler uninstall is no longer needed — the one-shot migration in `obsidian-zero.sh` handles that once.)

### Lint
Run `uv --project .temporiki run temporiki lint --autofix` and fix:
1. Missing frontmatter
2. Invalid frontmatter schema
3. Broken wikilinks
4. Orphan pages
5. Missing coverage in `wiki/index.md` (`missing_from_index`)
6. Active decision conflicts on same topic (`decision_conflicts`)
7. Stale claims or contradictions

### Obsidian UX Pack
Run `uv --project .temporiki run temporiki obsidian-ux-pack` to install:
1. Decision timeline dashboard
2. Stale pages dashboard
3. Wiki health dashboard
4. Webclips activity dashboard (`wiki/meta/webclips-activity.md`)
5. Canonical templates for decisions and concepts

## Logging Format
Use this heading format in `wiki/log.md`:
`## [YYYY-MM-DD] operation | Description`
