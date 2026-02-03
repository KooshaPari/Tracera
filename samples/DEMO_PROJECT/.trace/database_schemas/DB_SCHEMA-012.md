---
created: '2026-02-01T03:29:41.820769'
external_id: DB_SCHEMA-012
id: 9e6915d1-a067-4272-a9d9-604b5db114be
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.820769'
version: 1
---

# driver_vehicles

## Description

Driver vehicle records. Make, model, year, license plate, insurance.

## Metadata

**columns:**
- id
- driver_id
- make
- model
- year
- color
- license_plate
- insurance_expires
- status
**indexes:**
- driver_id_idx
- license_plate_idx
