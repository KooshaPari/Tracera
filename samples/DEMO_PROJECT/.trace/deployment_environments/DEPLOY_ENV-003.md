---
id: DEPLOY_ENV-003
type: deployment_environment
title: Production - eu-west-1
status: active
created_at: 2026-01-31T20:26:53.283990
---

# Production - eu-west-1

## Description
Production environment in eu-west-1 region with full HA setup

## Metadata
```yaml
auto_scaling: true
cache_clusters:
- redis-primary
- redis-replica
disaster_recovery: true
environment_type: production
ha_enabled: true
kubernetes_cluster: swiftride-prod-eu-west-1
rds_instances:
- primary
- replica-1
- replica-2
region: eu-west-1

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
