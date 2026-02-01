---
id: PIPELINE-006
type: ci_cd_pipeline
title: rider-service - Build
status: active
created_at: 2026-01-31T20:31:54.008210
---

# rider-service - Build

## Description
Build pipeline for rider-service microservice

## Metadata
```yaml
docker_registry: ECR
pipeline_type: build
runtime: GitHub Actions
service: rider-service
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
