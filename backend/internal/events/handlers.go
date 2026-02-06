package events

import (
	"context"
	"fmt"
	"strconv"

	"github.com/google/uuid"
	"github.com/kooshapari/tracertm-backend/internal/models"
)

// ItemEventHandler processes item events and updates state.
type ItemEventHandler struct {
	store EventStore
}

// NewItemEventHandler creates a new item event handler
func NewItemEventHandler(store EventStore) *ItemEventHandler {
	return &ItemEventHandler{store: store}
}

// HandleCreate processes item creation and emits event
func (handler *ItemEventHandler) HandleCreate(
	_ context.Context,
	item *models.Item,
	userID string,
	correlationID *string,
) (*Event, error) {
	// Create event data from item
	data := map[string]interface{}{
		"title":       item.Title,
		"description": item.Description,
		"type":        item.Type,
		"status":      item.Status,
		"priority":    item.Priority,
		"metadata":    item.Metadata,
	}

	// Create the event
	event := NewEvent(item.ProjectID, item.ID, EntityTypeItem, EventTypeCreated, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	// Store the event
	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store create event: %w", err)
	}

	return event, nil
}

// HandleUpdate processes item updates and emits event
func (handler *ItemEventHandler) HandleUpdate(
	_ context.Context,
	item *models.Item,
	userID string,
	correlationID *string,
	causationID *string,
) (*Event, error) {
	// Get current version
	events, err := handler.store.GetByEntityID(item.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	// Create event data
	data := map[string]interface{}{
		"title":       item.Title,
		"description": item.Description,
		"type":        item.Type,
		"status":      item.Status,
		"priority":    item.Priority,
		"metadata":    item.Metadata,
	}

	event := NewEvent(item.ProjectID, item.ID, EntityTypeItem, EventTypeUpdated, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}
	if causationID != nil {
		event.WithCausation(*causationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store update event: %w", err)
	}

	return event, nil
}

func (handler *ItemEventHandler) handleItemChange(
	itemID string,
	projectID string,
	userID string,
	correlationID *string,
	eventType EventType,
	data map[string]interface{},
	eventLabel string,
) (*Event, error) {
	events, err := handler.store.GetByEntityID(itemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	event := NewEvent(projectID, itemID, EntityTypeItem, eventType, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store %s event: %w", eventLabel, err)
	}

	return event, nil
}

func (handler *ItemEventHandler) handleItemFieldChange(
	itemID string,
	projectID string,
	userID string,
	correlationID *string,
	eventType EventType,
	oldKey string,
	oldValue interface{},
	newKey string,
	newValue interface{},
	eventLabel string,
) (*Event, error) {
	data := map[string]interface{}{
		oldKey: oldValue,
		newKey: newValue,
	}
	return handler.handleItemChange(
		itemID,
		projectID,
		userID,
		correlationID,
		eventType,
		data,
		eventLabel,
	)
}

// HandleStatusChange processes status changes and emits specific event
func (handler *ItemEventHandler) HandleStatusChange(
	_ context.Context,
	itemID string,
	projectID string,
	oldStatus string,
	newStatus string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return handler.handleItemFieldChange(
		itemID,
		projectID,
		userID,
		correlationID,
		EventTypeItemStatusChanged,
		"old_status",
		oldStatus,
		"new_status",
		newStatus,
		"status change",
	)
}

// HandlePriorityChange processes priority changes
func (handler *ItemEventHandler) HandlePriorityChange(
	_ context.Context,
	itemID string,
	projectID string,
	oldPriority int32,
	newPriority int32,
	userID string,
	correlationID *string,
) (*Event, error) {
	return handler.handleItemFieldChange(
		itemID,
		projectID,
		userID,
		correlationID,
		EventTypeItemPriorityChanged,
		"old_priority",
		oldPriority,
		"new_priority",
		newPriority,
		"priority change",
	)
}

// HandleDelete processes item deletion and emits event
func (handler *ItemEventHandler) HandleDelete(
	_ context.Context,
	itemID string,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	events, err := handler.store.GetByEntityID(itemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	data := map[string]interface{}{
		"deleted": true,
	}

	event := NewEvent(projectID, itemID, EntityTypeItem, EventTypeDeleted, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store delete event: %w", err)
	}

	return event, nil
}

// LinkEventHandler handles link events
type LinkEventHandler struct {
	store EventStore
}

// NewLinkEventHandler creates a new link event handler
func NewLinkEventHandler(store EventStore) *LinkEventHandler {
	return &LinkEventHandler{store: store}
}

// HandleCreate processes link creation
func (handler *LinkEventHandler) HandleCreate(
	_ context.Context,
	link *models.Link,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	data := map[string]interface{}{
		"source_id": link.SourceID,
		"target_id": link.TargetID,
		"type":      link.Type,
		"metadata":  link.Metadata,
	}

	event := NewEvent(projectID, link.ID, EntityTypeLink, EventTypeLinkCreated, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store link create event: %w", err)
	}

	return event, nil
}

// HandleDelete processes link deletion
func (handler *LinkEventHandler) HandleDelete(
	_ context.Context,
	linkID string,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	data := map[string]interface{}{
		"deleted": true,
	}

	event := NewEvent(projectID, linkID, EntityTypeLink, EventTypeLinkDeleted, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store link delete event: %w", err)
	}

	return event, nil
}

// ProjectEventHandler handles project events
type ProjectEventHandler struct {
	store EventStore
}

// NewProjectEventHandler creates a new project event handler
func NewProjectEventHandler(store EventStore) *ProjectEventHandler {
	return &ProjectEventHandler{store: store}
}

// HandleCreate processes project creation
func (handler *ProjectEventHandler) HandleCreate(
	_ context.Context,
	project *models.Project,
	userID string,
	correlationID *string,
) (*Event, error) {
	data := map[string]interface{}{
		"name":        project.Name,
		"description": project.Description,
		"metadata":    project.Metadata,
	}

	event := NewEvent(project.ID, project.ID, EntityTypeProject, EventTypeCreated, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store project create event: %w", err)
	}

	return event, nil
}

// HandleUpdate processes project updates
func (handler *ProjectEventHandler) HandleUpdate(
	_ context.Context,
	project *models.Project,
	userID string,
	correlationID *string,
) (*Event, error) {
	events, err := handler.store.GetByEntityID(project.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	data := map[string]interface{}{
		"name":        project.Name,
		"description": project.Description,
		"metadata":    project.Metadata,
	}

	event := NewEvent(project.ID, project.ID, EntityTypeProject, EventTypeUpdated, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store project update event: %w", err)
	}

	return event, nil
}

// HandleDelete processes project deletion
func (handler *ProjectEventHandler) HandleDelete(
	_ context.Context,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	events, err := handler.store.GetByEntityID(projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	data := map[string]interface{}{
		"deleted": true,
	}

	event := NewEvent(projectID, projectID, EntityTypeProject, EventTypeDeleted, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store project delete event: %w", err)
	}

	return event, nil
}

// AgentEventHandler handles agent events
type AgentEventHandler struct {
	store EventStore
}

// NewAgentEventHandler creates a new agent event handler
func NewAgentEventHandler(store EventStore) *AgentEventHandler {
	return &AgentEventHandler{store: store}
}

// HandleCreate processes agent creation
func (handler *AgentEventHandler) HandleCreate(
	_ context.Context,
	agent *models.Agent,
	userID string,
	correlationID *string,
) (*Event, error) {
	data := map[string]interface{}{
		"name":     agent.Name,
		"status":   agent.Status,
		"metadata": agent.Metadata,
	}

	event := NewEvent(agent.ProjectID, agent.ID, EntityTypeAgent, EventTypeCreated, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store agent create event: %w", err)
	}

	return event, nil
}

// HandleStart processes agent start
func (handler *AgentEventHandler) HandleStart(
	_ context.Context,
	agentID string,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	events, err := handler.store.GetByEntityID(agentID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	data := map[string]interface{}{
		"status": "active",
	}

	event := NewEvent(projectID, agentID, EntityTypeAgent, EventTypeAgentStarted, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store agent start event: %w", err)
	}

	return event, nil
}

// HandleStop processes agent stop
func (handler *AgentEventHandler) HandleStop(
	_ context.Context,
	agentID string,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	events, err := handler.store.GetByEntityID(agentID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	data := map[string]interface{}{
		"status": "idle",
	}

	event := NewEvent(projectID, agentID, EntityTypeAgent, EventTypeAgentStopped, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store agent stop event: %w", err)
	}

	return event, nil
}

// HandleActivity processes agent activity
func (handler *AgentEventHandler) HandleActivity(
	_ context.Context,
	agentID string,
	projectID string,
	activity string,
	userID string,
	metadata map[string]interface{},
	correlationID *string,
) (*Event, error) {
	events, err := handler.store.GetByEntityID(agentID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	data := map[string]interface{}{
		"activity": activity,
	}

	// Merge in additional metadata
	for key, value := range metadata {
		data[key] = value
	}

	event := NewEvent(projectID, agentID, EntityTypeAgent, EventTypeAgentActivity, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "agent")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store agent activity event: %w", err)
	}

	return event, nil
}

// HandleError processes agent errors
func (handler *AgentEventHandler) HandleError(
	_ context.Context,
	agentID string,
	projectID string,
	errorMsg string,
	userID string,
	correlationID *string,
) (*Event, error) {
	events, err := handler.store.GetByEntityID(agentID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

	data := map[string]interface{}{
		"error":  errorMsg,
		"status": "error",
	}

	event := NewEvent(projectID, agentID, EntityTypeAgent, EventTypeAgentError, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "agent")
	event.WithVersion(version)

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

	if err := handler.store.Store(event); err != nil {
		return nil, fmt.Errorf("failed to store agent error event: %w", err)
	}

	return event, nil
}

func applyItemStringField(data map[string]interface{}, key string, apply func(string)) {
	value, ok := data[key].(string)
	if !ok {
		return
	}
	apply(value)
}

func applyItemPriorityField(item *models.Item, data map[string]interface{}, key string) {
	value, ok := data[key]
	if !ok {
		return
	}
	item.Priority = priorityFromData(value)
}

func applyCreatedOrUpdated(item *models.Item, event *Event) {
	applyItemStringField(event.Data, "title", func(value string) {
		item.Title = value
	})
	applyItemStringField(event.Data, "description", func(value string) {
		item.Description = value
	})
	applyItemStringField(event.Data, "type", func(value string) {
		item.Type = value
	})
	applyItemStringField(event.Data, "status", func(value string) {
		item.Status = value
	})
	applyItemPriorityField(item, event.Data, "priority")
	item.ProjectID = event.ProjectID
	item.CreatedAt = event.CreatedAt
}

func applyStatusChange(item *models.Item, event *Event) {
	applyItemStringField(event.Data, "new_status", func(value string) {
		item.Status = value
	})
}

func applyPriorityChange(item *models.Item, event *Event) {
	applyItemPriorityField(item, event.Data, "new_priority")
}

func applyDeleted(item *models.Item, event *Event) {
	now := event.CreatedAt
	item.DeletedAt = &now
}

// ReconstructItemFromEvents rebuilds an item from its event history
func ReconstructItemFromEvents(entityID string, store EventStore) (*models.Item, error) {
	events, err := store.GetByEntityID(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get events: %w", err)
	}

	if len(events) == 0 {
		return nil, fmt.Errorf("no events found for entity %s", entityID)
	}

	item := &models.Item{
		ID: entityID,
	}

	for _, event := range events {
		switch event.EventType {
		case EventTypeCreated, EventTypeUpdated:
			applyCreatedOrUpdated(item, event)

		case EventTypeItemStatusChanged:
			applyStatusChange(item, event)

		case EventTypeItemPriorityChanged:
			applyPriorityChange(item, event)

		case EventTypeDeleted:
			applyDeleted(item, event)
		case EventTypeLinkCreated,
			EventTypeLinkDeleted,
			EventTypeAgentStarted,
			EventTypeAgentStopped,
			EventTypeAgentActivity,
			EventTypeAgentError,
			EventTypeSnapshot,
			EventTypeRollback:
			// Not applicable for item reconstruction.
		}
	}

	return item, nil
}

// priorityFromData converts event data (string, int32, float64) to int32 for models.Item.Priority
func priorityFromData(v interface{}) models.Priority {
	switch value := v.(type) {
	case int32:
		return models.Priority(value)
	case models.Priority:
		return value
	case float64:
		return models.Priority(int32(value))
	case string:
		if i, err := strconv.ParseInt(value, 10, 32); err == nil {
			return models.Priority(int32(i))
		}
		switch value {
		case "low":
			return models.PriorityLow
		case "medium":
			return models.PriorityMedium
		case "high":
			return models.PriorityHigh
		case "critical":
			return models.PriorityCritical
		}
		return 0
	}
	return 0
}

// GenerateCorrelationID creates a new correlation ID for tracing related operations
func GenerateCorrelationID() string {
	return uuid.New().String()
}
