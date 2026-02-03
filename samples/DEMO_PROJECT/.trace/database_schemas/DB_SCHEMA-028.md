---
created: '2026-02-01T03:29:41.840456'
external_id: DB_SCHEMA-028
id: 15658c89-82a7-499a-8568-545b853d3459
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.840456'
version: 1
---

# ride_estimates

## Description

Pre-ride pricing estimates. Cached estimates for common routes.

## Metadata

**columns:**
- id
- pickup_lat
- pickup_lng
- dropoff_lat
- dropoff_lng
- estimated_fare
- estimated_duration
- expires_at
**indexes:**
- pickup_lat_lng_idx
- expires_at_idx
