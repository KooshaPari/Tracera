---
created: '2026-02-01T03:29:41.874887'
external_id: DB_SCHEMA-050
id: 7ae92961-2917-43ec-9b69-a950b101e74b
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.874887'
version: 1
---

# emails

## Description

Email delivery log. Sendgrid tracking.

## Metadata

**columns:**
- id
- user_id
- to_email
- subject
- template
- status
- sent_at
- opened_at
- clicked_at
**indexes:**
- user_id_idx
- status_idx
