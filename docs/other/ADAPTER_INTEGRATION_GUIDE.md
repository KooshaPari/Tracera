# Adapter Integration Guide - Phase 3

## Quick Start

### 1. Initialize Adapters in main.go

```go
package main

import (
    "os"
    "github.com/kooshapari/tracertm-backend/internal/adapters"
)

func main() {
    // Create adapter factory
    factory, err := adapters.NewAdapterFactory(adapters.AdapterConfig{
        AuthProvider:     os.Getenv("AUTH_PROVIDER"),      // "authkit" or "supabase"
        AuthKitAPIKey:    os.Getenv("AUTHKIT_API_KEY"),
        AuthKitAPIURL:    os.Getenv("AUTHKIT_API_URL"),
        SupabaseURL:      os.Getenv("SUPABASE_URL"),
        SupabaseKey:      os.Getenv("SUPABASE_KEY"),
        RealtimeProvider: os.Getenv("REALTIME_PROVIDER"),  // "nats" or "supabase"
        NATSConn:         natsConnection,
    })
    if err != nil {
        log.Fatal(err)
    }
    defer factory.Close()

    // Pass factory to handlers
    setupRoutes(e, factory)
}
```

### 2. Use Adapters in Handlers

```go
// internal/handlers/auth_handler.go
type AuthHandler struct {
    authProvider auth.AuthProvider
    broadcaster  realtime.RealtimeBroadcaster
}

func NewAuthHandler(factory *adapters.AdapterFactory) *AuthHandler {
    return &AuthHandler{
        authProvider: factory.GetAuthProvider(),
        broadcaster:  factory.GetRealtimeBroadcaster(),
    }
}

func (h *AuthHandler) Login(c echo.Context) error {
    // Get user from auth provider
    user, err := h.authProvider.ValidateToken(c.Request().Context(), token)
    if err != nil {
        return c.JSON(http.StatusUnauthorized, map[string]string{
            "error": "Invalid credentials",
        })
    }

    // Publish login event
    h.broadcaster.Publish(c.Request().Context(), &realtime.RealtimeEvent{
        Type:      "LOGIN",
        Table:     "users",
        Record:    map[string]interface{}{"user_id": user.ID},
        Timestamp: time.Now().Unix(),
    })

    return c.JSON(http.StatusOK, user)
}
```

### 3. Middleware Setup

```go
// In main.go
e.Use(middleware.AuthAdapterMiddleware(middleware.AuthAdapterConfig{
    AuthProvider: factory.GetAuthProvider(),
    Skipper: func(c echo.Context) bool {
        return c.Path() == "/health" || 
               c.Path() == "/login" ||
               c.Path() == "/signup"
    },
}))
```

## Handler Pattern with Adapters

### Item Handler Example

```go
type ItemHandler struct {
    db          *pgxpool.Pool
    authProvider auth.AuthProvider
    broadcaster  realtime.RealtimeBroadcaster
    cache        *cache.RedisCache
}

func (h *ItemHandler) CreateItem(c echo.Context) error {
    // Get authenticated user from context
    user := c.Get("user").(*auth.User)

    // Create item in database
    queries := db.New(h.db)
    item, err := queries.CreateItem(c.Request().Context(), db.CreateItemParams{
        ProjectID: user.ProjectID,
        Title:     req.Title,
        // ... other fields
    })
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "Failed to create item",
        })
    }

    // Invalidate cache
    h.cache.InvalidatePattern(c.Request().Context(), h.cache.ProjectKeyPattern)

    // Publish realtime event
    h.broadcaster.Publish(c.Request().Context(), &realtime.RealtimeEvent{
        Type:      "INSERT",
        Table:     "items",
        Record:    map[string]interface{}{"id": item.ID, "title": item.Title},
        Timestamp: time.Now().Unix(),
    })

    return c.JSON(http.StatusCreated, item)
}
```

## Testing with Adapters

### Mock Adapter Example

```go
// tests/mocks/mock_auth_provider.go
type MockAuthProvider struct {
    ValidateTokenFunc func(ctx context.Context, token string) (*auth.User, error)
}

func (m *MockAuthProvider) ValidateToken(ctx context.Context, token string) (*auth.User, error) {
    return m.ValidateTokenFunc(ctx, token)
}

// ... implement other methods
```

### Test Usage

```go
func TestCreateItem(t *testing.T) {
    mockAuth := &MockAuthProvider{
        ValidateTokenFunc: func(ctx context.Context, token string) (*auth.User, error) {
            return &auth.User{
                ID:        "user-123",
                Email:     "test@example.com",
                ProjectID: "project-123",
                Role:      "admin",
            }, nil
        },
    }

    handler := &ItemHandler{
        authProvider: mockAuth,
        // ... other fields
    }

    // Test handler
    // ...
}
```

## Switching Providers

### From AuthKit to Supabase

**Before** (with AuthKit):
```bash
AUTH_PROVIDER=authkit
AUTHKIT_API_KEY=your_key
AUTHKIT_API_URL=https://api.authkit.com
```

**After** (with Supabase):
```bash
AUTH_PROVIDER=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
```

**Code changes**: NONE! The adapter pattern handles it automatically.

### From NATS to Supabase Realtime

**Before** (with NATS):
```bash
REALTIME_PROVIDER=nats
```

**After** (with Supabase):
```bash
REALTIME_PROVIDER=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
```

**Code changes**: NONE! The adapter pattern handles it automatically.

## Error Handling

```go
// Graceful fallback if adapter fails
func (h *ItemHandler) CreateItem(c echo.Context) error {
    // ... create item ...

    // Try to publish event, but don't fail if it errors
    if err := h.broadcaster.Publish(c.Request().Context(), event); err != nil {
        c.Logger().Warnf("Failed to publish realtime event: %v", err)
        // Continue - don't fail the request
    }

    return c.JSON(http.StatusCreated, item)
}
```

## Monitoring Adapters

```go
// Add health check endpoint
func (h *HealthHandler) CheckAdapters(c echo.Context) error {
    status := map[string]interface{}{
        "auth":      "ok",
        "realtime":  "ok",
        "database":  "ok",
    }

    // Check auth provider
    if _, err := h.authProvider.GetUser(c.Request().Context(), "health-check"); err != nil {
        status["auth"] = "error: " + err.Error()
    }

    return c.JSON(http.StatusOK, status)
}
```

---

**Next**: Implement actual API calls in AuthKit and Supabase adapters

