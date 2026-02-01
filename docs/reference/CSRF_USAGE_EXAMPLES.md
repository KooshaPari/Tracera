# CSRF Protection - Usage Examples

This document provides practical examples of how to use the CSRF protection system.

## Frontend Usage

### Automatic Usage (Recommended)

The CSRF protection is **automatic** and requires no code changes:

```typescript
// This works automatically - CSRF token is injected!
const { data, error } = await apiClient.POST("/api/v1/items", {
  body: {
    name: "New Item",
    description: "Item description"
  }
});
```

The API client automatically:
- Fetches CSRF token on app startup
- Includes `X-CSRF-Token` header in state-changing requests
- Handles token rotation
- Recovers from CSRF errors

### Manual Token Access

If you need direct token access:

```typescript
import { getCSRFToken, setCSRFToken, refreshCSRFToken } from "@/lib/csrf";

// Get current token
const token = getCSRFToken();
console.log("Current token:", token);

// Refresh token (if expired or needed)
await refreshCSRFToken();

// Make request with token
const response = await fetch(`${API_BASE_URL}/api/v1/items`, {
  method: "POST",
  headers: {
    "X-CSRF-Token": token,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ name: "Item" }),
});
```

### Debugging CSRF Issues

```typescript
import { logCSRFState, getCSRFCookies } from "@/lib/csrf";

// Log current CSRF state
logCSRFState();
// Output:
// [CSRF] Current State
// Token in memory: Yes
// Token value: eyJhbGc...
// Cookies: { csrf_token: 'eyJhbGc...' }

// Get all CSRF cookies
const cookies = getCSRFCookies();
console.log("CSRF Cookie:", cookies.csrf_token);
```

## Backend Usage

### Automatic Usage (Recommended)

CSRF protection is **automatic** for all state-changing requests:

```go
// POST /api/v1/items
// Client sends:
//   X-CSRF-Token: <token>
//   Cookie: csrf_token=<same-token>
//
// Server validates automatically (no code needed)
//
// If valid: Process request, generate new token
// If invalid: Return 403 Forbidden

func (h *ProjectHandler) CreateProject(c echo.Context) error {
    // CSRF validation already done by middleware
    // Just implement your business logic
    var req struct {
        Name string `json:"name"`
    }
    if err := c.Bind(&req); err != nil {
        return err
    }

    // Your logic here...
    return c.JSON(http.StatusCreated, result)
}
```

### Accessing CSRF Token in Handler

```go
import custommw "github.com/kooshapari/tracertm-backend/internal/middleware"

func MyHandler(c echo.Context) error {
    // Get CSRF token from context (if needed for response)
    token, ok := c.Get(custommw.CSRFTokenContextKey).(string)
    if !ok {
        return c.JSON(http.StatusInternalServerError,
            map[string]string{"error": "CSRF token not available"})
    }

    // Use token if needed
    return c.JSON(http.StatusOK, map[string]string{
        "token": token,
    })
}
```

### Exempting Routes from CSRF

Some routes don't need CSRF protection:

```go
// These are automatically exempted:
// - /health - Health checks
// - /metrics - Monitoring
// - /auth/login - Login
// - /auth/register - Registration
// - /auth/refresh - Token refresh
// - /auth/callback - OAuth callbacks
// - /webhook/* - External webhooks

// Custom exemption in setupRoutes():
s.echo.GET("/special-endpoint", specialHandler)
// This will have CSRF protection

// To exempt a route, it should be in CSRFSkipper
```

### Configuring CSRF

```go
// In middleware setup
csrfConfig := custommw.NewCSRFConfig()

// Options:
csrfConfig.TokenLength = 32  // bytes
csrfConfig.TokenExpiry = 24 * time.Hour
csrfConfig.SameSite = "Strict"  // or "Lax", "None"
csrfConfig.Enabled = true  // auto-disabled if CSRF_SECRET empty

s.echo.Use(custommw.CSRFMiddleware(csrfConfig))
```

## Real-World Workflows

### Creating a New Item

#### Frontend
```typescript
import { apiClient } from "@/api/client";

async function createItem(name: string, description: string) {
  try {
    // CSRF token automatically included!
    const { data, error } = await apiClient.POST("/api/v1/items", {
      body: { name, description }
    });

    if (error) {
      console.error("Failed to create item:", error);
      return null;
    }

    return data;
  } catch (error) {
    console.error("Request failed:", error);
    // If it's a CSRF error (403), token will be refreshed automatically
    // Consider retrying the request
    throw error;
  }
}
```

#### Backend
```go
func (h *ItemHandler) CreateItem(c echo.Context) error {
    // CSRF already validated by middleware

    var req struct {
        Name        string `json:"name"`
        Description string `json:"description"`
    }

    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest,
            ErrorResponse{Error: "invalid request"})
    }

    // Create item in database
    item := &db.Item{
        Name:        req.Name,
        Description: req.Description,
    }

    // Save and return
    return c.JSON(http.StatusCreated, item)
}
```

### Form Submission with Fetch

```typescript
// Traditional form submission with CSRF token

async function submitForm(formData: FormData) {
  const token = getCSRFToken();

  const response = await fetch("/api/v1/items", {
    method: "POST",
    headers: {
      "X-CSRF-Token": token, // Include CSRF token
    },
    body: formData, // Send form data
  });

  if (response.status === 403) {
    // Token might have been rotated
    const newResponse = await submitForm(formData); // Retry
    return newResponse;
  }

  return response.json();
}
```

### Handling CSRF Errors

```typescript
import { handleCSRFError, refreshCSRFToken } from "@/lib/csrf";

// In API error handling
async function handleApiError(response: Response) {
  // Check if it's a CSRF error
  const wasCsrfError = await handleCSRFError(response.clone());

  if (wasCsrfError) {
    console.log("CSRF token was refreshed");
    // Caller should retry the request with the new token
    return { shouldRetry: true };
  }

  // Handle other errors
  return { shouldRetry: false };
}
```

## Testing Examples

### Frontend Tests

```typescript
import { fetchCSRFToken, getCSRFToken } from "@/lib/csrf";

describe("CSRF Protection", () => {
  it("should fetch token on init", async () => {
    const token = await fetchCSRFToken();
    expect(token).toBeDefined();
    expect(getCSRFToken()).toBe(token);
  });

  it("should add CSRF header to POST requests", async () => {
    const token = await fetchCSRFToken();
    const headers = getCSRFHeaders("POST");
    expect(headers["X-CSRF-Token"]).toBe(token);
  });
});
```

### Backend Tests

```go
func TestCreateItemWithCSRF(t *testing.T) {
    e := echo.New()

    // Setup CSRF middleware
    config := custommw.CSRFConfig{
        Secret:  []byte("test-secret"),
        Enabled: true,
    }
    e.Use(custommw.CSRFMiddleware(config))

    // Create handler
    e.POST("/api/v1/items", itemHandler.CreateItem)

    // Get CSRF token
    token, _ := custommw.generateCSRFToken(32)

    // Make request with token
    body := `{"name":"Test Item"}`
    req := httptest.NewRequest("POST", "/api/v1/items",
        strings.NewReader(body))
    req.Header.Set("X-CSRF-Token", token)
    req.AddCookie(&http.Cookie{
        Name:  custommw.CSRFTokenCookie,
        Value: token,
    })

    rec := httptest.NewRecorder()
    e.ServeHTTP(rec, req)

    assert.Equal(t, http.StatusCreated, rec.Code)
}
```

## Common Patterns

### Retry on CSRF Error

```typescript
async function makeRequestWithCSRFRetry(
  method: string,
  path: string,
  body?: unknown
): Promise<Response> {
  const makeRequest = async () => {
    return fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        "X-CSRF-Token": getCSRFToken() || "",
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  };

  let response = await makeRequest();

  if (response.status === 403) {
    // Refresh token and retry
    await refreshCSRFToken();
    response = await makeRequest();
  }

  return response;
}
```

### Bulk Operations with CSRF

```typescript
async function bulkCreateItems(items: ItemInput[]) {
  const results = [];

  for (const item of items) {
    try {
      const { data, error } = await apiClient.POST("/api/v1/items", {
        body: item
      });

      if (error) {
        results.push({ ...item, error });
      } else {
        results.push({ ...item, success: true, data });
      }
    } catch (error) {
      results.push({ ...item, error });
    }
  }

  return results;
}
```

### Form Data Submission

```go
// Backend can accept token from form data
func (h *ItemHandler) CreateItem(c echo.Context) error {
    // Token can be in:
    // 1. X-CSRF-Token header (preferred)
    // 2. _csrf_token form field
    // 3. csrf_token cookie

    // Middleware validates automatically

    var req struct {
        Name string `form:"name"`
        Description string `form:"description"`
    }

    if err := c.Bind(&req); err != nil {
        return err
    }

    // Process form data...
    return c.JSON(http.StatusCreated, result)
}
```

## Environment Setup

### Development

```bash
# .env.local or .env.development
CSRF_SECRET=development-secret-change-in-production

# Or generate random:
# openssl rand -base64 64
CSRF_SECRET=xK8mN2pQr7sT9vW1yZ3aB5cD6eF7gH8iJ9kL0mN1oP2qR3sT4uV5wX6yZ7aB8cD9e==
```

### Production

```bash
# .env.production
# CRITICAL: Generate a new random secret
CSRF_SECRET=$(openssl rand -base64 64)

# Verify it's set
echo $CSRF_SECRET
```

## Troubleshooting Guide

### Token Not Being Set

```typescript
// Check if token is initialized
const token = getCSRFToken();
if (!token) {
  console.warn("CSRF token not initialized");
  // Try refreshing
  await refreshCSRFToken();
}

// Log state for debugging
logCSRFState();
```

### 403 Forbidden Errors

```go
// Check backend logs for CSRF validation failures
// Enable debug logging:
// c.Logger().Debugf("CSRF validation failed: token mismatch")

// Verify:
// 1. X-CSRF-Token header is present
// 2. csrf_token cookie is set
// 3. Both values match (server-side validation)
```

### Token Expires During Long Operations

```typescript
// For long-running operations, refresh token before starting
await refreshCSRFToken();

// Then make request
const response = await fetch(url, {
  method: "POST",
  headers: { "X-CSRF-Token": getCSRFToken() },
  body: largePayload,
});
```

## Best Practices

✅ **DO**:
- Let the system manage tokens automatically
- Use the API client for requests (tokens injected)
- Refresh tokens on 403 errors
- Log CSRF state when debugging
- Keep CSRF_SECRET secure in production
- Use HTTPS in production (for Secure cookie flag)

❌ **DON'T**:
- Store tokens in localStorage
- Disable CSRF protection in production
- Hardcode tokens in code
- Share CSRF_SECRET across environments
- Use same CSRF_SECRET for dev and prod
- Commit CSRF_SECRET to git

## Additional Resources

- See `/docs/CSRF_PROTECTION.md` for complete documentation
- Check test files for more examples
- Review OWASP guidelines: https://cheatsheetseries.owasp.org/
