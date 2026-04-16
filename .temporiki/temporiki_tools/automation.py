from __future__ import annotations

import datetime as dt
import json
import time
from pathlib import Path
from typing import Any

from temporiki_tools.mempalace_chroma import is_chroma_available
from temporiki_tools.mempalace_router import auto_mine
from temporiki_tools.ops import archive_webclips, ingest_delta, lint_wiki


def run_cycle(
    root: Path,
    run_lint: bool,
    run_health: bool,
    lint_autofix: bool = True,
    wing: str = "raw",
    room: str = "general",
) -> dict[str, Any]:
    root = root.resolve()
    changed = ingest_delta(root)
    archive = archive_webclips(root, changed)
    changed_effective = archive["changed"]

    mining = None
    if changed_effective:
        mining = auto_mine(root=root, wing=wing, room=room)

    lint = lint_wiki(root, autofix=lint_autofix) if run_lint else None

    health = None
    if run_health:
        health = {
            "chroma_available": is_chroma_available(),
        }

    return {
        "timestamp": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "changed_count": len(changed_effective),
        "changed": changed_effective,
        "archive": archive,
        "mining": mining,
        "lint": lint,
        "health": health,
    }


def run_event_cycle(
    root: Path,
    lint_every_seconds: int = 300,
    health_every_seconds: int = 120,
    lint_autofix: bool = True,
) -> dict[str, Any]:
    root = root.resolve()
    state_dir = root / ".memplite"
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / "event-state.json"

    now = time.time()
    state: dict[str, float] = {"last_lint_at": 0.0, "last_health_at": 0.0}
    if state_path.exists():
        try:
            loaded = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                state["last_lint_at"] = float(loaded.get("last_lint_at", 0.0) or 0.0)
                state["last_health_at"] = float(loaded.get("last_health_at", 0.0) or 0.0)
        except Exception:
            state = {"last_lint_at": 0.0, "last_health_at": 0.0}

    run_lint_now = (now - state["last_lint_at"]) >= max(1, lint_every_seconds)
    run_health_now = (now - state["last_health_at"]) >= max(1, health_every_seconds)

    report = run_cycle(
        root=root,
        run_lint=run_lint_now,
        run_health=run_health_now,
        lint_autofix=lint_autofix,
    )

    if run_lint_now:
        state["last_lint_at"] = now
    if run_health_now:
        state["last_health_at"] = now
    state_path.write_text(
        json.dumps(state, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
