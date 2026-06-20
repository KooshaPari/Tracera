---
id: SCALE-023
type: scaling_policy
title: api-gateway - Aggressive Scale Up
status: active
created_at: 2026-01-31T20:31:54.211525
---

# api-gateway - Aggressive Scale Up

## Description
Rapid scaling during traffic spikes for api-gateway

## Metadata
```yaml
direction: step_up
policy_type: step
service: api-gateway
steps:
- adjustment: 1
  threshold: 50
- adjustment: 2
  threshold: 75
- adjustment: 5
  threshold: 90

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
