from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from temporiki_tools.mempalace_lite import _chunk_text


def _try_import_chromadb():
    try:
        import chromadb  # type: ignore

        return chromadb
    except Exception:
        return None


def _chroma_config() -> tuple[str, str]:
    base_url = os.environ.get("MEMORIKI_CHROMA_URL", "http://127.0.0.1:8000")
    collection = os.environ.get("TEMPORIKI_CHROMA_COLLECTION", "temporiki_drawers")
    return base_url, collection


def _client():
    chromadb = _try_import_chromadb()
    if chromadb is None:
        return None

    base_url, _ = _chroma_config()
    parsed = urlparse(base_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    ssl = parsed.scheme == "https"
    return chromadb.HttpClient(host=host, port=port, ssl=ssl)


def is_chroma_available() -> bool:
    c = _client()
    if c is None:
        return False
    try:
        c.heartbeat()
        return True
    except Exception:
        return False


def _collection(create: bool = True):
    c = _client()
    if c is None:
        return None
    _, name = _chroma_config()
    try:
        if create:
            return c.get_or_create_collection(name=name)
        return c.get_collection(name=name)
    except Exception:
        return None


def _iter_raw_chunks(root: Path, wing: str, room: str) -> list[tuple[str, str, dict[str, str]]]:
    rows: list[tuple[str, str, dict[str, str]]] = []
    for path in sorted((root / "raw").rglob("*.md")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for chunk in _chunk_text(text):
            digest = hashlib.sha256(f"{rel}|{wing}|{room}|{chunk}".encode("utf-8")).hexdigest()[:20]
            rows.append(
                (
                    digest,
                    chunk,
                    {"wing": wing, "room": room, "source_file": rel},
                )
            )
    return rows


def mine_chroma(root: Path, wing: str = "raw", room: str = "general") -> int:
    root = root.resolve()
    col = _collection(create=True)
    if col is None:
        return 0

    rows = _iter_raw_chunks(root, wing=wing, room=room)
    if not rows:
        return 0

    batch_size = 64
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        ids = [r[0] for r in batch]
        docs = [r[1] for r in batch]
        metas = [r[2] for r in batch]
        col.upsert(ids=ids, documents=docs, metadatas=metas)

    return len(rows)


def search_chroma(
    query: str,
    wing: str | None = None,
    room: str | None = None,
    n_results: int = 5,
) -> list[dict[str, Any]]:
    col = _collection(create=False)
    if col is None:
        return []

    where: dict[str, str] | None = None
    if wing and room:
        where = {"$and": [{"wing": wing}, {"room": room}]}
    elif wing:
        where = {"wing": wing}
    elif room:
        where = {"room": room}

    try:
        kwargs: dict[str, Any] = {
            "query_texts": [query],
            "n_results": max(1, n_results),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where
        res = col.query(**kwargs)
    except Exception:
        return []

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    out: list[dict[str, Any]] = []
    for doc, meta, dist in zip(docs, metas, dists):
        meta = meta or {}
        out.append(
            {
                "text": doc,
                "wing": meta.get("wing", ""),
                "room": meta.get("room", ""),
                "source_file": meta.get("source_file", ""),
                "distance": round(float(dist), 4),
                "similarity": round(max(0.0, 1 - float(dist)), 4),
            }
        )
    return out
