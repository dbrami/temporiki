from __future__ import annotations

from pathlib import Path

from temporiki_tools.automation import run_cycle


def test_run_cycle_triggers_mine_when_changes_exist(monkeypatch) -> None:
    monkeypatch.setattr("temporiki_tools.automation.ingest_delta", lambda root: [{"path": "raw/a.md"}])
    monkeypatch.setattr(
        "temporiki_tools.automation.archive_webclips",
        lambda root, changed: {"changed": changed, "moved": [], "rewritten_pages": []},
    )
    monkeypatch.setattr(
        "temporiki_tools.automation.auto_mine",
        lambda root, wing="raw", room="general": {"lite_indexed": 2, "chroma_indexed": 0, "chroma_active": False},
    )
    monkeypatch.setattr(
        "temporiki_tools.automation.lint_wiki",
        lambda root, autofix=False: {
            "missing_frontmatter": [],
            "invalid_frontmatter": [],
            "autofixed_frontmatter": [],
            "broken_links": [],
            "orphans": [],
        },
    )
    monkeypatch.setattr("temporiki_tools.automation.is_chroma_available", lambda: False)

    out = run_cycle(Path("."), run_lint=True, run_health=True)
    assert out["changed_count"] == 1
    assert out["mining"]["lite_indexed"] == 2
    assert out["health"]["chroma_available"] is False
    assert out["archive"]["moved"] == []


def test_run_cycle_skips_mine_when_no_changes(monkeypatch) -> None:
    monkeypatch.setattr("temporiki_tools.automation.ingest_delta", lambda root: [])
    monkeypatch.setattr(
        "temporiki_tools.automation.archive_webclips",
        lambda root, changed: {"changed": changed, "moved": [], "rewritten_pages": []},
    )
    monkeypatch.setattr(
        "temporiki_tools.automation.auto_mine",
        lambda root, wing="raw", room="general": {"lite_indexed": 999},
    )
    monkeypatch.setattr(
        "temporiki_tools.automation.lint_wiki",
        lambda root, autofix=False: {
            "missing_frontmatter": [],
            "invalid_frontmatter": [],
            "autofixed_frontmatter": [],
            "broken_links": [],
            "orphans": [],
        },
    )
    monkeypatch.setattr("temporiki_tools.automation.is_chroma_available", lambda: True)

    out = run_cycle(Path("."), run_lint=False, run_health=False)
    assert out["changed_count"] == 0
    assert out["mining"] is None
    assert out["lint"] is None
    assert out["health"] is None
    assert out["archive"]["moved"] == []


def test_run_cycle_uses_archived_changed_paths(monkeypatch) -> None:
    monkeypatch.setattr(
        "temporiki_tools.automation.ingest_delta",
        lambda root: [{"path": "raw/webclips/clip.md", "sha256": "abc", "reason": "new"}],
    )
    monkeypatch.setattr(
        "temporiki_tools.automation.archive_webclips",
        lambda root, changed: {
            "changed": [{"path": "raw/webclips/_archive/2026-04/clip.md", "sha256": "abc", "reason": "archived-after-ingest"}],
            "moved": [{"from": "raw/webclips/clip.md", "to": "raw/webclips/_archive/2026-04/clip.md"}],
            "rewritten_pages": ["wiki/sources/clip.md"],
        },
    )
    monkeypatch.setattr(
        "temporiki_tools.automation.auto_mine",
        lambda root, wing="raw", room="general": {"lite_indexed": 1, "chroma_indexed": 0, "chroma_active": False},
    )
    monkeypatch.setattr("temporiki_tools.automation.lint_wiki", lambda root, autofix=False: None)
    monkeypatch.setattr("temporiki_tools.automation.is_chroma_available", lambda: False)

    out = run_cycle(Path("."), run_lint=False, run_health=False)
    assert out["changed_count"] == 1
    assert out["changed"][0]["path"].startswith("raw/webclips/_archive/")
    assert out["archive"]["moved"][0]["from"] == "raw/webclips/clip.md"
