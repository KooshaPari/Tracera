---
created: '2026-02-01T03:29:41.869843'
external_id: DB_SCHEMA-044
id: f06f89ad-ed13-4a9e-b820-40bb20e362f5
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.869843'
version: 1
---

# surge_zones

## Description

Dynamic surge pricing zones. Demand multipliers by area.

## Metadata

**columns:**
- id
- service_area_id
- polygon
- surge_multiplier
- effective_from
- effective_until
**indexes:**
- service_area_id_idx
- effective_from_idx
