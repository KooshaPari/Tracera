package agents

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
)

// AssignOperationToAgents assigns parts of an operation to multiple agents
func (dc *DistributedCoordinator) AssignOperationToAgents(
	_ context.Context,
	operationID string,
	agentAssignments map[string][]string,
) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return fmt.Errorf("operation not found: %w", err)
	}

	if op.Status != string(TaskStatusPending) {
		return errors.New("operation is not in pending status")
	}

	for agentID, items := range agentAssignments {
		participant := &OperationParticipant{
			ID:            uuid.New().String(),
			OperationID:   operationID,
			AgentID:       agentID,
			Status:        statusReady,
			AssignedItems: items,
			Result:        make(map[string]interface{}),
			CreatedAt:     time.Now(),
			UpdatedAt:     time.Now(),
		}

		if err := dc.db.Create(participant).Error; err != nil {
			return fmt.Errorf("failed to create participant: %w", err)
		}
	}

	now := time.Now()
	op.Status = statusInProgress
	op.StartedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(&op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}

	dc.operations[operationID] = &op
	return nil
}

// StartParticipation marks an agent as starting work on their part of the operation
func (dc *DistributedCoordinator) StartParticipation(_ context.Context, operationID, agentID string) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var participant OperationParticipant
	if err := dc.db.Where(
		"operation_id = ? AND agent_id = ?",
		operationID,
		agentID,
	).First(&participant).Error; err != nil {
		return fmt.Errorf("participant not found: %w", err)
	}

	if participant.Status != statusReady {
		return errors.New("participant is not in ready status")
	}

	now := time.Now()
	participant.Status = statusWorking
	participant.StartedAt = &now
	participant.UpdatedAt = now

	if err := dc.db.Save(&participant).Error; err != nil {
		return fmt.Errorf("failed to update participant: %w", err)
	}

	return nil
}

// CompleteParticipation marks an agent's part of the operation as complete
func (dc *DistributedCoordinator) CompleteParticipation(
	ctx context.Context,
	operationID,
	agentID string,
	result map[string]interface{},
) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var participant OperationParticipant
	if err := dc.db.Where(
		"operation_id = ? AND agent_id = ?",
		operationID,
		agentID,
	).First(&participant).Error; err != nil {
		return fmt.Errorf("participant not found: %w", err)
	}

	now := time.Now()
	participant.Status = string(TaskStatusCompleted)
	participant.Result = JSONMap(result)
	participant.CompletedAt = &now
	participant.UpdatedAt = now

	if err := dc.db.Save(&participant).Error; err != nil {
		return fmt.Errorf("failed to update participant: %w", err)
	}

	return dc.checkOperationCompletion(ctx, operationID)
}

// FailParticipation marks an agent's part of the operation as failed
func (dc *DistributedCoordinator) FailParticipation(
	ctx context.Context,
	operationID,
	agentID string,
	errorMsg string,
) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var participant OperationParticipant
	if err := dc.db.Where(
		"operation_id = ? AND agent_id = ?",
		operationID,
		agentID,
	).First(&participant).Error; err != nil {
		return fmt.Errorf("participant not found: %w", err)
	}

	now := time.Now()
	participant.Status = string(TaskStatusFailed)
	participant.Error = errorMsg
	participant.CompletedAt = &now
	participant.UpdatedAt = now

	if err := dc.db.Save(&participant).Error; err != nil {
		return fmt.Errorf("failed to update participant: %w", err)
	}

	return dc.checkOperationCompletion(ctx, operationID)
}

// GetParticipantStatus returns the status of a participant in a distributed operation
func (dc *DistributedCoordinator) GetParticipantStatus(
	_ context.Context,
	operationID string,
	agentID string,
) (*OperationParticipant, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	var participant OperationParticipant
	if err := dc.db.Where(
		"operation_id = ? AND agent_id = ?",
		operationID,
		agentID,
	).First(&participant).Error; err != nil {
		return nil, fmt.Errorf("participant not found: %w", err)
	}

	return &participant, nil
}

// SubmitParticipantResult submits a result from a participant in a distributed operation
func (dc *DistributedCoordinator) SubmitParticipantResult(
	ctx context.Context,
	operationID string,
	agentID string,
	result map[string]interface{},
) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var participant OperationParticipant
	if err := dc.db.Where(
		"operation_id = ? AND agent_id = ?",
		operationID,
		agentID,
	).First(&participant).Error; err != nil {
		return fmt.Errorf("participant not found: %w", err)
	}

	now := time.Now()
	participant.Status = string(TaskStatusCompleted)
	participant.Result = JSONMap(result)
	participant.CompletedAt = &now
	participant.UpdatedAt = now

	if err := dc.db.Save(&participant).Error; err != nil {
		return fmt.Errorf("failed to update participant: %w", err)
	}

	return dc.checkOperationCompletion(ctx, operationID)
}

// GetOperationResults returns aggregated results from a distributed operation
func (dc *DistributedCoordinator) GetOperationResults(
	_ context.Context,
	operationID string,
) (map[string]interface{}, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return nil, fmt.Errorf("operation not found: %w", err)
	}

	var participants []OperationParticipant
	if err := dc.db.Where("operation_id = ?", operationID).Find(&participants).Error; err != nil {
		return nil, fmt.Errorf("failed to get participants: %w", err)
	}

	results := make(map[string]interface{})
	results["operation_id"] = operationID
	results["operation_status"] = op.Status
	results["completed_at"] = op.CompletedAt
	results["participants"] = make(map[string]interface{})

	participantsMap, ok := results["participants"].(map[string]interface{})
	if !ok {
		return nil, errors.New("participants map is not initialized")
	}
	for _, p := range participants {
		participantsMap[p.AgentID] = map[string]interface{}{
			"status": p.Status,
			"result": p.Result,
			"error":  p.Error,
		}
	}

	return results, nil
}
