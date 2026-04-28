// Package events defines domain event types and helpers.
package events

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

// EntityType represents the type of entity an event relates to
type EntityType string

// Entity types for event payloads.
const (
	EntityTypeItem    EntityType = "item"
	EntityTypeLink    EntityType = "link"
	EntityTypeProject EntityType = "project"
	EntityTypeAgent   EntityType = "agent"
)

// EventType represents the type of operation performed
type EventType string

// Event types for domain actions.
const (
	EventTypeCreated EventType = "created"
	EventTypeUpdated EventType = "updated"
	EventTypeDeleted EventType = "deleted"

	// Item specific events
	EventTypeItemStatusChanged   EventType = "item.status_changed"
	EventTypeItemPriorityChanged EventType = "item.priority_changed"

	// Link specific events
	EventTypeLinkCreated EventType = "link.created"
	EventTypeLinkDeleted EventType = "link.deleted"

	// Agent specific events
	EventTypeAgentStarted  EventType = "agent.started"
	EventTypeAgentStopped  EventType = "agent.stopped"
	EventTypeAgentActivity EventType = "agent.activity"
	EventTypeAgentError    EventType = "agent.error"

	// System events
	EventTypeSnapshot EventType = "snapshot"
	EventTypeRollback EventType = "rollback"
)

// Event represents a domain event in the system
type Event struct {
	ID            string                 `json:"id"`
	ProjectID     string                 `json:"project_id"`
	EntityType    EntityType             `json:"entity_type"`
	EntityID      string                 `json:"entity_id"`
	EventType     EventType              `json:"event_type"`
	Data          map[string]interface{} `json:"data"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
	Version       int64                  `json:"version"`                  // For optimistic locking and ordering
	CausationID   *string                `json:"causation_id,omitempty"`   // ID of command/event that caused this
	CorrelationID *string                `json:"correlation_id,omitempty"` // ID for tracing related events
	CreatedAt     time.Time              `json:"created_at"`
}

// NewEvent creates a new event with generated ID and timestamp
func NewEvent(
	projectID string,
	entityID string,
	entityType EntityType,
	eventType EventType,
	data map[string]interface{},
) *Event {
	return &Event{
		ID:         uuid.New().String(),
		ProjectID:  projectID,
		EntityType: entityType,
		EntityID:   entityID,
		EventType:  eventType,
		Data:       data,
		Metadata:   make(map[string]interface{}),
		CreatedAt:  time.Now().UTC(),
		Version:    1,
	}
}

// WithMetadata adds metadata to the event
func (e *Event) WithMetadata(key string, value interface{}) *Event {
	if e.Metadata == nil {
		e.Metadata = make(map[string]interface{})
	}
	e.Metadata[key] = value
	return e
}

// WithCausation sets the causation ID (ID of event/command that caused this event)
func (e *Event) WithCausation(causationID string) *Event {
	e.CausationID = &causationID
	return e
}

// WithCorrelation sets the correlation ID for tracing related events
func (e *Event) WithCorrelation(correlationID string) *Event {
	e.CorrelationID = &correlationID
	return e
}

// WithVersion sets the version explicitly
func (e *Event) WithVersion(version int64) *Event {
	e.Version = version
	return e
}

// ToJSON serializes the event to JSON
func (e *Event) ToJSON() ([]byte, error) {
	return json.Marshal(e)
}

// FromJSON deserializes an event from JSON
func FromJSON(data []byte) (*Event, error) {
	var event Event
	if err := json.Unmarshal(data, &event); err != nil {
		return nil, err
	}
	return &event, nil
}

// Snapshot represents a point-in-time snapshot of an entity's state
type Snapshot struct {
	ID         string                 `json:"id"`
	ProjectID  string                 `json:"project_id"`
	EntityType EntityType             `json:"entity_type"`
	EntityID   string                 `json:"entity_id"`
	Version    int64                  `json:"version"` // Event version at which snapshot was taken
	State      map[string]interface{} `json:"state"`   // Complete entity state
	CreatedAt  time.Time              `json:"created_at"`
}

// NewSnapshot creates a new snapshot
func NewSnapshot(
	projectID string,
	entityID string,
	entityType EntityType,
	version int64,
	state map[string]interface{},
) *Snapshot {
	return &Snapshot{
		ID:         uuid.New().String(),
		ProjectID:  projectID,
		EntityType: entityType,
		EntityID:   entityID,
		Version:    version,
		State:      state,
		CreatedAt:  time.Now().UTC(),
	}
}

// EventStore defines the interface for event storage and retrieval
type EventStore interface {
	// Store saves an event to the store
	Store(event *Event) error

	// StoreMany saves multiple events atomically
	StoreMany(events []*Event) error

	// GetByEntityID retrieves all events for a specific entity
	GetByEntityID(entityID string) ([]*Event, error)

	// GetByEntityIDAfterVersion retrieves events after a specific version
	GetByEntityIDAfterVersion(entityID string, version int64) ([]*Event, error)

	// GetByProjectID retrieves all events for a project
	GetByProjectID(projectID string, limit, offset int) ([]*Event, error)

	// GetByProjectIDAndType retrieves events by project and entity type
	GetByProjectIDAndType(projectID string, entityType EntityType, limit, offset int) ([]*Event, error)

	// GetByTimeRange retrieves events within a time range
	GetByTimeRange(projectID string, start, end time.Time) ([]*Event, error)

	// SaveSnapshot saves a snapshot
	SaveSnapshot(snapshot *Snapshot) error

	// GetLatestSnapshot retrieves the most recent snapshot for an entity
	GetLatestSnapshot(entityID string) (*Snapshot, error)

	// GetSnapshotAtVersion retrieves a snapshot at or before a specific version
	GetSnapshotAtVersion(entityID string, version int64) (*Snapshot, error)

	// Replay replays events to reconstruct entity state
	Replay(entityID string) (map[string]interface{}, error)

	// ReplayFromSnapshot replays events from a snapshot
	ReplayFromSnapshot(entityID string, snapshotVersion int64) (map[string]interface{}, error)
}

// EventPublisher defines the interface for publishing events to external systems
type EventPublisher interface {
	// Publish publishes an event to all subscribers
	Publish(event *Event) error

	// PublishToProject publishes an event to project-specific subscribers
	PublishToProject(projectID string, event *Event) error

	// PublishToEntity publishes an event to entity-specific subscribers
	PublishToEntity(entityID string, event *Event) error
}

// EventSubscriber defines the interface for subscribing to events
type EventSubscriber interface {
	// Subscribe subscribes to all events
	Subscribe(handler func(*Event)) error

	// SubscribeToProject subscribes to project-specific events
	SubscribeToProject(projectID string, handler func(*Event)) error

	// SubscribeToEntity subscribes to entity-specific events
	SubscribeToEntity(entityID string, handler func(*Event)) error

	// SubscribeToEventType subscribes to specific event types
	SubscribeToEventType(eventType EventType, handler func(*Event)) error

	// Unsubscribe removes a subscription
	Unsubscribe(subscriptionID string) error
}

// EventHandler defines the interface for handling events
type EventHandler interface {
	// Handle processes an event
	Handle(event *Event) error

	// CanHandle checks if this handler can process the event
	CanHandle(event *Event) bool
}

// Aggregate represents an aggregate root in DDD
type Aggregate interface {
	// GetID returns the aggregate ID
	GetID() string

	// GetVersion returns the current version
	GetVersion() int64

	// ApplyEvent applies an event to update the aggregate state
	ApplyEvent(event *Event) error

	// GetUncommittedEvents returns events that haven't been persisted
	GetUncommittedEvents() []*Event

	// MarkEventsAsCommitted marks events as persisted
	MarkEventsAsCommitted()

	// LoadFromHistory loads the aggregate from event history
	LoadFromHistory(events []*Event) error
}

// BaseAggregate provides common aggregate functionality
type BaseAggregate struct {
	ID                string
	Version           int64
	UncommittedEvents []*Event
}

// NewBaseAggregate creates a new base aggregate
func NewBaseAggregate(id string) *BaseAggregate {
	return &BaseAggregate{
		ID:                id,
		Version:           0,
		UncommittedEvents: make([]*Event, 0),
	}
}

// GetID returns the aggregate ID
func (a *BaseAggregate) GetID() string {
	return a.ID
}

// GetVersion returns the current version
func (a *BaseAggregate) GetVersion() int64 {
	return a.Version
}

// AddUncommittedEvent adds an event to the uncommitted list
func (a *BaseAggregate) AddUncommittedEvent(event *Event) {
	event.Version = a.Version + 1
	a.UncommittedEvents = append(a.UncommittedEvents, event)
	a.Version++
}

// GetUncommittedEvents returns uncommitted events
func (a *BaseAggregate) GetUncommittedEvents() []*Event {
	return a.UncommittedEvents
}

// MarkEventsAsCommitted clears uncommitted events
func (a *BaseAggregate) MarkEventsAsCommitted() {
	a.UncommittedEvents = make([]*Event, 0)
}

// EventBus coordinates event publishing and subscription
type EventBus interface {
	EventPublisher
	EventSubscriber
}
