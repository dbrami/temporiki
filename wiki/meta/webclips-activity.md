---
title: webclips-activity
type: source
sources:
- wiki/meta/webclips-activity.md
related: []
created: '2026-04-15'
updated: '2026-04-15'
---

# Webclips Activity

## Inbox (Awaiting Archive)
```dataview
TABLE file.mtime as Modified
FROM "raw/webclips"
WHERE !contains(file.folder, "_archive")
SORT file.mtime DESC
```

## Recently Archived
```dataview
TABLE file.mtime as ArchivedAt
FROM "raw/webclips/_archive"
SORT file.mtime DESC
LIMIT 100
```
