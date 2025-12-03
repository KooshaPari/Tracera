# API Design & Architecture Patterns - REST vs GraphQL vs tRPC + Hexagonal + Microservices

**Date**: 2025-11-22  
**Scope**: API design, hexagonal architecture, microservices, TDD/SDD

---

## PART 1: API DESIGN COMPARISON

### REST vs GraphQL vs tRPC

| Aspect | REST | GraphQL | tRPC |
|--------|------|---------|------|
| **Type Safety** | ⚠️ Medium | ⚠️ Medium | ✅ Excellent |
| **Over-fetching** | ❌ Yes | ✅ No | ✅ No |
| **Under-fetching** | ❌ Yes | ✅ No | ✅ No |
| **Caching** | ✅ Easy | ⚠️ Hard | ⚠️ Hard |
| **Learning Curve** | ✅ Easy | ⚠️ Medium | ✅ Easy |
| **Ecosystem** | ✅ Largest | ✅ Large | ⚠️ Growing |
| **Performance** | ✅ Good | ⚠️ Medium | ✅ Excellent |
| **Complexity** | ✅ Low | ❌ High | ✅ Low |
| **Debugging** | ✅ Easy | ⚠️ Medium | ✅ Easy |
| **Monitoring** | ✅ Easy | ⚠️ Hard | ⚠️ Medium |

### REST Advantages

- ✅ Simple and well-understood
- ✅ Easy caching (HTTP caching)
- ✅ Easy monitoring (standard HTTP)
- ✅ Largest ecosystem
- ✅ Easy debugging (curl, Postman)
- ✅ Stateless by design

### REST Disadvantages

- ❌ Over-fetching (get more data than needed)
- ❌ Under-fetching (need multiple requests)
- ❌ Versioning complexity (v1, v2, v3)
- ❌ No type safety (need OpenAPI)

### GraphQL Advantages

- ✅ No over-fetching
- ✅ No under-fetching
- ✅ Single endpoint
- ✅ Strongly typed schema
- ✅ Introspection

### GraphQL Disadvantages

- ❌ Complex to implement
- ❌ Hard to cache
- ❌ Hard to monitor
- ❌ N+1 query problem
- ❌ Steep learning curve
- ❌ Overkill for simple APIs

### tRPC Advantages

- ✅ Full type safety (TypeScript)
- ✅ No over-fetching
- ✅ No under-fetching
- ✅ Simple to implement
- ✅ Excellent DX
- ✅ No schema needed
- ✅ Automatic client generation

### tRPC Disadvantages

- ❌ TypeScript-only (frontend + backend)
- ❌ Smaller ecosystem
- ❌ Not suitable for public APIs
- ❌ Not suitable for mobile clients
- ❌ Not suitable for third-party integrations

---

## PART 2: API DESIGN FOR TRACERTM

### TraceRTM API Requirements

1. **Internal API** (frontend ↔ backend)
   - ✅ Type-safe
   - ✅ No over-fetching
   - ✅ Excellent DX
   - ✅ Automatic client generation

2. **Agent API** (agents ↔ backend)
   - ✅ Type-safe
   - ✅ Programmatic access
   - ✅ Batch operations
   - ✅ Webhooks

3. **Integration API** (external services)
   - ✅ REST (standard)
   - ✅ Webhooks (bidirectional)
   - ✅ Public documentation

4. **Real-Time API** (WebSocket)
   - ✅ Event streaming
   - ✅ Agent coordination
   - ✅ Live updates

### Verdict: Hybrid Approach

**Internal API**: tRPC (type-safe, excellent DX)
**Agent API**: REST + tRPC (flexibility)
**Integration API**: REST + Webhooks (standard)
**Real-Time API**: WebSocket (Supabase Realtime)

---

## PART 3: HEXAGONAL ARCHITECTURE (PORTS & ADAPTERS)

### Core Concept

```
┌─────────────────────────────────────────────────────────┐
│                    EXTERNAL WORLD                        │
│  (HTTP, WebSocket, Database, Message Queue, etc.)       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    ADAPTERS (Input)                      │
│  (HTTP Handler, WebSocket Handler, CLI, etc.)           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    PORTS (Input)                         │
│  (Interfaces: CreateItemPort, UpdateItemPort, etc.)     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION CORE                        │
│  (Use Cases, Domain Logic, Business Rules)              │
│  (CreateItemUseCase, UpdateItemUseCase, etc.)           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    PORTS (Output)                        │
│  (Interfaces: ItemRepository, EventBus, etc.)           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   ADAPTERS (Output)                      │
│  (PostgreSQL, Redis, Message Queue, etc.)               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    EXTERNAL WORLD                        │
│  (Database, Cache, Message Queue, etc.)                 │
└─────────────────────────────────────────────────────────┘
```

### TraceRTM Hexagonal Architecture

**Input Ports**:
- CreateItemPort
- UpdateItemPort
- DeleteItemPort
- CreateLinkPort
- UpdateLinkPort
- DeleteLinkPort
- QueryItemsPort
- QueryLinksPort

**Input Adapters**:
- HTTPAdapter (REST/tRPC)
- WebSocketAdapter (real-time)
- CLIAdapter (command-line)
- AgentAPIAdapter (programmatic)

**Application Core**:
- CreateItemUseCase
- UpdateItemUseCase
- DeleteItemUseCase
- CreateLinkUseCase
- UpdateLinkUseCase
- DeleteLinkUseCase
- QueryItemsUseCase
- QueryLinksUseCase
- ResolveConflictUseCase
- SyncAgentUseCase

**Output Ports**:
- ItemRepository
- LinkRepository
- EventBus
- NotificationService
- IntegrationService

**Output Adapters**:
- PostgreSQLAdapter (database)
- SupabaseRealtimeAdapter (real-time)
- NATSAdapter (message queue)
- SlackAdapter (notifications)
- JiraAdapter (integrations)

---

## PART 4: MICROSERVICES ARCHITECTURE

### Bounded Contexts (Domain-Driven Design)

**1. Item Management Service**
- Create, read, update, delete items
- Item versioning
- Item status workflow

**2. Link Management Service**
- Create, read, update, delete links
- Link validation
- Cycle detection

**3. Agent Coordination Service**
- Agent registration
- Workload distribution
- Conflict resolution

**4. Event Sourcing Service**
- Event storage
- Event replay
- Temporal queries

**5. Search Service**
- Full-text search
- Semantic search (pgvector)
- Indexing

**6. Integration Service**
- Jira sync
- GitHub sync
- Slack notifications

**7. Real-Time Service**
- WebSocket management
- Event broadcasting
- Live updates

**8. Notification Service**
- Push notifications
- Email notifications
- Webhook notifications

### Microservices Communication

**Synchronous**:
- REST API calls
- tRPC calls
- gRPC calls

**Asynchronous**:
- Message queue (NATS)
- Event bus (Supabase Realtime)
- Webhooks

### Microservices Deployment

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                          │
│  (Route requests to appropriate service)                │
└─────────────────────────────────────────────────────────┘
        ↓           ↓           ↓           ↓
┌──────────────┬──────────────┬──────────────┬──────────────┐
│    Item      │    Link      │    Agent     │    Event     │
│  Service     │  Service     │  Service     │  Service     │
│  (Go)        │  (Go)        │  (Go)        │  (Python)    │
└──────────────┴──────────────┴──────────────┴──────────────┘
        ↓           ↓           ↓           ↓
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   Search     │ Integration  │  Real-Time   │ Notification │
│  Service     │  Service     │  Service     │  Service     │
│  (Python)    │  (Go)        │  (Go)        │  (Go)        │
└──────────────┴──────────────┴──────────────┴──────────────┘
        ↓           ↓           ↓           ↓
┌─────────────────────────────────────────────────────────┐
│              Shared Infrastructure                       │
│  (PostgreSQL, Redis, NATS, Supabase Realtime)           │
└─────────────────────────────────────────────────────────┘
```

---

## PART 5: TEST-DRIVEN DESIGN (TDD)

### TDD Workflow

```
1. Write failing test
   ↓
2. Write minimal code to pass test
   ↓
3. Refactor code
   ↓
4. Repeat
```

### TraceRTM TDD Structure

**Unit Tests** (test business logic):
```go
func TestCreateItem(t *testing.T) {
    // Arrange
    repo := NewMockItemRepository()
    useCase := NewCreateItemUseCase(repo)
    
    // Act
    item, err := useCase.Execute(CreateItemRequest{
        Title: "Test Item",
        Type: "feature",
    })
    
    // Assert
    assert.NoError(t, err)
    assert.Equal(t, "Test Item", item.Title)
    assert.Equal(t, "feature", item.Type)
}
```

**Integration Tests** (test with real database):
```go
func TestCreateItemIntegration(t *testing.T) {
    // Setup database
    db := setupTestDB()
    defer db.Close()
    
    repo := NewPostgresItemRepository(db)
    useCase := NewCreateItemUseCase(repo)
    
    // Execute
    item, err := useCase.Execute(CreateItemRequest{
        Title: "Test Item",
        Type: "feature",
    })
    
    // Assert
    assert.NoError(t, err)
    assert.NotNil(t, item.ID)
}
```

**E2E Tests** (test full flow):
```go
func TestCreateItemE2E(t *testing.T) {
    // Start server
    server := startTestServer()
    defer server.Close()
    
    // Make HTTP request
    resp, err := http.Post(
        server.URL + "/items",
        "application/json",
        bytes.NewReader([]byte(`{"title":"Test","type":"feature"}`)),
    )
    
    // Assert
    assert.Equal(t, 201, resp.StatusCode)
}
```

---

## PART 6: SCHEMA-DRIVEN DESIGN (SDD)

### Schema-First Approach

**Step 1: Define OpenAPI Schema**
```yaml
openapi: 3.0.0
paths:
  /items:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateItemRequest'
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Item'

components:
  schemas:
    CreateItemRequest:
      type: object
      properties:
        title:
          type: string
        type:
          type: string
          enum: [feature, code, test, api, database, wireframe, documentation, deployment]
        description:
          type: string
      required: [title, type]
    
    Item:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        type:
          type: string
        description:
          type: string
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time
```

**Step 2: Generate Code from Schema**
```bash
# Generate Go types from OpenAPI
oapi-codegen -package api schema.yaml > api/types.go

# Generate TypeScript types from OpenAPI
openapi-typescript schema.yaml > api/types.ts
```

**Step 3: Implement Handlers**
```go
func (h *ItemHandler) CreateItem(w http.ResponseWriter, r *http.Request) {
    var req api.CreateItemRequest
    json.NewDecoder(r.Body).Decode(&req)
    
    item, err := h.useCase.Execute(req)
    if err != nil {
        http.Error(w, err.Error(), 400)
        return
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(item)
}
```

**Step 4: Generate Client from Schema**
```typescript
// Auto-generated client
const client = createClient<paths>({
  baseUrl: 'http://localhost:8000',
});

// Type-safe API calls
const response = await client.POST('/items', {
  body: {
    title: 'Test Item',
    type: 'feature',
  },
});
```

---

## PART 7: COMPLETE ARCHITECTURE STACK

### Backend Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                          │
│  (Echo framework, rate limiting, auth)                  │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│                  Input Adapters                          │
│  (HTTP, WebSocket, CLI, Agent API)                      │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│                  Input Ports                            │
│  (Interfaces for use cases)                             │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│              Application Core (Use Cases)               │
│  (CreateItem, UpdateItem, DeleteItem, etc.)             │
│  (Domain logic, business rules)                         │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│                  Output Ports                           │
│  (Interfaces for repositories, services)                │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│                 Output Adapters                         │
│  (PostgreSQL, Redis, NATS, Supabase, etc.)              │
└─────────────────────────────────────────────────────────┘
```

### Microservices

```
Item Service (Go)
├─ CreateItemUseCase
├─ UpdateItemUseCase
├─ DeleteItemUseCase
└─ QueryItemsUseCase

Link Service (Go)
├─ CreateLinkUseCase
├─ UpdateLinkUseCase
├─ DeleteLinkUseCase
└─ QueryLinksUseCase

Agent Service (Go)
├─ RegisterAgentUseCase
├─ AssignWorkloadUseCase
├─ ResolveConflictUseCase
└─ SyncAgentUseCase

Event Service (Python)
├─ StoreEventUseCase
├─ ReplayEventUseCase
└─ QueryEventsUseCase

Search Service (Python)
├─ IndexItemUseCase
├─ FullTextSearchUseCase
└─ SemanticSearchUseCase

Integration Service (Go)
├─ SyncToJiraUseCase
├─ SyncFromGitHubUseCase
└─ NotifySlackUseCase

Real-Time Service (Go)
├─ BroadcastEventUseCase
├─ SubscribeToUpdatesUseCase
└─ ManageConnectionsUseCase

Notification Service (Go)
├─ SendPushNotificationUseCase
├─ SendEmailUseCase
└─ SendWebhookUseCase
```

### API Design

```
Internal API (tRPC)
├─ items.create
├─ items.update
├─ items.delete
├─ items.list
├─ links.create
├─ links.update
├─ links.delete
└─ links.list

Agent API (REST)
├─ POST /api/v1/items
├─ PUT /api/v1/items/{id}
├─ DELETE /api/v1/items/{id}
├─ GET /api/v1/items
├─ POST /api/v1/links
├─ PUT /api/v1/links/{id}
├─ DELETE /api/v1/links/{id}
└─ GET /api/v1/links

Integration API (REST + Webhooks)
├─ POST /webhooks/jira
├─ POST /webhooks/github
├─ POST /webhooks/slack
└─ GET /integrations

Real-Time API (WebSocket)
├─ subscribe:items
├─ subscribe:links
├─ subscribe:agents
└─ subscribe:events
```

---

## CONCLUSION

### ✅ COMPLETE ARCHITECTURE FINALIZED

**Backend Language**: Go (Echo framework)
**API Design**: Hybrid (tRPC internal, REST external, WebSocket real-time)
**Architecture**: Hexagonal (ports & adapters)
**Microservices**: 8 bounded contexts
**Design Approach**: TDD + SDD (test-driven + schema-driven)

**This architecture is**:
- ✅ Scalable (microservices)
- ✅ Testable (hexagonal)
- ✅ Maintainable (clear separation)
- ✅ Type-safe (schema-driven)
- ✅ Performance-optimized (Go)
- ✅ Real-time capable (WebSocket)


