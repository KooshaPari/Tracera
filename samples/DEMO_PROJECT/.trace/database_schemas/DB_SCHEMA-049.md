---
created: '2026-02-01T03:29:41.874389'
external_id: DB_SCHEMA-049
id: 461dc2ee-0e1f-41fd-9067-21ce4909cba8
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.874389'
version: 1
---

# sms_messages

## Description

SMS message log. Twilio delivery tracking.

## Metadata

**columns:**
- id
- user_id
- phone
- message
- status
- provider_id
- sent_at
- delivered_at
**indexes:**
- user_id_idx
- status_idx
