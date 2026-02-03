---
id: SCALE-024
type: scaling_policy
title: matching-service - Aggressive Scale Up
status: active
created_at: 2026-01-31T20:31:54.214941
---

# matching-service - Aggressive Scale Up

## Description
Rapid scaling during traffic spikes for matching-service

## Metadata
```yaml
direction: step_up
policy_type: step
service: matching-service
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
