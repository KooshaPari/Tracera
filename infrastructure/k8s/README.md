# TraceRTM Kubernetes Deployment Manifests

Production-ready Kubernetes manifests for deploying the TraceRTM hybrid backend architecture.

## Quick Start

```bash
# 1. Validate manifests
./scripts/validate_k8s.sh

# 2. Update secrets (REQUIRED)
vi infrastructure/k8s/02-secrets.yaml

# 3. Deploy
./scripts/deploy_k8s.sh

# 4. Check health
./scripts/health_check.sh tracertm
```

## Manifest Overview

| File | Description | Resources |
|------|-------------|-----------|
| `00-namespace.yaml` | Namespace definition | Namespace |
| `01-configmaps.yaml` | Application & Nginx config | ConfigMaps (2) |
| `02-secrets.yaml` | Sensitive configuration | Secrets (3) |
| `03-postgres.yaml` | PostgreSQL database | StatefulSet, Service, PVC, CronJob |
| `04-redis.yaml` | Redis cache | StatefulSet, Service, PVC, Exporter |
| `05-nats.yaml` | NATS messaging | StatefulSet, Service, PVC, Exporter |
| `06-go-backend.yaml` | Go backend service | Deployment, Service, HPA, PDB |
| `07-python-backend.yaml` | Python backend service | Deployment, Service, HPA, PDB |
| `08-ingress.yaml` | Nginx ingress | Deployment, Service, HPA, PDB |
| `09-monitoring.yaml` | Prometheus & Grafana | Deployments, Services, ConfigMaps |
| `10-network-policies.yaml` | Network security | NetworkPolicies (10+) |

## Architecture

```
Internet
    │
    ▼
┌─────────────────┐
│ Nginx Ingress   │ (2+ replicas)
│ LoadBalancer    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────┐  ┌────────┐
│  Go  │  │ Python │
│ API  │  │  API   │
│(3+)  │  │  (2+)  │
└──┬───┘  └───┬────┘
   │          │
   └────┬─────┘
        │
    ┌───┴───┬────────┬────────┐
    ▼       ▼        ▼        ▼
┌────────┐ ┌────┐ ┌─────┐  ┌──────┐
│Postgres│ │Redis│ │NATS │  │Backup│
│(StatefulSet)    │ │(StatefulSet) │CronJob
└────────┘ └────┘ └─────┘  └──────┘
```

## Resource Requirements

### Minimum (Development)
- **Nodes**: 3 × (4 CPU, 16GB RAM)
- **Storage**: 50GB SSD
- **Total**: 12 CPU, 48GB RAM

### Recommended (Production)
- **Nodes**: 5 × (8 CPU, 32GB RAM)
- **Storage**: 200GB SSD
- **Total**: 40 CPU, 160GB RAM

### Per Component

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit | Storage |
|-----------|-------------|-----------|----------------|--------------|---------|
| Go Backend (each) | 250m | 500m | 256Mi | 512Mi | - |
| Python Backend (each) | 500m | 1000m | 512Mi | 2Gi | - |
| PostgreSQL | 500m | 1000m | 1Gi | 2Gi | 20Gi |
| Redis | 250m | 500m | 512Mi | 1Gi | 10Gi |
| NATS | 250m | 500m | 512Mi | 1Gi | 5Gi |
| Nginx (each) | 100m | 200m | 128Mi | 256Mi | - |

## Scaling Configuration

### Horizontal Pod Autoscaler (HPA)

**Go Backend:**
- Min replicas: 3
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

**Python Backend:**
- Min replicas: 2
- Max replicas: 5
- Target CPU: 75%
- Target Memory: 85%

**Nginx:**
- Min replicas: 2
- Max replicas: 5
- Target CPU: 70%
- Target Memory: 80%

### Manual Scaling

```bash
# Scale Go backend to 5 replicas
kubectl scale deployment/go-backend --replicas=5 -n tracertm

# Scale Python backend to 3 replicas
kubectl scale deployment/python-backend --replicas=3 -n tracertm
```

## Important Configuration

### Secrets (02-secrets.yaml)

**MUST UPDATE BEFORE DEPLOYMENT:**

- `DATABASE_PASSWORD`: Strong random password (20+ chars)
- `JWT_SECRET`: Random string (32+ chars)
- `WORKOS_API_KEY`: Your WorkOS API key
- `WORKOS_CLIENT_ID`: Your WorkOS client ID
- `SECRET_KEY`: Application secret key
- `tls.crt`: Valid TLS certificate
- `tls.key`: Valid TLS private key

### ConfigMaps (01-configmaps.yaml)

**Review and adjust:**

- `CORS_ORIGINS`: Your frontend domains
- `DB_POOL_SIZE`: Database connection pool size
- Nginx routing rules (if using different paths)

## Networking

### Services

| Service | Type | Port | Target Port |
|---------|------|------|-------------|
| nginx-service | LoadBalancer | 80, 443 | 80, 443 |
| go-backend-service | ClusterIP | 8080, 9090 | 8080, 9090 |
| python-backend-service | ClusterIP | 8000, 9091 | 8000, 9091 |
| postgres-service | ClusterIP (Headless) | 5432 | 5432 |
| redis-service | ClusterIP (Headless) | 6379 | 6379 |
| nats-service | ClusterIP (Headless) | 4222, 8222 | 4222, 8222 |

### Network Policies

Network policies enforce zero-trust networking:

- Default deny all ingress
- Nginx can receive from internet
- Nginx can reach backends
- Backends can reach databases
- Cross-backend communication allowed
- Prometheus can scrape metrics
- DNS allowed for all pods

## Monitoring

### Prometheus Targets

- Go Backend: `:9090/metrics`
- Python Backend: `:9091/metrics`
- Redis: `:9121/metrics` (via exporter)
- NATS: `:7777/metrics` (via exporter)
- PostgreSQL: `:9187/metrics` (via exporter)

### Accessing Monitoring

```bash
# Prometheus UI
kubectl port-forward svc/prometheus-service 9090:9090 -n tracertm
# Open: http://localhost:9090

# Grafana UI
kubectl port-forward svc/grafana-service 3000:3000 -n tracertm
# Open: http://localhost:3000 (admin/admin)
```

## Backup and Restore

### Automated Backups

PostgreSQL backups run daily at 2 AM via CronJob:

```bash
# View backup jobs
kubectl get cronjob postgres-backup -n tracertm

# Manually trigger backup
kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%s) -n tracertm

# View backup logs
kubectl logs job/<job-name> -n tracertm
```

### Manual Backup

```bash
# Backup PostgreSQL
kubectl exec -it postgres-0 -n tracertm -- \
  pg_dump -U tracertm -Fc tracertm > backup.dump

# Backup Redis
kubectl exec -it redis-0 -n tracertm -- redis-cli BGSAVE
kubectl cp tracertm/redis-0:/data/dump.rdb ./redis-backup.rdb

# Backup NATS JetStream
kubectl exec -it nats-0 -n tracertm -- \
  tar -czf /tmp/js-backup.tar.gz /data/jetstream
kubectl cp tracertm/nats-0:/tmp/js-backup.tar.gz ./nats-backup.tar.gz
```

## Health Checks

All services include liveness and readiness probes:

- **Go Backend**: `GET /health`
- **Python Backend**: `GET /health`
- **PostgreSQL**: `pg_isready`
- **Redis**: `redis-cli ping`
- **NATS**: `GET /healthz`

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name> -n tracertm
kubectl logs <pod-name> -n tracertm
```

**Database connection issues:**
```bash
kubectl exec -it postgres-0 -n tracertm -- psql -U tracertm
kubectl logs deployment/python-backend -c migrations -n tracertm
```

**Service not accessible:**
```bash
kubectl get endpoints -n tracertm
kubectl port-forward svc/<service-name> <port>:<port> -n tracertm
```

**High resource usage:**
```bash
kubectl top pods -n tracertm
kubectl describe hpa -n tracertm
```

### Debug Commands

```bash
# View all resources
kubectl get all -n tracertm

# View events
kubectl get events -n tracertm --sort-by='.lastTimestamp'

# Shell into pod
kubectl exec -it <pod-name> -n tracertm -- /bin/sh

# View logs from all pods
kubectl logs -f -l app=go-backend -n tracertm --all-containers=true

# Check resource usage
kubectl top nodes
kubectl top pods -n tracertm
```

## Security Best Practices

- ✅ Non-root containers
- ✅ Read-only root filesystem
- ✅ Drop all capabilities
- ✅ Network policies enabled
- ✅ Pod Security Standards
- ✅ Resource limits enforced
- ✅ TLS encryption
- ⚠️ Update secrets before deployment
- ⚠️ Use private registry in production
- ⚠️ Enable RBAC
- ⚠️ Regular security scans

## Next Steps

1. **Read Full Guide**: `/docs/deployment/kubernetes_guide.md`
2. **Update Secrets**: Edit `02-secrets.yaml`
3. **Build Images**: Build and push Docker images
4. **Deploy to Staging**: Test deployment
5. **Load Test**: Verify scaling behavior
6. **Production Deploy**: Follow production checklist
7. **Monitor**: Set up alerts and dashboards

## Support

- **Documentation**: `/docs/deployment/kubernetes_guide.md`
- **Validation**: `./scripts/validate_k8s.sh`
- **Health Check**: `./scripts/health_check.sh`
- **Deploy**: `./scripts/deploy_k8s.sh`

---

**Version**: 1.0.0
**Last Updated**: 2026-01-30
