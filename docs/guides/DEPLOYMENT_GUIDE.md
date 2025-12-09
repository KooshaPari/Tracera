# TraceRTM Deployment Guide

Complete guide for deploying TraceRTM to production.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Configuration](#configuration)
3. [Docker Compose Deployment](#docker-compose-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **Kubernetes**: 1.28+ (for K8s deployment)
- **kubectl**: 1.28+
- **Helm**: 3.12+ (optional, recommended)

### Required Resources

**Minimum** (Development/Testing):
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD

**Recommended** (Production):
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 200+ GB SSD
- Network: 1 Gbps+

### Cloud Provider Setup

**AWS**:
- EKS cluster (1.28+)
- RDS PostgreSQL (15+) with pgvector
- ElastiCache Redis (7.0+)
- Application Load Balancer
- Route 53 for DNS
- ACM for SSL certificates

**GCP**:
- GKE cluster (1.28+)
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Load Balancing
- Cloud DNS
- Managed SSL certificates

**Azure**:
- AKS cluster (1.28+)
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Application Gateway
- Azure DNS
- SSL certificates

---

## Configuration

### 1. Environment Variables

Create environment files for each environment:

**Staging** (`.env.staging`):
```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=tracertm
DB_PASSWORD=<generate-secure-password>
DB_NAME=tracertm_staging
DB_SSL_MODE=require

# Redis
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=<generate-secure-password>

# NATS
NATS_URL=nats://nats:4222
NATS_CLUSTER_ID=tracertm-staging

# Backend
PORT=8080
ENV=staging
LOG_LEVEL=info
JWT_SECRET=<generate-secure-secret>
WORKOS_API_KEY=<your-workos-key>
WORKOS_CLIENT_ID=<your-workos-client-id>

# Frontend
NEXT_PUBLIC_API_URL=https://api-staging.tracertm.com
NEXT_PUBLIC_WS_URL=wss://api-staging.tracertm.com/ws
```

**Production** (`.env.production`):
```bash
# Same as staging but with production values
DB_HOST=prod-postgres.tracertm.com
# ... etc
```

### 2. Secrets Management

**Using Kubernetes Secrets**:
```bash
# Create secrets from file
kubectl create secret generic tracertm-secrets \
  --from-env-file=.env.production \
  --namespace=tracertm-production

# Or create individual secrets
kubectl create secret generic db-credentials \
  --from-literal=username=tracertm \
  --from-literal=password=$(openssl rand -base64 32) \
  --namespace=tracertm-production
```

**Using HashiCorp Vault** (Recommended for Production):
```bash
# Store secrets in Vault
vault kv put secret/tracertm/production \
  db_password="$(openssl rand -base64 32)" \
  jwt_secret="$(openssl rand -base64 64)" \
  workos_api_key="your-key"

# Use Vault agent injector in K8s
```

### 3. Database Configuration

**Initialize pgvector extension**:
```sql
-- Connect to database
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For full-text search
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;  -- For query analysis
```

**Configure PostgreSQL** (`postgresql.conf`):
```conf
# Performance tuning
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 16MB
min_wal_size = 1GB
max_wal_size = 4GB

# Connection settings
max_connections = 200
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_lock_waits = on
log_temp_files = 0
```

---

## Docker Compose Deployment

### Quick Start

1. **Clone repository**:
```bash
git clone https://github.com/kooshapari/tracertm.git
cd tracertm
```

2. **Configure environment**:
```bash
cp .env.example .env.production
# Edit .env.production with your values
```

3. **Start services**:
```bash
docker-compose up -d
```

4. **Verify deployment**:
```bash
docker-compose ps
curl http://localhost:8080/health
```

### Custom Configuration

**docker-compose.override.yml**:
```yaml
version: '3.8'

services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### SSL with Docker Compose

**Using Let's Encrypt**:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - backend
```

---

## Kubernetes Deployment

### 1. Cluster Setup

**Create EKS cluster** (AWS):
```bash
eksctl create cluster \
  --name tracertm-production \
  --version 1.28 \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed
```

**Create GKE cluster** (GCP):
```bash
gcloud container clusters create tracertm-production \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n2-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade
```

### 2. Deploy Using Script

```bash
./scripts/deploy.sh production v1.0.0
```

### 3. Manual Deployment

**Step-by-step**:

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create secrets
kubectl apply -f k8s/secret.yaml

# 3. Create ConfigMaps
kubectl apply -f k8s/configmap.yaml

# 4. Deploy databases
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/nats-deployment.yaml

# 5. Wait for databases
kubectl wait --for=condition=ready pod -l app=postgres -n tracertm --timeout=300s

# 6. Run migrations
kubectl exec -n tracertm deployment/tracertm-backend -- ./migrate up

# 7. Deploy applications
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/api-deployment.yaml

# 8. Deploy ingress
kubectl apply -f k8s/ingress.yaml

# 9. Deploy monitoring
kubectl apply -f k8s/monitoring.yaml

# 10. Deploy autoscaling
kubectl apply -f k8s/hpa.yaml
```

### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n tracertm

# Check services
kubectl get svc -n tracertm

# Check ingress
kubectl get ingress -n tracertm

# Check logs
kubectl logs -f deployment/tracertm-backend -n tracertm

# Check health
curl https://api.tracertm.com/health
```

---

## Monitoring Setup

### 1. Prometheus

**Install Prometheus Operator**:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values monitoring/prometheus-values.yaml
```

**Apply custom configuration**:
```bash
kubectl apply -f monitoring/prometheus.yml
kubectl apply -f monitoring/alerts/backend.yml
```

### 2. Grafana

**Access Grafana**:
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

**Import dashboards**:
```bash
kubectl apply -f monitoring/grafana/dashboards/
```

Default credentials:
- Username: `admin`
- Password: (retrieve with) `kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`

### 3. Alerting

**Configure AlertManager**:
```yaml
# alertmanager-config.yaml
global:
  resolve_timeout: 5m
  slack_api_url: '<your-slack-webhook>'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'slack-notifications'

receivers:
- name: 'slack-notifications'
  slack_configs:
  - channel: '#alerts'
    title: 'TraceRTM Alert'
    text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

---

## SSL/TLS Configuration

### Using cert-manager (Recommended)

**Install cert-manager**:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

**Create ClusterIssuer**:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@tracertm.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

**Update Ingress**:
```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.tracertm.com
    secretName: tracertm-tls
```

---

## Backup and Recovery

### Database Backups

**Automated backups with CronJob**:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: tracertm
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgres -U tracertm tracertm | \
              gzip > /backups/backup-$(date +%Y%m%d-%H%M%S).sql.gz

              # Upload to S3
              aws s3 cp /backups/backup-*.sql.gz s3://tracertm-backups/
          restartPolicy: OnFailure
```

**Manual backup**:
```bash
kubectl exec -n tracertm postgres-0 -- \
  pg_dump -U tracertm tracertm | \
  gzip > backup-$(date +%Y%m%d).sql.gz
```

**Restore from backup**:
```bash
gunzip -c backup-20231129.sql.gz | \
  kubectl exec -i -n tracertm postgres-0 -- \
  psql -U tracertm tracertm
```

---

## Troubleshooting

### Common Issues

**1. Pod Not Starting**
```bash
# Check pod status
kubectl describe pod <pod-name> -n tracertm

# Check logs
kubectl logs <pod-name> -n tracertm

# Check events
kubectl get events -n tracertm --sort-by='.lastTimestamp'
```

**2. Database Connection Issues**
```bash
# Test connection from pod
kubectl exec -it deployment/tracertm-backend -n tracertm -- \
  psql -h postgres -U tracertm -d tracertm

# Check database logs
kubectl logs -n tracertm postgres-0
```

**3. High Memory Usage**
```bash
# Check resource usage
kubectl top pods -n tracertm

# Increase memory limits
kubectl set resources deployment tracertm-backend \
  --limits=memory=2Gi \
  --requests=memory=1Gi \
  -n tracertm
```

**4. Slow Queries**
```bash
# Check slow queries
kubectl exec -n tracertm postgres-0 -- \
  psql -U tracertm -d tracertm -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

### Debug Mode

**Enable debug logging**:
```bash
kubectl set env deployment/tracertm-backend LOG_LEVEL=debug -n tracertm
```

### Performance Tuning

**Adjust HPA**:
```bash
kubectl autoscale deployment tracertm-backend \
  --cpu-percent=70 \
  --min=3 \
  --max=15 \
  -n tracertm
```

---

## Production Checklist

Before going live:

- [ ] SSL certificates configured
- [ ] Database backups scheduled
- [ ] Monitoring and alerting active
- [ ] Resource limits configured
- [ ] Auto-scaling enabled
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] Runbooks prepared
- [ ] On-call rotation established
- [ ] Rollback procedure tested

---

## Support

For deployment assistance:
- Documentation: https://docs.tracertm.com
- GitHub Issues: https://github.com/kooshapari/tracertm/issues
- Email: support@tracertm.com

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
