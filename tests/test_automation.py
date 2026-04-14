from __future__ import annotations

from pathlib import Path

from memoriki_tools.automation import run_cycle


def test_run_cycle_triggers_mine_when_changes_exist(monkeypatch) -> None:
    monkeypatch.setattr("memoriki_tools.automation.ingest_delta", lambda root: [{"path": "raw/a.md"}])
    monkeypatch.setattr(
        "memoriki_tools.automation.auto_mine",
        lambda root, wing="raw", room="general": {"lite_indexed": 2, "chroma_indexed": 0, "chroma_active": False},
    )
    monkeypatch.setattr(
        "memoriki_tools.automation.lint_wiki",
        lambda root, autofix=False: {
            "missing_frontmatter": [],
            "invalid_frontmatter": [],
            "autofixed_frontmatter": [],
            "broken_links": [],
            "orphans": [],
        },
    )
    monkeypatch.setattr("memoriki_tools.automation.is_chroma_available", lambda: False)

    out = run_cycle(Path("."), run_lint=True, run_health=True)
    assert out["changed_count"] == 1
    assert out["mining"]["lite_indexed"] == 2
    assert out["health"]["chroma_available"] is False


def test_run_cycle_skips_mine_when_no_changes(monkeypatch) -> None:
    monkeypatch.setattr("memoriki_tools.automation.ingest_delta", lambda root: [])
    monkeypatch.setattr(
        "memoriki_tools.automation.auto_mine",
        lambda root, wing="raw", room="general": {"lite_indexed": 999},
    )
    monkeypatch.setattr(
        "memoriki_tools.automation.lint_wiki",
        lambda root, autofix=False: {
            "missing_frontmatter": [],
            "invalid_frontmatter": [],
            "autofixed_frontmatter": [],
            "broken_links": [],
            "orphans": [],
        },
    )
    monkeypatch.setattr("memoriki_tools.automation.is_chroma_available", lambda: True)

    out = run_cycle(Path("."), run_lint=False, run_health=False)
    assert out["changed_count"] == 0
    assert out["mining"] is None
    assert out["lint"] is None
    assert out["health"] is None
