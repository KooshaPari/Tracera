# Process Compose Quick Reference

**Startup Target:** ~30-35 seconds (50% faster than before)

## Service Dependency Map

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: Infrastructure (t=0s, all parallel)                    │
│ postgres | redis | neo4j | nats | minio | prometheus | node-exp │
└──────────┬──────────────────────────────────────────────────────┘
           │ (all healthy by t=15s)
┌──────────▼──────────────────────────────────────────────────────┐
│ Layer 2: Workflow (t=5s)                                         │
│ temporal (depends: postgres) | exporters                         │
└──────────┬──────────────────────────────────────────────────────┘
           │ (all healthy by t=25s)
┌──────────▼──────────────────────────────────────────────────────┐
│ Layer 3: Applications (t=15-20s, all parallel)                   │
│ go-backend | python-backend | frontend                           │
└──────────┬──────────────────────────────────────────────────────┘
           │ (all healthy by t=30s)
┌──────────▼──────────────────────────────────────────────────────┐
│ Layer 4: Gateway (t=30s)                                         │
│ caddy | grafana                                                  │
└─────────────────────────────────────────────────────────────────┘
         ↓
    READY (t=35s)
```

## Health Check Settings

### Fast Services (period_seconds: 3)
- redis: 1s initial delay
- nats: 2s initial delay

### Standard Services (period_seconds: 5)
- postgres: 2s initial delay
- minio: 3s initial delay
- temporal: 5s initial delay
- neo4j: 15s initial delay (JVM startup)
- prometheus: 3s initial delay
- go-backend: 20s initial delay (migrations)
- python-backend: 5s initial delay
- frontend: 25s initial delay (Vite build)
- caddy: 5s initial delay
- grafana: 10s initial delay

### Thresholds (All Services)
- success_threshold: 1 (healthy on first success)
- failure_threshold: 2 (unhealthy after 2 failures)

## Key Optimizations

| Optimization | Savings |
|--------------|---------|
| Parallel Layer 1 (8 services) | ~10s |
| Layer 2 overlap with Layer 1 | ~5s |
| Removed python-backend→go-backend dep | ~10s |
| Reduced health check intervals | ~10-15s |
| Optimized timeout values | ~5-10s |
| **Total Savings** | **~30s (50% reduction)** |

## Commands

```bash
# Start all services
process-compose up

# Start in TUI mode with live monitoring
process-compose up --tui

# View live logs
process-compose logs -f

# Check service health
process-compose ps

# Stop all services
process-compose down

# Restart specific service
process-compose restart go-backend

# View specific service logs
process-compose logs go-backend

# Follow recent logs with timestamps
process-compose logs --follow --timestamps backend
```

## Troubleshooting

### Service stuck in "pending" state
- Check dependencies: `process-compose ps`
- View logs: `process-compose logs <service>`
- Increase initial_delay if service needs more startup time

### Repeated restart loops
- Check port conflicts: `lsof -i :<port>`
- Review health check timeout: may be too aggressive
- Check logs for actual service errors

### Parallel startup issues
- Remove `depends_on` blocking parallel start
- Ensure services handle missing dependencies gracefully
- Test cross-service communication after full startup

## Performance Metrics

### Before Optimization
```
Startup Time: ~60 seconds
Parallel Services: 3 (postgres, redis, neo4j)
Sequential Blocks: 4 major stages
Health Check Period: 5-15s (inconsistent)
```

### After Optimization
```
Startup Time: ~30-35 seconds
Parallel Services: 8 (Layer 1) + 3 (Layer 3) + 2 (Layer 4)
Sequential Blocks: 2 major stages (Layer 1→2→3→4)
Health Check Period: 3-5s (consistent, faster)
```

## Configuration Structure

Each service has:
```yaml
service_name:
  command: "..."
  depends_on:
    parent_service:
      condition: process_healthy
  readiness_probe:
    http_get/exec:
      ...
    initial_delay_seconds: N
    period_seconds: N
    timeout_seconds: N
    success_threshold: 1
    failure_threshold: 2
  environment:
    - VAR=value
```

## Testing Checklist

- [ ] All services start without errors
- [ ] Startup completes in ~30-35 seconds
- [ ] Health checks pass cleanly (no flapping)
- [ ] API endpoints respond
- [ ] Database migrations complete
- [ ] No race conditions in logs
- [ ] Cross-service communication works
- [ ] Restart-on-failure works correctly

## Files

- **Configuration:** `process-compose.yaml`
- **Report:** `docs/reports/PROCESS_COMPOSE_PARALLELIZATION_REPORT.md`
- **Design:** `docs/plans/2026-01-31-native-process-orchestration-design.md`
- **Implementation:** `docs/plans/2026-01-31-native-process-orchestration-implementation.md`
