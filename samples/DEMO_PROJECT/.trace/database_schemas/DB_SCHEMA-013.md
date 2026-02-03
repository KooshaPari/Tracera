---
created: '2026-02-01T03:29:41.821512'
external_id: DB_SCHEMA-013
id: 55cf1d11-f099-4bdc-a833-8b7ef6d1bdc3
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.821512'
version: 1
---

# driver_documents

## Description

Driver uploaded documents. License, insurance, registration scans.

## Metadata

**columns:**
- id
- driver_id
- document_type
- file_url
- status
- expires_at
- uploaded_at
**indexes:**
- driver_id_idx
- status_idx
