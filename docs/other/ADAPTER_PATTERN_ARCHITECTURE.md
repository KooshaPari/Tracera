# Adapter Pattern Architecture - TraceRTM Phase 3

## Overview

The TraceRTM backend now implements a **Hexagonal Architecture** with the **Adapter Pattern** to decouple business logic from external services. This allows easy swapping of authentication providers, real-time systems, and other infrastructure components without changing core application code.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP Handlers (Echo)                      │
├─────────────────────────────────────────────────────────────┤
│                    Middleware Layer                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ AuthAdapterMiddleware (uses AuthProvider interface)  │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                      │
│  (Services, Repositories, Domain Models)                    │
├─────────────────────────────────────────────────────────────┤
│                    Adapter Layer (Ports & Adapters)         │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Auth Adapters   │  │ Realtime Adapters│                │
│  ├──────────────────┤  ├──────────────────┤                │
│  │ • AuthKit        │  │ • Supabase       │                │
│  │ • Supabase Auth  │  │ • NATS           │                │
│  │ • Custom         │  │ • Custom         │                │
│  └──────────────────┘  └──────────────────┘                │
├─────────────────────────────────────────────────────────────┤
│                    External Services                         │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ AuthKit Service  │  │ Supabase Realtime│                │
│  │ Supabase Auth    │  │ NATS Messaging   │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Auth Adapters

**Location**: `backend/internal/auth/`

#### Ports (Interfaces)
- `AuthProvider` - Main authentication interface
- `SessionManager` - Session management interface
- `PermissionChecker` - Permission checking interface

#### Adapters
- `AuthKitAdapter` - AuthKit integration
- `SupabaseAuthAdapter` - Supabase Auth integration

**Usage**:
```go
// In middleware
authProvider := factory.GetAuthProvider()
user, err := authProvider.ValidateToken(ctx, token)
```

### 2. Realtime Adapters

**Location**: `backend/internal/realtime/`

#### Ports (Interfaces)
- `RealtimeSubscriber` - Subscribe to real-time events
- `RealtimePublisher` - Publish real-time events
- `RealtimeBroadcaster` - Combined interface

#### Adapters
- `SupabaseRealtimeAdapter` - Supabase Realtime integration
- `NATSRealtimeAdapter` - NATS messaging integration

**Usage**:
```go
// In handlers
broadcaster := factory.GetRealtimeBroadcaster()
broadcaster.Publish(ctx, &RealtimeEvent{...})
```

### 3. Adapter Factory

**Location**: `backend/internal/adapters/factory.go`

Centralized factory for creating and managing all adapters:

```go
factory, err := adapters.NewAdapterFactory(adapters.AdapterConfig{
    AuthProvider:     "authkit",      // or "supabase"
    RealtimeProvider: "nats",         // or "supabase"
    AuthKitAPIKey:    os.Getenv("AUTHKIT_API_KEY"),
    NATSConn:         natsConnection,
})

authProvider := factory.GetAuthProvider()
broadcaster := factory.GetRealtimeBroadcaster()
```

## Configuration

### Environment Variables

```bash
# Auth Configuration
AUTH_PROVIDER=authkit              # or "supabase"
AUTHKIT_API_KEY=your_api_key
AUTHKIT_API_URL=https://api.authkit.com

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Realtime Configuration
REALTIME_PROVIDER=nats             # or "supabase"
```

## Middleware Integration

### Using AuthAdapterMiddleware

```go
// In main.go
e := echo.New()

// Create adapter factory
factory, err := adapters.NewAdapterFactory(config)
if err != nil {
    log.Fatal(err)
}

// Use auth adapter middleware
e.Use(middleware.AuthAdapterMiddleware(middleware.AuthAdapterConfig{
    AuthProvider: factory.GetAuthProvider(),
    Skipper: func(c echo.Context) bool {
        return c.Path() == "/health" || c.Path() == "/login"
    },
}))
```

## Adding New Adapters

### Step 1: Define Port Interface

```go
// internal/myfeature/ports.go
type MyFeatureProvider interface {
    DoSomething(ctx context.Context) error
}
```

### Step 2: Implement Adapter

```go
// internal/myfeature/my_adapter.go
type MyAdapter struct {
    // configuration
}

func (a *MyAdapter) DoSomething(ctx context.Context) error {
    // implementation
}
```

### Step 3: Register in Factory

```go
// internal/adapters/factory.go
func (f *AdapterFactory) initMyFeature() error {
    switch f.config.MyFeatureProvider {
    case "my_adapter":
        f.myFeature = myfeature.NewMyAdapter(...)
    }
}
```

## Benefits

1. **Loose Coupling** - Business logic doesn't depend on specific implementations
2. **Easy Testing** - Mock adapters for unit tests
3. **Easy Swapping** - Change providers with configuration changes
4. **Scalability** - Add new adapters without modifying existing code
5. **Maintainability** - Clear separation of concerns

## Current Adapters Status

| Adapter | Status | Implementation |
|---------|--------|-----------------|
| AuthKit | ✅ Defined | TODO: Implement API calls |
| Supabase Auth | ✅ Defined | TODO: Implement API calls |
| Supabase Realtime | ✅ Defined | TODO: Implement WebSocket |
| NATS Realtime | ✅ Implemented | Ready to use |

## Next Steps (Phase 3)

1. Implement AuthKit adapter API calls
2. Implement Supabase Auth adapter API calls
3. Implement Supabase Realtime WebSocket connection
4. Integrate adapters into handlers
5. Add comprehensive tests for each adapter
6. Add adapter health checks and monitoring

---

**Architecture Pattern**: Hexagonal Architecture (Ports & Adapters)
**Design Pattern**: Factory Pattern + Strategy Pattern
**Principle**: Dependency Inversion Principle (DIP)

