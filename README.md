# Temporiki

A personal knowledge base that gets smarter every time you use it.

Clip articles, save meeting notes, drop transcripts and files — Temporiki automatically organizes, connects, and remembers everything so you can ask questions and get answers with full context of when and why.

Built on Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern. Runs locally with Obsidian. Works with any MCP-capable AI agent.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.6-informational)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![GitHub stars](https://img.shields.io/github/stars/dbrami/temporiki?style=social)

## How It Works

**1. Capture** — Clip web pages with Obsidian Web Clipper, paste meeting notes, or drop any file into `raw/`. `raw/webclips/` is ingress-only.

**2. Organize** — Temporiki reads your sources, extracts key facts and decisions, creates linked wiki pages, indexes everything for search, and auto-moves processed webclips to `raw/webclips/_archive/YYYY-MM/` (with wiki `sources:` links rewritten). Happens automatically in the background.

**3. Ask** — Query your knowledge base in natural language. Get answers grounded in your own material, with citations and timestamps so you know where it came from and when.
High-confidence `palace-search` results are auto-saved into `wiki/queries/` so insights compound instead of staying in chat.

## Quick Start

```bash
# Clone and enter
git clone https://github.com/dbrami/temporiki.git
cd temporiki

# Bootstrap (creates venv, installs deps, sets up Obsidian vault)
./.temporiki/hooks/obsidian-zero.sh
```

**That's it.** Drop files into `raw/`, clip pages with Web Clipper to `raw/webclips/`, and ask your agent questions. Temporiki handles the rest, including auto-archiving processed clips.
`./.temporiki/hooks/obsidian-zero.sh` also auto-sets Obsidian `Attachment folder path` to `raw/webclips`.

Prefer a guided walkthrough? Run `uv --project .temporiki run temporiki onboard` for an interactive checklist.

## Demo

Add a 15-30 second GIF or short Loom showing:
1. Drop a clipped page into `raw/webclips/`.
2. Obsidian vault reflects updated knowledge pages.
3. LLM terminal query returns temporal answer with citations.

Suggested embed:

```markdown
![Zero-command Temporiki flow](docs/media/temporiki-zero-flow.gif)
```

## Why Temporiki?

| | Plain Obsidian | Original Memoriki | Temporiki |
|---|---|---|---|
| Knowledge pattern | Manual notes | Karpathy LLM Wiki | LLM Wiki + temporal Context Graph |
| Memory | None — files only | Wiki-first, manual | Dual-store: SQLite FTS5 + Chroma (auto-routed) |
| Daily workflow | Manual organization | Python commands | Zero-command (clip, drop, ask) |
| Guided onboarding | None | Manual docs-led | `temporiki onboard` checklist |
| Web capture | Web Clipper to a folder | Not included | Web Clipper inbox with auto-ingest |
| Inbox clutter | User-managed | User-managed | `raw/webclips/` ingress + immediate auto-archive |
| Temporal reasoning | None | Limited | Time-scoped decisions with `as-of` queries |
| Background automation | None | Partial | Full (ingest, lint, health, indexing) |
| Agent support | N/A | Claude-only | Any MCP-capable agent |

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
  .temporiki/AGENTS.md               # Agent schema (Codex/OpenCode/Cursor)
  .temporiki/CLAUDE.md               # Claude compatibility mirror
  .temporiki/mempalace.yaml
  .memplite/palace.sqlite3 # Lightweight memory DB (created on demand)
```

### Zero-Command UX (full detail)

One-time Obsidian setup:
1. Open Obsidian and create/select a vault from the repo folder.
2. Install/enable Obsidian Terminal and Web Clipper.
3. (Optional) confirm Web Clipper target folder is `raw/webclips/` (Temporiki auto-sets Obsidian attachment path there).

Daily use:
1. Open Obsidian vault.
2. Open a terminal inside Obsidian, launch your LLM CLI (`claude`, `codex`, `gemini`, etc.), and chat.
3. Clip content to `raw/webclips/`; the background monitor auto-detects, catalogs, and indexes it.
4. Processed clips are moved to `raw/webclips/_archive/YYYY-MM/` automatically.

No manual `uv run ...` commands are required for normal use.

### Optional Developer CLI

```bash
uv --project .temporiki run temporiki ingest
uv --project .temporiki run temporiki onboard
uv --project .temporiki run temporiki palace-mine
uv --project .temporiki run temporiki palace-search "auth decision"
uv --project .temporiki run temporiki palace-kg-query --as-of 2026-04-13
uv --project .temporiki run temporiki lint
uv --project .temporiki run temporiki lint --autofix
uv --project .temporiki run temporiki query "What decisions are active?" --answer "..."
```

### What Is Implemented

- Hash-based delta ingest tracked in `.manifest.json`
- Query save-back to `wiki/queries/` (compounding knowledge)
- High-confidence auto-save from `palace-search` to `wiki/queries/`
- Wiki linting for missing frontmatter, broken links, and orphans
- Lint checks for pages missing from `wiki/index.md`
- Lint contradiction watch for overlapping active decisions on the same topic
- Built-in `mempalace-lite` (SQLite FTS5 memory search + temporal decision query)
- Thin Chroma integration via `chromadb-client` (HTTP mode)
- Hybrid retrieval reranking with confidence + citation rationale
- Intelligent query routing (KG -> Hybrid -> SQLite fallback)
- Pydantic + YAML schema validation with lint autofix support
- Context Graph mode guidance in `.temporiki/AGENTS.md` (`wiki/decisions/` + temporal precedence)
- Session-launch hook for local Chroma Docker autostart
- Session-start daemon hook (`.temporiki/hooks/session-start.sh`) for automatic monitoring
- Web Clipper inbox at `raw/webclips/` with automatic ingest/index loop
- Webclips activity dashboard at `wiki/meta/webclips-activity.md` (inbox + recent archives)
- Lightweight default install: no `chromadb`/`kubernetes` stack unless `--extra mempalace` is requested

### Why RAG Alone Isn't Enough

Most retrieval-augmented-generation systems rely on similarity in high-dimensional embedding spaces to pull context for the LLM. This has a well-known weakness — the [curse of dimensionality](https://en.wikipedia.org/wiki/Curse_of_dimensionality): as dimensions grow, distances between points become less discriminating, and "semantically similar" can drift from "actually relevant."

A Stanford RegLab study of commercial legal RAG tools ([Magesh et al. 2025, *Journal of Empirical Legal Studies*](https://doi.org/10.1111/jels.12413)) measured hallucination rates of 17–33% on systems marketed as "hallucination-free." The paper identifies three failure modes that trace back to retrieval limitations:

1. **Text-similar but irrelevant retrieval** — shared surface tokens (a name, a word) pulling unrelated sources
2. **Temporal drift** — retrieved sources that were once correct but have been superseded
3. **Misgrounding** — citations to real sources that don't actually support the claim

Temporiki mitigates each of these with structural, not purely statistical, choices:

| Failure mode | Temporiki's mitigation |
|---|---|
| Embedding-only retrieval is fragile | **Hybrid routing** — KG-first for decision queries, then lexical + vector rerank, then SQLite FTS5 fallback. No single similarity metric decides what's retrieved. |
| Temporal drift | **Time-scoped decisions** with `validity_until` and `as-of` query filters. Superseded content is surfaced as such, not returned as current. |
| Misgrounding | **Immutable `raw/` sources + YAML provenance** on every wiki page. Every claim links back to a specific source file; reasoning (`why_this_choice`, `precedent_references`) is stored separately from extracted facts. |
| "Distracting" similar documents | **Context Graph layer** — explicit entity/decision/concept links, not just embedding proximity. Relevance is graph-walkable, not purely statistical. |

Temporiki does not eliminate hallucinations — no RAG system does. It narrows the surface area where the common failure modes live.

### Versioning

- SemVer tags are used (`vMAJOR.MINOR.PATCH`).
- `.temporiki/pyproject.toml` is the authoritative package version.
- `.temporiki/CHANGELOG.md` tracks release notes.
- GitHub Releases are auto-created when a SemVer tag is pushed.
- Version Guard CI fails if impactful runtime changes are made without a version bump and changelog update.

Release command:
```bash
./.temporiki/scripts/release.sh 0.1.3
git push origin main --follow-tags
```

For day-to-day work:
```bash
# Bump version based on change scope
./.temporiki/scripts/bump_version.sh patch   # bugfix/small behavior change
./.temporiki/scripts/bump_version.sh minor   # backward-compatible feature
./.temporiki/scripts/bump_version.sh major   # breaking change
```

</details>

## Sources

- Karpathy, Andrej — LLM Wiki pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- AyanbekDos/memoriki (original upstream fork source): https://github.com/AyanbekDos/memoriki
- MemPalace (reference architecture + MCP tool model): https://github.com/MemPalace/mempalace
- Chroma docs (client/server model and API): https://docs.trychroma.com/
- Obsidian Dataview plugin docs (dashboards/queries): https://blacksmithgu.github.io/obsidian-dataview/
- NicholasSpisak/second-brain (onboarding + multi-agent skill packaging ideas): https://github.com/NicholasSpisak/second-brain

## License

MIT
