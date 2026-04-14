from __future__ import annotations

from pathlib import Path

from temporiki_tools.mempalace_router import auto_search


def test_auto_search_hybrid_merges_chroma_and_lite(monkeypatch) -> None:
    monkeypatch.setattr("temporiki_tools.mempalace_router.is_chroma_available", lambda: True)
    monkeypatch.setattr("temporiki_tools.mempalace_router.kg_query_decisions", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        "temporiki_tools.mempalace_router.search_chroma",
        lambda **kwargs: [
            {
                "text": "Auth decision was to use OIDC",
                "wing": "raw",
                "room": "general",
                "source_file": "raw/a.md",
                "distance": 0.2,
                "similarity": 0.8,
            }
        ],
    )
    monkeypatch.setattr(
        "temporiki_tools.mempalace_router.search_lite",
        lambda **kwargs: [
            {
                "id": "x1",
                "text": "Auth decision was to use OIDC",
                "wing": "raw",
                "room": "general",
                "source_file": "raw/a.md",
                "score": -2.3,
            },
            {
                "id": "x2",
                "text": "Billing uses monthly close",
                "wing": "raw",
                "room": "general",
                "source_file": "raw/b.md",
                "score": -1.2,
            },
        ],
    )

    out = auto_search(Path("."), "auth decision")
    assert out["strategy"] == "hybrid"
    assert len(out["results"]) >= 2
    assert "confidence" in out["results"][0]
    assert out["results"][0]["provenance"] in {"both", "chroma", "lite"}
