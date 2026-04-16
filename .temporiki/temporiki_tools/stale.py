from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


def _load_sources(root: Path) -> dict[str, dict] | None:
    manifest_path = root / ".manifest.json"
    if not manifest_path.exists():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    sources = data.get("sources")
    if not isinstance(sources, dict):
        return {}
    return sources


def _parse_iso_ts(value: object) -> float:
    if not isinstance(value, str) or not value:
        return 0.0
    try:
        return dt.datetime.fromisoformat(value).timestamp()
    except ValueError:
        return 0.0


def should_run_ingest(root: Path) -> bool:
    """Return True if raw/ has changed since the last ingest sweep.

    Compares each raw file against its own per-source `last_seen` in
    `.manifest.json`. A file that is not in the manifest at all is treated as
    new. This is correct even when a file is copied in with `cp -p` (preserved
    mtime): unknown paths always trigger, so new content is never missed.
    """

    root = root.resolve()
    raw_dir = root / "raw"
    if not raw_dir.is_dir():
        return False

    sources = _load_sources(root)
    if sources is None:
        for path in raw_dir.rglob("*"):
            if path.is_file() and path.name != ".gitkeep":
                return True
        return False

    for path in raw_dir.rglob("*"):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        rel = path.relative_to(root).as_posix()
        entry = sources.get(rel)
        if entry is None:
            return True
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        last_seen = _parse_iso_ts(entry.get("last_seen"))
        if mtime > last_seen:
            return True
    return False
