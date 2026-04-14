from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

from temporiki_tools.mempalace_chroma import is_chroma_available, mine_chroma, search_chroma
from temporiki_tools.mempalace_lite import kg_query_decisions, mine_raw, search_lite

_DECISION_HINT_RE = re.compile(
    r"\b(decision|decisions|precedent|why|rationale|validity|as[- ]of|event clock)\b",
    re.IGNORECASE,
)


def _is_decision_intent(query: str) -> bool:
    return bool(_DECISION_HINT_RE.search(query))


def _rrf(rank: int, k: int = 60) -> float:
    return 1.0 / (k + rank)


def _hit_key(hit: dict[str, Any]) -> str:
    source = str(hit.get("source_file", ""))
    text = str(hit.get("text", ""))[:180]
    return f"{source}|{text}"


def _normalize_chroma_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, h in enumerate(hits, start=1):
        out.append(
            {
                "text": h.get("text", ""),
                "wing": h.get("wing", ""),
                "room": h.get("room", ""),
                "source_file": h.get("source_file", ""),
                "chroma_rank": i,
                "chroma_similarity": float(h.get("similarity", 0.0)),
                "lite_rank": None,
            }
        )
    return out


def _normalize_lite_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, h in enumerate(hits, start=1):
        out.append(
            {
                "text": h.get("text", ""),
                "wing": h.get("wing", ""),
                "room": h.get("room", ""),
                "source_file": h.get("source_file", ""),
                "chroma_rank": None,
                "chroma_similarity": None,
                "lite_rank": i,
            }
        )
    return out


def _merge_and_score(chroma_hits: list[dict[str, Any]], lite_hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}

    for h in _normalize_chroma_hits(chroma_hits):
        key = _hit_key(h)
        merged[key] = h

    for h in _normalize_lite_hits(lite_hits):
        key = _hit_key(h)
        if key not in merged:
            merged[key] = h
        else:
            merged[key]["lite_rank"] = h["lite_rank"]

    scored: list[dict[str, Any]] = []
    for v in merged.values():
        score = 0.0
        if v["chroma_rank"] is not None:
            score += 0.55 * _rrf(int(v["chroma_rank"]))
            score += 0.25 * max(0.0, min(1.0, float(v.get("chroma_similarity") or 0.0)))
        if v["lite_rank"] is not None:
            score += 0.45 * _rrf(int(v["lite_rank"]))
        if v.get("source_file"):
            score += 0.05

        # Saturating confidence score to [0, 1]
        confidence = 1 - math.exp(-8.0 * score)

        if v["chroma_rank"] and v["lite_rank"]:
            provenance = "both"
        elif v["chroma_rank"]:
            provenance = "chroma"
        else:
            provenance = "lite"

        scored.append(
            {
                "text": v["text"],
                "wing": v.get("wing", ""),
                "room": v.get("room", ""),
                "source_file": v.get("source_file", ""),
                "provenance": provenance,
                "confidence": round(float(confidence), 4),
                "citation": {
                    "source_file": v.get("source_file", ""),
                    "why": (
                        "cross-store agreement" if provenance == "both" else f"single-store: {provenance}"
                    ),
                },
            }
        )

    scored.sort(key=lambda x: x["confidence"], reverse=True)
    return scored


def auto_mine(root: Path, wing: str = "raw", room: str = "general") -> dict[str, Any]:
    root = root.resolve()
    lite_count = mine_raw(root, wing=wing, room=room)

    chroma_count = 0
    chroma_active = is_chroma_available()
    if chroma_active:
        chroma_count = mine_chroma(root, wing=wing, room=room)

    return {
        "lite_indexed": lite_count,
        "chroma_indexed": chroma_count,
        "chroma_active": chroma_active,
    }


def auto_search(
    root: Path,
    query: str,
    wing: str | None = None,
    room: str | None = None,
    n_results: int = 5,
    as_of: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()

    if _is_decision_intent(query):
        decisions = kg_query_decisions(root, topic=None, as_of=as_of)
        if decisions:
            for d in decisions:
                d["confidence"] = 0.95
                d["provenance"] = "kg"
                d["citation"] = {"source_file": d.get("source", ""), "why": "temporal validity filter"}
            return {"strategy": "kg", "results": decisions}

    chroma_hits: list[dict[str, Any]] = []
    if is_chroma_available():
        chroma_hits = search_chroma(query=query, wing=wing, room=room, n_results=n_results)

    lite_hits = search_lite(root=root, query=query, wing=wing, room=room, n_results=n_results)

    if chroma_hits and lite_hits:
        return {"strategy": "hybrid", "results": _merge_and_score(chroma_hits, lite_hits)}
    if chroma_hits:
        return {"strategy": "chroma", "results": _merge_and_score(chroma_hits, [])}
    return {"strategy": "lite", "results": _merge_and_score([], lite_hits)}
