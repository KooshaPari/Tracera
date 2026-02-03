---
id: ALERT-019
type: alert_rule
title: Pod Restart Rate High
status: active
created_at: 2026-01-31T20:29:13.408781
---

# Pod Restart Rate High

## Description
Kubernetes pods restarting frequently

## Metadata
```yaml
category: performance
condition: pod_restart_count > 5
evaluation_period: 10m
notification_channels: DevOps Team
severity: warning

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
