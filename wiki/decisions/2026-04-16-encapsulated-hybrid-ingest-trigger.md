---
title: Decision on Replacing OS File Watcher with Encapsulated Hybrid Ingest Trigger
type: decision
sources: []
related: []
created: '2026-04-16'
updated: '2026-04-16'
date: '2026-04-16'
validity_until: indefinite
context: "Prior to 0.2.0, `obsidian-zero.sh` installed an OS-level file watcher (launchd\
  \ on macOS, systemd path+timer on Linux, Task Scheduler on Windows) that fired `temporiki\
  \ palace-event` on every change under `raw/`. Two problems surfaced: (1) orphan\
  \ state \u2014 launchd agents persisted across clone moves/deletions with nothing\
  \ to garbage-collect them, and one agent silently failed with exit 127 because launchd's\
  \ PATH didn't include `uv`; (2) philosophical mismatch \u2014 runtime state lived\
  \ in the host OS outside the repo, so `git clone` did not reproduce it and `rm -rf`\
  \ did not clean it up."
alternatives_considered:
- "Keep OS scheduler, patch PATH and add a self-GC script \u2014 fixes symptoms but\
  \ keeps the host-OS dependency."
- "Replace OS scheduler with a resident Python daemon \u2014 removes OS coupling but\
  \ introduces a long-lived process the user can forget about (same garbage-collection\
  \ class of problem)."
- "Obsidian-plugin only (no lazy guard) \u2014 simple, but misses the Finder/CLI-while-Obsidian-closed\
  \ case."
- "Lazy-on-query only (no plugin) \u2014 covers correctness but the vault feels stale\
  \ while Obsidian is open since ingest only runs when the user asks."
- "Hybrid plugin (eager) + lazy-on-query guard \u2014 chosen."
- "Keep OS scripts as an opt-in mode for hypothetical headless users \u2014 rejected\
  \ after analysis: any headless persona is also a CLI-first user, and the lazy guard\
  \ already covers every query path."
precedent_references: []
why_this_choice: The hybrid plugin+lazy pair covers every realistic ingress (Web Clipper,
  Obsidian drag, Obsidian editor, Finder/CLI) with zero host-OS surface area. The
  plugin lives in the repo and is installed via an idempotent symlink, so a `git clone`
  reproduces the runtime and `rm -rf` cleans it up. The lazy guard is cheap (O(files)
  stat calls, no hashing) and only runs once per user query, so the rare Finder-drop-while-Obsidian-closed
  case still yields a correct answer without an always-on process. Maintaining three
  cross-OS install scripts for a use case the lazy path already covers was defensive
  over-engineering.
event_clock: "On 2026-04-15 investigation found two orphan `com.temporiki.autorun.*`\
  \ launchd agents on a workstation \u2014 one pointing to a clone that had been moved,\
  \ another failing with exit 127 due to missing `uv` in launchd's PATH. Both had\
  \ been installed by earlier runs of `scheduler-install.sh` and nothing garbage-collected\
  \ them when the corresponding clones moved or were deleted. This made the philosophical\
  \ mismatch concrete and motivated the move to a fully encapsulated design."
---

## Summary

Temporiki 0.2.0 replaces the OS-level file watcher with a **hybrid in-repo ingest trigger**:

- **Eager path** — An in-vault Obsidian plugin at `.temporiki/obsidian-plugin/` listens to `vault.on('create'|'modify')` under `raw/`, debounces 2s, and spawns `temporiki palace-event --root <vault>` via Node's argv-based process launch (no shell interpolation).
- **Lazy path** — `temporiki_tools/stale.py:should_run_ingest(root)` does a cheap mtime-vs-per-source-`last_seen` comparison before `palace-search` and `palace-kg-query` answer. If stale, it runs `run_event_cycle(root)` so the query always reflects current `raw/` state — even when Obsidian is closed.
- **Shared entry point** — `run_event_cycle()` in `temporiki_tools/automation.py` is the single ingest/archive/mine/lint-cadence gateway reused by both paths.
- **Migration** — `obsidian-zero.sh` includes a one-shot cross-OS cleanup (unloads/removes any residual `com.temporiki.autorun.*` launchd plists, `temporiki-auto-*` systemd units, `TemporikiAuto-*` Task Scheduler entries). Scheduled for removal in a later release.
- **Removed** — `scheduler-install.sh`, `scheduler-uninstall.sh`, `auto-run-once.sh`, `hooks/windows/temporiki-auto-once.ps1`, and the corresponding `Makefile` targets.

## Rationale

**Why a plugin + lazy guard instead of just one or the other?**

| Ingress path                | Obsidian open          | Obsidian closed                                    |
|-----------------------------|------------------------|----------------------------------------------------|
| Web Clipper                 | Plugin (eager)         | n/a                                                |
| Drag into Obsidian          | Plugin (eager)         | n/a                                                |
| Editor new file             | Plugin (eager)         | n/a                                                |
| Finder / CLI `cp`/`mv`      | Plugin (vault polling) | Lazy guard on next `palace-search` / `palace-kg-query` |

Every quadrant is covered without an OS-level process. The plugin handles the warm case where Obsidian is already open (fast, ~2s after event). The lazy guard handles the cold case where the user dropped files via Finder or CLI while Obsidian was closed — the next query absorbs a one-time ingest (~1–3s) rather than returning a stale answer.

**Why compare against per-source `last_seen`, not the global `updated_at`?**

The manifest's top-level `updated_at` is rewritten on every `ingest_delta` call, so it represents the last sweep, not per-file seen-time. A file copied in with `cp -p` (preserving an older mtime) would have mtime < sweep time and be silently skipped. Comparing each file's mtime against its own per-source `last_seen` entry — and treating any file not in `sources` as new — closes that gap. This was flagged during code review and fixed in the follow-up commit.

**Why an argv-based process launch?**

Both command and args come from the vault base path plus hard-coded temporiki tokens. There is no user-controlled string in the command line, but argv-based spawn is used anyway for defense in depth: no shell interprets the arguments, so a basePath containing `;`, `$(...)`, quotes, or spaces cannot escape into a command injection.

**Why not keep the OS scripts as an opt-in for headless users?**

The headless-user persona is always also a CLI user; they run `temporiki palace-search` / `palace-kg-query` directly, which already trigger the lazy guard. No realistic persona needs a resident watcher that the lazy path does not already cover. Maintaining three cross-OS install scripts for a hypothetical persona was defensive over-engineering and kept the philosophical mismatch alive.

## Consequences

- `git clone` + `./.temporiki/hooks/obsidian-zero.sh` reproduces the full runtime. No residual state in `~/Library/LaunchAgents/`, `~/.config/systemd/user/`, or Task Scheduler.
- Tests (`tests/test_stale.py`) cover the guard's correctness under the copy-with-preserved-mtime case, corrupt manifest, and the common warm/cold states.
- The inline migration cleanup in `obsidian-zero.sh` is scheduled for removal in a later release once known clones have migrated.
