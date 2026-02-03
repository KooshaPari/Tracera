---
created: '2026-02-01T03:29:41.884773'
external_id: DB_SCHEMA-057
id: 4d5d8b78-c91d-453c-9a78-1bedcab58abe
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.884773'
version: 1
---

# driver_analytics

## Description

Driver performance metrics. Acceptance rate, completion rate.

## Metadata

**columns:**
- driver_id
- date
- rides_completed
- acceptance_rate
- cancellation_rate
- avg_rating
- total_earnings
**indexes:**
- driver_id_date_idx
