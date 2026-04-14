# Temporiki Repo Growth Strategy — Design

**Date**: 2026-04-14
**Status**: Approved design, ready for implementation plan
**Goal**: Grow `dbrami/temporiki` from 1 star / 0 forks / 0 watchers into a
discoverable, convertible open-source project with steady traffic and star
growth, driven primarily by self-posted content on X and LinkedIn plus
passive discovery via awesome-lists and GitHub search.

---

## 1. Context

### Current state
- Repo: `dbrami/temporiki`
- Stars: 1 | Forks: 0 | Watchers: 0
- Description set, 9 topics set, `homepageUrl` empty
- README at v0.1.2 — technically solid (~159 lines), reads like internal
  documentation rather than a landing page
- CI workflows in place (Release, Version Guard)
- Issue templates and Discussion templates already defined
- New `uv run temporiki onboard` command (inspired by
  NicholasSpisak/second-brain) provides guided setup

### Target audience (ordered by priority)
1. Novices who want to use AI but don't know what a good use looks like
2. Obsidian power users who want LLM-augmented knowledge management
3. Claude Code / AI coding agent users who want persistent memory
4. PKM tool builders who'd fork and extend

### Primary distribution channels
- X (Twitter) — self-posted threads and single posts
- LinkedIn — self-posted long-form posts
- Secondary: awesome-list PRs for passive discovery

### What's explicitly out of scope (for now)
- Video/GIF demo production — user opted text-first
- Repo rename — user wants to keep "temporiki" as the brand
- Paid promotion, influencer outreach, launch coordination (HN/Reddit)

---

## 2. Strategy Overview

Two parallel tracks:

**Track 1 (primary): README as Landing Page + Social Content Kit**
Rewrite the README to convert visitors into stargazers, then produce
reusable social post templates the user can adapt without rewriting from
scratch each time.

**Track 2 (secondary): Awesome-List + GitHub Discoverability**
Low-effort repo polish and awesome-list PRs for compounding passive
traffic.

---

## 3. Track 1: README Rewrite

### 3.1 New structure (top-to-bottom)

1. **Hero block** — name, one-liner hook, expansion paragraph, credibility
   anchors
2. **Badges row** — license, version, Python, stars
3. **How It Works** — three-step Capture → Organize → Ask
4. **Quick Start** — three commands plus what to do next
5. **Why Temporiki?** — comparison table vs plain Obsidian vs original Memoriki
6. **Under the Hood** — existing technical content collapsed under `<details>`
   fold (architecture, full CLI, implemented features, versioning)
7. **Works With** — MCP-capable agent list
8. **Sources + License** — bottom

The structural principle: the first screen a visitor sees must answer
"why should I care?" before "how is it built?"

### 3.2 Hero block copy

```markdown
# Temporiki

A personal knowledge base that gets smarter every time you use it.

Clip articles, save meeting notes, drop transcripts and files — Temporiki
automatically organizes, connects, and remembers everything so you can ask
questions and get answers with full context of when and why.

Built on Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.
Runs locally with Obsidian. Works with any MCP-capable AI agent.
```

**Badges** (right after the tagline):
- MIT License
- Version (0.1.2)
- Python 3.11+
- GitHub Stars

### 3.3 How It Works section

```markdown
## How It Works

**1. Capture** — Clip web pages with Obsidian Web Clipper, paste meeting
notes, or drop any file into `raw/`. That's your inbox.

**2. Organize** — Temporiki reads your sources, extracts key facts and
decisions, creates linked wiki pages, and indexes everything for search.
Happens automatically in the background.

**3. Ask** — Query your knowledge base in natural language. Get answers
grounded in your own material, with citations and timestamps so you know
where it came from and when.
```

Design rules for this section:
- No tool names (no "SQLite FTS5", "Chroma", "mempalace-lite")
- Three single-word anchors (Capture / Organize / Ask) — scannable and
  reusable as the structure of social posts
- "Your own material" distinguishes from ChatGPT-style answers

### 3.4 Quick Start section

```markdown
## Quick Start

```bash
# Clone and enter
git clone https://github.com/dbrami/temporiki.git
cd temporiki

# Bootstrap (creates venv, installs deps, sets up Obsidian vault)
./hooks/obsidian-zero.sh
```

**That's it.** Drop files into `raw/`, clip pages with Web Clipper to
`raw/webclips/`, and ask your agent questions. Temporiki handles the rest.

Prefer a guided walkthrough? Run `uv run temporiki onboard` for an
interactive checklist.
```

### 3.5 Comparison table

Expand the existing two-column table to three columns by adding "Plain
Obsidian" as the baseline. Keep all existing rows including the new
"Guided onboarding" row (`temporiki onboard`).

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

### 3.6 Under the Hood (collapsed)

Everything currently in the README from "Architecture" through "Versioning"
moves into a `<details>` fold. Nothing is deleted — power users still see
full technical content, it just doesn't block the conversion path.

The fold summary label: **"Architecture, CLI, and developer details"**

### 3.7 Things preserved from current README

- Karpathy LLM Wiki link
- Optional Developer CLI list (inside fold)
- What Is Implemented list (inside fold)
- Versioning / release workflow (inside fold)
- Sources list (bottom, unchanged — includes NicholasSpisak/second-brain)
- Demo placeholder — kept as-is for future GIF/Loom

---

## 4. Track 1: Social Content Kit

**Storage decision**: Post copy lives in this spec document only, not in
the repo. Rationale: templates are static marketing copy, not functional
artifacts — shipping them in `docs/social/` would add weight without giving
users anything executable. Daniel references this spec when posting.

### 4.1 X thread template (3 posts)

```
Post 1 (hook):
I built a personal knowledge base that gets smarter every time I use it.

Clip articles, drop meeting transcripts, save notes — it automatically
organizes, connects, and remembers everything.

Then you just ask questions. Thread ↓

Post 2 (how):
It works in 3 steps:

1. Capture — Web Clipper, meeting notes, any file
2. Organize — AI reads, extracts decisions, links everything
3. Ask — natural language questions with citations and timestamps

Runs locally in Obsidian. No cloud. Your data stays yours.

Post 3 (CTA):
Built on @karpathy's LLM Wiki pattern, extended with temporal memory so
it tracks *when* you learned something and *why* you decided what you did.

Open source, MIT licensed:
github.com/dbrami/temporiki

Star it if this is useful ⭐
```

### 4.2 LinkedIn post template

```
Most of what I read, discuss, and decide gets lost within a week.

Meeting notes sit in a folder. Articles get bookmarked and forgotten.
Decisions get made and the reasoning disappears.

So I built Temporiki — a personal knowledge base that gets smarter
every time you use it.

Clip an article. Paste meeting notes. Drop a transcript. Temporiki
automatically organizes, connects, and indexes everything.

Later, ask a question in plain English. Get an answer grounded in
your own material — with citations and timestamps.

It runs locally in Obsidian, works with AI coding agents (Claude,
Cursor, Codex), and it's open source.

→ github.com/dbrami/temporiki

If you've ever wished your AI assistant actually remembered what
you've told it — this is that.
```

### 4.3 Reusable hashtags

`#obsidian #pkm #knowledgemanagement #ai #opensource #secondbrain #llm #productivity`

### 4.4 Post cadence suggestion (not prescriptive)

- Week 1: Launch post (LinkedIn long-form + X thread on same day)
- Weeks 2–4: One focused single-use-case post per week (e.g., "how I use
  Temporiki for meeting notes", "how it remembers my coding decisions")
- Ongoing: Post every new feature release

---

## 5. Track 2: GitHub Discoverability

### 5.1 Repo metadata fixes

- **homepageUrl**: Set to the rundatarun.io Context Graph article (or a
  future pinned LinkedIn article). Fills an empty field that search engines
  and GitHub UI render prominently.
- **LICENSE**: Add Daniel Brami as a second copyright holder (dual
  copyright, not replacement) — standard practice for MIT forks. Keep
  MIT license text unchanged. Result:
  ```
  Copyright (c) 2026 AyanbekDos
  Copyright (c) 2026 Daniel Brami
  ```
- **Additional topics** (beyond existing 9): `ai-agents`, `knowledge-management`,
  `pkm`, `web-clipper`, `mcp`
- **Pin the repo** on Daniel's GitHub profile
- **Enable GitHub Discussions** (templates already exist — just turn on in
  repo settings)

### 5.2 Awesome-list PRs

Target five awesome-lists with a one-line PR each. Each PR takes ~5 minutes
and is independent.

| Awesome list | Repo | Category to add under |
|---|---|---|
| awesome-obsidian | `kmaasrud/awesome-obsidian` or `sindresorhus/awesome-obsidian` | AI / automation integrations |
| awesome-claude-code | `hesreallyhim/awesome-claude-code` | Memory / knowledge tools |
| awesome-pkm | `Kourva/Awesome-PKM` or similar | AI-augmented PKM |
| awesome-mcp-servers | `punkpeye/awesome-mcp-servers` | Clients / integrations |
| awesome-llm-apps | `Shubhamsaboo/awesome-llm-apps` | Personal productivity |

One-line format for each:

```markdown
- [Temporiki](https://github.com/dbrami/temporiki) — Personal knowledge base with real memory, built on Karpathy's LLM Wiki pattern. Web Clipper inbox + temporal decisions + MCP-agent support.
```

Each PR should be opened separately so the user can track merge status
individually.

### 5.3 Minor polish

- Add a short `docs/why-temporiki.md` essay linked from the README fold
  (optional — can be deferred)
- Add a `CONTRIBUTING.md` pointing contributors to Discussions for ideas
  and Issues for bugs

---

## 6. Deliverables Summary

**File changes:**
1. `README.md` — rewritten per §3
2. `LICENSE` — dual-copyright update per §5.1
3. `CONTRIBUTING.md` — new file per §5.3

Social post copy (§4) stays in this spec document only — not shipped in
the repo.

**GitHub settings changes (manual, not in repo):**
- Set `homepageUrl`
- Add 5 new topics
- Enable Discussions
- Pin repo on profile

**External actions (manual, not in repo):**
- Open 5 awesome-list PRs with the one-line entry

---

## 7. Success Criteria

Within 90 days of completing Track 1:
- README conversion-path sections (hero → quick start) verifiable by human
  review
- At least one awesome-list PR merged (Track 2 sanity check)
- At least 10 stars (baseline growth signal; not hard target)

Longer-term signal (6+ months):
- Organic issues, discussions, or forks from users unknown to Daniel
- Inbound interest via X/LinkedIn DMs or mentions

These are directional, not pass/fail. The real measure is whether Temporiki
starts attracting the audiences identified in §1.

---

## 8. Non-Goals

- Not optimizing for HN front-page launch (deferred, separate initiative)
- Not building community moderation infrastructure (premature at current scale)
- Not translating README or social content to non-English
- Not doing SEO for a marketing site (the repo itself is the site for now)
