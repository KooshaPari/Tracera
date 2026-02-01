---
created: '2026-02-01T03:29:41.882604'
external_id: DB_SCHEMA-054
id: bca8f9c0-c06f-483f-9e81-982bc91d0427
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.882604'
version: 1
---

# campaigns

## Description

Marketing campaigns. Email blasts, push campaigns.

## Metadata

**columns:**
- id
- name
- type
- status
- target_segment
- scheduled_at
- sent_at
- completed_at
**indexes:**
- status_idx
- scheduled_at_idx
