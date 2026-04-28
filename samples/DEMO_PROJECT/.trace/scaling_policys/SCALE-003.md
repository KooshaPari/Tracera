---
id: SCALE-003
type: scaling_policy
title: payment-service - CPU Scaling
status: active
created_at: 2026-01-31T20:31:54.177580
---

# payment-service - CPU Scaling

## Description
CPU-based auto-scaling policy for payment-service

## Metadata
```yaml
max_capacity: 50
metric: cpu_utilization
min_capacity: 3
policy_type: target_tracking
scale_down_cooldown: 300
scale_up_cooldown: 60
service: payment-service
target_value: 70

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
