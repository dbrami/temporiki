from __future__ import annotations

import json
from pathlib import Path

from temporiki_tools.cli import palace_search


def test_palace_search_auto_saves_high_confidence(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "temporiki_tools.cli.auto_search",
        lambda **kwargs: {
            "strategy": "hybrid",
            "results": [
                {
                    "text": "Use short-lived auth tokens.",
                    "source_file": "raw/webclips/auth.md",
                    "confidence": 0.94,
                    "provenance": "both",
                }
            ],
        },
    )

    def _fake_save(root: Path, question: str, answer: str, tags: list[str] | None = None) -> Path:
        out = root / "wiki" / "queries" / "auto.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(answer, encoding="utf-8")
        return out

    monkeypatch.setattr("temporiki_tools.cli.save_query_result", _fake_save)

    captured: list[str] = []
    monkeypatch.setattr("typer.echo", lambda msg: captured.append(str(msg)))
    palace_search("auth policy", root=tmp_path, auto_save=True, auto_save_min_confidence=0.9)

    out = json.loads(captured[-1])
    assert out["auto_saved"] is True
    assert out["saved_query_path"] == "wiki/queries/auto.md"


def test_palace_search_skips_auto_save_below_threshold(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "temporiki_tools.cli.auto_search",
        lambda **kwargs: {
            "strategy": "lite",
            "results": [
                {
                    "text": "Low-confidence retrieval.",
                    "source_file": "raw/webclips/x.md",
                    "confidence": 0.41,
                    "provenance": "lite",
                }
            ],
        },
    )

    called = {"saved": False}

    def _fake_save(root: Path, question: str, answer: str, tags: list[str] | None = None) -> Path:
        called["saved"] = True
        return root / "wiki" / "queries" / "never.md"

    monkeypatch.setattr("temporiki_tools.cli.save_query_result", _fake_save)

    captured: list[str] = []
    monkeypatch.setattr("typer.echo", lambda msg: captured.append(str(msg)))
    palace_search("weak query", root=tmp_path, auto_save=True, auto_save_min_confidence=0.9)

    out = json.loads(captured[-1])
    assert out["auto_saved"] is False
    assert called["saved"] is False

