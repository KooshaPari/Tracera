# Architectural Patterns Deep Dive

## 1. Domain-Driven Design (DDD)

### Core Concepts

**Bounded Contexts:** Separate domains with clear boundaries
```
TraceRTM System:
├── Project Context (manage projects)
├── Item Context (manage requirements)
├── Link Context (manage relationships)
├── View Context (manage visualizations)
└── Agent Context (manage AI agents)
```

**Aggregates:** Clusters of entities treated as single unit
```go
// Project Aggregate
type Project struct {
    ID        ProjectID
    Name      string
    Items     []Item        // Child entities
    Links     []Link        // Child entities
    CreatedAt time.Time
    UpdatedAt time.Time
}

// Item Aggregate
type Item struct {
    ID        ItemID
    ProjectID ProjectID     // Reference to parent
    Title     string
    Content   string
    Status    ItemStatus
}
```

**Value Objects:** Immutable objects with no identity
```go
type ProjectID struct {
    value string
}

type ItemStatus string
const (
    StatusDraft     ItemStatus = "draft"
    StatusReview    ItemStatus = "review"
    StatusApproved  ItemStatus = "approved"
)
```

**Domain Events:** Significant business events
```go
type DomainEvent interface {
    EventType() string
    Timestamp() time.Time
}

type ItemCreatedEvent struct {
    ItemID    ItemID
    ProjectID ProjectID
    Title     string
    CreatedAt time.Time
}

type LinkEstablishedEvent struct {
    LinkID    LinkID
    SourceID  ItemID
    TargetID  ItemID
    Type      LinkType
    CreatedAt time.Time
}
```

**Repositories:** Abstraction for data access
```go
type ProjectRepository interface {
    Save(ctx context.Context, project *Project) error
    FindByID(ctx context.Context, id ProjectID) (*Project, error)
    FindAll(ctx context.Context) ([]*Project, error)
    Delete(ctx context.Context, id ProjectID) error
}
```

### Implementation Steps

1. **Identify Bounded Contexts**
   - Project management
   - Item management
   - Link management
   - View management
   - Agent coordination

2. **Define Aggregates**
   - Project aggregate (root)
   - Item aggregate (root)
   - Link aggregate (root)

3. **Create Value Objects**
   - ProjectID, ItemID, LinkID
   - ItemStatus, LinkType
   - ProjectName, ItemTitle

4. **Define Domain Events**
   - ItemCreated, ItemUpdated, ItemDeleted
   - LinkCreated, LinkDeleted
   - ProjectCreated, ProjectArchived

5. **Implement Repositories**
   - ProjectRepository
   - ItemRepository
   - LinkRepository

## 2. CQRS (Command Query Responsibility Segregation)

### Separation of Concerns

**Commands:** Operations that change state
```go
type CreateProjectCommand struct {
    Name        string
    Description string
}

type UpdateItemCommand struct {
    ItemID  ItemID
    Title   string
    Content string
}

type EstablishLinkCommand struct {
    SourceID ItemID
    TargetID ItemID
    Type     LinkType
}
```

**Queries:** Operations that read state
```go
type GetProjectQuery struct {
    ProjectID ProjectID
}

type ListItemsQuery struct {
    ProjectID ProjectID
    Filter    ItemFilter
    Sort      SortOrder
}

type SearchLinksQuery struct {
    ProjectID ProjectID
    Query     string
}
```

**Command Handlers:** Execute commands
```go
type CreateProjectHandler struct {
    repo ProjectRepository
}

func (h *CreateProjectHandler) Handle(ctx context.Context, cmd CreateProjectCommand) error {
    project := NewProject(cmd.Name, cmd.Description)
    return h.repo.Save(ctx, project)
}
```

**Query Handlers:** Execute queries
```go
type GetProjectHandler struct {
    repo ProjectRepository
}

func (h *GetProjectHandler) Handle(ctx context.Context, query GetProjectQuery) (*ProjectDTO, error) {
    project, err := h.repo.FindByID(ctx, query.ProjectID)
    if err != nil {
        return nil, err
    }
    return toDTO(project), nil
}
```

### Benefits
- Scalability: Read and write models can scale independently
- Performance: Optimize reads and writes separately
- Clarity: Clear separation of concerns
- Testability: Easy to test commands and queries

## 3. Event Sourcing

### Core Concept: Store Events, Not State

**Traditional Approach:**
```
Database: { Project: { id: 1, name: "P1", status: "active" } }
```

**Event Sourcing Approach:**
```
Event Store:
1. ProjectCreatedEvent { id: 1, name: "P1" }
2. ProjectRenamedEvent { id: 1, newName: "Project 1" }
3. ProjectStatusChangedEvent { id: 1, status: "active" }
```

**Rebuild State from Events:**
```go
func (p *Project) ApplyEvent(event DomainEvent) {
    switch e := event.(type) {
    case ProjectCreatedEvent:
        p.ID = e.ProjectID
        p.Name = e.Name
    case ProjectRenamedEvent:
        p.Name = e.NewName
    case ProjectStatusChangedEvent:
        p.Status = e.Status
    }
}
```

### Benefits
- Complete audit trail
- Time-travel debugging
- Event replay
- Temporal queries
- Compliance

## 4. Hexagonal Architecture

### Layers

```
┌─────────────────────────────────────┐
│         Adapters (HTTP, CLI, gRPC)  │
├─────────────────────────────────────┤
│      Application (Use Cases)        │
├─────────────────────────────────────┤
│      Domain (Business Logic)        │
├─────────────────────────────────────┤
│  Infrastructure (DB, Cache, Msg)    │
└─────────────────────────────────────┘
```

**Domain Layer:** Core business logic
```go
// backend/internal/domain/project/project.go
type Project struct {
    ID    ProjectID
    Name  string
    Items []Item
}

func (p *Project) CreateItem(title string) (*Item, error) {
    // Business logic
}
```

**Application Layer:** Use cases
```go
// backend/internal/application/project/create_project.go
type CreateProjectUseCase struct {
    repo ProjectRepository
}

func (uc *CreateProjectUseCase) Execute(cmd CreateProjectCommand) error {
    // Orchestrate domain logic
}
```

**Adapter Layer:** External interfaces
```go
// backend/internal/adapter/http/project_handler.go
func (h *ProjectHandler) CreateProject(c echo.Context) error {
    // Parse HTTP request
    // Call use case
    // Return HTTP response
}
```

**Infrastructure Layer:** Technical details
```go
// backend/internal/infrastructure/repository/project_repository.go
type PostgresProjectRepository struct {
    db *sql.DB
}

func (r *PostgresProjectRepository) Save(ctx context.Context, p *Project) error {
    // Database operations
}
```

## 5. Reactive Programming

### Streams and Observables

**TypeScript Example:**
```typescript
// frontend/src/hooks/useProjectStream.ts
import { Observable } from 'rxjs'
import { map, filter, debounceTime } from 'rxjs/operators'

export function useProjectStream(projectId: string) {
  return projectStream(projectId).pipe(
    filter(p => p.status === 'active'),
    debounceTime(300),
    map(p => ({ ...p, updated: new Date() }))
  )
}
```

**Go Example:**
```go
// backend/internal/event/stream.go
type EventStream struct {
    events chan DomainEvent
}

func (s *EventStream) Subscribe(ctx context.Context) <-chan DomainEvent {
    return s.events
}

func (s *EventStream) Publish(event DomainEvent) {
    s.events <- event
}
```

## 6. Microservices Patterns

### Service Boundaries

```
Project Service
├── Create project
├── Update project
├── Delete project
└── List projects

Item Service
├── Create item
├── Update item
├── Delete item
└── List items

Link Service
├── Create link
├── Delete link
└── List links

View Service
├── Create view
├── Update view
└── Render view
```

### Inter-Service Communication

**Synchronous:** REST/gRPC
```go
// Call Item Service from Link Service
resp, err := itemClient.GetItem(ctx, &GetItemRequest{ID: itemID})
```

**Asynchronous:** Message Queue
```go
// Publish event to NATS
nats.Publish("item.created", itemCreatedEvent)

// Subscribe to events
nats.Subscribe("item.created", func(msg *nats.Msg) {
    // Handle event
})
```

## Summary

These patterns provide:
- ✅ Clear business logic separation
- ✅ Scalability and performance
- ✅ Testability and maintainability
- ✅ Audit trail and compliance
- ✅ Flexibility and extensibility

**Recommended Implementation Order:**
1. DDD (foundation)
2. Hexagonal Architecture (structure)
3. CQRS (separation)
4. Event Sourcing (audit trail)
5. Reactive Programming (responsiveness)

