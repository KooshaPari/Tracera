---
created: '2026-02-01T03:29:41.825132'
external_id: DB_SCHEMA-016
id: 4fa23f8d-26ef-4de3-b981-a5a4afcbace2
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.825132'
version: 1
---

# driver_earnings

## Description

Driver earnings records. Per-trip earnings, tips, bonuses.

## Metadata

**columns:**
- id
- driver_id
- ride_id
- base_fare
- distance_fare
- time_fare
- surge_multiplier
- tips
- total
**indexes:**
- driver_id_idx
- ride_id_idx
