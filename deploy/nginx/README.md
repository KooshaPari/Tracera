# TracerTM Nginx API Gateway

Production-ready Nginx configuration for intelligent routing between Go and Python backends.

## Architecture Overview

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Nginx API Gateway               │
│  - Rate limiting                        │
│  - Load balancing                       │
│  - Caching (Go endpoints)               │
│  - SSL/TLS termination                  │
│  - Security headers                     │
└─────────┬───────────────────────────────┘
          │
          ├──────────────────┬──────────────────┐
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │    Go    │      │  Python  │      │   NATS   │
    │ Backend  │      │ Backend  │      │  Queue   │
    └────┬─────┘      └────┬─────┘      └──────────┘
         │                 │
         └────────┬────────┘
                  ▼
          ┌──────────────┐
          │  PostgreSQL  │
          │    Redis     │
          └──────────────┘
```

## Backend Routing Strategy

### Python Backend (AI & Analytics)
Handles compute-intensive and AI operations:
- `/api/v1/ai/*` - AI/LLM operations
- `/api/v1/specifications/*` - Specification management
- `/api/v1/spec-analytics/*` - Analytics
- `/api/v1/execution/*` - Test execution
- `/api/v1/mcp/*` - MCP operations
- `/api/v1/auth/*` - Authentication
- `/api/v1/blockchain/*` - Blockchain operations

### Go Backend (High Performance)
Handles high-throughput CRUD operations:
- `/api/v1/items/*` - Item management
- `/api/v1/links/*` - Link management
- `/api/v1/projects/*` - Project management
- `/api/v1/graph/*` - Graph operations
- `/api/v1/bulk/*` - Bulk operations
- `/api/v1/search/*` - Search
- `/api/v1/webhooks/*` - Webhook management
- `/api/v1/traceability/*` - Traceability matrix

### WebSocket
- `/ws` - Real-time updates (Go backend only)

## Features

### 1. Rate Limiting
- **API Limit**: 100 requests/second with burst of 50
- **AI Limit**: 10 requests/second with burst of 20
- **Connection Limit**: 50 concurrent connections per IP

### 2. Caching
- Go backend GET requests cached for 5 minutes
- Cache key includes request URI and body
- X-Cache-Status header shows HIT/MISS/BYPASS

### 3. Load Balancing
- Keepalive connections (32 for Python, 64 for Go)
- Health-based failover (3 max fails, 30s timeout)

### 4. Security
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- CORS support
- SSL/TLS with modern cipher suites
- HSTS enabled (production)

### 5. Monitoring
- Prometheus metrics at `/metrics`
- Detailed access logs with backend routing info
- Health checks for both backends

## Setup

### Development

1. **Start services**:
   ```bash
   docker-compose up -d
   ```

2. **Verify health**:
   ```bash
   curl http://localhost/health
   curl http://localhost/health/go
   curl http://localhost/health/python
   ```

3. **Run tests**:
   ```bash
   ./scripts/test_gateway.sh
   ```

### Production

1. **Update SSL certificates**:
   - Place certificates in `nginx/certs/`
   - Update `ssl.conf` with your domain name

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Deploy**:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

4. **Enable SSL**:
   - Uncomment SSL configuration in `nginx/conf.d/ssl.conf`
   - Restart Nginx: `docker-compose restart nginx`

## SSL/TLS Setup

### Using Let's Encrypt

1. **Install certbot**:
   ```bash
   docker-compose run --rm certbot certonly --webroot \
     -w /var/www/certbot \
     -d tracertm.example.com \
     --email admin@example.com \
     --agree-tos
   ```

2. **Update SSL config**:
   - Edit `nginx/conf.d/ssl.conf`
   - Change `tracertm.example.com` to your domain

3. **Enable auto-renewal**:
   ```bash
   # Add to crontab
   0 0 * * * docker-compose run --rm certbot renew
   ```

### Using Custom Certificates

Place your certificates in `nginx/certs/`:
- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key
- `chain.pem` - CA certificate chain

## Monitoring

### Prometheus Metrics

Access Prometheus at `http://localhost:9090`

Key metrics:
- `http_requests_total` - Request count by backend
- `http_request_duration_seconds` - Response time
- `nginx_cache_hits_total` - Cache hits
- `nginx_cache_misses_total` - Cache misses

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (admin/admin)

Pre-configured dashboards:
- Backend Performance Comparison
- Request Rate & Latency
- Cache Hit Ratio
- Error Rates

### Nginx Logs

View logs in real-time:
```bash
docker-compose logs -f nginx
```

Log format includes:
- Backend address (`backend=`)
- Cache status (`cache=`)
- Request time (`rt=`)
- Upstream response time (`urt=`)

## Performance Tuning

### Worker Processes

Edit `nginx/nginx.conf`:
```nginx
worker_processes auto;  # Auto-detect CPU cores
worker_connections 4096; # Connections per worker
```

### Buffer Sizes

Adjust based on your payload sizes:
```nginx
client_body_buffer_size 1M;    # Request body buffer
client_max_body_size 100M;     # Max upload size
```

### Cache Settings

Tune cache size and TTL:
```nginx
proxy_cache_path /var/cache/nginx/go
    levels=1:2
    keys_zone=go_cache:10m    # Cache metadata (10MB)
    max_size=1g                # Max cache size (1GB)
    inactive=60m;              # Evict after 60min inactive
```

### Timeouts

Adjust for your workload:
```nginx
proxy_connect_timeout 60s;   # Connection timeout
proxy_send_timeout 300s;     # Send timeout
proxy_read_timeout 300s;     # Read timeout (increase for AI)
```

## Troubleshooting

### 502 Bad Gateway

1. Check backend health:
   ```bash
   docker-compose ps
   docker-compose logs go-backend
   docker-compose logs python-backend
   ```

2. Verify network connectivity:
   ```bash
   docker-compose exec nginx ping go-backend
   docker-compose exec nginx ping python-backend
   ```

### 429 Too Many Requests

Rate limit triggered. Adjust limits in `tracertm.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
```

### Cache Not Working

1. Check cache directory exists:
   ```bash
   docker-compose exec nginx ls -la /var/cache/nginx/
   ```

2. Verify cache headers:
   ```bash
   curl -I http://localhost/api/v1/items
   # Look for: X-Cache-Status: HIT
   ```

### SSL Issues

1. Verify certificate paths:
   ```bash
   docker-compose exec nginx ls -la /etc/nginx/certs/
   ```

2. Test SSL configuration:
   ```bash
   docker-compose exec nginx nginx -t
   ```

## Testing

### Manual Testing

```bash
# Test Go backend route
curl http://localhost/api/v1/items

# Test Python backend route
curl http://localhost/api/v1/ai/health

# Test WebSocket
wscat -c ws://localhost/ws

# Test health checks
curl http://localhost/health
curl http://localhost/health/go
curl http://localhost/health/python

# Test rate limiting
for i in {1..110}; do curl http://localhost/api/v1/items; done

# Test cache
curl -I http://localhost/api/v1/items
curl -I http://localhost/api/v1/items  # Should show X-Cache-Status: HIT
```

### Automated Testing

```bash
./scripts/test_gateway.sh
```

## Configuration Files

### Main Configuration
- `nginx/nginx.conf` - Main Nginx configuration
- `nginx/conf.d/tracertm.conf` - API Gateway routing rules
- `nginx/conf.d/ssl.conf` - SSL/TLS configuration

### Monitoring
- `monitoring/prometheus.yml` - Prometheus scrape config
- `monitoring/dashboards/backend-comparison.json` - Grafana dashboard

### Docker
- `docker-compose.yml` - Production deployment
- `.env` - Environment variables

## Best Practices

1. **Always use HTTPS in production**
2. **Monitor cache hit rates** - Aim for >70%
3. **Set appropriate rate limits** based on load testing
4. **Enable access logs** for troubleshooting
5. **Use health checks** for automatic failover
6. **Keep Nginx updated** for security patches
7. **Monitor backend response times** and adjust timeouts
8. **Use connection pooling** (keepalive) for performance

## Support

For issues or questions:
1. Check logs: `docker-compose logs nginx`
2. Verify configuration: `docker-compose exec nginx nginx -t`
3. Run test suite: `./scripts/test_gateway.sh`
4. Review metrics in Grafana

## License

Proprietary - TracerTM
