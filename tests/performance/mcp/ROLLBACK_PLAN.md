# MCP Optimization Rollback Plan

## Overview

This document provides a comprehensive rollback plan for MCP optimizations. All optimizations are controlled via environment variables and can be disabled independently or all at once.

## Quick Rollback (Complete)

To disable all MCP optimizations immediately:

```bash
# Disable all optimizations
export TRACERTM_MCP_LAZY_LOADING=false
export TRACERTM_MCP_COMPRESSION=false
export TRACERTM_MCP_STREAMING=false
export TRACERTM_MCP_TOKEN_OPTIMIZATION=false
export TRACERTM_MCP_CONNECTION_POOL_SIZE=0

# Restart MCP server
systemctl restart tracertm-mcp
```

## Feature-Specific Rollback

### 1. Lazy Loading Rollback

**Issue**: Tools not loading correctly, missing functionality

**Rollback**:
```bash
export TRACERTM_MCP_LAZY_LOADING=false
systemctl restart tracertm-mcp
```

**Impact**:
- Server startup time increases from <100ms to ~500ms
- All tools loaded immediately on startup
- Higher initial memory usage

**Verification**:
```bash
# Check that all tools are available
curl -X GET http://localhost:8000/mcp/tools | jq '.tools | length'
```

### 2. Compression Rollback

**Issue**: Response parsing errors, client compatibility issues

**Rollback**:
```bash
export TRACERTM_MCP_COMPRESSION=false
systemctl restart tracertm-mcp
```

**Impact**:
- Network bandwidth usage increases by ~60-70%
- Response sizes larger (no compression)
- Slightly slower over slow connections

**Verification**:
```bash
# Check response is not compressed
curl -v http://localhost:8000/mcp/test 2>&1 | grep "Content-Encoding"
# Should NOT show "Content-Encoding: gzip"
```

### 3. Streaming Rollback

**Issue**: Streaming responses incomplete, client buffering issues

**Rollback**:
```bash
export TRACERTM_MCP_STREAMING=false
systemctl restart tracertm-mcp
```

**Impact**:
- Large responses take longer to start
- Higher memory usage for large responses
- Time-to-first-byte increases

**Verification**:
```bash
# Check response is not streamed
curl -v http://localhost:8000/mcp/large-dataset 2>&1 | grep "Transfer-Encoding"
# Should NOT show "Transfer-Encoding: chunked"
```

### 4. Token Optimization Rollback

**Issue**: Responses truncated, pagination not working

**Rollback**:
```bash
export TRACERTM_MCP_TOKEN_OPTIMIZATION=false
systemctl restart tracertm-mcp
```

**Impact**:
- Token usage may exceed Claude's context limits
- Larger responses without pagination
- May hit rate limits faster

**Verification**:
```bash
# Check response size
curl -s http://localhost:8000/mcp/items | wc -c
# Should be larger without token optimization
```

### 5. Connection Pooling Rollback

**Issue**: Connection pool exhaustion, deadlocks

**Rollback**:
```bash
export TRACERTM_MCP_CONNECTION_POOL_SIZE=0
systemctl restart tracertm-mcp
```

**Impact**:
- New connection for each request
- Higher latency (connection setup overhead)
- More database load

**Verification**:
```bash
# Check active connections
psql -U tracertm -c "SELECT count(*) FROM pg_stat_activity WHERE datname='tracertm';"
# Should see fewer persistent connections
```

## Rollback Testing Procedure

### 1. Pre-Rollback

```bash
# Save current configuration
env | grep TRACERTM_MCP > /tmp/mcp_config_backup.env

# Run health check
python tests/performance/mcp/health_check.py

# Save baseline metrics
curl http://localhost:8000/metrics > /tmp/metrics_before_rollback.json
```

### 2. Execute Rollback

```bash
# Disable specific optimization(s)
export TRACERTM_MCP_LAZY_LOADING=false

# Restart service
systemctl restart tracertm-mcp

# Wait for startup
sleep 5
```

### 3. Post-Rollback Verification

```bash
# Health check
python tests/performance/mcp/health_check.py

# Run regression tests
pytest tests/mcp/test_server_integration.py -v

# Check metrics
curl http://localhost:8000/metrics > /tmp/metrics_after_rollback.json

# Compare
python tests/performance/mcp/compare_metrics.py \
  /tmp/metrics_before_rollback.json \
  /tmp/metrics_after_rollback.json
```

## Monitoring After Rollback

### Key Metrics to Monitor

1. **Response Time**
   - Target: <500ms for tool calls
   - Alert if: >1000ms

2. **Error Rate**
   - Target: <1% errors
   - Alert if: >5%

3. **Memory Usage**
   - Target: <500MB
   - Alert if: >1GB

4. **CPU Usage**
   - Target: <50% average
   - Alert if: >80%

### Monitoring Commands

```bash
# Watch response times
watch -n 5 'curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/mcp/test'

# Monitor error logs
tail -f /var/log/tracertm/mcp.log | grep ERROR

# Check resource usage
watch -n 5 'ps aux | grep mcp'
```

## Rollback Decision Matrix

| Symptom | Likely Cause | Rollback Action |
|---------|--------------|-----------------|
| Tools not found | Lazy loading issue | Disable lazy loading |
| Garbled responses | Compression issue | Disable compression |
| Incomplete responses | Streaming issue | Disable streaming |
| Token limit errors | Token optimization issue | Disable token optimization |
| Connection timeouts | Pool exhaustion | Disable connection pooling |
| High memory usage | All optimizations working | Keep optimizations |
| Slow responses | Expected without optimization | Re-enable optimizations |

## Emergency Rollback

For critical issues affecting production:

```bash
#!/bin/bash
# emergency_rollback.sh

echo "=== MCP EMERGENCY ROLLBACK ==="

# Disable ALL optimizations
export TRACERTM_MCP_LAZY_LOADING=false
export TRACERTM_MCP_COMPRESSION=false
export TRACERTM_MCP_STREAMING=false
export TRACERTM_MCP_TOKEN_OPTIMIZATION=false
export TRACERTM_MCP_CONNECTION_POOL_SIZE=0

# Save to systemd environment
cat > /etc/systemd/system/tracertm-mcp.service.d/override.conf <<EOF
[Service]
Environment="TRACERTM_MCP_LAZY_LOADING=false"
Environment="TRACERTM_MCP_COMPRESSION=false"
Environment="TRACERTM_MCP_STREAMING=false"
Environment="TRACERTM_MCP_TOKEN_OPTIMIZATION=false"
Environment="TRACERTM_MCP_CONNECTION_POOL_SIZE=0"
EOF

# Reload and restart
systemctl daemon-reload
systemctl restart tracertm-mcp

# Wait for startup
sleep 10

# Verify
if systemctl is-active --quiet tracertm-mcp; then
  echo "✓ Emergency rollback successful"
  python tests/performance/mcp/health_check.py
else
  echo "✗ Rollback failed - service not running"
  systemctl status tracertm-mcp
  exit 1
fi
```

## Gradual Re-enablement

After a rollback, re-enable optimizations gradually:

### Week 1: Re-enable Lazy Loading
```bash
export TRACERTM_MCP_LAZY_LOADING=true
systemctl restart tracertm-mcp
# Monitor for 7 days
```

### Week 2: Re-enable Compression
```bash
export TRACERTM_MCP_COMPRESSION=true
systemctl restart tracertm-mcp
# Monitor for 7 days
```

### Week 3: Re-enable Streaming
```bash
export TRACERTM_MCP_STREAMING=true
systemctl restart tracertm-mcp
# Monitor for 7 days
```

### Week 4: Re-enable Token Optimization
```bash
export TRACERTM_MCP_TOKEN_OPTIMIZATION=true
systemctl restart tracertm-mcp
# Monitor for 7 days
```

### Week 5: Re-enable Connection Pooling
```bash
export TRACERTM_MCP_CONNECTION_POOL_SIZE=10
systemctl restart tracertm-mcp
# Monitor for 7 days
```

## Rollback Communication Template

```
Subject: MCP Optimization Rollback - [OPTIMIZATION_NAME]

Date: [DATE]
Severity: [Low/Medium/High]
Status: [In Progress/Completed]

ISSUE:
[Describe the issue that triggered rollback]

ROLLBACK ACTION:
[Specific optimization(s) disabled]

IMPACT:
- Performance: [Expected performance impact]
- Functionality: [Any functionality changes]
- Users: [User-facing impact]

TIMELINE:
- Issue detected: [TIME]
- Rollback initiated: [TIME]
- Rollback completed: [TIME]
- Service restored: [TIME]

VERIFICATION:
[Steps taken to verify successful rollback]

NEXT STEPS:
[Plan for investigation and potential re-enablement]

CONTACT:
[On-call engineer contact]
```

## Testing Rollback (Staging)

Before performing production rollback, test in staging:

```bash
# 1. Deploy to staging with optimizations
./deploy_staging.sh --with-optimizations

# 2. Run full test suite
pytest tests/mcp/ tests/integration/ -v

# 3. Perform rollback
./emergency_rollback.sh

# 4. Verify rollback
pytest tests/mcp/test_server_integration.py -v

# 5. Check performance baselines
python tests/performance/mcp/benchmark_mcp.py

# 6. If successful, apply to production
```

## Rollback Sign-off Checklist

Before declaring rollback complete:

- [ ] Service is running and healthy
- [ ] All integration tests passing
- [ ] No error rate spike
- [ ] Response times within acceptable range
- [ ] Memory usage stable
- [ ] No customer reports of issues
- [ ] Metrics logged and analyzed
- [ ] Post-mortem scheduled
- [ ] Communication sent to stakeholders

## Support Contacts

- **On-call Engineer**: [PHONE/EMAIL]
- **MCP Team Lead**: [PHONE/EMAIL]
- **DevOps**: [PHONE/EMAIL]
- **Escalation**: [PHONE/EMAIL]

## References

- MCP Optimization Documentation: `docs/mcp/OPTIMIZATIONS.md`
- Performance Baselines: `tests/performance/mcp/performance_baselines.json`
- Health Check Script: `tests/performance/mcp/health_check.py`
- Benchmark Script: `tests/performance/mcp/benchmark_mcp.py`
