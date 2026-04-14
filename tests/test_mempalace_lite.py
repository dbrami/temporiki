from __future__ import annotations

from pathlib import Path

from memoriki_tools.mempalace_lite import (
    init_lite,
    kg_query_decisions,
    mine_raw,
    search_lite,
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_mine_and_search_lite_returns_ranked_hits(tmp_path: Path) -> None:
    write(tmp_path / "raw" / "a.md", "GraphQL auth decision notes for billing service")
    write(tmp_path / "raw" / "b.md", "Completely unrelated gardening content")

    init_lite(tmp_path)
    added = mine_raw(tmp_path)
    assert added >= 2

    hits = search_lite(tmp_path, query="GraphQL auth", n_results=3)
    assert len(hits) >= 1
    assert "graphql" in hits[0]["text"].lower()


def test_kg_query_decisions_filters_by_validity_window(tmp_path: Path) -> None:
    write(
        tmp_path / "wiki" / "decisions" / "auth.md",
        """---
 title: Decision on Auth
 date: 2026-01-10
 validity_until: 2026-12-31
 context: auth provider selection
 alternatives_considered: [A, B]
 why_this_choice: stable sdk
 event_clock: switched after outage
 ---
""",
    )
    write(
        tmp_path / "wiki" / "decisions" / "legacy.md",
        """---
 title: Decision on Legacy CDN
 date: 2024-01-10
 validity_until: 2024-12-31
 context: old infra
 alternatives_considered: [X]
 why_this_choice: migration pending
 event_clock: superseded
 ---
""",
    )

    active = kg_query_decisions(tmp_path, as_of="2026-04-13")
    titles = {d["title"] for d in active}
    assert "Decision on Auth" in titles
    assert "Decision on Legacy CDN" not in titles
