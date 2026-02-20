---
created: '2026-02-01T03:29:41.842606'
external_id: DB_SCHEMA-032
id: fe1d6fa8-83a9-43f0-a3cc-8aec14153ac7
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.842606'
version: 1
---

# ride_feedback

## Description

Post-ride feedback. Issues, compliments, suggestions.

## Metadata

**columns:**
- id
- ride_id
- user_id
- feedback_type
- message
- created_at
**indexes:**
- ride_id_idx
- user_id_idx
