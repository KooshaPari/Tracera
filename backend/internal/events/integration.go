package events

import (
	"context"
	"errors"
	"fmt"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// EventSourcedRepository wraps a repository with event sourcing capabilities
type EventSourcedRepository struct {
	itemHandler    *ItemEventHandler
	linkHandler    *LinkEventHandler
	projectHandler *ProjectEventHandler
	agentHandler   *AgentEventHandler
	replayService  *EventReplayService
}

// NewEventSourcedRepository creates a new event-sourced repository
func NewEventSourcedRepository(store EventStore) *EventSourcedRepository {
	return &EventSourcedRepository{
		itemHandler:    NewItemEventHandler(store),
		linkHandler:    NewLinkEventHandler(store),
		projectHandler: NewProjectEventHandler(store),
		agentHandler:   NewAgentEventHandler(store),
		replayService:  NewEventReplayService(store),
	}
}

// CreateItem creates an item and emits creation event
func (repo *EventSourcedRepository) CreateItem(
	ctx context.Context,
	item *models.Item,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.itemHandler.HandleCreate(ctx, item, userID, correlationID)
}

// UpdateItem updates an item and emits update event
func (repo *EventSourcedRepository) UpdateItem(
	ctx context.Context,
	item *models.Item,
	userID string,
	correlationID *string,
	causationID *string,
) (*Event, error) {
	return repo.itemHandler.HandleUpdate(ctx, item, userID, correlationID, causationID)
}

// DeleteItem deletes an item and emits deletion event
func (repo *EventSourcedRepository) DeleteItem(
	ctx context.Context,
	itemID string,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.itemHandler.HandleDelete(ctx, itemID, projectID, userID, correlationID)
}

// ChangeItemStatus changes item status and emits specific event
func (repo *EventSourcedRepository) ChangeItemStatus(
	ctx context.Context,
	itemID string,
	projectID string,
	oldStatus string,
	newStatus string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.itemHandler.HandleStatusChange(
		ctx,
		itemID,
		projectID,
		oldStatus,
		newStatus,
		userID,
		correlationID,
	)
}

// ChangeItemPriority changes item priority and emits specific event
func (repo *EventSourcedRepository) ChangeItemPriority(
	ctx context.Context,
	itemID string,
	projectID string,
	oldPriority int32,
	newPriority int32,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.itemHandler.HandlePriorityChange(
		ctx,
		itemID,
		projectID,
		oldPriority,
		newPriority,
		userID,
		correlationID,
	)
}

// ReconstructItem rebuilds an item from its event history
func (repo *EventSourcedRepository) ReconstructItem(_ context.Context, itemID string) (*models.Item, error) {
	return ReconstructItemFromEvents(itemID, repo.itemHandler.store)
}

// GetItemHistory returns the complete audit trail for an item
func (repo *EventSourcedRepository) GetItemHistory(ctx context.Context, itemID string) (*AuditTrail, error) {
	return repo.replayService.GetAuditTrail(ctx, itemID)
}

// GetItemAtTimestamp returns item state at a specific point in time
func (repo *EventSourcedRepository) GetItemAtTimestamp(_ context.Context, _ string, _ string) (*TemporalResult, error) {
	// Parse timestamp
	// Note: In production, you'd parse the string to time.Time
	// For now, this is a placeholder
	return nil, errors.New("timestamp parsing not implemented")
}

// CreateLink creates a link and emits creation event
func (repo *EventSourcedRepository) CreateLink(
	ctx context.Context,
	link *models.Link,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.linkHandler.HandleCreate(ctx, link, projectID, userID, correlationID)
}

// DeleteLink deletes a link and emits deletion event
func (repo *EventSourcedRepository) DeleteLink(
	ctx context.Context,
	linkID string,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.linkHandler.HandleDelete(ctx, linkID, projectID, userID, correlationID)
}

// CreateProject creates a project and emits creation event
func (repo *EventSourcedRepository) CreateProject(
	ctx context.Context,
	project *models.Project,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.projectHandler.HandleCreate(ctx, project, userID, correlationID)
}

// UpdateProject updates a project and emits update event
func (repo *EventSourcedRepository) UpdateProject(
	ctx context.Context,
	project *models.Project,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.projectHandler.HandleUpdate(ctx, project, userID, correlationID)
}

// DeleteProject deletes a project and emits deletion event
func (repo *EventSourcedRepository) DeleteProject(
	ctx context.Context,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.projectHandler.HandleDelete(ctx, projectID, userID, correlationID)
}

// GetProjectStats returns statistics for a project
func (repo *EventSourcedRepository) GetProjectStats(ctx context.Context, projectID string) (*ProjectStats, error) {
	return repo.replayService.GetProjectStats(ctx, projectID)
}

// CreateAgent creates an agent and emits creation event
func (repo *EventSourcedRepository) CreateAgent(
	ctx context.Context,
	agent *models.Agent,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.agentHandler.HandleCreate(
		ctx,
		agent,
		userID,
		correlationID,
	)
}

// StartAgent starts an agent and emits start event
func (repo *EventSourcedRepository) StartAgent(
	ctx context.Context,
	agentID string,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.agentHandler.HandleStart(
		ctx,
		agentID,
		projectID,
		userID,
		correlationID,
	)
}

// StopAgent stops an agent and emits stop event
func (repo *EventSourcedRepository) StopAgent(
	ctx context.Context,
	agentID string,
	projectID string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.agentHandler.HandleStop(
		ctx,
		agentID,
		projectID,
		userID,
		correlationID,
	)
}

// RecordAgentActivity records agent activity and emits activity event
func (repo *EventSourcedRepository) RecordAgentActivity(
	ctx context.Context,
	agentID string,
	projectID string,
	activity string,
	userID string,
	metadata map[string]interface{},
	correlationID *string,
) (*Event, error) {
	return repo.agentHandler.HandleActivity(
		ctx,
		agentID,
		projectID,
		activity,
		userID,
		metadata,
		correlationID,
	)
}

// RecordAgentError records agent error and emits error event
func (repo *EventSourcedRepository) RecordAgentError(
	ctx context.Context,
	agentID string,
	projectID string,
	errorMsg string,
	userID string,
	correlationID *string,
) (*Event, error) {
	return repo.agentHandler.HandleError(
		ctx,
		agentID,
		projectID,
		errorMsg,
		userID,
		correlationID,
	)
}

// CompareItemVersions compares item state between two versions
func (repo *EventSourcedRepository) CompareItemVersions(
	ctx context.Context,
	itemID string,
	fromVersion int64,
	toVersion int64,
) (*StateComparison, error) {
	return repo.replayService.CompareVersions(ctx, itemID, fromVersion, toVersion)
}

// GetEventChain returns the causation chain for an event
func (repo *EventSourcedRepository) GetEventChain(
	ctx context.Context,
	eventID string,
	projectID string,
) ([]*Event, error) {
	return repo.replayService.GetEventChain(ctx, eventID, projectID)
}

// GetCorrelatedEvents returns all events with the same correlation ID
func (repo *EventSourcedRepository) GetCorrelatedEvents(
	ctx context.Context,
	correlationID string,
	projectID string,
) ([]*Event, error) {
	return repo.replayService.GetCorrelatedEvents(ctx, correlationID, projectID)
}

// BatchOperations represents a set of operations that should be correlated
type BatchOperations struct {
	correlationID string
	operations    []func(correlationID *string) error
}

// NewBatchOperations creates a new batch operation with a unique correlation ID
func NewBatchOperations() *BatchOperations {
	return &BatchOperations{
		correlationID: GenerateCorrelationID(),
		operations:    make([]func(correlationID *string) error, 0),
	}
}

// AddOperation adds an operation to the batch
func (b *BatchOperations) AddOperation(op func(correlationID *string) error) {
	b.operations = append(b.operations, op)
}

// Execute runs all operations with the same correlation ID
func (b *BatchOperations) Execute() error {
	for _, op := range b.operations {
		if err := op(&b.correlationID); err != nil {
			return fmt.Errorf("batch operation failed: %w", err)
		}
	}
	return nil
}

// GetCorrelationID returns the batch correlation ID
func (b *BatchOperations) GetCorrelationID() string {
	return b.correlationID
}

// EventSourcedService provides high-level event sourcing operations
type EventSourcedService struct {
	repository *EventSourcedRepository
}

// NewEventSourcedService creates a new event-sourced service
func NewEventSourcedService(store EventStore) *EventSourcedService {
	return &EventSourcedService{
		repository: NewEventSourcedRepository(store),
	}
}

// ExecuteBatch executes multiple operations as a correlated batch
func (s *EventSourcedService) ExecuteBatch(operations []func(correlationID *string) error) (string, error) {
	batch := NewBatchOperations()
	for _, op := range operations {
		batch.AddOperation(op)
	}
	if err := batch.Execute(); err != nil {
		return "", err
	}
	return batch.GetCorrelationID(), nil
}

// GetRepository returns the underlying repository
func (s *EventSourcedService) GetRepository() *EventSourcedRepository {
	return s.repository
}
