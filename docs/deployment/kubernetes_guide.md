# TraceRTM Kubernetes Deployment Guide

Complete guide for deploying the TraceRTM hybrid backend architecture to Kubernetes.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment](#detailed-deployment)
- [Configuration](#configuration)
- [Scaling Strategies](#scaling-strategies)
- [Monitoring](#monitoring)
- [Backup and Restore](#backup-and-restore)
- [Troubleshooting](#troubleshooting)
- [Production Checklist](#production-checklist)

---

## Architecture Overview

The TraceRTM platform deploys as a microservices architecture with:

### Backend Services
- **Go Backend** (3+ replicas): High-performance API endpoints, webhooks, events
- **Python Backend** (2+ replicas): Complex queries, business logic, SQLAlchemy workload
- **Nginx Ingress** (2+ replicas): Load balancing, TLS termination, routing

### Infrastructure
- **PostgreSQL** (StatefulSet): Primary database with persistent storage
- **Redis** (StatefulSet): Shared cache and session storage
- **NATS** (StatefulSet): Event streaming with JetStream

### Monitoring (Optional)
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Exporters**: PostgreSQL, Redis, NATS metrics

---

## Prerequisites

### Required Tools

1. **kubectl** (v1.24+)
   ```bash
   # macOS
   brew install kubectl

   # Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   chmod +x kubectl
   sudo mv kubectl /usr/local/bin/
   ```

2. **Kubernetes Cluster** (one of):
   - Google Kubernetes Engine (GKE)
   - Amazon Elastic Kubernetes Service (EKS)
   - Azure Kubernetes Service (AKS)
   - DigitalOcean Kubernetes
   - Local: minikube, kind, k3s

3. **Container Images**
   - Build and push Docker images to a registry
   - Update image references in manifests

### Cluster Requirements

- **Kubernetes Version**: 1.24+
- **Node Resources**:
  - Minimum: 3 nodes, 4 CPU, 16GB RAM each
  - Recommended: 5 nodes, 8 CPU, 32GB RAM each
- **Storage**:
  - Dynamic volume provisioning
  - Storage classes for SSD (recommended)
- **Load Balancer**: Cloud provider LB or MetalLB for on-prem

### Optional
- **Helm** (for advanced deployments)
- **cert-manager** (for automatic TLS certificates)
- **Prometheus Operator** (for advanced monitoring)

---

## Quick Start

### 1. Build and Push Container Images

```bash
# Build Go backend
cd backend
docker build -t your-registry/tracertm-go-backend:latest .
docker push your-registry/tracertm-go-backend:latest

# Build Python backend
cd ../src
docker build -t your-registry/tracertm-python-backend:latest .
docker push your-registry/tracertm-python-backend:latest
```

### 2. Update Image References

Edit the deployment manifests to use your images:

```bash
# Update Go backend image
sed -i 's|tracertm/go-backend:latest|your-registry/tracertm-go-backend:latest|g' \
  infrastructure/k8s/06-go-backend.yaml

# Update Python backend image
sed -i 's|tracertm/python-backend:latest|your-registry/tracertm-python-backend:latest|g' \
  infrastructure/k8s/07-python-backend.yaml
```

### 3. Configure Secrets

**CRITICAL**: Update production secrets before deployment!

```bash
# Edit secrets file
vi infrastructure/k8s/02-secrets.yaml

# Required changes:
# - DATABASE_PASSWORD: Use strong random password
# - JWT_SECRET: Minimum 32 characters, random
# - WORKOS_API_KEY: Your WorkOS API key
# - WORKOS_CLIENT_ID: Your WorkOS client ID
# - SECRET_KEY: Application secret key
```

### 4. Configure TLS Certificates

Option A: Use existing certificates:
```bash
# Base64 encode your certificates
cat your-cert.crt | base64 > cert.b64
cat your-key.key | base64 > key.b64

# Update 02-secrets.yaml with encoded values
```

Option B: Generate self-signed (testing only):
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=tracertm.local/O=TraceRTM"

cat tls.crt | base64 > cert.b64
cat tls.key | base64 > key.b64
```

Option C: Use cert-manager (recommended for production):
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f infrastructure/k8s/cert-manager-issuer.yaml
```

### 5. Deploy to Kubernetes

```bash
# Make script executable
chmod +x scripts/deploy_k8s.sh

# Dry run first (validate manifests)
DRY_RUN=true ./scripts/deploy_k8s.sh

# Deploy to current context
./scripts/deploy_k8s.sh

# Or deploy to specific context
./scripts/deploy_k8s.sh my-prod-cluster
```

### 6. Verify Deployment

```bash
# Check all resources
kubectl get all -n tracertm

# Check pod status
kubectl get pods -n tracertm -w

# Check external IP
kubectl get svc nginx-service -n tracertm

# Check logs
kubectl logs -f deployment/go-backend -n tracertm
kubectl logs -f deployment/python-backend -n tracertm
```

---

## Detailed Deployment

### Manual Step-by-Step Deployment

If you prefer manual control over the deployment process:

#### 1. Create Namespace
```bash
kubectl apply -f infrastructure/k8s/00-namespace.yaml
```

#### 2. Configure Application
```bash
kubectl apply -f infrastructure/k8s/01-configmaps.yaml
kubectl apply -f infrastructure/k8s/02-secrets.yaml
```

#### 3. Deploy Infrastructure
```bash
# PostgreSQL
kubectl apply -f infrastructure/k8s/03-postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n tracertm --timeout=300s

# Redis
kubectl apply -f infrastructure/k8s/04-redis.yaml
kubectl wait --for=condition=ready pod -l app=redis -n tracertm --timeout=300s

# NATS
kubectl apply -f infrastructure/k8s/05-nats.yaml
kubectl wait --for=condition=ready pod -l app=nats -n tracertm --timeout=300s
```

#### 4. Deploy Backends
```bash
# Go Backend
kubectl apply -f infrastructure/k8s/06-go-backend.yaml
kubectl rollout status deployment/go-backend -n tracertm

# Python Backend (with migrations)
kubectl apply -f infrastructure/k8s/07-python-backend.yaml
kubectl rollout status deployment/python-backend -n tracertm
```

#### 5. Deploy Ingress
```bash
kubectl apply -f infrastructure/k8s/08-ingress.yaml
kubectl rollout status deployment/nginx -n tracertm
```

#### 6. Deploy Monitoring (Optional)
```bash
kubectl apply -f infrastructure/k8s/09-monitoring.yaml
kubectl apply -f infrastructure/k8s/10-network-policies.yaml
```

---

## Configuration

### Environment Variables

Key configuration via ConfigMaps and Secrets:

**ConfigMap (`app-config`):**
- `DATABASE_HOST`: PostgreSQL service hostname
- `REDIS_HOST`: Redis service hostname
- `NATS_URL`: NATS connection URL
- `GO_BACKEND_URL`: Internal Go backend URL
- `PYTHON_BACKEND_URL`: Internal Python backend URL
- `FEATURE_*`: Feature flags

**Secrets (`app-secrets`):**
- `DATABASE_PASSWORD`: Database password
- `JWT_SECRET`: JWT signing key
- `WORKOS_API_KEY`: WorkOS authentication
- `SECRET_KEY`: Application secret

### Updating Configuration

```bash
# Edit ConfigMap
kubectl edit configmap app-config -n tracertm

# Restart pods to pick up changes
kubectl rollout restart deployment/go-backend -n tracertm
kubectl rollout restart deployment/python-backend -n tracertm
```

### Storage Classes

For production, configure appropriate storage classes:

```yaml
# Example: Use fast SSD storage
storageClassName: fast-ssd  # GKE: pd-ssd, EKS: gp3, AKS: managed-premium
```

Update in:
- `03-postgres.yaml` (PostgreSQL data)
- `04-redis.yaml` (Redis persistence)
- `05-nats.yaml` (NATS JetStream)

---

## Scaling Strategies

### Horizontal Scaling

#### Auto-scaling (Configured)

HPA automatically scales based on CPU/memory:

```bash
# View current HPA status
kubectl get hpa -n tracertm

# Expected output:
# NAME                 REFERENCE             TARGETS   MINPODS   MAXPODS   REPLICAS
# go-backend-hpa       Deployment/go-backend 45%/70%   3         10        3
# python-backend-hpa   Deployment/python     50%/75%   2         5         2
```

#### Manual Scaling

```bash
# Scale Go backend
kubectl scale deployment/go-backend --replicas=5 -n tracertm

# Scale Python backend
kubectl scale deployment/python-backend --replicas=3 -n tracertm

# Scale Nginx
kubectl scale deployment/nginx --replicas=3 -n tracertm
```

#### Adjust HPA Limits

Edit HPA manifests and reapply:

```yaml
spec:
  minReplicas: 5
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Scale at 60% CPU
```

### Vertical Scaling

#### Adjust Resource Requests/Limits

```bash
# Edit deployment
kubectl edit deployment go-backend -n tracertm

# Update resources:
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

#### Using VPA (Vertical Pod Autoscaler)

Uncomment VPA configuration in `07-python-backend.yaml` if VPA is installed.

---

## Monitoring

### Prometheus and Grafana

Deployed via `09-monitoring.yaml`:

```bash
# Access Prometheus UI
kubectl port-forward svc/prometheus-service 9090:9090 -n tracertm
# Open: http://localhost:9090

# Access Grafana UI
kubectl port-forward svc/grafana-service 3000:3000 -n tracertm
# Open: http://localhost:3000
# Default: admin/admin (CHANGE IN PRODUCTION)
```

### Metrics Endpoints

Each service exposes metrics:

- **Go Backend**: `http://go-backend-service:9090/metrics`
- **Python Backend**: `http://python-backend-service:9091/metrics`
- **Redis**: `http://redis-exporter-service:9121/metrics`
- **NATS**: `http://nats-exporter-service:7777/metrics`
- **PostgreSQL**: `http://postgres-exporter-service:9187/metrics`

### Key Metrics to Monitor

**Application:**
- Request rate, latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query time
- Cache hit rate

**Infrastructure:**
- CPU, memory usage
- Disk I/O, space
- Network throughput
- Pod restarts

### Alerting

Configure Prometheus alerts (add to `prometheus.yml`):

```yaml
alerting:
  alertmanagers:
  - static_configs:
    - targets: ['alertmanager:9093']

rule_files:
  - /etc/prometheus/alerts/*.yml
```

Example alerts:
- High error rate (>5% for 5min)
- High latency (p95 >1s for 5min)
- Pod crash loop
- Disk space <20%

---

## Backup and Restore

### Automated Backups

PostgreSQL automated daily backups via CronJob (in `03-postgres.yaml`):

```bash
# View backup jobs
kubectl get cronjob -n tracertm

# Manually trigger backup
kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%s) -n tracertm

# View backup logs
kubectl logs job/manual-backup-<timestamp> -n tracertm
```

### Manual Backup

```bash
# Backup PostgreSQL
kubectl exec -it postgres-0 -n tracertm -- \
  pg_dump -U tracertm -Fc tracertm > backup-$(date +%Y%m%d).dump

# Backup Redis (RDB snapshot)
kubectl exec -it redis-0 -n tracertm -- redis-cli BGSAVE

# Backup NATS JetStream
kubectl exec -it nats-0 -n tracertm -- \
  tar -czf /tmp/jetstream-backup.tar.gz /data/jetstream

kubectl cp tracertm/nats-0:/tmp/jetstream-backup.tar.gz \
  ./jetstream-backup-$(date +%Y%m%d).tar.gz
```

### Restore from Backup

```bash
# Restore PostgreSQL
cat backup-20260130.dump | \
  kubectl exec -i postgres-0 -n tracertm -- \
  pg_restore -U tracertm -d tracertm --clean

# Restore Redis
kubectl cp dump.rdb tracertm/redis-0:/data/dump.rdb
kubectl delete pod redis-0 -n tracertm  # Restart to load

# Restore NATS
kubectl cp jetstream-backup-20260130.tar.gz tracertm/nats-0:/tmp/
kubectl exec -it nats-0 -n tracertm -- \
  tar -xzf /tmp/jetstream-backup-20260130.tar.gz -C /
kubectl delete pod nats-0 -n tracertm  # Restart
```

### Volume Snapshots

Use Kubernetes VolumeSnapshots for point-in-time recovery:

```bash
# Create snapshot
kubectl create -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snapshot-$(date +%Y%m%d)
  namespace: tracertm
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: postgres-storage-postgres-0
EOF

# Restore from snapshot (update PVC to use snapshot)
```

---

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Check pod status
kubectl get pods -n tracertm

# Describe pod for events
kubectl describe pod <pod-name> -n tracertm

# Check logs
kubectl logs <pod-name> -n tracertm
kubectl logs <pod-name> -n tracertm --previous  # Previous container
```

**Common causes:**
- Image pull errors: Check image name, registry auth
- Resource limits: Increase requests/limits
- Liveness probe failing: Check health endpoint
- Init container failure: Check database connectivity

#### 2. Database Connection Issues

```bash
# Test PostgreSQL connectivity
kubectl exec -it postgres-0 -n tracertm -- psql -U tracertm -c "SELECT 1"

# Check database service
kubectl get svc postgres-service -n tracertm

# Check database logs
kubectl logs postgres-0 -n tracertm

# Test from backend pod
kubectl exec -it <go-backend-pod> -n tracertm -- \
  nc -zv postgres-service 5432
```

#### 3. Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n tracertm

# Check if pods are ready
kubectl get pods -l app=go-backend -n tracertm

# Test service internally
kubectl run -it --rm debug --image=busybox --restart=Never -n tracertm -- \
  wget -O- http://go-backend-service:8080/health
```

#### 4. High Memory Usage

```bash
# Check resource usage
kubectl top pods -n tracertm

# Check OOMKilled events
kubectl get events -n tracertm | grep OOMKilled

# Increase memory limits
kubectl set resources deployment/python-backend \
  --limits=memory=4Gi -n tracertm
```

#### 5. Failed Migrations

```bash
# Check migration init container logs
kubectl logs <python-backend-pod> -c migrations -n tracertm

# Manually run migrations
kubectl exec -it <python-backend-pod> -n tracertm -- \
  alembic upgrade head
```

### Debug Commands

```bash
# Interactive shell in pod
kubectl exec -it <pod-name> -n tracertm -- /bin/sh

# Port forward for local testing
kubectl port-forward svc/python-backend-service 8000:8000 -n tracertm

# View all events
kubectl get events -n tracertm --sort-by='.lastTimestamp'

# Check resource usage
kubectl top nodes
kubectl top pods -n tracertm

# View HPA status
kubectl describe hpa go-backend-hpa -n tracertm

# Check network policies
kubectl get networkpolicies -n tracertm
kubectl describe networkpolicy <policy-name> -n tracertm
```

### Logs Collection

```bash
# Collect all logs
for pod in $(kubectl get pods -n tracertm -o name); do
  echo "=== $pod ===" >> all-logs.txt
  kubectl logs $pod -n tracertm >> all-logs.txt 2>&1
done

# Stream logs from all pods
kubectl logs -f -l app=go-backend -n tracertm --all-containers=true

# Export logs to external system (e.g., Elasticsearch)
# Configure Fluentd/Fluent Bit daemonset
```

---

## Production Checklist

### Pre-Deployment

- [ ] Update all secrets in `02-secrets.yaml`
- [ ] Configure valid TLS certificates
- [ ] Update image references to production registry
- [ ] Review and adjust resource requests/limits
- [ ] Configure persistent storage classes
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerting
- [ ] Review network policies
- [ ] Test disaster recovery procedures

### Security

- [ ] Enable RBAC (Role-Based Access Control)
- [ ] Use Pod Security Standards
- [ ] Enable network policies
- [ ] Rotate secrets regularly
- [ ] Use private container registry
- [ ] Enable audit logging
- [ ] Implement image scanning
- [ ] Use read-only root filesystem where possible
- [ ] Drop all unnecessary capabilities
- [ ] Run containers as non-root

### High Availability

- [ ] Deploy across multiple availability zones
- [ ] Configure Pod Disruption Budgets
- [ ] Set appropriate replica counts (min 2-3)
- [ ] Configure anti-affinity rules
- [ ] Test failover scenarios
- [ ] Configure health checks properly
- [ ] Set up database replication (if needed)

### Performance

- [ ] Configure HPA with appropriate thresholds
- [ ] Set resource requests accurately
- [ ] Enable caching (Redis)
- [ ] Configure connection pooling
- [ ] Optimize database queries
- [ ] Enable gzip compression (nginx)
- [ ] Use fast storage (SSD)

### Monitoring

- [ ] Prometheus scraping all endpoints
- [ ] Grafana dashboards configured
- [ ] Alerts configured and tested
- [ ] Log aggregation set up
- [ ] APM integration (optional)
- [ ] Uptime monitoring (external)

### Compliance

- [ ] Data encryption at rest
- [ ] Data encryption in transit (TLS)
- [ ] Audit logging enabled
- [ ] Access controls documented
- [ ] Compliance checks automated

---

## Next Steps

1. **Review Architecture**: Understand the hybrid backend design
2. **Customize Configuration**: Adjust for your environment
3. **Deploy to Staging**: Test full deployment
4. **Load Testing**: Verify scaling behavior
5. **Production Deploy**: Follow checklist above
6. **Monitor**: Set up dashboards and alerts
7. **Iterate**: Optimize based on metrics

## Support

- **Documentation**: `/docs/deployment/`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Version**: 1.0.0
**Last Updated**: 2026-01-30
