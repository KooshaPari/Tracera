---
created: '2026-02-01T03:29:41.831930'
external_id: DB_SCHEMA-018
id: c8c5305b-b414-4de3-bf1b-bc430ba29983
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.831930'
version: 1
---

# driver_ratings

## Description

Individual rating records. Per-ride ratings from riders.

## Metadata

**columns:**
- id
- driver_id
- ride_id
- rider_id
- rating
- comment
- created_at
**indexes:**
- driver_id_idx
- ride_id_idx
