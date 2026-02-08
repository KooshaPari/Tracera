package events

import (
	"context"
	"fmt"

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
	data := map[string]interface{}{
		"title":       item.Title,
		"description": item.Description,
		"type":        item.Type,
		"status":      item.Status,
		"priority":    item.Priority,
		"metadata":    item.Metadata,
	}

	event := NewEvent(item.ProjectID, item.ID, EntityTypeItem, EventTypeCreated, data)
	event.WithMetadata("user_id", userID)
	event.WithMetadata("source", "api")

	if correlationID != nil {
		event.WithCorrelation(*correlationID)
	}

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
	events, err := handler.store.GetByEntityID(item.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to get entity events: %w", err)
	}

	version := int64(len(events) + 1)

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
