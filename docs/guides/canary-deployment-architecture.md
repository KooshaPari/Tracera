# Canary Deployment Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users / Traffic                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                ┌───────────▼────────────┐
                │  NGINX Ingress        │
                │  Controller            │
                │  • Canary Annotations  │
                │  • Weight-based        │
                │  • Header-based        │
                └───────────┬────────────┘
                            │
            ┌───────────────┴───────────────┐
            │    Traffic Splitting          │
            │    (nginx.ingress.kubernetes  │
            │     .io/canary-weight)        │
            └───────────────┬───────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │                                      │
    10% Traffic                            90% Traffic
         │                                      │
         │                                      │
┌────────▼──────────┐                  ┌────────▼──────────┐
│  Canary Version   │                  │  Stable Version   │
│  (New Deployment) │                  │ (Current Prod)    │
├───────────────────┤                  ├───────────────────┤
│ • tracertm-api    │                  │ • tracertm-api    │
│   -canary         │                  │   (stable)        │
│                   │                  │                   │
│ • tracertm-backend│                  │ • tracertm-backend│
│   -canary         │                  │   (stable)        │
│                   │                  │                   │
│ Labels:           │                  │ Labels:           │
│   version: canary │                  │   version: stable │
└────────┬──────────┘                  └────────┬──────────┘
         │                                      │
         └──────────────────┬───────────────────┘
                            │
                   ┌────────▼─────────┐
                   │   Prometheus     │
                   │   • Metrics      │
                   │   • Alerts       │
                   │   • Comparison   │
                   └────────┬─────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
      ┌───────▼────────┐         ┌───────▼────────┐
      │  Recording     │         │    Alerts      │
      │  Rules         │         │  • Error Rate  │
      │                │         │  • Latency     │
      │ • error_rate   │         │  • Pod Health  │
      │ • latency_p95  │         │                │
      │ • latency_p99  │         └────────┬───────┘
      │ • success_rate │                  │
      └────────────────┘                  │
                                  ┌───────▼───────┐
                                  │  Rollback     │
                                  │  Trigger      │
                                  │  (if failed)  │
                                  └───────────────┘
```

## Deployment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Canary Deployment Flow                        │
└─────────────────────────────────────────────────────────────────┘

1. Validation Phase (2 min)
   ├─ Check stable health
   ├─ Validate image tag
   ├─ Verify cluster access
   └─ Check prerequisites

2. Deploy Canary (3 min)
   ├─ Apply canary deployments
   ├─ Update container images
   ├─ Wait for rollout
   └─ Verify pod readiness

3. Stage 1: 10% Traffic (5 min)
   ├─ Set traffic weight to 10%
   ├─ Monitor metrics every 60s
   │  ├─ Error rate < 1%
   │  ├─ P95 latency < 500ms
   │  ├─ Success rate > 99%
   │  └─ Pod health checks
   └─ Decision: Proceed or Rollback

4. Stage 2: 50% Traffic (5 min)
   ├─ Set traffic weight to 50%
   ├─ Monitor metrics every 60s
   │  ├─ Error rate < 1%
   │  ├─ P95 latency < 500ms
   │  ├─ Success rate > 99%
   │  └─ Pod health checks
   └─ Decision: Proceed or Rollback

5. Promotion (3 min)
   ├─ Update stable deployments
   ├─ Wait for stable rollout
   ├─ Set canary weight to 0%
   └─ Scale down canary pods

Total Time: ~10 minutes
```

## Traffic Progression

```
Stage 1: 10% Canary
┌──────────────────────────────────────┐
│ ██ Canary (10%)                      │
│ ████████████████████████████ Stable  │
└──────────────────────────────────────┘

Stage 2: 50% Canary
┌──────────────────────────────────────┐
│ ███████████████ Canary (50%)         │
│ ███████████████ Stable               │
└──────────────────────────────────────┘

Promotion: 100% Stable (new version)
┌──────────────────────────────────────┐
│ ████████████████████████████████████ │
│ Stable (promoted from canary)        │
└──────────────────────────────────────┘
```

## Health Check Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Health Check System                         │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │  Kubernetes  │
                    │   Probes     │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐    ┌───────▼────┐    ┌──────▼──────┐
   │ Liveness │    │ Readiness  │    │  Startup    │
   │  Probe   │    │   Probe    │    │   Probe     │
   │          │    │            │    │             │
   │ /health/ │    │ /health/   │    │ /health     │
   │ liveness │    │ readiness  │    │             │
   └────┬─────┘    └───────┬────┘    └──────┬──────┘
        │                  │                 │
        └──────────────────┼─────────────────┘
                           │
                    ┌──────▼───────┐
                    │    Health    │
                    │   Endpoint   │
                    │              │
                    │ /health/     │
                    │ canary       │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐    ┌───────▼────┐    ┌──────▼──────┐
   │ Database │    │   Redis    │    │    NATS     │
   │  Health  │    │   Health   │    │   Health    │
   └────┬─────┘    └───────┬────┘    └──────┬──────┘
        │                  │                 │
        └──────────────────┼─────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Combined   │
                    │    Status    │
                    │              │
                    │ • healthy    │
                    │ • degraded   │
                    │ • unhealthy  │
                    └──────────────┘
```

## Metrics Collection

```
┌─────────────────────────────────────────────────────────────────┐
│                    Metrics Collection Flow                       │
└─────────────────────────────────────────────────────────────────┘

Application Pods
├─ Canary Pods (version: canary)
│  ├─ Expose /metrics endpoint
│  └─ Labels: version=canary
│
└─ Stable Pods (version: stable)
   ├─ Expose /metrics endpoint
   └─ Labels: version=stable
           │
           │ scraped by
           ▼
   ServiceMonitor
   ├─ Scrape interval: 30s
   ├─ Scrape timeout: 10s
   └─ Selectors: app=tracertm-*
           │
           │ sends to
           ▼
     Prometheus
     ├─ Recording Rules
     │  ├─ tracertm:canary:error_rate
     │  ├─ tracertm:canary:latency_p95
     │  ├─ tracertm:canary:latency_p99
     │  ├─ tracertm:canary:success_rate
     │  ├─ tracertm:stable:error_rate
     │  └─ tracertm:stable:latency_p95
     │
     └─ Alert Rules
        ├─ CanaryHighErrorRate (>1%)
        ├─ CanaryHighLatency (>500ms)
        ├─ CanaryPodCrashing (>2 restarts)
        └─ CanaryPodNotReady (<100% ready)
                │
                │ triggers
                ▼
          Alertmanager
                │
                │ notifies
                ▼
        Rollback Automation
```

## Rollback Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rollback Decision Tree                        │
└─────────────────────────────────────────────────────────────────┘

            ┌──────────────────┐
            │  Health Check    │
            │  Every 60s       │
            └────────┬─────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        │   Check Metrics         │
        │   • Error Rate          │
        │   • Latency P95/P99     │
        │   • Success Rate        │
        │   • Pod Health          │
        │                         │
        └────────┬────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
  Pass                     Fail
    │                         │
    ▼                         ▼
┌────────┐           ┌─────────────┐
│Continue│           │   Rollback  │
│Next    │           │             │
│Stage   │           │ 1. Set      │
└────┬───┘           │    weight=0 │
     │               │ 2. Scale    │
     │               │    down     │
     │               │ 3. Verify   │
     ▼               └──────┬──────┘
┌────────┐                  │
│Promote │                  ▼
│to      │           ┌─────────────┐
│Stable  │           │   Alert     │
└────────┘           │   Notify    │
                     │   Document  │
                     └─────────────┘
```

## Service Mesh Integration (Optional)

```
┌─────────────────────────────────────────────────────────────────┐
│              Service Mesh Canary (Optional)                      │
└─────────────────────────────────────────────────────────────────┘

        ┌──────────────┐
        │   Istio      │
        │   Gateway    │
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │ VirtualService│
        │  • weight: 10 │
        │  • weight: 90 │
        └──────┬───────┘
               │
     ┌─────────┴─────────┐
     │                   │
┌────▼────┐        ┌─────▼────┐
│CanaryDst│        │StableDst │
│ Rule    │        │ Rule     │
└────┬────┘        └─────┬────┘
     │                   │
     └─────────┬─────────┘
               │
        ┌──────▼───────┐
        │   Service    │
        │   Endpoints  │
        └──────────────┘
```

## Integration Points

### 1. CI/CD Integration
```
GitHub Actions
    ├─ Build & Test
    ├─ Docker Build
    ├─ Push to Registry
    └─ Trigger Canary Deploy
            │
            ▼
    Canary Workflow
            │
            ▼
    Kubernetes Cluster
```

### 2. Monitoring Integration
```
Applications
    ├─ Prometheus Metrics
    ├─ Health Endpoints
    └─ Logs
            │
            ▼
    Observability Stack
    ├─ Prometheus
    ├─ Grafana
    └─ Alertmanager
```

### 3. Notification Integration
```
Alerts / Events
    ├─ Slack
    ├─ Email
    ├─ PagerDuty
    └─ Status Page
```

## Security Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      Security Architecture                       │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Ingress    │
    │   TLS        │
    │   (443)      │
    └──────┬───────┘
           │ HTTPS
    ┌──────▼───────┐
    │   Services   │
    │   (Internal) │
    └──────┬───────┘
           │ Internal
    ┌──────▼───────┐
    │     Pods     │
    │   • Secrets  │
    │   • EnvVars  │
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  Database    │
    │  (Internal)  │
    └──────────────┘
```

## Failure Scenarios

### Scenario 1: High Error Rate
```
Error Rate > 1% → Alert → Rollback
Time to Detect: 60s
Time to Rollback: 60s
Total Recovery: 120s
```

### Scenario 2: High Latency
```
P95 > 500ms → Alert → Rollback
Time to Detect: 60s
Time to Rollback: 60s
Total Recovery: 120s
```

### Scenario 3: Pod Crash Loop
```
Restarts > 2 → Alert → Rollback
Time to Detect: 30s
Time to Rollback: 60s
Total Recovery: 90s
```

## Scaling Considerations

### Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tracertm-api-canary
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tracertm-api-canary
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Best Practices

1. **Always test in staging first**
2. **Monitor actively during deployment**
3. **Have rollback script ready**
4. **Document changes clearly**
5. **Use header-based testing**
6. **Set up proper alerts**
7. **Review metrics post-deployment**

---

For implementation details, see:
- Main documentation: `scripts/canary/README.md`
- Quick start: `docs/guides/quick-start/canary-deployment-quickstart.md`
- Completion report: `docs/reports/task-109-canary-deployment-system-completion.md`
