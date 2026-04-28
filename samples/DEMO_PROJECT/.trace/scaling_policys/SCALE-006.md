---
id: SCALE-006
type: scaling_policy
title: matching-service - Memory Scaling
status: active
created_at: 2026-01-31T20:31:54.181066
---

# matching-service - Memory Scaling

## Description
Memory-based auto-scaling policy for matching-service

## Metadata
```yaml
max_capacity: 50
metric: memory_utilization
min_capacity: 3
policy_type: target_tracking
scale_down_cooldown: 300
scale_up_cooldown: 60
service: matching-service
target_value: 80

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
