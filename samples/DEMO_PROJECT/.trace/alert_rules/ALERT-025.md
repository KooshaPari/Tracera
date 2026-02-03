---
id: ALERT-025
type: alert_rule
title: Account Takeover Attempts
status: active
created_at: 2026-01-31T20:29:13.411934
---

# Account Takeover Attempts

## Description
Multiple failed login attempts

## Metadata
```yaml
category: security
condition: failed_login_attempts > 100
evaluation_period: 5m
notification_channels: Security Team + PagerDuty
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
