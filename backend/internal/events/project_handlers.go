package events

import (
	"context"
	"fmt"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

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
