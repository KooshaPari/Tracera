package agents

import (
	"context"
	"fmt"
)

// GetOperationStatus returns the status of a distributed operation
func (dc *DistributedCoordinator) GetOperationStatus(
	_ context.Context,
	operationID string,
) (*DistributedOperation, []OperationParticipant, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return nil, nil, fmt.Errorf("operation not found: %w", err)
	}

	var participants []OperationParticipant
	if err := dc.db.Where("operation_id = ?", operationID).Find(&participants).Error; err != nil {
		return nil, nil, fmt.Errorf("failed to get participants: %w", err)
	}

	return &op, participants, nil
}

// GetAgentOperations returns all operations an agent is participating in
func (dc *DistributedCoordinator) GetAgentOperations(
	_ context.Context,
	agentID string,
	status string,
) ([]DistributedOperation, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	var operations []DistributedOperation
	query := dc.db.Where("participant_ids @> ?", fmt.Sprintf(`["%s"]`, agentID))

	if status != "" {
		query = query.Where("status = ?", status)
	}

	if err := query.Find(&operations).Error; err != nil {
		return nil, fmt.Errorf("failed to get operations: %w", err)
	}

	return operations, nil
}

// GetDistributedOperation retrieves a distributed operation by ID
func (dc *DistributedCoordinator) GetDistributedOperation(
	_ context.Context,
	operationID string,
) (*DistributedOperation, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return nil, fmt.Errorf("operation not found: %w", err)
	}

	return &op, nil
}

// ListOperations lists all distributed operations with optional filtering
func (dc *DistributedCoordinator) ListOperations(
	_ context.Context,
	projectID string,
	statusFilter string,
) ([]DistributedOperation, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	var operations []DistributedOperation
	query := dc.db.Where("project_id = ?", projectID)

	if statusFilter != "" {
		query = query.Where("status = ?", statusFilter)
	}

	if err := query.Find(&operations).Error; err != nil {
		return nil, fmt.Errorf("failed to list operations: %w", err)
	}

	return operations, nil
}
