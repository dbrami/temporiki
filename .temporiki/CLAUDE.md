# Compatibility Note

Claude Code users should follow `.temporiki/AGENTS.md`.

This file intentionally mirrors the same schema so all agents use one workflow.

---

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
0. Mandatory first action each session: run `./.temporiki/hooks/session-start.sh` before any analysis. On a fresh clone, run `./.temporiki/hooks/obsidian-zero.sh` instead; at shutdown, `./.temporiki/hooks/session-stop.sh` stops the background monitor.
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
2. Run `uv --project .temporiki run temporiki palace-mine` to index `raw/`:
   - always into `.memplite/palace.sqlite3`
   - into Chroma too when Chroma is available
3. Read changed sources from `raw/`.
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
4. For high-value answers, save to `wiki/queries/` (use `uv --project .temporiki run temporiki query ...`)

### Session Hooks
All hooks live in `.temporiki/hooks/` and are idempotent.

**First-time bootstrap:** `./.temporiki/hooks/obsidian-zero.sh`
Scaffolds `raw/webclips`, `raw/assets`, `wiki/queries`, `wiki/meta`, `wiki/_templates`, runs `uv sync --extra chroma-client`, applies `temporiki onboard` defaults (including Obsidian Web Clipper attachment path), then invokes `session-start.sh`.

**Every session (mandatory first action):** `./.temporiki/hooks/session-start.sh`
1. Ensures vault folders exist (`raw/webclips`, `raw/assets`, `wiki/queries`, `wiki/meta`, `wiki/_templates`).
2. Runs `uv sync --project .temporiki --extra chroma-client` (best-effort).
3. Runs `uv --project .temporiki run temporiki onboard` to refresh Obsidian/vault defaults.
4. Calls `session-launch.sh` to start local Chroma Docker when available (honors `TEMPORIKI_DISABLE_CHROMA_AUTOSTART=1`; exports `TEMPORIKI_CHROMA_URL` / `MEMORIKI_CHROMA_URL`).
5. Starts background `temporiki palace-auto` monitor if not already running; PID at `.memplite/auto.pid`, log at `.memplite/auto.log`. The monitor watches `raw/` and runs periodic lint/health with lint autofix enabled by default.

**Chroma-only launch:** `./.temporiki/hooks/session-launch.sh`
Starts/reuses the `temporiki-chroma` Docker container on `${TEMPORIKI_CHROMA_PORT:-8000}` with data at `.chroma-data/`. No-op when Docker is unavailable.

**Session stop:** `./.temporiki/hooks/session-stop.sh`
Kills the `palace-auto` process via `.memplite/auto.pid` and removes the pid file.

### Lint
Run `uv --project .temporiki run temporiki lint --autofix` and fix:
1. Missing frontmatter
2. Invalid frontmatter schema
3. Broken wikilinks
4. Orphan pages
5. Stale claims or contradictions

### Obsidian UX Pack
Run `uv --project .temporiki run temporiki obsidian-ux-pack` to install:
1. Decision timeline dashboard
2. Stale pages dashboard
3. Wiki health dashboard
4. Canonical templates for decisions and concepts

## Logging Format
Use this heading format in `wiki/log.md`:
`## [YYYY-MM-DD] operation | Description`
