package events

import (
	"context"
	"fmt"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

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
