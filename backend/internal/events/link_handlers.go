package events

import (
	"context"
	"fmt"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

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
