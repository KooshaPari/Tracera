---
created: '2026-02-01T03:29:41.841369'
external_id: DB_SCHEMA-030
id: 93a696ed-c0a8-4853-8eeb-437a1a339983
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.841369'
version: 1
---

# ride_schedules

## Description

Scheduled future rides. Advance booking records.

## Metadata

**columns:**
- id
- rider_id
- pickup_address
- dropoff_address
- scheduled_time
- status
- created_at
**indexes:**
- rider_id_idx
- scheduled_time_idx
- status_idx
