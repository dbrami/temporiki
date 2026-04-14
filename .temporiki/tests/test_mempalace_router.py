from __future__ import annotations

from pathlib import Path

from temporiki_tools.mempalace_router import auto_mine, auto_search


def test_auto_search_prefers_kg_for_decision_queries(monkeypatch) -> None:
    monkeypatch.setattr(
        "temporiki_tools.mempalace_router.kg_query_decisions",
        lambda root, topic=None, as_of=None: [{"title": "Decision on Auth"}],
    )
    monkeypatch.setattr(
        "temporiki_tools.mempalace_router.search_chroma",
        lambda *args, **kwargs: [{"text": "from chroma"}],
    )
    monkeypatch.setattr(
        "temporiki_tools.mempalace_router.search_lite",
        lambda *args, **kwargs: [{"text": "from sqlite"}],
    )

    out = auto_search(Path("."), "what decisions are active?", as_of="2026-04-13")
    assert out["strategy"] == "kg"
    assert out["results"][0]["title"] == "Decision on Auth"


def test_auto_search_falls_back_to_lite_when_chroma_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("temporiki_tools.mempalace_router.is_chroma_available", lambda: False)
    monkeypatch.setattr(
        "temporiki_tools.mempalace_router.search_lite",
        lambda *args, **kwargs: [{"text": "sqlite-hit"}],
    )

    out = auto_search(Path("."), "auth architecture")
    assert out["strategy"] == "lite"
    assert out["results"][0]["text"] == "sqlite-hit"


def test_auto_mine_indexes_lite_and_chroma_when_available(monkeypatch) -> None:
    monkeypatch.setattr("temporiki_tools.mempalace_router.is_chroma_available", lambda: True)
    monkeypatch.setattr("temporiki_tools.mempalace_router.mine_raw", lambda *args, **kwargs: 3)
    monkeypatch.setattr("temporiki_tools.mempalace_router.mine_chroma", lambda *args, **kwargs: 2)

    out = auto_mine(Path("."))
    assert out["lite_indexed"] == 3
    assert out["chroma_indexed"] == 2
