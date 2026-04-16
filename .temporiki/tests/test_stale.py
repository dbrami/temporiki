from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

from temporiki_tools.stale import should_run_ingest


def _make_raw(root: Path) -> Path:
    raw = root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / ".gitkeep").write_text("", encoding="utf-8")
    return raw


def _write_manifest(root: Path, sources: dict[str, dict]) -> None:
    manifest = {
        "version": 1,
        "updated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "sources": sources,
    }
    (root / ".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


def test_empty_raw_returns_false(tmp_path: Path) -> None:
    _make_raw(tmp_path)
    assert should_run_ingest(tmp_path) is False


def test_missing_raw_returns_false(tmp_path: Path) -> None:
    assert should_run_ingest(tmp_path) is False


def test_new_file_without_manifest(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    (raw / "a.md").write_text("hello", encoding="utf-8")
    assert should_run_ingest(tmp_path) is True


def test_new_file_with_existing_manifest(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    (raw / "a.md").write_text("old", encoding="utf-8")
    _write_manifest(
        tmp_path,
        {"raw/a.md": {"sha256": "x", "last_seen": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()}},
    )
    (raw / "b.md").write_text("new", encoding="utf-8")
    assert should_run_ingest(tmp_path) is True


def test_preserved_mtime_cp_copy_new_file(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    (raw / "a.md").write_text("old", encoding="utf-8")
    _write_manifest(
        tmp_path,
        {"raw/a.md": {"sha256": "x", "last_seen": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()}},
    )

    new_file = raw / "b.md"
    new_file.write_text("content", encoding="utf-8")
    old_epoch = dt.datetime(2020, 1, 1, tzinfo=dt.UTC).timestamp()
    os.utime(new_file, (old_epoch, old_epoch))

    assert should_run_ingest(tmp_path) is True


def test_touched_file_with_advanced_mtime(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    a = raw / "a.md"
    a.write_text("old", encoding="utf-8")
    old_last_seen = dt.datetime(2024, 1, 1, tzinfo=dt.UTC).isoformat()
    _write_manifest(tmp_path, {"raw/a.md": {"sha256": "x", "last_seen": old_last_seen}})

    future_epoch = dt.datetime.now(dt.UTC).timestamp() + 10
    os.utime(a, (future_epoch, future_epoch))

    assert should_run_ingest(tmp_path) is True


def test_clean_state_returns_false(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    a = raw / "a.md"
    a.write_text("stable", encoding="utf-8")
    fresh_last_seen = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    _write_manifest(tmp_path, {"raw/a.md": {"sha256": "x", "last_seen": fresh_last_seen}})
    past_epoch = dt.datetime.now(dt.UTC).timestamp() - 3600
    os.utime(a, (past_epoch, past_epoch))

    assert should_run_ingest(tmp_path) is False


def test_gitkeep_is_ignored(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    (raw / "assets").mkdir()
    (raw / "assets" / ".gitkeep").write_text("", encoding="utf-8")
    _write_manifest(tmp_path, {})
    assert should_run_ingest(tmp_path) is False


def test_corrupt_manifest_treated_as_missing(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    (raw / "a.md").write_text("hello", encoding="utf-8")
    (tmp_path / ".manifest.json").write_text("{not: valid json", encoding="utf-8")
    assert should_run_ingest(tmp_path) is True
