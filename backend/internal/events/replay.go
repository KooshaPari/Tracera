package events

import (
	"context"
	"encoding/json"
	"fmt"
	"time"
)

const (
	eventReplayProjectFetchLimit = 10000
	eventReplayStatsFetchLimit   = 100000
	eventReplayMaxChainDepth     = 100
)

// TemporalQuery represents a point-in-time query
type TemporalQuery struct {
	EntityID  string
	Timestamp *time.Time // If nil, returns current state
	Version   *int64     // If specified, returns state at this version
}

// TemporalResult represents the result of a temporal query
type TemporalResult struct {
	EntityID  string                 `json:"entity_id"`
	State     map[string]interface{} `json:"state"`
	Version   int64                  `json:"version"`
	Timestamp time.Time              `json:"timestamp"`
	EventIDs  []string               `json:"event_i_ds"` // List of events that contributed to this state
}

type temporalResultJSON struct {
	EntityID  string                 `json:"entity_id"`
	State     map[string]interface{} `json:"state"`
	Version   int64                  `json:"version"`
	Timestamp time.Time              `json:"timestamp"`
	EventIDs  []string               `json:"event_i_ds"`
}

// MarshalJSON implements json.Marshaler.
func (result TemporalResult) MarshalJSON() ([]byte, error) {
	payload := map[string]interface{}{
		"entity_id": result.EntityID,
		"state":     result.State,
		"version":   result.Version,
		"timestamp": result.Timestamp,
		"event_ids": result.EventIDs,
	}
	return json.Marshal(payload)
}

// UnmarshalJSON implements json.Unmarshaler.
func (result *TemporalResult) UnmarshalJSON(data []byte) error {
	var payload temporalResultJSON
	if err := json.Unmarshal(data, &payload); err != nil {
		return err
	}

	result.EntityID = payload.EntityID
	result.State = payload.State
	result.Version = payload.Version
	result.Timestamp = payload.Timestamp
	result.EventIDs = payload.EventIDs

	if len(result.EventIDs) == 0 {
		var raw map[string]json.RawMessage
		if err := json.Unmarshal(data, &raw); err != nil {
			return err
		}
		rawEventIDs, ok := raw["event_ids"]
		if !ok {
			return nil
		}
		if err := json.Unmarshal(rawEventIDs, &result.EventIDs); err != nil {
			return err
		}
	}
	return nil
}

// EventReplayService provides event replay and temporal analysis
type EventReplayService struct {
	store EventStore
}

// NewEventReplayService creates a new replay service
func NewEventReplayService(store EventStore) *EventReplayService {
	return &EventReplayService{store: store}
}

// ReplayToTimestamp replays events up to a specific timestamp
func (service *EventReplayService) ReplayToTimestamp(
	_ context.Context,
	entityID string,
	timestamp time.Time,
) (*TemporalResult, error) {
	// Get all events for the entity
	events, err := service.store.GetByEntityID(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get events: %w", err)
	}

	if len(events) == 0 {
		return nil, fmt.Errorf("no events found for entity %s", entityID)
	}

	state := make(map[string]interface{})
	eventIDs := make([]string, 0)
	var finalVersion int64
	var finalTimestamp time.Time

	// Replay events up to the specified timestamp
	for _, event := range events {
		if event.CreatedAt.After(timestamp) {
			break
		}

		// Apply event data to state
		for key, value := range event.Data {
			state[key] = value
		}

		eventIDs = append(eventIDs, event.ID)
		finalVersion = event.Version
		finalTimestamp = event.CreatedAt
	}

	if len(eventIDs) == 0 {
		return nil, fmt.Errorf("no events before timestamp %s", timestamp)
	}

	return &TemporalResult{
		EntityID:  entityID,
		State:     state,
		Version:   finalVersion,
		Timestamp: finalTimestamp,
		EventIDs:  eventIDs,
	}, nil
}

// ReplayToVersion replays events up to a specific version
func (service *EventReplayService) ReplayToVersion(
	_ context.Context,
	entityID string,
	version int64,
) (*TemporalResult, error) {
	// Get all events for the entity
	events, err := service.store.GetByEntityID(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get events: %w", err)
	}

	if len(events) == 0 {
		return nil, fmt.Errorf("no events found for entity %s", entityID)
	}

	state := make(map[string]interface{})
	eventIDs := make([]string, 0)
	var finalTimestamp time.Time

	// Replay events up to the specified version
	for _, event := range events {
		if event.Version > version {
			break
		}

		// Apply event data to state
		for key, value := range event.Data {
			state[key] = value
		}

		eventIDs = append(eventIDs, event.ID)
		finalTimestamp = event.CreatedAt
	}

	if len(eventIDs) == 0 {
		return nil, fmt.Errorf("no events at or before version %d", version)
	}

	return &TemporalResult{
		EntityID:  entityID,
		State:     state,
		Version:   version,
		Timestamp: finalTimestamp,
		EventIDs:  eventIDs,
	}, nil
}

// GetCurrentState returns the current state by replaying all events
func (service *EventReplayService) GetCurrentState(_ context.Context, entityID string) (*TemporalResult, error) {
	state, err := service.store.Replay(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to replay events: %w", err)
	}

	events, err := service.store.GetByEntityID(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get events: %w", err)
	}

	if len(events) == 0 {
		return nil, fmt.Errorf("no events found for entity %s", entityID)
	}

	eventIDs := make([]string, len(events))
	for index, event := range events {
		eventIDs[index] = event.ID
	}

	lastEvent := events[len(events)-1]

	return &TemporalResult{
		EntityID:  entityID,
		State:     state,
		Version:   lastEvent.Version,
		Timestamp: lastEvent.CreatedAt,
		EventIDs:  eventIDs,
	}, nil
}

// GetStateAtMultiplePoints returns state at multiple points in time
func (service *EventReplayService) GetStateAtMultiplePoints(
	ctx context.Context,
	entityID string,
	timestamps []time.Time,
) ([]*TemporalResult, error) {
	results := make([]*TemporalResult, 0, len(timestamps))

	for _, ts := range timestamps {
		result, err := service.ReplayToTimestamp(ctx, entityID, ts)
		if err != nil {
			// Skip timestamps with no events
			continue
		}
		results = append(results, result)
	}

	return results, nil
}

// StateComparison compares state between two versions or timestamps.
type StateComparison struct {
	EntityID       string                 `json:"entity_id"`
	FromVersion    int64                  `json:"from_version"`
	ToVersion      int64                  `json:"to_version"`
	FromTimestamp  time.Time              `json:"from_timestamp"`
	ToTimestamp    time.Time              `json:"to_timestamp"`
	AddedFields    map[string]interface{} `json:"added_fields"`
	RemovedFields  []string               `json:"removed_fields"`
	ModifiedFields map[string]interface{} `json:"modified_fields"` // Shows new values
	UnchangedCount int                    `json:"unchanged_count"`
}

func newStateComparison(
	entityID string,
	fromVersion int64,
	toVersion int64,
	fromTimestamp time.Time,
	toTimestamp time.Time,
) *StateComparison {
	return &StateComparison{
		EntityID:       entityID,
		FromVersion:    fromVersion,
		ToVersion:      toVersion,
		FromTimestamp:  fromTimestamp,
		ToTimestamp:    toTimestamp,
		AddedFields:    make(map[string]interface{}),
		RemovedFields:  make([]string, 0),
		ModifiedFields: make(map[string]interface{}),
	}
}

func compareStateMaps(
	fromState map[string]interface{},
	toState map[string]interface{},
) (map[string]interface{}, []string, map[string]interface{}, int) {
	addedFields := make(map[string]interface{})
	removedFields := make([]string, 0)
	modifiedFields := make(map[string]interface{})
	unchangedCount := 0

	for key, value := range toState {
		oldValue, exists := fromState[key]
		if !exists {
			addedFields[key] = value
			continue
		}
		if fmt.Sprint(oldValue) != fmt.Sprint(value) {
			modifiedFields[key] = value
			continue
		}
		unchangedCount++
	}

	for key := range fromState {
		if _, exists := toState[key]; !exists {
			removedFields = append(removedFields, key)
		}
	}

	return addedFields, removedFields, modifiedFields, unchangedCount
}

// CompareVersions compares state between two versions
func (service *EventReplayService) CompareVersions(
	ctx context.Context,
	entityID string,
	fromVersion int64,
	toVersion int64,
) (*StateComparison, error) {
	fromState, err := service.ReplayToVersion(ctx, entityID, fromVersion)
	if err != nil {
		return nil, fmt.Errorf("failed to replay from version: %w", err)
	}

	toState, err := service.ReplayToVersion(ctx, entityID, toVersion)
	if err != nil {
		return nil, fmt.Errorf("failed to replay to version: %w", err)
	}

	comparison := newStateComparison(entityID, fromVersion, toVersion, fromState.Timestamp, toState.Timestamp)
	addedFields, removedFields, modifiedFields, unchangedCount := compareStateMaps(fromState.State, toState.State)
	comparison.AddedFields = addedFields
	comparison.RemovedFields = removedFields
	comparison.ModifiedFields = modifiedFields
	comparison.UnchangedCount = unchangedCount

	return comparison, nil
}

// GetEventChain returns the chain of causation for an event
func (service *EventReplayService) GetEventChain(
	_ context.Context,
	eventID string,
	projectID string,
) ([]*Event, error) {
	// Get all events for the project
	allEvents, err := service.store.GetByProjectID(projectID, eventReplayProjectFetchLimit, 0)
	if err != nil {
		return nil, fmt.Errorf("failed to get project events: %w", err)
	}

	// Build event map for quick lookup
	eventMap := make(map[string]*Event)
	for _, e := range allEvents {
		eventMap[e.ID] = e
	}

	// Find the starting event
	startEvent, exists := eventMap[eventID]
	if !exists {
		return nil, fmt.Errorf("event %s not found", eventID)
	}

	// Build the chain by following causation links
	chain := make([]*Event, 0)
	current := startEvent

	// Prevent infinite loops
	maxDepth := eventReplayMaxChainDepth
	depth := 0

	for current != nil && depth < maxDepth {
		chain = append(chain, current)

		// Get the causing event
		if current.CausationID == nil {
			break
		}

		current = eventMap[*current.CausationID]
		depth++
	}

	// Reverse to show oldest first
	for i, j := 0, len(chain)-1; i < j; i, j = i+1, j-1 {
		chain[i], chain[j] = chain[j], chain[i]
	}

	return chain, nil
}

// GetCorrelatedEvents returns all events with the same correlation ID
func (service *EventReplayService) GetCorrelatedEvents(
	_ context.Context,
	correlationID string,
	projectID string,
) ([]*Event, error) {
	// Get all events for the project
	allEvents, err := service.store.GetByProjectID(projectID, eventReplayProjectFetchLimit, 0)
	if err != nil {
		return nil, fmt.Errorf("failed to get project events: %w", err)
	}

	// Filter by correlation ID
	correlated := make([]*Event, 0)
	for _, e := range allEvents {
		if e.CorrelationID != nil && *e.CorrelationID == correlationID {
			correlated = append(correlated, e)
		}
	}

	return correlated, nil
}

// AuditTrail represents a complete audit trail for an entity
type AuditTrail struct {
	EntityID     string                 `json:"entity_id"`
	EntityType   EntityType             `json:"entity_type"`
	TotalEvents  int                    `json:"total_events"`
	FirstEvent   time.Time              `json:"first_event"`
	LastEvent    time.Time              `json:"last_event"`
	Events       []*AuditTrailItem      `json:"events"`
	CurrentState map[string]interface{} `json:"current_state"`
}

// AuditTrailItem represents a single audit trail entry
type AuditTrailItem struct {
	EventID       string                 `json:"event_id"`
	EventType     EventType              `json:"event_type"`
	Version       int64                  `json:"version"`
	Timestamp     time.Time              `json:"timestamp"`
	UserID        string                 `json:"user_id,omitempty"`
	Source        string                 `json:"source,omitempty"`
	Changes       map[string]interface{} `json:"changes"`
	CausationID   *string                `json:"causation_id,omitempty"`
	CorrelationID *string                `json:"correlation_id,omitempty"`
}

// GetAuditTrail returns a complete audit trail for an entity
func (service *EventReplayService) GetAuditTrail(_ context.Context, entityID string) (*AuditTrail, error) {
	events, err := service.store.GetByEntityID(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get events: %w", err)
	}

	if len(events) == 0 {
		return nil, fmt.Errorf("no events found for entity %s", entityID)
	}

	trail := &AuditTrail{
		EntityID:    entityID,
		EntityType:  events[0].EntityType,
		TotalEvents: len(events),
		FirstEvent:  events[0].CreatedAt,
		LastEvent:   events[len(events)-1].CreatedAt,
		Events:      make([]*AuditTrailItem, len(events)),
	}

	// Build audit trail items
	for index, event := range events {
		item := &AuditTrailItem{
			EventID:       event.ID,
			EventType:     event.EventType,
			Version:       event.Version,
			Timestamp:     event.CreatedAt,
			Changes:       event.Data,
			CausationID:   event.CausationID,
			CorrelationID: event.CorrelationID,
		}

		// Extract metadata
		if userID, ok := event.Metadata["user_id"].(string); ok {
			item.UserID = userID
		}
		if source, ok := event.Metadata["source"].(string); ok {
			item.Source = source
		}

		trail.Events[index] = item
	}

	// Get current state
	currentState, err := service.store.Replay(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get current state: %w", err)
	}
	trail.CurrentState = currentState

	return trail, nil
}

// ProjectStats represents statistics for a project's events
type ProjectStats struct {
	ProjectID          string             `json:"project_id"`
	TotalEvents        int                `json:"total_events"`
	EventsByType       map[EventType]int  `json:"events_by_type"`
	EventsByEntity     map[EntityType]int `json:"events_by_entity"`
	FirstEvent         time.Time          `json:"first_event"`
	LastEvent          time.Time          `json:"last_event"`
	UniqueEntities     int                `json:"unique_entities"`
	AvgEventsPerEntity float64            `json:"avg_events_per_entity"`
}

// GetProjectStats returns statistics for a project
func (service *EventReplayService) GetProjectStats(_ context.Context, projectID string) (*ProjectStats, error) {
	events, err := service.store.GetByProjectID(projectID, eventReplayStatsFetchLimit, 0)
	if err != nil {
		return nil, fmt.Errorf("failed to get project events: %w", err)
	}

	if len(events) == 0 {
		return &ProjectStats{
			ProjectID:      projectID,
			EventsByType:   make(map[EventType]int),
			EventsByEntity: make(map[EntityType]int),
		}, nil
	}

	stats := &ProjectStats{
		ProjectID:      projectID,
		TotalEvents:    len(events),
		EventsByType:   make(map[EventType]int),
		EventsByEntity: make(map[EntityType]int),
		FirstEvent:     events[len(events)-1].CreatedAt, // Events are DESC
		LastEvent:      events[0].CreatedAt,
	}

	uniqueEntities := make(map[string]bool)

	for _, event := range events {
		stats.EventsByType[event.EventType]++
		stats.EventsByEntity[event.EntityType]++
		uniqueEntities[event.EntityID] = true
	}

	stats.UniqueEntities = len(uniqueEntities)
	if stats.UniqueEntities > 0 {
		stats.AvgEventsPerEntity = float64(stats.TotalEvents) / float64(stats.UniqueEntities)
	}

	return stats, nil
}
