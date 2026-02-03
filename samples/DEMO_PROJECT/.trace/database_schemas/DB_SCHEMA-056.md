---
created: '2026-02-01T03:29:41.884313'
external_id: DB_SCHEMA-056
id: cff0c4d4-b2b9-4efd-b5fc-e3deef060b2b
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.884313'
version: 1
---

# ride_analytics

## Description

Aggregated ride metrics. Daily/hourly ride statistics.

## Metadata

**columns:**
- date
- hour
- total_rides
- completed_rides
- cancelled_rides
- total_revenue
- avg_ride_duration
**indexes:**
- date_hour_idx
