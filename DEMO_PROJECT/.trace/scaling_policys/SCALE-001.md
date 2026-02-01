---
id: SCALE-001
type: scaling_policy
title: api-gateway - CPU Scaling
status: active
created_at: 2026-01-31T20:31:54.176927
---

# api-gateway - CPU Scaling

## Description
CPU-based auto-scaling policy for api-gateway

## Metadata
```yaml
max_capacity: 50
metric: cpu_utilization
min_capacity: 3
policy_type: target_tracking
scale_down_cooldown: 300
scale_up_cooldown: 60
service: api-gateway
target_value: 70

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
