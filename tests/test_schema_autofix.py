from __future__ import annotations

from pathlib import Path

from memoriki_tools.ops import lint_wiki


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_lint_autofix_inserts_frontmatter_and_clears_missing(tmp_path: Path) -> None:
    write(tmp_path / "wiki" / "concepts" / "missing.md", "Plain content with no frontmatter\n")
    write(tmp_path / "wiki" / "index.md", "# Index\n")
    write(tmp_path / "wiki" / "log.md", "# Log\n")

    before = lint_wiki(tmp_path)
    assert "wiki/concepts/missing.md" in before["missing_frontmatter"]

    after = lint_wiki(tmp_path, autofix=True)
    assert "wiki/concepts/missing.md" not in after["missing_frontmatter"]
    assert "wiki/concepts/missing.md" in after["autofixed_frontmatter"]

    content = (tmp_path / "wiki" / "concepts" / "missing.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "title: missing" in content
