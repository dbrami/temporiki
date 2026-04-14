# Temporiki

A personal knowledge base that gets smarter every time you use it.

Clip articles, save meeting notes, drop transcripts and files — Temporiki automatically organizes, connects, and remembers everything so you can ask questions and get answers with full context of when and why.

Built on Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern. Runs locally with Obsidian. Works with any MCP-capable AI agent.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.2-informational)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![GitHub stars](https://img.shields.io/github/stars/dbrami/temporiki?style=social)

## How It Works

**1. Capture** — Clip web pages with Obsidian Web Clipper, paste meeting notes, or drop any file into `raw/`. That's your inbox.

**2. Organize** — Temporiki reads your sources, extracts key facts and decisions, creates linked wiki pages, and indexes everything for search. Happens automatically in the background.

**3. Ask** — Query your knowledge base in natural language. Get answers grounded in your own material, with citations and timestamps so you know where it came from and when.

## Quick Start

```bash
# Clone and enter
git clone https://github.com/dbrami/temporiki.git
cd temporiki

# Bootstrap (creates venv, installs deps, sets up Obsidian vault)
./hooks/obsidian-zero.sh
```

**That's it.** Drop files into `raw/`, clip pages with Web Clipper to `raw/webclips/`, and ask your agent questions. Temporiki handles the rest.

Prefer a guided walkthrough? Run `uv run temporiki onboard` for an interactive checklist.

## Why Temporiki?

| | Plain Obsidian | Original Memoriki | Temporiki |
|---|---|---|---|
| Knowledge pattern | Manual notes | Karpathy LLM Wiki | LLM Wiki + temporal Context Graph |
| Memory | None — files only | Wiki-first, manual | Dual-store: SQLite FTS5 + Chroma (auto-routed) |
| Daily workflow | Manual organization | Python commands | Zero-command (clip, drop, ask) |
| Guided onboarding | None | Manual docs-led | `temporiki onboard` checklist |
| Web capture | Web Clipper to a folder | Not included | Web Clipper inbox with auto-ingest |
| Temporal reasoning | None | Limited | Time-scoped decisions with `as-of` queries |
| Background automation | None | Partial | Full (ingest, lint, health, indexing) |
| Agent support | N/A | Claude-only | Any MCP-capable agent |

## Demo

Add a 15-30 second GIF or short Loom showing:
1. Drop a clipped page into `raw/webclips/`.
2. Obsidian vault reflects updated knowledge pages.
3. LLM terminal query returns temporal answer with citations.

Suggested embed:

```markdown
![Zero-command Temporiki flow](docs/media/temporiki-zero-flow.gif)
```

## Works With

Any MCP-capable coding agent (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, OpenClaw).

## Under the Hood

<details>
<summary>Architecture, CLI, and developer details</summary>

### Architecture

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

### Zero-Command UX (full detail)

One-time Obsidian setup:
1. Open Obsidian and create/select a vault from the repo folder.
2. Install/enable Obsidian Terminal and Web Clipper.
3. Set Web Clipper target folder to `raw/webclips/`.

Daily use:
1. Open Obsidian vault.
2. Open a terminal inside Obsidian, launch your LLM CLI (`claude`, `codex`, `gemini`, etc.), and chat.
3. Clip content to `raw/webclips/`; the background monitor auto-detects, catalogs, and indexes it.

No manual `uv run ...` commands are required for normal use.

### Optional Developer CLI

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

### What Is Implemented

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

### Versioning

- SemVer tags are used (`vMAJOR.MINOR.PATCH`).
- `pyproject.toml` is the authoritative package version.
- `CHANGELOG.md` tracks release notes.
- GitHub Releases are auto-created when a SemVer tag is pushed.
- Version Guard CI fails if impactful runtime changes are made without a version bump and changelog update.

Release command:
```bash
./scripts/release.sh 0.1.2
git push origin main --follow-tags
```

For day-to-day work:
```bash
# Bump version based on change scope
./scripts/bump_version.sh patch   # bugfix/small behavior change
./scripts/bump_version.sh minor   # backward-compatible feature
./scripts/bump_version.sh major   # breaking change
```

</details>

## Sources

- Karpathy, Andrej — LLM Wiki pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- MemPalace (reference architecture + MCP tool model): https://github.com/MemPalace/mempalace
- Chroma docs (client/server model and API): https://docs.trychroma.com/
- Obsidian Dataview plugin docs (dashboards/queries): https://blacksmithgu.github.io/obsidian-dataview/
- NicholasSpisak/second-brain (onboarding + multi-agent skill packaging ideas): https://github.com/NicholasSpisak/second-brain

## License

MIT
