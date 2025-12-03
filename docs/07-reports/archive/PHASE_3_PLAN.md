# Phase 3: Handler Integration & Adapter Implementation

## Overview

Phase 3 focuses on integrating the adapter pattern into all handlers and implementing the actual API calls for AuthKit and Supabase adapters.

## Architecture

```
Handlers (Echo)
    ↓
Middleware (AuthAdapterMiddleware)
    ↓
Business Logic (Services, Repositories)
    ↓
Adapters (AuthProvider, RealtimeBroadcaster)
    ↓
External Services (AuthKit, Supabase, NATS)
```

## Phase 3 Tasks

### Task 1: Implement AuthKit Adapter ✅ Defined
**Files**: `backend/internal/auth/authkit_adapter.go`
**Status**: Skeleton created, needs implementation

**Subtasks**:
- [ ] Implement ValidateToken using AuthKit API
- [ ] Implement GetUser using AuthKit API
- [ ] Implement CreateUser using AuthKit API
- [ ] Implement UpdateUser using AuthKit API
- [ ] Implement DeleteUser using AuthKit API
- [ ] Implement ListUsers using AuthKit API
- [ ] Add error handling and logging
- [ ] Add unit tests

### Task 2: Implement Supabase Auth Adapter ✅ Defined
**Files**: `backend/internal/auth/supabase_adapter.go`
**Status**: Skeleton created, needs implementation

**Subtasks**:
- [ ] Implement ValidateToken using Supabase Auth API
- [ ] Implement GetUser using Supabase Auth API
- [ ] Implement CreateUser using Supabase Auth API
- [ ] Implement UpdateUser using Supabase Auth API
- [ ] Implement DeleteUser using Supabase Auth API
- [ ] Implement ListUsers using Supabase Auth API
- [ ] Add error handling and logging
- [ ] Add unit tests

### Task 3: Implement Supabase Realtime Adapter ✅ Defined
**Files**: `backend/internal/realtime/supabase_realtime_adapter.go`
**Status**: Skeleton created, needs implementation

**Subtasks**:
- [ ] Implement WebSocket connection to Supabase Realtime
- [ ] Implement Subscribe using Supabase Realtime API
- [ ] Implement SubscribeWithFilter using Supabase Realtime API
- [ ] Implement Unsubscribe
- [ ] Implement Publish
- [ ] Implement PublishToChannel
- [ ] Add error handling and reconnection logic
- [ ] Add unit tests

### Task 4: Integrate Adapters into Handlers ✅ Defined
**Files**: `backend/internal/handlers/handlers.go`
**Status**: Needs refactoring

**Subtasks**:
- [ ] Update ItemHandler to use adapters
- [ ] Update LinkHandler to use adapters
- [ ] Update AgentHandler to use adapters
- [ ] Update ProjectHandler to use adapters
- [ ] Add realtime event publishing on mutations
- [ ] Add cache invalidation on mutations
- [ ] Update all handlers to use AuthAdapterMiddleware
- [ ] Add integration tests

### Task 5: Add Caching Layer Integration ✅ Defined
**Files**: `backend/internal/cache/redis.go`
**Status**: Implemented, needs handler integration

**Subtasks**:
- [ ] Integrate cache into ItemHandler
- [ ] Integrate cache into LinkHandler
- [ ] Integrate cache into AgentHandler
- [ ] Integrate cache into ProjectHandler
- [ ] Add cache invalidation on mutations
- [ ] Add cache statistics endpoint
- [ ] Add unit tests

### Task 6: Add NATS Event Publishing ✅ Defined
**Files**: `backend/internal/nats/publisher.go`
**Status**: Implemented, needs handler integration

**Subtasks**:
- [ ] Integrate NATS publisher into ItemHandler
- [ ] Integrate NATS publisher into LinkHandler
- [ ] Integrate NATS publisher into AgentHandler
- [ ] Integrate NATS publisher into ProjectHandler
- [ ] Publish events on all mutations
- [ ] Add event filtering and routing
- [ ] Add unit tests

### Task 7: Add WebSocket Integration ✅ Defined
**Files**: `backend/internal/websocket/websocket.go`
**Status**: Implemented, needs handler integration

**Subtasks**:
- [ ] Connect WebSocket hub to realtime broadcaster
- [ ] Implement project-specific subscriptions
- [ ] Implement entity-specific subscriptions
- [ ] Add WebSocket authentication
- [ ] Add WebSocket error handling
- [ ] Add connection statistics
- [ ] Add unit tests

### Task 8: Update Main Application ✅ Defined
**Files**: `backend/main.go`
**Status**: Needs refactoring

**Subtasks**:
- [ ] Initialize adapter factory
- [ ] Initialize cache layer
- [ ] Initialize NATS publisher
- [ ] Initialize WebSocket hub
- [ ] Setup middleware with adapters
- [ ] Setup routes with handlers
- [ ] Add graceful shutdown
- [ ] Add health check endpoint

### Task 9: Add Comprehensive Tests ✅ Defined
**Files**: `backend/tests/`
**Status**: Needs expansion

**Subtasks**:
- [ ] Add adapter unit tests
- [ ] Add handler integration tests
- [ ] Add end-to-end tests with real services
- [ ] Add performance tests
- [ ] Add load tests
- [ ] Add chaos tests
- [ ] Add test fixtures and mocks

### Task 10: Add Documentation ✅ Defined
**Files**: Documentation files
**Status**: Partially complete

**Subtasks**:
- [x] Create ADAPTER_PATTERN_ARCHITECTURE.md
- [x] Create ADAPTER_INTEGRATION_GUIDE.md
- [x] Create PHASE_3_PLAN.md
- [ ] Create API documentation
- [ ] Create deployment guide
- [ ] Create troubleshooting guide
- [ ] Create performance tuning guide

## Implementation Order

1. **Week 1**: Implement AuthKit and Supabase Auth adapters
2. **Week 2**: Implement Supabase Realtime adapter
3. **Week 3**: Integrate adapters into handlers
4. **Week 4**: Add caching, NATS, and WebSocket integration
5. **Week 5**: Testing and documentation
6. **Week 6**: Performance optimization and deployment

## Key Files

### Adapter Files
- `backend/internal/auth/ports.go` - Auth interfaces
- `backend/internal/auth/authkit_adapter.go` - AuthKit implementation
- `backend/internal/auth/supabase_adapter.go` - Supabase Auth implementation
- `backend/internal/realtime/ports.go` - Realtime interfaces
- `backend/internal/realtime/supabase_realtime_adapter.go` - Supabase Realtime implementation
- `backend/internal/realtime/nats_realtime_adapter.go` - NATS implementation
- `backend/internal/adapters/factory.go` - Adapter factory

### Handler Files
- `backend/internal/handlers/handlers.go` - Main handlers
- `backend/internal/middleware/middleware.go` - Middleware with adapters

### Configuration
- `backend/.env.production` - Production environment variables
- `backend/.env.example` - Example environment variables

## Configuration Variables

```bash
# Auth
AUTH_PROVIDER=authkit              # or "supabase"
AUTHKIT_API_KEY=your_key
AUTHKIT_API_URL=https://api.authkit.com

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Realtime
REALTIME_PROVIDER=nats             # or "supabase"

# Redis
REDIS_URL=redis://localhost:6379

# NATS
NATS_URL=nats://connect.ngs.global:4222
NATS_CREDS=/path/to/credentials.creds
```

## Success Criteria

- [ ] All adapters implemented and tested
- [ ] All handlers integrated with adapters
- [ ] All tests passing (100+ tests)
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Deployment guide ready
- [ ] Zero breaking changes to API

## Rollback Plan

If issues arise:
1. Keep old JWT middleware as fallback
2. Keep old handler implementations
3. Use feature flags to switch between old/new
4. Monitor error rates and performance
5. Gradual rollout to production

---

**Status**: Phase 3 Architecture Complete ✅
**Next**: Implement adapters and integrate into handlers

