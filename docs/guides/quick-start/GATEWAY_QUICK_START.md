# API Gateway Quick Start Guide

Get the TracerTM API Gateway running in under 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- Ports 80, 443, 3000, 8080, 8000, 5432, 6379, 4222, 9090 available

## Quick Start

### 1. Configure Environment

```bash
cp .env.gateway .env
# Edit .env and set secure passwords
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

Expected output:
```
NAME                          STATUS
tracertm-nginx                Up (healthy)
tracertm-go-backend           Up (healthy)
tracertm-python-backend       Up (healthy)
tracertm-postgres             Up (healthy)
tracertm-redis                Up (healthy)
tracertm-nats                 Up (healthy)
```

### 3. Verify Health

```bash
curl http://localhost/health        # Main health
curl http://localhost/health/go     # Go backend
curl http://localhost/health/python # Python backend
```

All should return HTTP 200.

### 4. Run Test Suite

```bash
chmod +x ./scripts/test_gateway.sh
./scripts/test_gateway.sh
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| API Gateway | http://localhost | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Go Backend (direct) | http://localhost:8080 | - |
| Python Backend (direct) | http://localhost:4000 | - |

## API Endpoints

### Go Backend (High Performance)

```bash
# Items
curl http://localhost/api/v1/items

# Links
curl http://localhost/api/v1/links

# Projects
curl http://localhost/api/v1/projects

# Graph
curl http://localhost/api/v1/graph

# Search
curl http://localhost/api/v1/search
```

### Python Backend (AI & Analytics)

```bash
# AI
curl http://localhost/api/v1/ai/health

# Specifications
curl http://localhost/api/v1/specifications

# Analytics
curl http://localhost/api/v1/spec-analytics

# Auth
curl http://localhost/api/v1/auth/health
```

### WebSocket

```bash
# Install wscat if needed
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost/ws
```

## Monitoring

### Grafana Dashboard

1. Open http://localhost:3000
2. Login: admin/admin
3. Navigate to Dashboards → Backend Performance Comparison

Metrics available:
- Request rate by backend
- Response time (p50, p95, p99)
- Error rates
- Cache hit ratio
- WebSocket connections
- CPU/Memory usage

### Prometheus Queries

Access http://localhost:9090 and try:

```promql
# Request rate
rate(http_requests_total[5m])

# Response time (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Cache hit rate
rate(nginx_cache_hits_total[5m]) / (rate(nginx_cache_hits_total[5m]) + rate(nginx_cache_misses_total[5m]))
```

## Testing Features

### Rate Limiting

```bash
# Trigger rate limit (100 req/s default)
for i in {1..110}; do curl http://localhost/api/v1/items; done
# Should see: HTTP 429 Too Many Requests
```

### Caching

```bash
# First request - cache miss
curl -I http://localhost/api/v1/items
# X-Cache-Status: MISS

# Second request - cache hit
curl -I http://localhost/api/v1/items
# X-Cache-Status: HIT
```

### Load Balancing

```bash
# Multiple requests show distributed load
for i in {1..10}; do
  curl -s http://localhost/api/v1/items | jq '.backend'
done
```

### WebSocket

```bash
# Connect and send message
wscat -c ws://localhost/ws
Connected (press CTRL+C to quit)
> {"type": "ping"}
< {"type": "pong"}
```

## Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nginx
docker-compose logs -f go-backend
docker-compose logs -f python-backend
```

### Restart Services

```bash
# Restart Nginx only
docker-compose restart nginx

# Restart all
docker-compose restart
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Update Configuration

```bash
# After editing nginx conf files
docker-compose exec nginx nginx -t  # Test config
docker-compose restart nginx        # Apply changes
```

## Development Mode

For local development with hot reload:

```bash
# Start only infrastructure
docker-compose up -d postgres redis nats nginx

# Run backends locally
cd backend && go run main.go  # Port 8080
cd src && uvicorn tracertm.api.main:app --reload  # Port 8000

# Frontend points to localhost
VITE_API_URL=http://localhost bun run dev
```

The Nginx gateway will automatically route requests to the appropriate backend based on the path.

## Production Deployment

### 1. SSL/TLS Setup

```bash
# Get Let's Encrypt certificate
docker-compose run --rm certbot certonly --webroot \
  -w /var/www/certbot \
  -d tracertm.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos

# Update nginx/conf.d/ssl.conf with your domain
sed -i 's/tracertm.example.com/tracertm.yourdomain.com/g' nginx/conf.d/ssl.conf

# Restart Nginx
docker-compose restart nginx
```

### 2. Secure Environment

```bash
# Generate secure passwords
export DB_PASSWORD=$(openssl rand -base64 32)
export GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 32)

# Update .env
echo "DB_PASSWORD=$DB_PASSWORD" >> .env
echo "GRAFANA_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD" >> .env
```

### 3. Production Deploy

```bash
# Pull latest images
docker-compose pull

# Deploy with zero downtime
docker-compose up -d --remove-orphans

# Verify health
./scripts/test_gateway.sh
```

## Troubleshooting

### 502 Bad Gateway

```bash
# Check backend health
docker-compose ps
docker-compose logs go-backend
docker-compose logs python-backend

# Verify network
docker-compose exec nginx ping go-backend
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart heavy services
docker-compose restart python-backend
```

### Slow Response Times

```bash
# Check Grafana for bottlenecks
# Look at: Response Time by Backend dashboard

# Clear cache if stale
docker-compose exec nginx rm -rf /var/cache/nginx/*
docker-compose restart nginx
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose logs postgres
docker-compose exec postgres psql -U tracertm -d tracertm -c "SELECT 1;"

# Reset connections
docker-compose restart go-backend python-backend
```

## Performance Tuning

### Increase Worker Processes

Edit `nginx/nginx.conf`:
```nginx
worker_processes auto;  # Use all CPU cores
worker_connections 8192; # Handle more concurrent connections
```

### Adjust Cache Size

Edit `nginx/conf.d/tracertm.conf`:
```nginx
proxy_cache_path /var/cache/nginx/go
    keys_zone=go_cache:100m  # Increase to 100MB
    max_size=10g;            # Increase to 10GB
```

### Increase Rate Limits

Edit `nginx/conf.d/tracertm.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=500r/s;  # 500 req/s
```

## Next Steps

1. **Configure monitoring alerts** in Grafana
2. **Set up log aggregation** (ELK stack, Loki, etc.)
3. **Enable HTTPS** for production
4. **Configure backup strategy** for PostgreSQL
5. **Set up CI/CD pipeline** for deployments
6. **Load test** with realistic traffic patterns

## Resources

- [Full Documentation](./nginx/README.md)
- [Test Suite](./scripts/test_gateway.sh)
- [Nginx Config](./nginx/conf.d/tracertm.conf)
- [Monitoring Dashboard](./monitoring/dashboards/backend-comparison.json)

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Run tests: `./scripts/test_gateway.sh`
3. Review Grafana metrics
4. Check Nginx config: `docker-compose exec nginx nginx -t`
