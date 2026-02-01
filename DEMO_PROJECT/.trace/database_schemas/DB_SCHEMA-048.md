---
created: '2026-02-01T03:29:41.873841'
external_id: DB_SCHEMA-048
id: b006e297-a6e6-4c8e-90b0-97ddfbae5ccd
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.873841'
version: 1
---

# push_notifications

## Description

Push notification queue. FCM/APNS delivery tracking.

## Metadata

**columns:**
- id
- notification_id
- device_token
- status
- sent_at
- delivered_at
- failed_at
- error
**indexes:**
- notification_id_idx
- status_idx
