# Temporiki

Personal knowledge base with real memory. Combines [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (Andrej Karpathy) + automatic dual-store memory:
- local SQLite FTS5 (`mempalace-lite`) always on
- Chroma (thin HTTP client) when available

Wiki gives structure. The router decides memory backend automatically.

## Architecture

```
temporiki/
  raw/                    # Immutable sources
  wiki/                   # LLM-maintained compiled knowledge
    index.md              # Catalog
    log.md                # Chronological operations
    entities/
    concepts/
    sources/
    synthesis/
    decisions/
    queries/
  AGENTS.md               # Agent schema (Codex/OpenCode/Cursor)
  CLAUDE.md               # Claude compatibility mirror
  mempalace.yaml
  .memplite/palace.sqlite3 # Lightweight memory DB (created on demand)
```

## UV Quick Start

```bash
# 1. Clone your fork
git clone https://github.com/dbrami/temporiki.git
cd temporiki

# 2. Create env and install dependencies
uv venv
source .venv/bin/activate
uv sync --extra dev

# 3. Initialize local memory (always on)
uv run temporiki palace-init
uv run temporiki palace-mine

# 4. Optional Chroma client mode (thin client; no kubernetes package)
uv sync --extra chroma-client
./hooks/session-start.sh
uv run temporiki palace-health
```

## CLI Operations

All commands are uv-native:

```bash
# Delta ingest: only new/changed raw files
uv run temporiki ingest

# Index raw/ into local mempalace-lite
uv run temporiki palace-mine

# Search automatically:
# - decision/precedent queries -> decision KG
# - otherwise hybrid rerank (Chroma + SQLite) when Chroma is healthy
# - fallback to SQLite FTS5 when Chroma is unavailable
uv run temporiki palace-search "auth decision"

# Query active decisions as-of a date
uv run temporiki palace-kg-query --as-of 2026-04-13

# Lint wiki structure (frontmatter, broken links, orphans)
uv run temporiki lint

# Lint + safe frontmatter autofix
uv run temporiki lint --autofix

# Save a high-value query answer back into wiki/queries/
uv run temporiki query "What decisions are active?" --answer "..."

# Watch raw/ and continuously detect deltas
uv run temporiki watch --interval-seconds 5

# Run full auto monitor loop (raw watch + auto-mine + periodic lint + health)
uv run temporiki palace-auto

# Install Obsidian dashboards + templates
uv run temporiki obsidian-ux-pack
```

## What Is Implemented

- Hash-based delta ingest tracked in `.manifest.json`
- Query save-back to `wiki/queries/` (compounding knowledge)
- Wiki linting for missing frontmatter, broken links, and orphans
- Built-in `mempalace-lite` (SQLite FTS5 memory search + temporal decision query)
- Thin Chroma integration via `chromadb-client` (HTTP mode)
- Hybrid retrieval reranking with confidence + citation rationale
- Intelligent query routing (KG -> Hybrid -> SQLite fallback)
- Pydantic + YAML schema validation with lint autofix support
- Context Graph mode guidance in `AGENTS.md` (`wiki/decisions/` + temporal precedence)
- Session-launch hook for local Chroma Docker autostart
- Session-start daemon hook (`hooks/session-start.sh`) for automatic monitoring
- Lightweight default install: no `chromadb`/`kubernetes` stack unless `--extra mempalace` is requested

## Works With

Any MCP-capable coding agent (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, OpenClaw).

## Sources

- Karpathy, Andrej — LLM Wiki pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- MemPalace (reference architecture + MCP tool model): https://github.com/MemPalace/mempalace
- Chroma docs (client/server model and API): https://docs.trychroma.com/
- Obsidian Dataview plugin docs (dashboards/queries): https://blacksmithgu.github.io/obsidian-dataview/

## License

MIT
