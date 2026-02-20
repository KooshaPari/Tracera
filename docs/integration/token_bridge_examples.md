# Token Bridge Examples

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  (React/Next.js with WorkOS AuthKit)                        │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ RS256 Token (WorkOS)
                    │ Bearer eyJhbGc...
                    │
        ┌───────────┴────────────┐
        │                        │
        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│   Go Backend     │    │  Python Backend  │
│   (Echo API)     │◄───┤  (FastAPI)       │
│   Port 8080      │───►│   Port 8000      │
└──────────────────┘    └──────────────────┘
        │                        │
        │ HS256 Service Token    │
        │ (5 min TTL)            │
        │                        │
        └────────────────────────┘
```

## Example 1: Frontend → Go Backend

**Scenario**: User logged in via WorkOS, calls Go API

**Flow**:
1. User authenticates with WorkOS
2. Frontend receives RS256 access token
3. Frontend sends token to Go backend
4. Go validates RS256 token via JWKS

**Frontend (React)**:
```typescript
// After WorkOS login
const { accessToken } = useAuth();

// Call Go backend
const response = await fetch('http://localhost:8080/api/v1/projects', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
});
```

**Go Backend**:
```go
// main.go
import (
    "github.com/kooshapari/tracertm-backend/internal/auth"
    "github.com/kooshapari/tracertm-backend/internal/middleware"
)

func main() {
    // Initialize token bridge
    bridge, err := auth.NewTokenBridge(
        []byte(os.Getenv("JWT_SECRET")),
        os.Getenv("WORKOS_JWKS_URL"),
        os.Getenv("WORKOS_CLIENT_ID"),
        "https://api.workos.com/",
    )
    if err != nil {
        log.Fatal(err)
    }
    defer bridge.Close()

    // Create auth adapter
    authAdapter := auth.NewBridgeAuthAdapter(bridge, db)

    // Setup middleware
    e := echo.New()
    e.Use(middleware.AuthAdapterMiddleware(middleware.AuthAdapterConfig{
        AuthProvider: authAdapter,
    }))

    e.GET("/api/v1/projects", handleGetProjects)
    e.Start(":8080")
}

func handleGetProjects(c echo.Context) error {
    // User is automatically authenticated by middleware
    user := c.Get("user").(*auth.User)

    // Use user.ID, user.ProjectID, etc.
    projects, err := getProjectsForUser(c.Request().Context(), user.ID)
    if err != nil {
        return err
    }

    return c.JSON(http.StatusOK, projects)
}
```

## Example 2: Frontend → Python Backend

**Scenario**: User calls Python API with WorkOS token

**Frontend (React)**:
```typescript
const response = await fetch('http://localhost:4000/api/v1/specifications', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,  // Same WorkOS token
  },
});
```

**Python Backend**:
```python
# main.py
from fastapi import FastAPI, Depends
from tracertm.api.deps import auth_guard

app = FastAPI()

@app.get("/api/v1/specifications")
async def get_specifications(claims: dict = Depends(auth_guard)):
    """Get specifications for authenticated user."""
    user_id = claims["sub"]
    org_id = claims.get("org_id")

    # Token is automatically validated (RS256 from WorkOS)
    specs = await get_user_specifications(user_id, org_id)
    return specs
```

## Example 3: Go → Python Service Call

**Scenario**: Go backend needs to call Python API on behalf of a user

**Go Backend**:
```go
package services

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"

    "github.com/kooshapari/tracertm-backend/internal/auth"
)

type PythonAPIClient struct {
    baseURL string
    bridge  *auth.TokenBridge
}

func NewPythonAPIClient(baseURL string, bridge *auth.TokenBridge) *PythonAPIClient {
    return &PythonAPIClient{
        baseURL: baseURL,
        bridge:  bridge,
    }
}

// GetSpecifications calls Python backend to get specifications
func (c *PythonAPIClient) GetSpecifications(userID, orgID string) ([]Specification, error) {
    // Create short-lived service token
    serviceToken, err := c.bridge.CreateBridgeToken(userID, orgID)
    if err != nil {
        return nil, fmt.Errorf("failed to create service token: %w", err)
    }

    // Call Python API
    req, err := http.NewRequest("GET", c.baseURL+"/api/v1/specifications", nil)
    if err != nil {
        return nil, err
    }

    req.Header.Set("Authorization", "Bearer "+serviceToken)
    req.Header.Set("Content-Type", "application/json")

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("python API returned status %d", resp.StatusCode)
    }

    var specs []Specification
    if err := json.NewDecoder(resp.Body).Decode(&specs); err != nil {
        return nil, err
    }

    return specs, nil
}

// Usage in handler
func handleGetProjectWithSpecs(c echo.Context) error {
    user := c.Get("user").(*auth.User)
    projectID := c.Param("id")

    // Get project from Go backend
    project, err := getProject(c.Request().Context(), projectID)
    if err != nil {
        return err
    }

    // Get specifications from Python backend
    pythonClient := NewPythonAPIClient(os.Getenv("PYTHON_BACKEND_URL"), bridge)
    specs, err := pythonClient.GetSpecifications(user.ID, user.ProjectID)
    if err != nil {
        return err
    }

    return c.JSON(http.StatusOK, map[string]interface{}{
        "project": project,
        "specifications": specs,
    })
}
```

## Example 4: Python → Go Service Call

**Scenario**: Python backend needs to call Go API on behalf of a user

**Python Backend**:
```python
# src/tracertm/clients/go_api_client.py
import httpx
from tracertm.services.token_bridge import get_token_bridge

class GoAPIClient:
    """Client for calling Go backend APIs."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.bridge = get_token_bridge()

    async def get_links(self, user_id: str, org_id: str) -> list[dict]:
        """Get links from Go backend."""
        # Create short-lived service token
        service_token = self.bridge.create_bridge_token(user_id, org_id)

        # Call Go API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/links",
                headers={
                    "Authorization": f"Bearer {service_token}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            return response.json()

    async def create_link(
        self,
        user_id: str,
        org_id: str,
        link_data: dict,
    ) -> dict:
        """Create a link in Go backend."""
        service_token = self.bridge.create_bridge_token(user_id, org_id)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/links",
                headers={
                    "Authorization": f"Bearer {service_token}",
                },
                json=link_data,
            )
            response.raise_for_status()
            return response.json()


# Usage in router
from fastapi import APIRouter, Depends
from tracertm.api.deps import auth_guard
from tracertm.clients.go_api_client import GoAPIClient
import os

router = APIRouter()

@router.get("/items/{item_id}/with-links")
async def get_item_with_links(
    item_id: str,
    claims: dict = Depends(auth_guard),
):
    """Get item with its links from Go backend."""
    user_id = claims["sub"]
    org_id = claims.get("org_id")

    # Get item from Python backend
    item = await get_item(item_id)

    # Get links from Go backend
    go_client = GoAPIClient(os.getenv("GO_BACKEND_URL"))
    links = await go_client.get_links(user_id, org_id)

    return {
        "item": item,
        "links": links,
    }
```

## Example 5: Service Token Expiry Handling

**Scenario**: Handle token expiry gracefully with retry logic

**Go Backend**:
```go
func (c *PythonAPIClient) GetSpecificationsWithRetry(userID, orgID string) ([]Specification, error) {
    maxRetries := 2
    var lastErr error

    for attempt := 0; attempt < maxRetries; attempt++ {
        // Create fresh service token for each attempt
        serviceToken, err := c.bridge.CreateBridgeToken(userID, orgID)
        if err != nil {
            return nil, fmt.Errorf("failed to create service token: %w", err)
        }

        specs, err := c.callPythonAPI(serviceToken)
        if err == nil {
            return specs, nil
        }

        // Check if it's a token expiry error
        if isTokenExpiredError(err) {
            log.Printf("Service token expired (attempt %d/%d), retrying...", attempt+1, maxRetries)
            lastErr = err
            continue
        }

        // Non-expiry error, don't retry
        return nil, err
    }

    return nil, fmt.Errorf("all retry attempts failed: %w", lastErr)
}
```

**Python Backend**:
```python
import asyncio
from httpx import HTTPStatusError

async def get_links_with_retry(
    client: GoAPIClient,
    user_id: str,
    org_id: str,
    max_retries: int = 2,
) -> list[dict]:
    """Get links with automatic retry on token expiry."""
    for attempt in range(max_retries):
        try:
            return await client.get_links(user_id, org_id)
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                # Token might be expired, retry with fresh token
                logger.warning(f"Service token expired (attempt {attempt + 1}/{max_retries}), retrying...")
                await asyncio.sleep(0.1)  # Brief delay
                continue
            raise

    raise Exception("All retry attempts failed")
```

## Example 6: Batch Operations

**Scenario**: Go backend needs to make multiple Python API calls efficiently

**Go Backend**:
```go
type BatchPythonClient struct {
    client      *PythonAPIClient
    tokenCache  string
    tokenExpiry time.Time
    mu          sync.RWMutex
}

func (c *BatchPythonClient) GetMultipleSpecifications(userID, orgID string, specIDs []string) ([]Specification, error) {
    // Reuse token for batch operations (within 5-minute window)
    token, err := c.getOrCreateToken(userID, orgID)
    if err != nil {
        return nil, err
    }

    // Make parallel requests
    var wg sync.WaitGroup
    results := make([]Specification, len(specIDs))
    errors := make([]error, len(specIDs))

    for i, specID := range specIDs {
        wg.Add(1)
        go func(idx int, id string) {
            defer wg.Done()
            spec, err := c.getSpecificationWithToken(token, id)
            if err != nil {
                errors[idx] = err
                return
            }
            results[idx] = spec
        }(i, specID)
    }

    wg.Wait()

    // Check for errors
    for i, err := range errors {
        if err != nil {
            return nil, fmt.Errorf("failed to get spec %s: %w", specIDs[i], err)
        }
    }

    return results, nil
}

func (c *BatchPythonClient) getOrCreateToken(userID, orgID string) (string, error) {
    c.mu.RLock()
    // Check if cached token is still valid (with 30s buffer)
    if c.tokenCache != "" && time.Now().Add(30*time.Second).Before(c.tokenExpiry) {
        token := c.tokenCache
        c.mu.RUnlock()
        return token, nil
    }
    c.mu.RUnlock()

    // Create new token
    c.mu.Lock()
    defer c.mu.Unlock()

    token, err := c.client.bridge.CreateBridgeToken(userID, orgID)
    if err != nil {
        return "", err
    }

    c.tokenCache = token
    c.tokenExpiry = time.Now().Add(5 * time.Minute)
    return token, nil
}
```

## Testing Examples

**Go Integration Test**:
```go
func TestPythonAPIIntegration(t *testing.T) {
    bridge, _ := auth.NewTokenBridge(
        []byte(os.Getenv("JWT_SECRET")),
        os.Getenv("WORKOS_JWKS_URL"),
        os.Getenv("WORKOS_CLIENT_ID"),
        "https://api.workos.com/",
    )
    defer bridge.Close()

    client := NewPythonAPIClient("http://localhost:4000", bridge)

    t.Run("get specifications", func(t *testing.T) {
        specs, err := client.GetSpecifications("user_test", "org_test")
        assert.NoError(t, err)
        assert.NotNil(t, specs)
    })
}
```

**Python Integration Test**:
```python
import pytest
from tracertm.clients.go_api_client import GoAPIClient

@pytest.mark.asyncio
async def test_go_api_integration():
    """Test calling Go backend with service token."""
    client = GoAPIClient("http://localhost:8080")

    links = await client.get_links("user_test", "org_test")
    assert isinstance(links, list)
```

## Performance Considerations

### Token Creation Overhead

- **Service token creation**: ~1ms (HS256 signing)
- **JWKS fetch**: ~50-100ms (cached for 24 hours)
- **Token validation**: ~0.5ms (HS256) or ~2ms (RS256)

### Recommended Patterns

1. **One token per request**: Create fresh service token for each cross-backend call
2. **Token reuse for batches**: Cache token for multiple operations within 5-minute window
3. **Connection pooling**: Reuse HTTP clients, not tokens
4. **Async/parallel**: Make independent calls concurrently

### Anti-Patterns to Avoid

- ❌ Storing service tokens for > 5 minutes
- ❌ Sending service tokens to frontend
- ❌ Using user tokens for service-to-service auth
- ❌ Hardcoding secrets in source code
