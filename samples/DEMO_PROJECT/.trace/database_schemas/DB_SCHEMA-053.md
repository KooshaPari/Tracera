---
created: '2026-02-01T03:29:41.881460'
external_id: DB_SCHEMA-053
id: 2dc99bfc-33ca-4668-9350-1f8346af9265
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.881460'
version: 1
---

# referrals

## Description

Referral program tracking. Referrer, referee, rewards.

## Metadata

**columns:**
- id
- referrer_id
- referee_id
- code
- status
- reward_amount
- completed_at
- created_at
**indexes:**
- referrer_id_idx
- referee_id_idx
- code_idx
