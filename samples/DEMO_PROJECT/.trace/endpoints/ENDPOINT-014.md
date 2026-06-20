---
created: '2026-01-31T01:20:30.986922'
external_id: ENDPOINT-014
id: a223c5f8-e24f-4442-9338-9d02f27690f5
links:
- target: TABLE-008
  type: uses
- target: TABLE-009
  type: uses
owner: null
parent: null
priority: critical
status: todo
type: endpoint
updated: '2026-01-31T01:20:30.986956'
version: 1
---

# POST /api/orders

## Description

Create new order from cart. Validates inventory, processes payment, creates order record, and sends confirmation email.

