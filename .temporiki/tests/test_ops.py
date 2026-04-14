from __future__ import annotations

import json
from pathlib import Path

from temporiki_tools.ops import ingest_delta, lint_wiki, save_query_result


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_ingest_delta_tracks_only_new_or_changed_sources(tmp_path: Path) -> None:
    write(tmp_path / "raw" / "a.md", "alpha")
    write(tmp_path / "raw" / "b.md", "beta")
    write(tmp_path / "wiki" / "index.md", "# Index\n")
    write(tmp_path / "wiki" / "log.md", "# Log\n")

    first = ingest_delta(tmp_path)
    assert {item["path"] for item in first} == {"raw/a.md", "raw/b.md"}

    second = ingest_delta(tmp_path)
    assert second == []

    write(tmp_path / "raw" / "a.md", "alpha v2")
    third = ingest_delta(tmp_path)
    assert [item["path"] for item in third] == ["raw/a.md"]

    manifest = json.loads((tmp_path / ".manifest.json").read_text(encoding="utf-8"))
    assert "raw/a.md" in manifest["sources"]


def test_ingest_delta_relocates_clippings_into_raw_webclips(tmp_path: Path) -> None:
    write(tmp_path / "Clippings" / "clip.md", "first")
    write(tmp_path / "raw" / "webclips" / "clip.md", "existing")
    write(tmp_path / "wiki" / "index.md", "# Index\n")
    write(tmp_path / "wiki" / "log.md", "# Log\n")

    changed = ingest_delta(tmp_path)
    assert {item["path"] for item in changed} == {"raw/webclips/clip-1.md", "raw/webclips/clip.md"}

    assert not (tmp_path / "Clippings").exists()
    assert (tmp_path / "raw" / "webclips" / "clip.md").read_text(encoding="utf-8") == "existing"
    assert (tmp_path / "raw" / "webclips" / "clip-1.md").read_text(encoding="utf-8") == "first"


def test_lint_wiki_reports_orphans_and_missing_frontmatter(tmp_path: Path) -> None:
    write(
        tmp_path / "wiki" / "concepts" / "a.md",
        "---\ntitle: A\n---\nLinks [[B]].\n",
    )
    write(tmp_path / "wiki" / "concepts" / "b.md", "No frontmatter\n")
    write(tmp_path / "wiki" / "index.md", "# Index\n")
    write(tmp_path / "wiki" / "log.md", "# Log\n")

    report = lint_wiki(tmp_path)
    assert "wiki/concepts/b.md" in report["missing_frontmatter"]
    assert "B" in report["broken_links"]
    assert "wiki/concepts/a.md" in report["orphans"]


def test_save_query_result_creates_query_page_and_updates_index_and_log(tmp_path: Path) -> None:
    write(tmp_path / "wiki" / "index.md", "# Index\n")
    write(tmp_path / "wiki" / "log.md", "# Log\n")

    page = save_query_result(
        root=tmp_path,
        question="What decisions exist?",
        answer="- Decision A",
        tags=["query", "decisions"],
    )

    assert page.exists()
    content = page.read_text(encoding="utf-8")
    assert "What decisions exist?" in content
    assert "- Decision A" in content

    index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
    assert page.name in index

    log = (tmp_path / "wiki" / "log.md").read_text(encoding="utf-8")
    assert "query-save" in log
