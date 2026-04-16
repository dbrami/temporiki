from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


def _manifest_updated_at(root: Path) -> float:
    manifest_path = root / ".manifest.json"
    if not manifest_path.exists():
        return 0.0
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        ts = str(data.get("updated_at", "") or "")
        if not ts:
            return 0.0
        return dt.datetime.fromisoformat(ts).timestamp()
    except Exception:
        return 0.0


def should_run_ingest(root: Path) -> bool:
    root = root.resolve()
    raw_dir = root / "raw"
    if not raw_dir.is_dir():
        return False

    manifest_ts = _manifest_updated_at(root)
    if manifest_ts == 0.0:
        for path in raw_dir.rglob("*"):
            if path.is_file() and path.name != ".gitkeep":
                return True
        return False

    for path in raw_dir.rglob("*"):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        try:
            if path.stat().st_mtime > manifest_ts:
                return True
        except OSError:
            continue
    return False
