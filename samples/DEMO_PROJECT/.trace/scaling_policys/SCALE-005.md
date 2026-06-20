---
id: SCALE-005
type: scaling_policy
title: api-gateway - Memory Scaling
status: active
created_at: 2026-01-31T20:31:54.180104
---

# api-gateway - Memory Scaling

## Description
Memory-based auto-scaling policy for api-gateway

## Metadata
```yaml
max_capacity: 50
metric: memory_utilization
min_capacity: 3
policy_type: target_tracking
scale_down_cooldown: 300
scale_up_cooldown: 60
service: api-gateway
target_value: 80

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
