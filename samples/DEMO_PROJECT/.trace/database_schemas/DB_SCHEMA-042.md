---
created: '2026-02-01T03:29:41.865385'
external_id: DB_SCHEMA-042
id: b7efa8eb-c462-4e3e-ae3f-0b7d0657e414
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.865385'
version: 1
---

# places

## Description

Geocoded place cache. Common addresses, POIs, airports.

## Metadata

**columns:**
- id
- address
- latitude
- longitude
- place_id
- place_type
- created_at
**indexes:**
- place_id_idx
- lat_lng_idx
