---
created: '2026-02-01T03:29:41.840921'
external_id: DB_SCHEMA-029
id: f2a7cb53-f462-49fc-965b-f4cb74765107
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.840921'
version: 1
---

# ride_cancellations

## Description

Ride cancellation records. Reason, cancelled by, fees.

## Metadata

**columns:**
- id
- ride_id
- cancelled_by
- reason
- cancellation_fee
- cancelled_at
**indexes:**
- ride_id_idx
