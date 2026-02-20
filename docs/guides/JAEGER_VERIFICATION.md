# Jaeger Trace Export Verification Guide

This guide provides step-by-step instructions to verify that Jaeger trace export is working correctly for both Go and Python backends.

## Quick Start Verification (2 minutes)

### 1. Start the Stack

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
docker compose up
```

Wait for all services to be healthy:
```
tracertm-jaeger: healthy
tracertm-postgres: healthy
tracertm-redis: healthy
tracertm-nats: healthy
tracertm-go-backend: healthy
tracertm-python-backend: healthy
```

### 2. Access Jaeger UI

Open your browser and navigate to:
```
http://localhost:16686
```

You should see the Jaeger UI with a list of services.

### 3. Verify Services Appear

In the left sidebar dropdown labeled "Service", you should see:
- `tracertm-backend` (Go backend)
- `tracertm-python-backend` (Python backend)

If services don't appear immediately, wait 10-15 seconds and refresh.

### 4. Generate Some Traces

Make a request to the Go backend API:
```bash
curl http://localhost:8080/api/v1/health
```

Or to the Python backend:
```bash
curl http://localhost:8000/health
```

### 5. View Traces in Jaeger

1. Select `tracertm-backend` from the Service dropdown
2. Click "Find Traces"
3. You should see traces appear in the timeline
4. Click on any trace to view the detailed breakdown

## Detailed Verification Checklist

### Checklist: Docker Compose Configuration

- [ ] Jaeger service is defined in docker-compose.yml
- [ ] Jaeger has port 4317 (OTLP gRPC) exposed
- [ ] Jaeger has port 16686 (UI) exposed
- [ ] Go backend has `JAEGER_ENDPOINT=jaeger:4317` environment variable
- [ ] Go backend has `JAEGER_ENVIRONMENT=docker` environment variable
- [ ] Python backend has `TRACING_ENABLED=true` environment variable
- [ ] Python backend has `OTLP_ENDPOINT=jaeger:4317` environment variable
- [ ] Python backend has `JAEGER_ENDPOINT=jaeger:4317` environment variable
- [ ] Python backend has `TRACING_ENVIRONMENT=docker` environment variable
- [ ] Both backends depend on `jaeger: condition: service_started`

**Verify:**
```bash
grep -A 30 "jaeger:" docker-compose.yml | head -40
grep "JAEGER_ENDPOINT" docker-compose.yml
grep "TRACING_ENABLED" docker-compose.yml
```

### Checklist: Service Startup Logs

Start Jaeger and check logs:
```bash
docker logs tracertm-jaeger
```

Should show:
```
COLLECTOR_OTLP_ENABLED: true
```

Start Go backend and check logs:
```bash
docker logs tracertm-go-backend
```

Should show:
```
🔍 Initializing distributed tracing (Jaeger endpoint: jaeger:4317, env: docker)
✅ Distributed tracing initialized successfully
```

Start Python backend and check logs:
```bash
docker logs tracertm-python-backend
```

Should show:
```
Initializing distributed tracing (service: tracertm-python-backend, env: docker, endpoint: jaeger:4317)
✅ Distributed tracing initialized successfully
✅ APM instrumentation enabled
```

**Verify:**
```bash
docker logs tracertm-go-backend 2>&1 | grep -i "tracing"
docker logs tracertm-python-backend 2>&1 | grep -i "tracing\|apm"
```

### Checklist: Network Connectivity

Verify Jaeger is reachable from backends:

From Go backend container:
```bash
docker exec tracertm-go-backend nc -zv jaeger 4317 && echo "✅ Go can reach Jaeger"
```

From Python backend container:
```bash
docker exec tracertm-python-backend nc -zv jaeger 4317 && echo "✅ Python can reach Jaeger"
```

From local machine:
```bash
curl http://localhost:16686 && echo "✅ Jaeger UI is accessible"
```

### Checklist: Trace Export

#### Test Go Backend Traces

1. Make a request to Go API:
```bash
curl -v http://localhost:8080/api/v1/health
```

2. In Jaeger UI:
   - Service: `tracertm-backend`
   - Operation: (leave blank or select `/api/v1/health`)
   - Click "Find Traces"
   - Should see trace within 5-10 seconds

3. Click on the trace to view details:
   - Should show span timeline
   - Should show HTTP span with status 200
   - Should show metadata and attributes

#### Test Python Backend Traces

1. Make a request to Python API:
```bash
curl -v http://localhost:8000/health
```

2. In Jaeger UI:
   - Service: `tracertm-python-backend`
   - Operation: (leave blank or select `/health`)
   - Click "Find Traces"
   - Should see trace within 5-10 seconds

3. Click on the trace to view details:
   - Should show span timeline
   - Should show HTTP span with method and path
   - Should show response status and metadata

#### Test Cross-Service Tracing

Make a request from Go to Python:

```bash
curl http://localhost:8080/api/v1/projects
```

This should trigger:
1. HTTP request to Go backend (/api/v1/projects)
2. HTTP client span in Go to call Python
3. HTTP server span in Python for the same request
4. All spans should have the same trace ID

In Jaeger UI:
1. Select either service
2. Find Traces
3. Click on a cross-service trace
4. You should see spans from both Go and Python with the same trace ID

**Verify trace context propagation:**
```bash
# Make a verbose request and check headers
curl -v http://localhost:8080/api/v1/projects 2>&1 | grep -i "traceparent\|trace-"
```

### Checklist: Span Attributes

Click on a trace and expand individual spans. Verify these attributes are present:

**Go backend spans:**
- `service.name`: `tracertm-backend`
- `service.version`: `1.0.0`
- `deployment.environment`: `docker`
- `library.language`: `go`
- `http.method`: GET, POST, etc.
- `http.status_code`: 200, 404, etc.
- `http.route`: API endpoint path

**Python backend spans:**
- `service.name`: `tracertm-python-backend`
- `service.version`: `1.0.0`
- `deployment.environment`: `docker`
- `library.language`: `python`
- `http.method`: GET, POST, etc.
- `http.status_code`: 200, 404, etc.

### Checklist: Error Traces

Trigger an error and verify it's captured:

1. Make a request that causes an error:
```bash
curl http://localhost:8080/api/v1/nonexistent
```

2. In Jaeger UI:
   - Find the trace (should appear within seconds)
   - Look for error tags (red warning icon)
   - Click on the span with error
   - Should show error details in "Tags" section
   - Should show error message and type

### Checklist: Performance Metrics

In Jaeger UI, verify performance data:

1. **Latency:** Click on a service, then "Service Performance"
   - Should show P50, P95, P99 latencies
   - Values should be reasonable (ms range)

2. **Request Rate:** Should show request counts per operation
   - Increasing as you generate more requests

3. **Error Rate:** Should show error percentages
   - Should be 0% for successful requests
   - Should increase when you generate errors

## Troubleshooting

### Symptoms: Jaeger UI shows "No Services Found"

**Cause:** Traces haven't been exported yet or backends can't reach Jaeger.

**Solution:**
```bash
# 1. Check Jaeger is running and healthy
docker ps | grep jaeger

# 2. Check if Jaeger logs show it's listening
docker logs tracertm-jaeger | tail -20

# 3. Check backend logs for export errors
docker logs tracertm-go-backend 2>&1 | grep -i "error\|fail"
docker logs tracertm-python-backend 2>&1 | grep -i "error\|fail"

# 4. Make a test request to generate traces
curl http://localhost:8080/api/v1/health
curl http://localhost:8000/health

# 5. Wait 10-15 seconds for batch processing
# (default batch timeout is 5 seconds, may need buffer)

# 6. Refresh Jaeger UI
```

### Symptoms: Services appear but no traces found

**Cause:** Backends are not making requests or sampling is disabled.

**Solution:**
```bash
# 1. Generate more requests
for i in {1..10}; do curl http://localhost:8080/api/v1/health; done

# 2. Check sampling configuration (should be 100% in dev)
# Go: Always sample (checked in tracer.go)
# Python: Always sample (checked in tracing.py)

# 3. Check batch processor settings
# Go: Default timeout 5s, batch size 512
# Python: Default timeout 5s, batch size 512

# 4. Wait longer (up to 10 seconds)
sleep 10
# Then refresh Jaeger UI
```

### Symptoms: Only one service shows, not both

**Cause:** One backend can't reach Jaeger or isn't exporting.

**Solution:**
```bash
# Check which backends can reach Jaeger
docker exec tracertm-go-backend nc -zv jaeger 4317
docker exec tracertm-python-backend nc -zv jaeger 4317

# Check network configuration
docker network inspect tracertm

# Verify endpoints in docker-compose.yml
grep "JAEGER_ENDPOINT\|OTLP_ENDPOINT" docker-compose.yml

# Restart the backend that's not showing
docker restart tracertm-go-backend
# or
docker restart tracertm-python-backend
```

### Symptoms: Traces show but missing attributes

**Cause:** Instrumentation not fully initialized or configured.

**Solution:**
```bash
# 1. Check Python backend has TRACING_ENABLED=true
docker exec tracertm-python-backend env | grep TRACING_ENABLED

# 2. Check environment variables are set correctly
docker exec tracertm-go-backend env | grep JAEGER
docker exec tracertm-python-backend env | grep OTLP

# 3. Check Go backend tracing is enabled
docker logs tracertm-go-backend 2>&1 | grep -i "tracing\|distributed"

# 4. Restart backends if env vars changed
docker restart tracertm-go-backend tracertm-python-backend
```

### Symptoms: Jaeger shows high memory usage

**Cause:** Too many traces being stored in memory.

**Solution:**
```bash
# Check current trace count in Jaeger
curl http://localhost:16686/api/traces | jq '.data | length'

# If high, either:
# 1. Reduce sampling rate (change sampler config)
# 2. Reduce request volume
# 3. Use persistent storage (Elasticsearch backend)

# Clear Jaeger in-memory storage
docker restart tracertm-jaeger
```

## Advanced Verification

### API-Based Verification

Query Jaeger API directly to verify traces:

```bash
# List all services
curl http://localhost:16686/api/services | jq .data

# Get traces for specific service
curl "http://localhost:16686/api/traces?service=tracertm-backend&limit=10" | jq '.data[0]'

# Get specific trace by ID
TRACE_ID="<replace-with-id>"
curl "http://localhost:16686/api/traces/$TRACE_ID" | jq .
```

### Log-Based Verification

Check what the backends are actually exporting:

```bash
# Enable debug logging in Go (set environment variable before starting)
# OTEL_SDK_DISABLED_SPANS=false

# Enable debug logging in Python
# OTEL_LOG_LEVEL=debug

# Then restart and check logs
docker restart tracertm-go-backend tracertm-python-backend
docker logs -f tracertm-go-backend 2>&1 | grep -i "span\|trace\|export"
docker logs -f tracertm-python-backend 2>&1 | grep -i "span\|trace\|export"
```

### Network Sniffing (Advanced)

Verify OTLP data is flowing on port 4317:

```bash
# Install tcpdump if needed
# brew install tcpdump

# Capture traffic to Jaeger
sudo tcpdump -i docker0 -nn port 4317 -w /tmp/jaeger.pcap

# Make a request to generate traces
curl http://localhost:8080/api/v1/health

# Analyze captured packets
tcpdump -r /tmp/jaeger.pcap -A | head -50
```

## Verification Report Template

Use this template to document your verification:

```markdown
## Jaeger Trace Export Verification Report

**Date:** [Date]
**Environment:** [Docker/Local/Production]
**Reviewer:** [Name]

### Configuration
- [ ] docker-compose.yml has Jaeger service with correct ports
- [ ] Go backend env vars set: JAEGER_ENDPOINT, JAEGER_ENVIRONMENT
- [ ] Python backend env vars set: TRACING_ENABLED, OTLP_ENDPOINT
- [ ] Backends depend on Jaeger with service_started condition

### Service Health
- [ ] Jaeger container is running and healthy
- [ ] Go backend container is running and healthy
- [ ] Python backend container is running and healthy
- [ ] Services can reach Jaeger on port 4317

### Trace Export
- [ ] Go backend exports traces (visible in Jaeger UI)
- [ ] Python backend exports traces (visible in Jaeger UI)
- [ ] Cross-service traces have matching trace IDs
- [ ] Trace attributes are complete and correct

### Performance
- [ ] Traces appear within 10 seconds of request
- [ ] Jaeger UI is responsive
- [ ] Memory usage is reasonable (<500MB)
- [ ] No error messages in logs

### Overall Status
- [ ] ✅ All checks passed
- [ ] ⚠️  Some checks need investigation
- [ ] ❌ Critical issues found

**Notes:**
[Any additional observations or issues found]

**Next Steps:**
[Any follow-up actions needed]
```

## Summary

Jaeger trace export is properly configured and working when:

1. ✅ **Jaeger UI is accessible** at `http://localhost:16686`
2. ✅ **Both services appear** in the Service dropdown
3. ✅ **Traces are exported** within 10 seconds of requests
4. ✅ **Trace attributes** are present and correct
5. ✅ **Cross-service tracing** works (same trace ID across services)
6. ✅ **Error traces** are captured with error details
7. ✅ **No errors** in backend logs related to tracing

If all of these are true, Jaeger distributed tracing is successfully configured!
