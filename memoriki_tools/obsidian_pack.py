from __future__ import annotations

from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def install_ux_pack(root: Path) -> list[str]:
    root = root.resolve()
    files: dict[Path, str] = {
        root / "wiki" / "meta" / "dashboard.md": """# Dashboard

## Health
```dataview
TABLE length(file.inlinks) as InboundLinks
FROM "wiki"
WHERE file.name != "index" AND file.name != "log"
SORT InboundLinks ASC
LIMIT 50
```

## Recently Updated
```dataview
TABLE updated
FROM "wiki"
WHERE updated
SORT updated DESC
LIMIT 30
```
""",
        root / "wiki" / "meta" / "decision-timeline.md": """# Decision Timeline

```dataview
TABLE date, validity_until, why_this_choice
FROM "wiki/decisions"
SORT date DESC
```
""",
        root / "wiki" / "meta" / "stale-pages.md": """# Stale Pages

```dataview
TABLE updated
FROM "wiki"
WHERE updated AND date(updated) <= date(today) - dur(90 days)
SORT updated ASC
```
""",
        root / "wiki" / "_templates" / "decision.md": """---
title: Decision on Topic
type: decision
sources: []
related: []
created: 2026-04-13
updated: 2026-04-13
date: 2026-04-13
validity_until: indefinite
context: ""
alternatives_considered: []
precedent_references: []
why_this_choice: ""
event_clock: ""
---

## Summary

## Rationale
""",
        root / "wiki" / "_templates" / "concept.md": """---
title: Concept Name
type: concept
sources: []
related: []
created: 2026-04-13
updated: 2026-04-13
---

## Definition

## Notes
""",
    }

    for path, content in files.items():
        _write(path, content)

    return [str(p.relative_to(root)) for p in files]
