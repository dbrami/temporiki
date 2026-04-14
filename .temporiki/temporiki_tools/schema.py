from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError

PageType = Literal["entity", "concept", "source", "synthesis", "decision", "query"]


class BasePageModel(BaseModel):
    title: str
    type: PageType
    sources: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    created: str
    updated: str


class DecisionPageModel(BasePageModel):
    type: Literal["decision"]
    date: str | None = None
    validity_until: str | None = None
    context: str | None = None
    alternatives_considered: list[str] = Field(default_factory=list)
    precedent_references: list[str] = Field(default_factory=list)
    why_this_choice: str | None = None
    event_clock: str | None = None


class QueryPageModel(BasePageModel):
    type: Literal["query"]
    tags: list[str] = Field(default_factory=list)


_MODEL_BY_TYPE: dict[str, type[BaseModel]] = {
    "decision": DecisionPageModel,
    "query": QueryPageModel,
    "entity": BasePageModel,
    "concept": BasePageModel,
    "source": BasePageModel,
    "synthesis": BasePageModel,
}


def today_iso() -> str:
    return dt.date.today().isoformat()


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    try:
        _, rest = text.split("---\n", 1)
        fm_raw, body = rest.split("---\n", 1)
    except ValueError:
        return {}, text

    fm = yaml.safe_load(fm_raw) or {}
    if not isinstance(fm, dict):
        return {}, text
    return normalize_frontmatter(fm), body


def dump_frontmatter(data: dict[str, Any]) -> str:
    rendered = yaml.safe_dump(data, sort_keys=False, allow_unicode=False).strip()
    return f"---\n{rendered}\n---\n"


def _normalize_value(v: Any) -> Any:
    if isinstance(v, dt.datetime):
        return v.date().isoformat()
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, list):
        return [_normalize_value(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _normalize_value(val) for k, val in v.items()}
    return v


def normalize_frontmatter(data: dict[str, Any]) -> dict[str, Any]:
    return {str(k): _normalize_value(v) for k, v in data.items()}


def infer_type_from_path(path: Path) -> str:
    folder = path.parent.name.lower()
    mapping = {
        "entities": "entity",
        "concepts": "concept",
        "sources": "source",
        "synthesis": "synthesis",
        "decisions": "decision",
        "queries": "query",
    }
    return mapping.get(folder, "source")


def minimal_frontmatter_for(path: Path, rel_source: str | None = None) -> dict[str, Any]:
    page_type = infer_type_from_path(path)
    data: dict[str, Any] = {
        "title": path.stem,
        "type": page_type,
        "sources": [rel_source] if rel_source else [],
        "related": [],
        "created": today_iso(),
        "updated": today_iso(),
    }
    if page_type == "query":
        data["tags"] = ["query"]
    if page_type == "decision":
        data.update(
            {
                "date": today_iso(),
                "validity_until": "indefinite",
                "context": "",
                "alternatives_considered": [],
                "precedent_references": [],
                "why_this_choice": "",
                "event_clock": "",
            }
        )
    return data


def validate_frontmatter(data: dict[str, Any]) -> list[str]:
    data = normalize_frontmatter(data)
    page_type = str(data.get("type", "source"))
    model = _MODEL_BY_TYPE.get(page_type, BasePageModel)
    try:
        model.model_validate(data)
        return []
    except ValidationError as e:
        return [err["msg"] for err in e.errors()]
