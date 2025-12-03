# Phase 2: Event Sourcing & CQRS - Detailed Implementation (Weeks 3-4, 80 hours)

## Overview

Complete event sourcing implementation with CQRS pattern for audit trail and performance.

## Week 1: Event Sourcing (40 hours)

### Day 1-2: Event Store (16 hours)

**Tasks:**
1. Create `backend/internal/events/event_store.go`:
   - Append-only event log
   - Event versioning
   - Timestamp tracking
   - Aggregate ID grouping

2. Create `backend/internal/events/event_types.go`:
   - ItemCreated
   - ItemUpdated
   - ItemDeleted
   - LinkCreated
   - LinkDeleted
   - ProjectCreated
   - ProjectUpdated

3. Implement event persistence:
   - Store in PostgreSQL events table
   - Add indexes for performance
   - Add constraints for integrity

### Day 3-4: Event Handlers & Replay (16 hours)

**Tasks:**
1. Create `backend/internal/events/event_handler.go`:
   - Handle each event type
   - Update materialized views
   - Publish to NATS
   - Update Neo4j

2. Implement event replay:
   - Replay from timestamp
   - Replay from event ID
   - Replay for aggregate
   - Verify consistency

3. Add snapshots:
   - Create snapshot after N events
   - Store aggregate state
   - Use for faster replay

### Day 5: Testing & Validation (8 hours)

**Tasks:**
1. Write event store tests
2. Write event handler tests
3. Test replay functionality
4. Test snapshot creation
5. Verify audit trail

## Week 2: CQRS Pattern (40 hours)

### Day 1-2: Read Model (16 hours)

**Tasks:**
1. Create `backend/internal/cqrs/read_model.go`:
   - Separate read database
   - Denormalized schema
   - Optimized for queries
   - Fast joins

2. Create read projections:
   - ItemReadModel
   - LinkReadModel
   - ProjectReadModel
   - AgentReadModel

3. Implement projection handlers:
   - Update on events
   - Maintain consistency
   - Handle failures

### Day 3-4: Write Model (16 hours)

**Tasks:**
1. Create `backend/internal/cqrs/write_model.go`:
   - Command handlers
   - Validation
   - Event generation
   - Consistency checks

2. Implement commands:
   - CreateItem
   - UpdateItem
   - DeleteItem
   - CreateLink
   - DeleteLink

3. Add command validation:
   - Business rules
   - Constraints
   - Permissions

### Day 5: Integration & Testing (8 hours)

**Tasks:**
1. Integrate read/write models
2. Update handlers to use CQRS
3. Write integration tests
4. Test consistency
5. Performance testing

## Implementation Details

### Event Store Schema

```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    version INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX (aggregate_id, version),
    INDEX (created_at)
);
```

### Event Structure

```go
type Event struct {
    ID            string
    AggregateID   string
    AggregateType string
    EventType     string
    EventData     map[string]interface{}
    Metadata      map[string]interface{}
    Version       int
    CreatedAt     time.Time
}
```

### CQRS Command

```go
type Command interface {
    GetAggregateID() string
    GetType() string
}

type CreateItemCommand struct {
    ProjectID   string
    Title       string
    Description string
    Type        string
}
```

## Success Criteria

✅ Event store working
✅ Event replay working
✅ Snapshots working
✅ Read model synchronized
✅ Write model validated
✅ All tests passing
✅ Audit trail complete

## Expected Results

- **Audit Trail:** Complete history of all changes
- **Consistency:** Strong consistency with event sourcing
- **Performance:** Read queries 10x faster
- **Scalability:** Separate read/write scaling

## Troubleshooting

**Issue:** Events not replaying correctly
- Check event versioning
- Check aggregate ID consistency
- Check event handler logic

**Issue:** Read model out of sync
- Check projection handlers
- Check event ordering
- Rebuild projections

**Issue:** Performance degradation
- Check snapshot frequency
- Check index usage
- Check query optimization

## Next Phase

After Phase 2 complete:
- Move to Phase 3: Distributed Systems
- Implement multi-level caching
- Add distributed tracing

