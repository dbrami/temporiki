---
title: stale-pages
type: source
sources:
- wiki/meta/stale-pages.md
related: []
created: '2026-04-13'
updated: '2026-04-13'
---

# Stale Pages

```dataview
TABLE updated
FROM "wiki"
WHERE updated AND date(updated) <= date(today) - dur(90 days)
SORT updated ASC
```
