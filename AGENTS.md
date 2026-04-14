# Temporiki Agent Schema

## Overview
This repository follows Karpathy's LLM Wiki pattern with automatic dual-store retrieval:
- local `mempalace-lite` (SQLite FTS5) always available
- Chroma HTTP retrieval when healthy
The agent maintains a persistent wiki in `wiki/` from immutable sources in `raw/`.

## Directory Structure
```
temporiki/
  AGENTS.md              # Agent schema (Codex/OpenCode/Cursor)
  CLAUDE.md              # Compatibility mirror for Claude Code
  idea-file.md           # Karpathy's original idea
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
1. Run `uv run temporiki ingest` to identify only new/changed sources (delta ingest).
2. Run `uv run temporiki palace-mine` to index `raw/`:
   - always into `.memplite/palace.sqlite3`
   - into Chroma too when Chroma is available
3. Read changed sources from `raw/`.
4. Update `wiki/sources/`, `wiki/entities/`, `wiki/concepts/`, and `wiki/decisions/` as needed.
5. Update `wiki/index.md`.
6. Append log entry in `wiki/log.md`.

### Query
Default query flow for non-trivial questions:
1. `uv run temporiki palace-search "<query>" --as-of YYYY-MM-DD`
2. Router strategy (automatic, no manual switch):
   - decision intent -> `wiki/decisions` temporal KG query
   - otherwise hybrid rerank of Chroma + SQLite if Chroma is healthy
   - otherwise SQLite FTS5 fallback
3. Return currently valid precedents plus `why` traces
4. For high-value answers, save to `wiki/queries/` (use `uv run temporiki query ...`)

### Session Launch Hook
At session start run:
`./hooks/session-start.sh`

This:
1. starts local Chroma Docker if available, and
2. starts a background auto-monitor loop (`palace-auto`) that watches raw/ and runs periodic lint/health (with lint autofix enabled by default).

### Lint
Run `uv run temporiki lint --autofix` and fix:
1. Missing frontmatter
2. Invalid frontmatter schema
3. Broken wikilinks
4. Orphan pages
5. Stale claims or contradictions

### Obsidian UX Pack
Run `uv run temporiki obsidian-ux-pack` to install:
1. Decision timeline dashboard
2. Stale pages dashboard
3. Wiki health dashboard
4. Canonical templates for decisions and concepts

## Logging Format
Use this heading format in `wiki/log.md`:
`## [YYYY-MM-DD] operation | Description`
