# Load Testing Guide

## Overview

This guide covers the comprehensive load testing suite for TraceRTM, designed to validate performance targets across the Go backend, Python backend, and WebSocket infrastructure.

## Performance Targets

### Go Backend (Port 8080)
- **p95 Latency**: <50ms
- **Throughput**: 10,000 requests/second
- **Use Cases**: CRUD operations, graph queries, search

### Python Backend (Port 8000)
- **p95 Latency**: <500ms
- **Throughput**: 1,000 requests/second
- **Use Cases**: Specification analytics, AI processing

### WebSocket
- **Concurrent Connections**: 1,000+
- **Connection Time**: <5s p95
- **Message Throughput**: 1,000+ messages

## Installation

### Install k6

```bash
# Run the installation script
chmod +x scripts/install_k6.sh
./scripts/install_k6.sh

# Verify installation
k6 version
```

### Manual Installation

**macOS**:
```bash
brew install k6
```

**Linux**:
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 \
  --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D00
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

## Running Load Tests

### Prerequisites

1. **Start the backend services**:
```bash
docker-compose up -d
```

2. **Verify services are healthy**:
```bash
curl http://localhost/health
curl http://localhost:8080/health
curl http://localhost:8000/health
```

### Run All Tests

Execute the complete test suite:

```bash
chmod +x scripts/run_load_tests.sh
./scripts/run_load_tests.sh
```

This runs:
1. Go Items CRUD test
2. Go Graph operations test
3. Python Specification analytics test
4. Python AI streaming test
5. WebSocket connections test
6. End-to-end scenario test

Results are saved to `load-test-results/` and an HTML report is generated.

### Run Individual Tests

**Go Items CRUD**:
```bash
k6 run --out json=load-test-results/go-items.json load-tests/go-items.js
```

**Go Graph Operations**:
```bash
k6 run --out json=load-test-results/go-graph.json load-tests/go-graph.js
```

**Python Specification Analytics**:
```bash
k6 run --out json=load-test-results/python-specs.json load-tests/python-specs.js
```

**Python AI Streaming**:
```bash
k6 run --out json=load-test-results/python-ai.json load-tests/python-ai.js
```

**WebSocket Connections**:
```bash
k6 run --out json=load-test-results/websocket.json load-tests/websocket.js
```

**End-to-End Scenario**:
```bash
k6 run --out json=load-test-results/e2e-scenario.json load-tests/e2e-scenario.js
```

### Custom Configuration

Override default URLs with environment variables:

```bash
GO_BACKEND_URL=http://api.example.com:8080 \
PYTHON_BACKEND_URL=http://api.example.com:8000 \
WS_URL=ws://api.example.com/ws \
k6 run load-tests/go-items.js
```

## Interpreting Results

### HTML Report

After running tests, open the generated HTML report:

```bash
open load-test-results/report.html
```

The report includes:
- **Metrics**: Request duration, throughput, error rates
- **Thresholds**: PASS/FAIL status for performance targets
- **Trends**: Performance over the test duration

### Console Output

k6 provides real-time output during test execution:

```
running (5m00.0s), 0000/1000 VUs, 50000 complete and 0 interrupted iterations
go_items ✓ [======================================] 1000 VUs  5m0s

     ✓ create status 201
     ✓ create has id
     ✓ get status 200

     checks.........................: 100.00% ✓ 150000      ✗ 0
     data_received..................: 50 MB   167 kB/s
     data_sent......................: 25 MB   83 kB/s
     http_req_duration..............: avg=25ms  min=10ms med=22ms max=150ms p(95)=45ms p(99)=80ms
     http_reqs......................: 100000  333.33/s
     iteration_duration.............: avg=3s    min=2.8s med=3s   max=3.5s  p(95)=3.2s p(99)=3.3s
```

### Key Metrics

**Request Duration** (`http_req_duration`):
- `avg`: Average latency
- `p(95)`: 95th percentile latency (target metric)
- `p(99)`: 99th percentile latency
- `max`: Maximum latency

**Request Rate** (`http_reqs`):
- Total number of requests and requests per second

**Error Rate** (`errors`):
- Percentage of failed requests (should be <1%)

**Custom Metrics**:
- `item_create_latency`: Latency for item creation
- `item_get_latency`: Latency for item retrieval

### Threshold Analysis

Thresholds are defined in each test file:

```javascript
thresholds: {
  'http_req_duration{type:create}': ['p(95)<50'],  // 95% under 50ms
  'errors': ['rate<0.01'],                         // Error rate < 1%
  'http_reqs': ['rate>10000'],                     // 10k req/s
}
```

- **Green/PASS**: Performance meets target
- **Red/FAIL**: Performance below target

## Performance Tuning

### Common Bottlenecks

#### 1. Database Connection Pool

**Symptom**: High latency under load, connection timeouts

**Go Backend** (`internal/infrastructure/database/postgres.go`):
```go
config := &DatabaseConfig{
    MaxOpenConns: 100,  // Increase if needed
    MaxIdleConns: 50,   // Keep connections alive
    MaxLifetime:  5 * time.Minute,
}
```

**Python Backend** (`.env`):
```env
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20
```

#### 2. Redis Connection Pool

**Symptom**: Cache misses, slow response times

**Configuration** (`.env`):
```env
REDIS_MAX_CONNECTIONS=100
REDIS_CONNECTION_TIMEOUT=5s
```

#### 3. CPU Bottlenecks

**Symptom**: High CPU usage, slow processing

**Solutions**:
- Scale horizontally (add more instances)
- Optimize algorithms (use indexing, caching)
- Profile code to find hotspots

**Profile Go Backend**:
```bash
go test -cpuprofile=cpu.prof -bench=.
go tool pprof cpu.prof
```

#### 4. Network Latency

**Symptom**: High latency but low CPU/memory usage

**Solutions**:
- Use connection pooling
- Enable HTTP/2
- Reduce payload sizes
- Enable gzip compression

### Nginx Tuning

**Worker Processes** (`nginx/nginx.conf`):
```nginx
worker_processes auto;
worker_connections 4096;

events {
    use epoll;  # Linux
    multi_accept on;
}
```

**Keepalive**:
```nginx
keepalive_timeout 65;
keepalive_requests 100;
```

**Buffering**:
```nginx
client_body_buffer_size 128k;
client_max_body_size 10m;
large_client_header_buffers 4 16k;
```

### PostgreSQL Tuning

**Connection Pooling** (`postgresql.conf`):
```conf
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 128MB
```

**Query Performance**:
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_items_project_id ON items(project_id);
CREATE INDEX idx_items_created_at ON items(created_at);
CREATE INDEX idx_links_source_target ON links(source_id, target_id);
```

### Redis Tuning

**Memory Management** (`redis.conf`):
```conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

**Persistence**:
```conf
# Disable persistence for cache-only usage
save ""
appendonly no
```

## Troubleshooting

### Tests Fail to Connect

**Error**: `connection refused` or `timeout`

**Solution**:
```bash
# Check if services are running
docker-compose ps

# Check health endpoints
curl http://localhost/health
curl http://localhost:8080/health
curl http://localhost:8000/health

# Restart services
docker-compose restart
```

### High Error Rates

**Error**: `errors > 1%` threshold failed

**Solutions**:
1. Check backend logs:
```bash
docker-compose logs go-backend
docker-compose logs python-backend
```

2. Reduce concurrent users in test:
```javascript
stages: [
  { duration: '1m', target: 100 },  // Reduce from 1000
]
```

3. Increase timeout:
```javascript
export const options = {
  timeout: '60s',  // Default is 30s
};
```

### Latency Targets Not Met

**Error**: `p(95) > 50ms` for Go backend

**Solutions**:
1. Enable caching
2. Optimize database queries
3. Add database indexes
4. Scale horizontally
5. Profile and optimize hot code paths

### Memory Issues

**Error**: Out of memory, GC pressure

**Solutions**:
1. Increase container memory limits:
```yaml
# docker-compose.yml
go-backend:
  deploy:
    resources:
      limits:
        memory: 2G
```

2. Tune garbage collection (Go):
```bash
GOGC=200 ./backend  # Run GC less frequently
```

3. Monitor memory usage:
```bash
docker stats
```

## Monitoring During Tests

### Prometheus Metrics

Access Prometheus during tests:
```bash
open http://localhost:9090
```

**Key Queries**:
```promql
# Request rate
rate(http_requests_total[1m])

# Request duration p95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[1m]))

# Error rate
rate(http_requests_total{status=~"5.."}[1m])
```

### Grafana Dashboards

Access Grafana:
```bash
open http://localhost:3000
# Username: admin
# Password: admin
```

Import dashboards from `monitoring/dashboards/`.

## Best Practices

1. **Warm-Up Period**: Start with low load to warm up caches
2. **Ramp-Up Gradually**: Increase load incrementally
3. **Sustained Load**: Test at target load for 2-5 minutes
4. **Peak Load**: Test 2x target load briefly
5. **Ramp-Down**: Gracefully decrease load
6. **Baseline**: Run tests regularly to detect regressions
7. **Production-Like**: Use realistic data and scenarios
8. **Monitor Resources**: Watch CPU, memory, disk I/O
9. **Cleanup**: Clear test data between runs
10. **Document Results**: Track performance over time

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/load-tests.yml`:

```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start services
        run: docker-compose up -d

      - name: Wait for services
        run: sleep 30

      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
            --keyserver hkp://keyserver.ubuntu.com:80 \
            --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D00
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
            sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load tests
        run: ./scripts/run_load_tests.sh

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: load-test-results/
```

## Advanced Topics

### Custom Scenarios

Define complex user behaviors:

```javascript
export const options = {
  scenarios: {
    read_heavy: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 500 },
      ],
      exec: 'readScenario',
    },
    write_heavy: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },
      ],
      exec: 'writeScenario',
    },
  },
};

export function readScenario() {
  http.get(`${BASE_URL}/api/v1/items`);
}

export function writeScenario() {
  http.post(`${BASE_URL}/api/v1/items`, payload);
}
```

### Data-Driven Testing

Use external data files:

```javascript
import { SharedArray } from 'k6/data';

const testData = new SharedArray('test data', function() {
  return JSON.parse(open('./test-data.json'));
});

export default function() {
  const item = testData[__VU % testData.length];
  http.post(`${BASE_URL}/api/v1/items`, JSON.stringify(item));
}
```

### Cloud Testing

Run tests from multiple regions using k6 Cloud:

```bash
k6 cloud load-tests/go-items.js
```

## Resources

- [k6 Documentation](https://k6.io/docs/)
- [Performance Testing Best Practices](https://k6.io/docs/testing-guides/test-types/)
- [Grafana k6 OSS](https://github.com/grafana/k6)
- [Prometheus Metrics](https://prometheus.io/docs/introduction/overview/)
