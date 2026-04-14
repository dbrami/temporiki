from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from memoriki_tools.schema import (
    dump_frontmatter,
    minimal_frontmatter_for,
    split_frontmatter,
    today_iso,
    validate_frontmatter,
)

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def _today() -> str:
    return dt.date.today().isoformat()


def _now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "updated_at": _now(), "sources": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_manifest(path: Path, data: dict[str, Any]) -> None:
    data["updated_at"] = _now()
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _append_log(root: Path, operation: str, description: str) -> None:
    log_path = root / "wiki" / "log.md"
    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("# Log\n", encoding="utf-8")
    entry = f"\n## [{_today()}] {operation} | {description}\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def ingest_delta(root: Path) -> list[dict[str, str]]:
    root = root.resolve()
    raw_dir = root / "raw"
    wiki_dir = root / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)

    index = wiki_dir / "index.md"
    if not index.exists():
        index.write_text("# Index\n", encoding="utf-8")

    manifest_path = root / ".manifest.json"
    manifest = _load_manifest(manifest_path)
    sources: dict[str, dict[str, str]] = manifest.setdefault("sources", {})

    changed: list[dict[str, str]] = []
    for path in sorted(p for p in raw_dir.rglob("*") if p.is_file() and p.name != ".gitkeep"):
        rel = _rel(path, root)
        sha = _sha256(path)
        current = sources.get(rel)
        if current is None or current.get("sha256") != sha:
            reason = "new" if current is None else "changed"
            changed.append({"path": rel, "sha256": sha, "reason": reason})
        sources[rel] = {
            "sha256": sha,
            "last_seen": _now(),
            "status": (
                "pending_agent_ingest"
                if any(c["path"] == rel for c in changed)
                else current.get("status", "up_to_date")
                if current
                else "pending_agent_ingest"
            ),
        }

    _write_manifest(manifest_path, manifest)

    if changed:
        _append_log(root, "ingest-delta", f"{len(changed)} source(s) changed")

    return changed


def _autofix_frontmatter(path: Path, root: Path, body: str) -> None:
    rel = _rel(path, root)
    fixed = minimal_frontmatter_for(path, rel_source=rel)
    rendered = dump_frontmatter(fixed)
    normalized_body = body.lstrip("\n")
    path.write_text(rendered + "\n" + normalized_body, encoding="utf-8")


def lint_wiki(root: Path, autofix: bool = False) -> dict[str, list[str]]:
    root = root.resolve()
    wiki_root = root / "wiki"

    pages = [p for p in wiki_root.rglob("*.md") if p.name not in {"index.md", "log.md"}]

    by_title: dict[str, str] = {}
    missing_frontmatter: list[str] = []
    invalid_frontmatter: list[str] = []
    autofixed_frontmatter: list[str] = []
    links_by_page: dict[str, set[str]] = {}
    inbound: dict[str, int] = {}

    for page in pages:
        rel = _rel(page, root)
        text = page.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)

        if not fm:
            missing_frontmatter.append(rel)
            if autofix:
                _autofix_frontmatter(page, root, text)
                autofixed_frontmatter.append(rel)
                text = page.read_text(encoding="utf-8")
                fm, body = split_frontmatter(text)

        if fm:
            errors = validate_frontmatter(fm)
            if errors:
                invalid_frontmatter.append(rel)
                if autofix:
                    merged = minimal_frontmatter_for(page, rel_source=rel)
                    merged.update({k: v for k, v in fm.items() if v not in (None, "")})
                    merged["updated"] = today_iso()
                    page.write_text(dump_frontmatter(merged) + "\n" + body.lstrip("\n"), encoding="utf-8")
                    autofixed_frontmatter.append(rel)
                    text = page.read_text(encoding="utf-8")
                    fm, body = split_frontmatter(text)
                    if not validate_frontmatter(fm):
                        invalid_frontmatter = [x for x in invalid_frontmatter if x != rel]

            if "title" in fm:
                by_title[str(fm["title"])] = rel

        links = set(WIKILINK_RE.findall(body))
        links_by_page[rel] = links
        inbound.setdefault(rel, 0)

    broken: set[str] = set()
    for _, links in links_by_page.items():
        for target in links:
            resolved = by_title.get(target)
            if resolved is None:
                broken.add(target)
            else:
                inbound[resolved] = inbound.get(resolved, 0) + 1

    orphans = sorted(
        [
            page
            for page, count in inbound.items()
            if count == 0
            and not page.startswith("wiki/_templates/")
            and not page.startswith("wiki/meta/")
        ]
    )

    return {
        "missing_frontmatter": sorted(set(missing_frontmatter) - set(autofixed_frontmatter)),
        "invalid_frontmatter": sorted(set(invalid_frontmatter)),
        "autofixed_frontmatter": sorted(set(autofixed_frontmatter)),
        "broken_links": sorted(broken),
        "orphans": orphans,
    }


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:64] or "query"


def save_query_result(
    root: Path,
    question: str,
    answer: str,
    tags: list[str] | None = None,
) -> Path:
    root = root.resolve()
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)

    queries = wiki / "queries"
    queries.mkdir(parents=True, exist_ok=True)

    index_path = wiki / "index.md"
    if not index_path.exists():
        index_path.write_text("# Index\n", encoding="utf-8")

    name = f"{_today()}-{_slugify(question)}.md"
    out = queries / name

    tags = tags or ["query"]
    frontmatter = {
        "title": question,
        "type": "query",
        "tags": tags,
        "sources": [],
        "related": [],
        "created": _today(),
        "updated": _today(),
    }
    body = f"## Question\n\n{question}\n\n## Answer\n\n{answer}\n"
    out.write_text(dump_frontmatter(frontmatter) + "\n" + body, encoding="utf-8")

    rel = _rel(out, root)
    with index_path.open("a", encoding="utf-8") as f:
        f.write(f"\n- [[{rel}]] - saved query\n")

    _append_log(root, "query-save", question)
    return out
