# Memoriki

Personal knowledge base with real memory. Combines [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (Andrej Karpathy) + [MemPalace](https://github.com/milla-jovovich/mempalace) (MCP server).

Wiki gives structure. MemPalace gives memory.

## The Problem

- **LLM Wiki without MemPalace** = library without a catalog. Search is just grep.
- **MemPalace without Wiki** = search engine without books. Semantic search over raw chunks.
- **Together** = structured knowledge + semantic search + entity graph.

## Three Layers of Knowledge

| Layer | What it does | Tool |
|-------|-------------|------|
| **Wiki** | Structure, [[wiki-links]], YAML frontmatter, index | Markdown + Obsidian |
| **MemPalace Drawers** | Semantic search over all content | `mempalace_search` |
| **MemPalace KG** | Entity relationship graph with timestamps | `mempalace_kg_query` |

## Architecture

```
memoriki/
  raw/                    # Your sources (articles, notes, transcripts)
  wiki/                   # LLM-generated wiki (LLM owns this entirely)
    index.md              # Page catalog - updated on every ingest
    log.md                # Operation log (append-only)
    entities/             # People, companies, products
    concepts/             # Ideas, patterns, frameworks
    sources/              # Summary page per source
    synthesis/            # Cross-cutting analysis, comparisons
  mempalace.yaml          # MemPalace config
  CLAUDE.md               # Schema and rules for the LLM
  idea-file.md            # Karpathy's original idea (reference)
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/AyanbekDos/memoriki.git my-knowledge-base
cd my-knowledge-base

# 2. Install MemPalace
pip install mempalace
mempalace init .

# 3. Connect MemPalace to Claude Code
claude mcp add mempalace -- python -m mempalace.mcp_server

# 4. Drop your first source
cp ~/some-article.md raw/

# 5. Launch Claude Code and start ingesting
claude
# > Read raw/some-article.md and ingest it into the wiki
```

## Operations

- **Ingest** - drop a file into `raw/`, tell the LLM to read and integrate it into the wiki
- **Query** - ask a question, LLM finds relevant pages and synthesizes an answer
- **Lint** - health check: contradictions, orphans, knowledge gaps

## Works With

Any MCP-compatible LLM agent:
- **Claude Code** - use `CLAUDE.md` as-is
- **OpenAI Codex** - rename `CLAUDE.md` to `AGENTS.md`
- **Cursor, Gemini CLI** and other MCP-compatible tools

## Use Cases

- **Founders**: customer discovery, interviews, competitors, pivots - all in one place
- **Researchers**: papers, articles, notes - wiki with compounding synthesis
- **Students**: lecture notes, books, projects - structured "second brain"
- **Teams**: Slack threads, meetings, decisions - AI-maintained wiki

## License

MIT

## Credits

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) - original LLM Wiki idea
- [MemPalace](https://github.com/milla-jovovich/mempalace) - MCP server for semantic search and knowledge graph
- [Claude Code](https://claude.com/claude-code) - LLM agent
