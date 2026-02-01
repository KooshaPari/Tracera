---
id: SCALE-025
type: scaling_policy
title: api-gateway - Gradual Scale Down
status: active
created_at: 2026-01-31T20:31:54.215414
---

# api-gateway - Gradual Scale Down

## Description
Slow scale down to avoid disruption for api-gateway

## Metadata
```yaml
direction: step_down
policy_type: step
service: api-gateway
steps:
- adjustment: -1
  threshold: 25
- adjustment: -2
  threshold: 10

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
