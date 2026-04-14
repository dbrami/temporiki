from __future__ import annotations

import datetime as dt
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
