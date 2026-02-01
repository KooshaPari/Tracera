# TraceRTM Unified Infrastructure Verification Checklist

End-to-end verification checklist for the unified infrastructure after running `rtm dev start`.

## Pre-Start Verification

### Infrastructure Services

- [ ] **PostgreSQL** is running
  ```bash
  rtm dev check
  # Should show: ✅ PostgreSQL (:5432)
  ```

- [ ] **Redis** is running
  ```bash
  rtm dev check
  # Should show: ✅ Redis (:6379)
  ```

- [ ] **Neo4j** is running
  ```bash
  rtm dev check
  # Should show: ✅ Neo4j (:7687)
  ```

- [ ] **NATS** is running
  ```bash
  rtm dev check
  # Should show: ✅ NATS (:4222)
  ```

### Tool Installation

- [ ] **Caddy** is installed
  ```bash
  which caddy
  # Should return: /opt/homebrew/bin/caddy (or similar)
  ```

- [ ] **Overmind** is installed
  ```bash
  which overmind
  # Should return: /opt/homebrew/bin/overmind (or similar)
  ```

- [ ] **tmux** is installed
  ```bash
  which tmux
  # Should return: /opt/homebrew/bin/tmux (or similar)
  ```

- [ ] **Air** is installed
  ```bash
  which air
  # Should return: /Users/[user]/go/bin/air (or similar)
  ```

## Post-Start Verification

### Service Startup

- [ ] All services started successfully
  ```bash
  rtm dev status
  # All services should show "Running"
  ```

- [ ] **Temporal** started
  ```bash
  rtm dev logs temporal | grep "Started"
  # Should show temporal server started message
  ```

- [ ] **Caddy** started
  ```bash
  rtm dev logs caddy | grep "serving"
  # Should show "serving initial configuration"
  ```

- [ ] **Go Backend** started
  ```bash
  rtm dev logs go | grep "Listening"
  # Should show "Listening on :8080"
  ```

- [ ] **Python Backend** started
  ```bash
  rtm dev logs python | grep "Started"
  # Should show "Application startup complete"
  ```

- [ ] **Frontend** started
  ```bash
  rtm dev logs frontend | grep "ready"
  # Should show "ready in XXXms"
  ```

### Health Checks

- [ ] **Gateway health** returns OK
  ```bash
  curl http://localhost/health
  # Expected: "OK - TraceRTM Gateway v1.0"
  ```

- [ ] **Go backend health** returns OK
  ```bash
  curl http://localhost/health/go
  # Expected: HTTP 200 with {"status": "healthy"}
  ```

- [ ] **Python backend health** returns OK
  ```bash
  curl http://localhost/health/python
  # Expected: HTTP 200 with {"status": "healthy"}
  ```

## API Routing Tests

### Go Backend Routes (via Caddy)

- [ ] **Projects API** is accessible
  ```bash
  curl -s http://localhost/api/v1/projects | jq .
  # Expected: HTTP 200 with JSON response
  ```

- [ ] **Items API** is accessible
  ```bash
  curl -s http://localhost/api/v1/items | jq .
  # Expected: HTTP 200 with JSON array
  ```

- [ ] **Links API** is accessible
  ```bash
  curl -s http://localhost/api/v1/links | jq .
  # Expected: HTTP 200 with JSON array
  ```

- [ ] **Graph API** is accessible
  ```bash
  curl -s http://localhost/api/v1/graph/health | jq .
  # Expected: HTTP 200 with graph service health
  ```

- [ ] **Search API** is accessible
  ```bash
  curl -s "http://localhost/api/v1/search?q=test" | jq .
  # Expected: HTTP 200 with search results
  ```

- [ ] **Agents API** is accessible
  ```bash
  curl -s http://localhost/api/v1/agents | jq .
  # Expected: HTTP 200 with agents list
  ```

### Python Backend Routes (via Caddy)

- [ ] **Specifications API** is accessible
  ```bash
  curl -s http://localhost/api/v1/specifications | jq .
  # Expected: HTTP 200 with specifications list
  ```

- [ ] **Executions API** is accessible
  ```bash
  curl -s http://localhost/api/v1/executions | jq .
  # Expected: HTTP 200 with executions list
  ```

- [ ] **MCP API** is accessible
  ```bash
  curl -s http://localhost/api/v1/mcp/tools | jq .
  # Expected: HTTP 200 with MCP tools list
  ```

- [ ] **Quality API** is accessible
  ```bash
  curl -s http://localhost/api/v1/quality/health | jq .
  # Expected: HTTP 200 with quality service health
  ```

- [ ] **Notifications API** is accessible
  ```bash
  curl -s http://localhost/api/v1/notifications | jq .
  # Expected: HTTP 200 with notifications
  ```

- [ ] **Auth API** is accessible
  ```bash
  curl -s http://localhost/api/v1/auth/status | jq .
  # Expected: HTTP 200 with auth status
  ```

### Frontend Routes

- [ ] **Frontend** serves the app
  ```bash
  curl -s http://localhost | grep "<div id=\"root\">"
  # Expected: HTML with root div
  ```

- [ ] **Frontend assets** are accessible
  ```bash
  curl -I http://localhost/assets/index.css
  # Expected: HTTP 200
  ```

## WebSocket Connection Tests

### Basic WebSocket Connection

- [ ] **WebSocket endpoint** accepts connections
  ```bash
  # In browser console (http://localhost):
  const ws = new WebSocket('ws://localhost/api/v1/ws');
  ws.onopen = () => console.log('✅ Connected');
  ws.onerror = (e) => console.error('❌ Error:', e);

  # Expected: "✅ Connected" in console
  ```

- [ ] **WebSocket** can send messages
  ```javascript
  ws.send(JSON.stringify({type: 'ping'}));
  // Expected: No errors
  ```

- [ ] **WebSocket** receives messages
  ```javascript
  ws.onmessage = (e) => console.log('Received:', e.data);
  // Trigger an event (create item via API) and check console
  ```

### WebSocket Real-Time Updates

- [ ] **Real-time item creation** works
  ```bash
  # Terminal 1: Open browser console with WebSocket connected

  # Terminal 2: Create item via API
  curl -X POST http://localhost/api/v1/items \
    -H "Content-Type: application/json" \
    -d '{"title": "Test Item", "type": "story"}'

  # Expected: WebSocket receives update in browser console
  ```

- [ ] **Real-time link creation** works
  ```bash
  # Create link via API while WebSocket is connected
  curl -X POST http://localhost/api/v1/links \
    -H "Content-Type: application/json" \
    -d '{"source_id": "item1", "target_id": "item2", "type": "depends"}'

  # Expected: WebSocket receives link update
  ```

## Auto-Reload Verification

### Frontend Hot Module Replacement (HMR)

- [ ] **React component** hot reloads
  ```bash
  # 1. Open http://localhost in browser
  # 2. Open DevTools Console
  # 3. Edit frontend/apps/web/src/pages/Dashboard.tsx
  # 4. Add: console.log('HMR Test')
  # 5. Save file

  # Expected:
  # - Console shows "HMR Test" in < 100ms
  # - No page refresh
  # - Component state preserved
  ```

- [ ] **CSS changes** hot reload
  ```bash
  # 1. Edit frontend/apps/web/src/index.css
  # 2. Change body background color
  # 3. Save file

  # Expected:
  # - Background color updates instantly
  # - No page refresh
  ```

### Python Backend Auto-Reload

- [ ] **Python code changes** trigger reload
  ```bash
  # Terminal 1: Monitor logs
  rtm dev logs python --follow

  # Terminal 2: Edit file
  echo "# test comment" >> src/tracertm/api/main.py

  # Expected in Terminal 1:
  # - "Shutting down"
  # - "Application startup complete" (within 1-3 seconds)
  ```

- [ ] **New Python endpoint** works after reload
  ```bash
  # 1. Add new endpoint to src/tracertm/api/routers/test.py
  @router.get("/test/reload")
  async def test_reload():
      return {"message": "Reload works!"}

  # 2. Save file
  # 3. Wait 1-3 seconds
  # 4. Test endpoint
  curl http://localhost/api/v1/test/reload

  # Expected: {"message": "Reload works!"}
  ```

### Go Backend Auto-Reload (Air)

- [ ] **Go code changes** trigger rebuild
  ```bash
  # Terminal 1: Monitor logs
  rtm dev logs go --follow

  # Terminal 2: Edit file
  echo "// test comment" >> backend/internal/handlers/health.go

  # Expected in Terminal 1:
  # - "[Air] Rebuilding..."
  # - "[Air] Build finished"
  # - "Listening on :8080" (within 2-5 seconds)
  ```

- [ ] **New Go endpoint** works after rebuild
  ```bash
  # 1. Add new route in backend/internal/routes/routes.go
  api.GET("/test/reload", func(c *gin.Context) {
      c.JSON(200, gin.H{"message": "Rebuild works!"})
  })

  # 2. Save file
  # 3. Wait for Air rebuild (2-5 seconds)
  # 4. Test endpoint
  curl http://localhost/api/v1/test/reload

  # Expected: {"message": "Rebuild works!"}
  ```

### Caddy Configuration Reload

- [ ] **Caddyfile changes** reload gracefully
  ```bash
  # Terminal 1: Monitor logs
  tail -f /tmp/caddy-tracertm.log

  # Terminal 2: Edit Caddyfile
  # Add a comment: # Test reload

  # Expected in Terminal 1:
  # - Configuration reloaded
  # - No service interruption
  # - Reload completes in < 1 second
  ```

- [ ] **New route** works after Caddyfile reload
  ```bash
  # 1. Add new route to Caddyfile (example):
  handle /test/caddy {
      respond "Caddy reload works!" 200
  }

  # 2. Save file
  # 3. Wait < 1 second
  # 4. Test endpoint
  curl http://localhost/test/caddy

  # Expected: "Caddy reload works!"
  ```

## Database Connectivity

### PostgreSQL

- [ ] **Go backend** connects to PostgreSQL
  ```bash
  # Check Go logs for connection
  rtm dev logs go | grep -i "postgres"
  # Expected: No connection errors
  ```

- [ ] **Python backend** connects to PostgreSQL
  ```bash
  # Check Python logs for connection
  rtm dev logs python | grep -i "postgres"
  # Expected: No connection errors
  ```

- [ ] **Can query database** via psql
  ```bash
  psql -U tracertm -d tracertm -h localhost -c "SELECT 1"
  # Expected: Returns 1
  ```

### Redis

- [ ] **Go backend** connects to Redis
  ```bash
  rtm dev logs go | grep -i "redis"
  # Expected: No connection errors
  ```

- [ ] **Python backend** connects to Redis
  ```bash
  rtm dev logs python | grep -i "redis"
  # Expected: No connection errors
  ```

- [ ] **Can ping Redis**
  ```bash
  redis-cli ping
  # Expected: PONG
  ```

### Neo4j

- [ ] **Go backend** connects to Neo4j
  ```bash
  rtm dev logs go | grep -i "neo4j"
  # Expected: No connection errors
  ```

- [ ] **Neo4j browser** is accessible
  ```bash
  curl -s http://localhost:7474 | grep "neo4j"
  # Expected: HTML page with neo4j
  ```

### NATS

- [ ] **Go backend** connects to NATS
  ```bash
  rtm dev logs go | grep -i "nats"
  # Expected: No connection errors
  ```

- [ ] **Python backend** connects to NATS
  ```bash
  rtm dev logs python | grep -i "nats"
  # Expected: No connection errors
  ```

- [ ] **NATS monitoring** is accessible
  ```bash
  curl -s http://localhost:8222/varz | jq .server_name
  # Expected: NATS server name
  ```

## Performance Tests

### Response Time

- [ ] **Go API** responds quickly (< 50ms)
  ```bash
  time curl -s http://localhost/api/v1/items > /dev/null
  # Expected: real time < 0.1s
  ```

- [ ] **Python API** responds (< 500ms for non-AI)
  ```bash
  time curl -s http://localhost/api/v1/specifications > /dev/null
  # Expected: real time < 0.5s
  ```

- [ ] **Frontend** loads quickly
  ```bash
  time curl -s http://localhost > /dev/null
  # Expected: real time < 0.2s
  ```

### Concurrent Requests

- [ ] **Multiple requests** handled concurrently
  ```bash
  # Run 10 concurrent requests
  for i in {1..10}; do
    curl -s http://localhost/api/v1/items &
  done
  wait

  # Expected: All requests complete successfully
  ```

## Error Handling

### Service Failure Recovery

- [ ] **Go backend restart** doesn't crash other services
  ```bash
  # Kill Go backend
  pkill -f "air"

  # Wait 5 seconds, check other services
  rtm dev status

  # Expected: Only Go shows as stopped, others still running

  # Restart Go
  rtm dev restart go
  ```

- [ ] **Python backend restart** doesn't crash other services
  ```bash
  # Kill Python backend
  pkill -f "uvicorn"

  # Check other services
  rtm dev status

  # Expected: Only Python shows as stopped

  # Restart Python
  rtm dev restart python
  ```

### Database Disconnection

- [ ] **Backend handles** database reconnection
  ```bash
  # Stop PostgreSQL temporarily
  brew services stop postgresql@17

  # Try API call (should fail gracefully)
  curl http://localhost/api/v1/items
  # Expected: 500 error with JSON message

  # Restart PostgreSQL
  brew services start postgresql@17
  sleep 5

  # Try again
  curl http://localhost/api/v1/items
  # Expected: Success after reconnection
  ```

## Log Analysis

### No Critical Errors

- [ ] **Caddy logs** show no errors
  ```bash
  cat /tmp/caddy-tracertm.log | grep -i "error"
  # Expected: No critical errors
  ```

- [ ] **Go logs** show no errors
  ```bash
  rtm dev logs go | grep -i "error"
  # Expected: No uncaught errors
  ```

- [ ] **Python logs** show no errors
  ```bash
  rtm dev logs python | grep -i "error"
  # Expected: No uncaught exceptions
  ```

- [ ] **Frontend logs** show no errors
  ```bash
  rtm dev logs frontend | grep -i "error"
  # Expected: No build/runtime errors
  ```

## Security Checks

### Development Security

- [ ] **Caddy** is HTTP-only in dev
  ```bash
  curl -I http://localhost/health
  # Expected: HTTP (not HTTPS) in development
  ```

- [ ] **Ports** are localhost-bound
  ```bash
  netstat -an | grep LISTEN | grep -E ":(80|8000|8080|5173)"
  # Expected: All show 127.0.0.1 or localhost
  ```

- [ ] **Admin endpoints** are localhost-only
  ```bash
  curl http://localhost:2019/config/
  # Expected: Works (Caddy admin API)

  # From external network (if applicable):
  # Expected: Connection refused
  ```

## Final Verification

### End-to-End Flow

- [ ] **Complete user flow** works
  ```bash
  # 1. Open http://localhost in browser
  # 2. Navigate to Projects
  # 3. Create a new project
  # 4. Create items in project
  # 5. Create links between items
  # 6. View graph visualization
  # 7. Search for items
  # 8. View real-time updates (WebSocket)

  # Expected: All operations complete successfully
  ```

### Graceful Shutdown

- [ ] **All services stop** cleanly
  ```bash
  # In Overmind terminal: Ctrl+C

  # Expected:
  # - All services receive shutdown signal
  # - Services stop gracefully
  # - No zombie processes
  # - No errors in shutdown logs
  ```

- [ ] **No orphaned processes** remain
  ```bash
  ps aux | grep -E "(caddy|uvicorn|air|temporal)" | grep -v grep
  # Expected: No processes running
  ```

## Verification Summary

**Total Checks**: 100+

**Required for Pass**: All critical checks (marked as "Required")

**Optional Checks**: Performance and advanced features

### Critical Checks (Must Pass)
- ✅ All infrastructure services running
- ✅ All application services started
- ✅ Health checks return OK
- ✅ API routing works (Go and Python)
- ✅ WebSocket connects
- ✅ Basic auto-reload works
- ✅ No critical errors in logs

### Pass Criteria

**PASS**: All critical checks pass, < 5 optional checks fail

**FAIL**: Any critical check fails OR > 5 optional checks fail

## Troubleshooting Failed Checks

If any check fails, consult:

1. [DEVELOPMENT_WORKFLOW.md](../guides/DEVELOPMENT_WORKFLOW.md#troubleshooting) - Troubleshooting section
2. [RTM_DEV_QUICK_REFERENCE.md](../reference/RTM_DEV_QUICK_REFERENCE.md#troubleshooting-commands) - Quick fixes
3. Service logs: `rtm dev logs <service>`
4. Health check: `rtm dev check`

## Next Steps After Verification

Once all checks pass:

1. ✅ Development environment is ready
2. ✅ Start coding with hot reload
3. ✅ Refer to [DEVELOPMENT_WORKFLOW.md](../guides/DEVELOPMENT_WORKFLOW.md) for daily usage
4. ✅ Use [RTM_DEV_QUICK_REFERENCE.md](../reference/RTM_DEV_QUICK_REFERENCE.md) for commands
