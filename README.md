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

## Zero-Command UX (Obsidian + LLM Chat)

```bash
# 1) Clone your fork
git clone https://github.com/dbrami/temporiki.git
cd temporiki

# 2) Run one bootstrap script (no Python commands)
./hooks/obsidian-zero.sh
```

One-time Obsidian setup:
1. Open Obsidian and create/select a vault from the repo folder.
2. Install/enable Obsidian Terminal and Web Clipper.
3. Set Web Clipper target folder to `raw/webclips/`.

Daily use:
1. Open Obsidian vault.
2. Open a terminal inside Obsidian, launch your LLM CLI (`claude`, `codex`, `gemini`, etc.), and chat.
3. Clip content to `raw/webclips/`; the background monitor auto-detects, catalogs, and indexes it.

No manual `uv run ...` commands are required for normal use.

If you prefer guided setup in-agent (inspired by `second-brain`):

```bash
uv run temporiki onboard
```

This prints a checklist and ensures folders/templates are ready.

## Demo

Add a 15-30 second GIF or short Loom showing:
1. Drop a clipped page into `raw/webclips/`.
2. Obsidian vault reflects updated knowledge pages.
3. LLM terminal query returns temporal answer with citations.

Suggested embed:

```markdown
![Zero-command Temporiki flow](docs/media/temporiki-zero-flow.gif)
```

Or Loom:

```markdown
[Watch the 25s zero-command flow](https://www.loom.com/share/your-video-id)
```

## Comparison

Temporiki is built on and significantly extended from the original Memoriki foundation.

| Capability | Original Memoriki | Temporiki |
|---|---|---|
| Core pattern | Karpathy LLM Wiki | Karpathy LLM Wiki + temporal Context Graph |
| Storage | Wiki-first, manual ops | Dual memory: SQLite FTS5 + Chroma (auto-routed) |
| Daily UX | Manual Python command workflow | Zero-command daily flow (`./hooks/obsidian-zero.sh`) |
| Guided onboarding | Manual docs-led setup | `temporiki onboard` checklist + structure bootstrap |
| Obsidian integration | Basic vault usage | Web Clipper inbox + dashboards + templates |
| Temporal reasoning | Limited explicit precedence tracking | Time-scoped decision KG with `as-of` query support |
| Automation | Partial/manual | Background monitor (ingest, lint, health, indexing) |

## Optional Developer CLI

```bash
uv run temporiki ingest
uv run temporiki onboard
uv run temporiki palace-mine
uv run temporiki palace-search "auth decision"
uv run temporiki palace-kg-query --as-of 2026-04-13
uv run temporiki lint
uv run temporiki lint --autofix
uv run temporiki query "What decisions are active?" --answer "..."
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
- Web Clipper inbox at `raw/webclips/` with automatic ingest/index loop
- Lightweight default install: no `chromadb`/`kubernetes` stack unless `--extra mempalace` is requested

## Works With

Any MCP-capable coding agent (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, OpenClaw).

## Versioning

- SemVer tags are used (`vMAJOR.MINOR.PATCH`).
- `pyproject.toml` is the authoritative package version.
- `CHANGELOG.md` tracks release notes.
- GitHub Releases are auto-created when a SemVer tag is pushed.
- Version Guard CI fails if impactful runtime changes are made without a version bump and changelog update.

Release command:
```bash
./scripts/release.sh 0.1.1
git push origin main --follow-tags
```

For day-to-day work:
```bash
# Bump version based on change scope
./scripts/bump_version.sh patch   # bugfix/small behavior change
./scripts/bump_version.sh minor   # backward-compatible feature
./scripts/bump_version.sh major   # breaking change
```

## Sources

- Karpathy, Andrej — LLM Wiki pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- MemPalace (reference architecture + MCP tool model): https://github.com/MemPalace/mempalace
- Chroma docs (client/server model and API): https://docs.trychroma.com/
- Obsidian Dataview plugin docs (dashboards/queries): https://blacksmithgu.github.io/obsidian-dataview/
- NicholasSpisak/second-brain (onboarding + multi-agent skill packaging ideas): https://github.com/NicholasSpisak/second-brain

## License

MIT
