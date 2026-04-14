from __future__ import annotations

import datetime as dt
import hashlib
import sqlite3
from pathlib import Path
from typing import Any

from memoriki_tools.schema import split_frontmatter


def _db_path(root: Path) -> Path:
    return root.resolve() / ".memplite" / "palace.sqlite3"


def init_lite(root: Path) -> Path:
    db = _db_path(root)
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    try:
        conn.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS drawers (
              id TEXT PRIMARY KEY,
              text TEXT NOT NULL,
              wing TEXT NOT NULL,
              room TEXT NOT NULL,
              source_file TEXT NOT NULL,
              created_at TEXT NOT NULL
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS drawers_fts USING fts5(
              id UNINDEXED,
              text,
              wing,
              room,
              source_file,
              tokenize='unicode61'
            );
            """
        )
        conn.commit()
    finally:
        conn.close()
    return db


def _drawer_id(source_file: str, text: str, wing: str, room: str) -> str:
    digest = hashlib.sha256(f"{source_file}|{wing}|{room}|{text}".encode("utf-8")).hexdigest()
    return digest[:20]


def _chunk_text(text: str, max_chars: int = 1200) -> list[str]:
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf = ""
    for part in parts:
        if len(buf) + len(part) + 2 <= max_chars:
            buf = f"{buf}\n\n{part}".strip()
        else:
            if buf:
                chunks.append(buf)
            if len(part) <= max_chars:
                buf = part
            else:
                for i in range(0, len(part), max_chars):
                    chunks.append(part[i : i + max_chars])
                buf = ""
    if buf:
        chunks.append(buf)
    return chunks or [text[:max_chars]]


def mine_raw(root: Path, wing: str = "raw", room: str = "general") -> int:
    root = root.resolve()
    init_lite(root)
    db = _db_path(root)

    files = sorted(
        p for p in (root / "raw").rglob("*.md") if p.is_file() and p.name != ".gitkeep"
    )

    now = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    added = 0
    conn = sqlite3.connect(db)
    try:
        for path in files:
            rel = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
            for chunk in _chunk_text(text):
                drawer_id = _drawer_id(rel, chunk, wing, room)
                conn.execute(
                    """
                    INSERT OR REPLACE INTO drawers(id, text, wing, room, source_file, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (drawer_id, chunk, wing, room, rel, now),
                )
                conn.execute(
                    """
                    INSERT OR REPLACE INTO drawers_fts(id, text, wing, room, source_file)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (drawer_id, chunk, wing, room, rel),
                )
                added += 1
        conn.commit()
    finally:
        conn.close()

    return added


def search_lite(
    root: Path,
    query: str,
    wing: str | None = None,
    room: str | None = None,
    n_results: int = 5,
) -> list[dict[str, Any]]:
    root = root.resolve()
    db = _db_path(root)
    if not db.exists():
        return []

    filters: list[str] = ["drawers_fts MATCH ?"]
    params: list[Any] = [query]
    if wing:
        filters.append("wing = ?")
        params.append(wing)
    if room:
        filters.append("room = ?")
        params.append(room)

    where_sql = " AND ".join(filters)
    sql = f"""
      SELECT id, text, wing, room, source_file, bm25(drawers_fts) AS score
      FROM drawers_fts
      WHERE {where_sql}
      ORDER BY score ASC
      LIMIT ?
    """
    params.append(max(1, n_results))

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "id": row["id"],
                "text": row["text"],
                "wing": row["wing"],
                "room": row["room"],
                "source_file": row["source_file"],
                "score": float(row["score"]),
            }
        )
    return out


def _parse_frontmatter(text: str) -> dict[str, Any]:
    fm, _ = split_frontmatter(text)
    return fm


def _date_or_none(s: str | None) -> dt.date | None:
    if not s:
        return None
    s = str(s).strip().lower()
    if s in {"", "indefinite", "none", "null"}:
        return None
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def kg_query_decisions(root: Path, topic: str | None = None, as_of: str | None = None) -> list[dict[str, str]]:
    root = root.resolve()
    as_of_date = dt.date.fromisoformat(as_of) if as_of else dt.date.today()
    decision_dir = root / "wiki" / "decisions"
    if not decision_dir.exists():
        return []

    out: list[dict[str, str]] = []
    for path in sorted(decision_dir.glob("*.md")):
        fm = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if not fm:
            continue

        start = _date_or_none(fm.get("date"))
        end = _date_or_none(fm.get("validity_until"))
        if start and start > as_of_date:
            continue
        if end and end < as_of_date:
            continue

        title = fm.get("title", path.stem)
        context = fm.get("context", "")
        if topic:
            needle = topic.lower()
            if needle not in title.lower() and needle not in context.lower():
                continue

        out.append(
            {
                "title": title,
                "date": fm.get("date", ""),
                "validity_until": fm.get("validity_until", "indefinite"),
                "context": context,
                "why_this_choice": fm.get("why_this_choice", ""),
                "event_clock": fm.get("event_clock", ""),
                "source": path.relative_to(root).as_posix(),
            }
        )
    return out
