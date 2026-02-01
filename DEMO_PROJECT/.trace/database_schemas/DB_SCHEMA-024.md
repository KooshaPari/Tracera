---
created: '2026-02-01T03:29:41.838078'
external_id: DB_SCHEMA-024
id: d4b33ec2-e1a4-4055-bb07-16cdf0f453af
links: []
owner: null
parent: null
priority: critical
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.838078'
version: 1
---

# rides

## Description

Core ride records. Trip details, status, pricing, timestamps.

## Metadata

**columns:**
- id
- rider_id
- driver_id
- status
- pickup_lat
- pickup_lng
- dropoff_lat
- dropoff_lng
- requested_at
- accepted_at
- started_at
- completed_at
**indexes:**
- rider_id_idx
- driver_id_idx
- status_idx
- created_at_idx
