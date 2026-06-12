# Tracera /health upgrade spec

## Status: draft 2026-06-09

## Background

Current /health is generic; /health/liveness + /health/readiness exist but readiness should be the single source of truth for k8s.

## Proposed

1. /health → alias for /health/liveness
2. /ready → alias for /health/readiness
3. /live → alias for /health/liveness
4. Add /healthz + /readyz (k8s convention)

## Implementation

```python
@router.get('/healthz')
async def healthz() -> dict: return {'status': 'alive'}
```

## Test plan

- curl -i http://tracera:8000/healthz
- k8s probe config
