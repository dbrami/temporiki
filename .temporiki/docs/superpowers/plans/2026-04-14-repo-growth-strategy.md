# Temporiki Repo Growth Strategy — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `dbrami/temporiki` from internal-documentation-style repo into a conversion-optimized landing page with supporting discoverability assets, so self-posted content on X/LinkedIn and passive awesome-list traffic can reliably turn visitors into stargazers.

**Architecture:** Three file changes in repo (`README.md`, `LICENSE`, `CONTRIBUTING.md`) plus manual GitHub settings changes and 5 independent awesome-list PRs. No code changes. Social post copy lives in the spec document only, not shipped in repo (lightweight).

**Tech Stack:** Markdown, GitHub repo settings, GitHub CLI (`gh`) for verification.

**Source spec:** `docs/superpowers/specs/2026-04-14-repo-growth-strategy-design.md`

---

## Task 1: Rewrite README.md

**Files:**
- Modify: `README.md` (full rewrite, ~159 lines → new structure)

**Pre-flight context for engineer:**
Read the current README in full before starting. Note that the spec requires the existing technical content to be preserved under a `<details>` fold, not deleted. The Demo section placeholder (lines 60–77 in current README) should stay as-is pending future GIF/Loom asset.

- [ ] **Step 1: Read the current README to confirm all sections to preserve**

Run:
```bash
wc -l README.md && head -5 README.md
```
Expected: ~159 lines, starts with `# Temporiki`.

- [ ] **Step 2: Write the complete new README**

Replace the entire contents of `README.md` with the following. This is the final copy — do not paraphrase or reorder sections.

```markdown
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
```

- [ ] **Step 3: Visual verification — render the README locally or on GitHub**

Run:
```bash
head -20 README.md
```
Expected output starts with `# Temporiki` then the one-liner "A personal knowledge base that gets smarter every time you use it."

Check that:
- Hero block (name, one-liner, expansion paragraph, Karpathy credit) is the first thing visible
- Badges appear after the hero block
- "How It Works" appears before "Quick Start"
- "Under the Hood" is wrapped in `<details>` / `</details>`
- Sources section still includes all 5 references including NicholasSpisak/second-brain

- [ ] **Step 4: Verify no content was lost from the technical sections**

Run:
```bash
grep -c "mempalace-lite" README.md
grep -c "Version Guard" README.md
grep -c "obsidian-zero.sh" README.md
grep -c "Karpathy" README.md
```
Expected: each count >= 1 (technical content preserved under the fold).

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README as conversion-optimized landing page

- Restructure: hero → how it works → quick start → comparison → details fold
- Add Plain Obsidian column to comparison table
- Preserve all technical content under collapsible Under the Hood section
- Adds badge row for license/version/Python/stars"
```

---

## Task 2: Update LICENSE with dual copyright

**Files:**
- Modify: `LICENSE` (line 3 — add second copyright line)

Per spec §5.1: add Daniel Brami as a second copyright holder (dual copyright, not replacement). This is standard practice for MIT forks.

- [ ] **Step 1: Read current LICENSE to confirm line numbers**

Run:
```bash
head -5 LICENSE
```
Expected output:
```
MIT License

Copyright (c) 2026 AyanbekDos

Permission is hereby granted, free of charge, to any person obtaining a copy
```

- [ ] **Step 2: Add second copyright line**

Edit `LICENSE` to change line 3 from:

```
Copyright (c) 2026 AyanbekDos
```

to two consecutive lines:

```
Copyright (c) 2026 AyanbekDos
Copyright (c) 2026 Daniel Brami
```

All other lines in the file must remain unchanged.

- [ ] **Step 3: Verify the change**

Run:
```bash
sed -n '1,6p' LICENSE
```
Expected output:
```
MIT License

Copyright (c) 2026 AyanbekDos
Copyright (c) 2026 Daniel Brami

Permission is hereby granted, free of charge, to any person obtaining a copy
```

- [ ] **Step 4: Verify MIT body is untouched**

Run:
```bash
grep -c "THE SOFTWARE IS PROVIDED" LICENSE
grep -c "MERCHANTABILITY" LICENSE
```
Expected: both return `1`.

- [ ] **Step 5: Commit**

```bash
git add LICENSE
git commit -m "docs: add Daniel Brami as second copyright holder (dual MIT)"
```

---

## Task 3: Create CONTRIBUTING.md

**Files:**
- Create: `CONTRIBUTING.md` (new file)

Per spec §5.3: short file pointing contributors to Discussions for ideas and Issues for bugs. Keep it minimal — the spec emphasizes lightweight.

- [ ] **Step 1: Create the file with this exact content**

Write `CONTRIBUTING.md`:

```markdown
# Contributing to Temporiki

Thanks for your interest in Temporiki. Contributions are welcome across code, docs, and ideas.

## Where to start

- **Ideas, questions, use cases** → [GitHub Discussions](https://github.com/dbrami/temporiki/discussions)
- **Bugs, regressions, broken behavior** → [GitHub Issues](https://github.com/dbrami/temporiki/issues)
- **Pull requests** → fork, branch, PR against `main`

## Pull request guidelines

- Keep changes focused — one concern per PR
- Follow the versioning rules in the README (SemVer + CHANGELOG update for impactful changes)
- Run `uv run temporiki lint --autofix` before submitting if you touched wiki content
- Run `uv run python -m pytest -q` if you touched `temporiki_tools/`
- Reference the Discussion or Issue your PR addresses (e.g., `Closes #12`)

## Code of conduct

Be kind. Assume good intent. Critique ideas, not people.

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see `LICENSE`).
```

- [ ] **Step 2: Verify file exists and renders**

Run:
```bash
wc -l CONTRIBUTING.md && head -5 CONTRIBUTING.md
```
Expected: ~25 lines, starts with `# Contributing to Temporiki`.

- [ ] **Step 3: Verify links point to the correct repo**

Run:
```bash
grep "github.com/dbrami/temporiki" CONTRIBUTING.md
```
Expected: 2 matches (Discussions link and Issues link).

- [ ] **Step 4: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: add CONTRIBUTING.md pointing to Discussions and Issues"
```

---

## Task 4: GitHub repo settings (manual)

**Files:** None — this task is external to the repo. Use `gh` CLI where possible, GitHub web UI for the rest.

These changes happen on github.com, not in the working tree. The engineer should execute each sub-step and confirm success before moving on.

- [ ] **Step 1: Set homepageUrl**

Decision point: Daniel needs to provide the URL. Candidates per spec §5.1:
- rundatarun.io Context Graph article (e.g., `https://rundatarun.io/p/the-context-graph-ais-trillion-dollar`)
- A pinned LinkedIn article (once it exists)

Run (substituting Daniel's chosen URL):
```bash
gh repo edit dbrami/temporiki --homepage "https://rundatarun.io/p/the-context-graph-ais-trillion-dollar"
```

Verify:
```bash
gh repo view dbrami/temporiki --json homepageUrl
```
Expected: `homepageUrl` field is non-empty.

- [ ] **Step 2: Add 5 new topics**

Current topics (9): `claude-code`, `context-graph`, `llm-wiki`, `local-llm`, `mempalace`, `obsidian`, `personal-knowledge-base`, `second-brain`, `temporal-knowledge-graph`.

Add: `ai-agents`, `knowledge-management`, `pkm`, `web-clipper`, `mcp`.

Run:
```bash
gh repo edit dbrami/temporiki --add-topic ai-agents,knowledge-management,pkm,web-clipper,mcp
```

Verify:
```bash
gh repo view dbrami/temporiki --json repositoryTopics
```
Expected: 14 topics total, including the 5 new ones.

- [ ] **Step 3: Enable GitHub Discussions**

Run:
```bash
gh repo edit dbrami/temporiki --enable-discussions
```

Verify in browser: https://github.com/dbrami/temporiki/discussions should load without a "Discussions are not enabled" message.

- [ ] **Step 4: Pin the repo on Daniel's profile**

This cannot be done via `gh` CLI. Manual step:
1. Go to https://github.com/dbrami
2. Click **Customize your pins**
3. Select `temporiki` as one of the pinned repos
4. Save

Verify: `temporiki` appears in the pinned section of https://github.com/dbrami.

- [ ] **Step 5: No commit needed**

GitHub settings changes are not tracked in the repo. Skip commit.

---

## Task 5: Open awesome-list PRs

**Files:** None — each PR is a one-line addition to an external repo, not this one.

Per spec §5.2. Five independent PRs. Each takes ~5 minutes: fork, add one line in the right category section, open PR. The engineer should verify each target list is still actively maintained before opening the PR.

One-line entry template (identical across all 5 PRs):

```markdown
- [Temporiki](https://github.com/dbrami/temporiki) — Personal knowledge base with real memory, built on Karpathy's LLM Wiki pattern. Web Clipper inbox + temporal decisions + MCP-agent support.
```

- [ ] **Step 1: PR to awesome-obsidian**

1. Visit https://github.com/kmaasrud/awesome-obsidian (verify active — check last commit date is within 6 months; if stale, try `sindresorhus/awesome-obsidian` or search GitHub for "awesome obsidian" sorted by stars)
2. Fork the repo
3. Clone your fork, find the most appropriate category section (likely "AI" or "Integrations" or "Automation")
4. Add the one-line entry in alphabetical order within that section
5. Commit with message: `Add Temporiki`
6. Push and open PR with title: `Add Temporiki` and body referencing what Temporiki does in one sentence

- [ ] **Step 2: PR to awesome-claude-code**

Repeat Step 1 process targeting `hesreallyhim/awesome-claude-code`. Likely category: "Memory" or "Knowledge Tools" or "Integrations".

- [ ] **Step 3: PR to an awesome-pkm list**

Search GitHub for "awesome pkm" and "awesome second brain" sorted by stars. Candidates: `Kourva/Awesome-PKM`, `marcolardera/awesome-second-brain`. Pick the most active one. Likely category: "AI-augmented tools" or "Tools".

- [ ] **Step 4: PR to awesome-mcp-servers**

Target `punkpeye/awesome-mcp-servers`. Note: Temporiki is an MCP *client consumer* rather than an MCP *server*, so if the list is strictly servers, find a "Clients" or "Integrations" subsection — otherwise skip this PR and note the skip.

- [ ] **Step 5: PR to awesome-llm-apps**

Target `Shubhamsaboo/awesome-llm-apps`. Likely category: "Personal productivity" or "Knowledge management".

- [ ] **Step 6: Track PR status**

For each PR opened, record:
- URL
- Date opened
- Merge / close date
- Any maintainer feedback

Track this outside the repo (e.g., in Daniel's personal notes). No commit in Temporiki repo.

---

## Post-Implementation Verification

- [ ] **Final step: End-to-end repo check**

Run:
```bash
# All 3 repo files present
ls README.md LICENSE CONTRIBUTING.md

# Current README leads with the new hook
head -3 README.md

# Dual copyright in place
grep "Copyright" LICENSE

# CONTRIBUTING points to correct URLs
grep "github.com/dbrami/temporiki" CONTRIBUTING.md

# GitHub-side metadata
gh repo view dbrami/temporiki --json homepageUrl,repositoryTopics,stargazerCount
```

Expected:
- All three files exist
- README starts with `# Temporiki` then the one-liner hook
- LICENSE has both AyanbekDos and Daniel Brami copyright lines
- CONTRIBUTING.md has 2 matching repo URLs
- `homepageUrl` is non-empty, `repositoryTopics` contains 14 entries

- [ ] **Final commit (if any straggler changes)**

If the verification surfaces anything missed, fix inline and commit:

```bash
git add -A
git commit -m "docs: verification sweep for growth strategy rollout"
```

---

## Scope & Non-Goals (from spec)

**In scope:**
- README rewrite
- LICENSE dual copyright
- New CONTRIBUTING.md
- GitHub settings changes (5 items)
- 5 awesome-list PRs

**Out of scope:**
- Video/GIF demo production
- Repo rename
- HN/Reddit launch coordination
- Paid promotion
- Shipping new features for a launch
- Shipping social post templates as repo artifacts (they live in the spec document)
