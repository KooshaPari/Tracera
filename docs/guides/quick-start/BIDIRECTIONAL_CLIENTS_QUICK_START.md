# Bidirectional HTTP Clients - Quick Start Guide

## 🚀 Quick Start

### 1. Environment Setup

Add to your `.env` file:
```bash
GO_BACKEND_URL=http://localhost:8080
PYTHON_BACKEND_URL=http://localhost:8000
SERVICE_TOKEN=your_shared_service_token_here
```

### 2. Using Go → Python Client

```go
// In any Go handler
func (h *Handler) SomeHandler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    // Make a request to Python backend
    var response map[string]interface{}
    err := h.infra.PythonClient.DelegateRequest(
        ctx,
        "GET",                    // HTTP method
        "/api/specifications",    // Path
        nil,                      // Request body (nil for GET)
        &response,                // Response destination
        true,                     // Cacheable
        "specs-key",              // Cache key
        5 * time.Minute,          // Cache TTL
    )

    if err != nil {
        http.Error(w, err.Error(), http.StatusBadGateway)
        return
    }

    json.NewEncoder(w).Encode(response)
}
```

### 3. Using Python → Go Client

```python
from fastapi import Request, HTTPException

@router.get("/items/{item_id}")
async def get_item(item_id: str, request: Request):
    go_client = request.app.state.go_client

    try:
        # Get item from Go backend
        item = await go_client.get_item(item_id)
        return item
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Go backend error: {str(e)}"
        )
```

## 📦 Key Features

### Go Client
- ✅ Retry: 3 attempts, exponential backoff
- ✅ Circuit Breaker: 5 failures threshold
- ✅ Redis Cache: 5min TTL
- ✅ Timeout: 30s

### Python Client
- ✅ Retry: 3 attempts via tenacity
- ✅ Connection Pool: 100 max, 20 keepalive
- ✅ Timeout: 30s
- ✅ Auto cleanup with context manager

## 🧪 Testing

### Go Tests
```bash
cd backend/tests/integration/clients
go test -v
```

### Python Tests
```bash
pytest tests/integration/clients/test_go_integration.py -v
```

## 📊 Monitoring

### Check Circuit Breaker State (Go)
```go
state := pythonClient.GetCircuitBreakerState()
// 0 = Closed (normal)
// 1 = Half-Open (testing)
// 2 = Open (tripped)
```

### Generate Cache Key
```go
// Go
cacheKey := clients.GenerateCacheKey("prefix", "GET", "/path", body)
```

```python
# Python
from tracertm.clients.go_client import generate_cache_key
cache_key = generate_cache_key("prefix", "GET", "/path", body)
```

## 🔧 Common Operations

### Go Client Examples

**Non-cacheable request:**
```go
var response map[string]interface{}
err := pythonClient.DelegateRequest(
    ctx, "POST", "/api/items", requestBody, &response,
    false, "", 0,  // Not cacheable
)
```

**Cacheable request:**
```go
cacheKey := clients.GenerateCacheKey("items", "GET", "/api/items", nil)
var response map[string]interface{}
err := pythonClient.DelegateRequest(
    ctx, "GET", "/api/items", nil, &response,
    true, cacheKey, 5*time.Minute,
)
```

### Python Client Examples

**Get item:**
```python
item = await go_client.get_item("item-123")
```

**Create link:**
```python
link = await go_client.create_link(
    source_id="item-1",
    target_id="item-2",
    link_type="DEPENDS_ON",
    metadata={"weight": 1.0}
)
```

**Search items:**
```python
results = await go_client.search_items(
    "query",
    filters={"project_id": "proj-123"}
)
```

**Update item:**
```python
updated = await go_client.update_item(
    "item-123",
    {"title": "New Title"}
)
```

**Delete item:**
```python
result = await go_client.delete_item("item-123")
```

**Get graph data:**
```python
graph = await go_client.get_graph_data(
    project_id="proj-123",
    root_item_id="item-1",
    depth=3
)
```

**Health check:**
```python
health = await go_client.health_check()
```

## 🚨 Troubleshooting

### Circuit Breaker Keeps Tripping
```bash
# Check Python backend
curl http://localhost:4000/health

# Check circuit breaker state
# In Go handler:
log.Printf("CB State: %v", h.infra.PythonClient.GetCircuitBreakerState())
```

### Requests Timing Out
```bash
# Check backend connectivity
curl -w "@curl-format.txt" http://localhost:4000/api/items

# Increase timeout if needed (modify client initialization)
```

### Cache Not Working
```bash
# Check Redis
redis-cli ping

# Verify cache key
log.Printf("Cache Key: %s", cacheKey)
```

## 📚 Full Documentation

- **Implementation Guide**: `/backend/BIDIRECTIONAL_HTTP_CLIENTS.md`
- **Summary**: `/BIDIRECTIONAL_CLIENTS_IMPLEMENTATION_SUMMARY.md`
- **This Guide**: `/BIDIRECTIONAL_CLIENTS_QUICK_START.md`

## 🎯 Files Overview

```
backend/
├── internal/
│   ├── clients/
│   │   └── python_client.go          # Go → Python client
│   ├── config/
│   │   └── config.go                 # Added cross-backend config
│   └── infrastructure/
│       └── infrastructure.go         # Auto-init Python client
└── tests/integration/clients/
    ├── python_integration_test.go    # Go tests
    └── go.mod

src/tracertm/
├── clients/
│   └── go_client.py                  # Python → Go client
└── api/
    └── main.py                       # Auto-init Go client

tests/integration/clients/
├── __init__.py
└── test_go_integration.py            # Python tests

# Configuration
.env.integration                      # Test environment
backend/.env.example                  # Updated with vars
pyproject.toml                        # Added tenacity
```

## 🏁 Getting Started

1. **Update environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env and set GO_BACKEND_URL, PYTHON_BACKEND_URL, SERVICE_TOKEN
   ```

2. **Install dependencies**
   ```bash
   # Go
   cd backend
   go mod download

   # Python
   pip install tenacity httpx
   ```

3. **Start backends**
   ```bash
   # Terminal 1
   cd backend && go run main.go

   # Terminal 2
   cd src && uvicorn tracertm.api.main:app --reload --port 8000
   ```

4. **Test connectivity**
   ```bash
   # Health checks
   curl http://localhost:8080/health
   curl http://localhost:4000/health
   ```

5. **Use clients in your code** (see examples above)

## 💡 Pro Tips

1. **Always use caching for expensive operations** (GET requests)
2. **Monitor circuit breaker state** in production
3. **Use context managers** in Python for auto-cleanup
4. **Generate consistent cache keys** for cache hits
5. **Handle errors gracefully** - circuit breaker may trip
6. **Test failover scenarios** before production

## 🔐 Security Notes

- Always use strong SERVICE_TOKEN in production
- Rotate service tokens regularly
- Use HTTPS in production
- Never commit `.env` files
- Monitor for token leakage

---

**Need Help?** See full docs in `/backend/BIDIRECTIONAL_HTTP_CLIENTS.md`
