# Distributed Systems Patterns & Scaling 2025

## 🔄 1. Event-Driven Architecture (2025 Standard)

### Event Sourcing + CQRS Pattern
```go
// backend/internal/events/event_store.go
type Event struct {
    ID        string
    AggregateID string
    Type      string
    Data      json.RawMessage
    Timestamp time.Time
}

type EventStore interface {
    Append(ctx context.Context, event Event) error
    GetEvents(ctx context.Context, aggregateID string) ([]Event, error)
    Subscribe(ctx context.Context, eventType string) <-chan Event
}

// Implementation with PostgreSQL
type PostgresEventStore struct {
    db *sql.DB
}

func (es *PostgresEventStore) Append(ctx context.Context, event Event) error {
    _, err := es.db.ExecContext(ctx, `
        INSERT INTO events (id, aggregate_id, type, data, timestamp)
        VALUES ($1, $2, $3, $4, $5)
    `, event.ID, event.AggregateID, event.Type, event.Data, event.Timestamp)
    return err
}
```

### CQRS (Command Query Responsibility Segregation)
```go
// Separate write and read models
type CommandHandler interface {
    CreateItem(ctx context.Context, cmd CreateItemCommand) error
    UpdateItem(ctx context.Context, cmd UpdateItemCommand) error
}

type QueryHandler interface {
    GetItem(ctx context.Context, id string) (*ItemView, error)
    ListItems(ctx context.Context, filter Filter) ([]ItemView, error)
}

// Write model (normalized)
type Item struct {
    ID    string
    Title string
    Links []Link
}

// Read model (denormalized for performance)
type ItemView struct {
    ID              string
    Title           string
    LinkCount       int
    LastModified    time.Time
    RelatedItems    []string
}
```

## 🔀 2. Saga Pattern for Distributed Transactions

### Choreography vs Orchestration

**Choreography (Event-Driven)**
```python
# Each service listens to events and acts
class RequirementService:
    def on_item_created(self, event: ItemCreatedEvent):
        # Create requirement
        requirement = self.create_requirement(event)
        
        # Publish event
        self.publish(RequirementCreatedEvent(requirement))

class LinkService:
    def on_requirement_created(self, event: RequirementCreatedEvent):
        # Find similar requirements
        similar = self.find_similar(event.requirement)
        
        # Suggest links
        self.publish(LinksSuggestedEvent(similar))
```

**Orchestration (Centralized)**
```python
class RequirementOrchestrator:
    def create_requirement(self, item: Item):
        # Step 1: Create requirement
        requirement = self.requirement_service.create(item)
        
        # Step 2: Find similar
        similar = self.link_service.find_similar(requirement)
        
        # Step 3: Create links
        for s in similar:
            self.link_service.create_link(requirement.id, s.id)
        
        # Step 4: Validate
        self.qa_service.validate(requirement)
        
        # Rollback on failure
        if not requirement.is_valid:
            self.rollback(requirement)
```

## 🗄️ 3. Database Scaling Patterns (2025)

### Sharding Strategy
```go
// backend/internal/db/sharding.go
type ShardKey struct {
    ProjectID string
    Shard     int
}

func (sk ShardKey) GetShard(totalShards int) int {
    hash := fnv.New32a()
    hash.Write([]byte(sk.ProjectID))
    return int(hash.Sum32()) % totalShards
}

// Connection pooling per shard
type ShardedDB struct {
    shards map[int]*sql.DB
}

func (sdb *ShardedDB) GetConnection(projectID string) *sql.DB {
    shard := ShardKey{ProjectID: projectID}.GetShard(len(sdb.shards))
    return sdb.shards[shard]
}
```

### Read Replicas
```go
type ReplicaPool struct {
    primary   *sql.DB
    replicas  []*sql.DB
    readIndex int
}

func (rp *ReplicaPool) Read(ctx context.Context, query string) (*sql.Rows, error) {
    // Round-robin read replicas
    replica := rp.replicas[rp.readIndex%len(rp.replicas)]
    rp.readIndex++
    return replica.QueryContext(ctx, query)
}

func (rp *ReplicaPool) Write(ctx context.Context, query string) (sql.Result, error) {
    // Always write to primary
    return rp.primary.ExecContext(ctx, query)
}
```

## 🔀 4. Real-Time Collaboration (CRDT vs OT)

### CRDT (Conflict-free Replicated Data Type)
```typescript
// frontend/src/collaboration/crdt.ts
class CRDTText {
    private chars: Array<{char: string, id: string, timestamp: number}>
    
    insert(char: string, position: number, clientId: string) {
        const id = `${clientId}-${Date.now()}`
        this.chars.splice(position, 0, {
            char,
            id,
            timestamp: Date.now()
        })
        
        // Broadcast to other clients
        this.broadcast({type: 'insert', char, position, id})
    }
    
    delete(position: number) {
        const deleted = this.chars[position]
        this.chars.splice(position, 1)
        
        // Broadcast deletion
        this.broadcast({type: 'delete', id: deleted.id})
    }
    
    merge(remoteOps: Operation[]) {
        // CRDTs automatically resolve conflicts
        for (const op of remoteOps) {
            if (op.type === 'insert') {
                this.applyInsert(op)
            } else {
                this.applyDelete(op)
            }
        }
    }
}
```

### Operational Transformation (OT)
```typescript
class OTText {
    private text: string
    private version: number
    
    insert(char: string, position: number) {
        this.text = this.text.slice(0, position) + char + this.text.slice(position)
        this.version++
        
        return {
            type: 'insert',
            char,
            position,
            version: this.version
        }
    }
    
    transform(localOp: Operation, remoteOp: Operation): Operation {
        // Transform local operation against remote operation
        if (localOp.position < remoteOp.position) {
            return localOp
        } else if (localOp.position > remoteOp.position) {
            return {
                ...localOp,
                position: localOp.position + 1
            }
        }
        return localOp
    }
}
```

**For TraceRTM:** Use CRDT for requirement descriptions (simpler, no server needed)

## 🌐 5. Service Mesh & API Gateway (2025)

### Envoy Gateway (Recommended)
```yaml
# infrastructure/envoy-gateway.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: tracertm-gateway
spec:
  gatewayClassName: envoy
  listeners:
  - name: http
    protocol: HTTP
    port: 80
    routes:
    - name: api-routes
      matches:
      - path:
          type: PathPrefix
          value: /api
      backendRefs:
      - name: api-service
        port: 8080
```

### Service Mesh (Istio vs Linkerd)
```yaml
# Istio VirtualService for traffic management
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-service
spec:
  hosts:
  - api-service
  http:
  - match:
    - uri:
        prefix: /api/v1
    route:
    - destination:
        host: api-service
        port:
          number: 8080
      weight: 90
    - destination:
        host: api-service-canary
        port:
          number: 8080
      weight: 10
```

## 🔐 6. Distributed Transactions (Saga Pattern)

### Compensating Transactions
```go
type Saga struct {
    steps []SagaStep
}

type SagaStep struct {
    action      func() error
    compensation func() error
}

func (s *Saga) Execute() error {
    executed := []SagaStep{}
    
    for _, step := range s.steps {
        if err := step.action(); err != nil {
            // Rollback in reverse order
            for i := len(executed) - 1; i >= 0; i-- {
                executed[i].compensation()
            }
            return err
        }
        executed = append(executed, step)
    }
    
    return nil
}

// Usage
saga := &Saga{
    steps: []SagaStep{
        {
            action: func() error {
                return createRequirement(item)
            },
            compensation: func() error {
                return deleteRequirement(item.ID)
            },
        },
        {
            action: func() error {
                return findAndCreateLinks(item.ID)
            },
            compensation: func() error {
                return deleteLinks(item.ID)
            },
        },
    },
}
```

## 📊 7. Kubernetes Alternatives (2025)

### When to Use Alternatives

**Docker Swarm**
- Simple deployments
- Single machine or small cluster
- Lower operational overhead

**Nomad (HashiCorp)**
- Multi-workload orchestration
- Batch jobs + services
- Better for heterogeneous infrastructure

**Fly.io** (Already using!)
- Serverless containers
- Global edge deployment
- Best for TraceRTM

**Render/Railway**
- Simpler than Kubernetes
- Good for small teams
- Managed infrastructure

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Implement event sourcing
- [ ] Setup CQRS pattern
- [ ] Implement saga pattern
- [ ] Add database sharding
- [ ] Setup read replicas
- [ ] Implement CRDT for collaboration
- [ ] Setup Envoy Gateway
- [ ] Add distributed tracing

## 📊 EFFORT vs BENEFIT

| Pattern | Effort | Benefit | Priority |
|---------|--------|---------|----------|
| Event Sourcing | 8 hrs | Very High | ✅ High |
| CQRS | 6 hrs | High | ✅ High |
| Saga Pattern | 4 hrs | High | ✅ High |
| CRDT | 6 hrs | Medium | ⚠️ Medium |
| Sharding | 12 hrs | Very High | ⚠️ Future |

---

**Status:** Ready for implementation ✅

