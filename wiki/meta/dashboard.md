---
title: dashboard
type: source
sources:
- wiki/meta/dashboard.md
related: []
created: '2026-04-13'
updated: '2026-04-13'
---

# Dashboard

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
