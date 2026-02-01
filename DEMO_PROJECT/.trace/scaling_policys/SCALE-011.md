---
id: SCALE-011
type: scaling_policy
title: payment-service - Request Rate Scaling
status: active
created_at: 2026-01-31T20:31:54.191519
---

# payment-service - Request Rate Scaling

## Description
Request rate-based scaling for payment-service

## Metadata
```yaml
max_capacity: 100
metric: request_count_per_target
min_capacity: 3
policy_type: target_tracking
service: payment-service
target_value: 1000

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
