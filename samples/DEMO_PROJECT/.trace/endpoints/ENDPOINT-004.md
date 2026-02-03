---
created: '2026-01-31T01:20:30.957128'
external_id: ENDPOINT-004
id: 172f7b07-2a82-4086-8742-95ab05f064a6
links:
- target: TABLE-003
  type: uses
owner: null
parent: null
priority: high
status: todo
type: endpoint
updated: '2026-01-31T01:20:30.957156'
version: 1
---

# POST /api/auth/login

## Description

User login endpoint with email/password validation. Returns JWT access and refresh tokens. Rate limited to prevent brute force.

