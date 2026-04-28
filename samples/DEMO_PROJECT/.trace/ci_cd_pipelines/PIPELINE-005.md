---
id: PIPELINE-005
type: ci_cd_pipeline
title: driver-service - Build
status: active
created_at: 2026-01-31T20:31:54.007845
---

# driver-service - Build

## Description
Build pipeline for driver-service microservice

## Metadata
```yaml
docker_registry: ECR
pipeline_type: build
runtime: GitHub Actions
service: driver-service
stages:
- checkout
- test
- build
- scan
- publish
triggers:
- push to main
- pull request

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
