package agents

import (
	"context"
	"fmt"
	"log/slog"
	"time"
)

// finalizeOperation is the internal implementation for completing or cancelling operations
func (dc *DistributedCoordinator) finalizeOperation(
	ctx context.Context,
	operationID string,
	agentID string,
	finalStatus string,
	actionName string,
) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	operation, err := dc.fetchOperation(operationID)
	if err != nil {
		return err
	}
	if operation.CoordinatorID != agentID {
		return fmt.Errorf("only coordinator can %s the operation", actionName)
	}

	dc.releaseOperationLocks(ctx, operation, agentID)
	if err := dc.updateOperationStatusInternal(operation, finalStatus); err != nil {
		return err
	}

	delete(dc.operations, operationID)
	return nil
}

func (dc *DistributedCoordinator) fetchOperation(operationID string) (*DistributedOperation, error) {
	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return nil, fmt.Errorf("operation not found: %w", err)
	}
	return &op, nil
}

func (dc *DistributedCoordinator) releaseOperationLocks(ctx context.Context, op *DistributedOperation, agentID string) {
	lockIDsRaw, exists := op.OperationData["lock_ids"]
	if !exists {
		return
	}
	lockIDs, ok := lockIDsRaw.([]interface{})
	if !ok {
		return
	}
	for _, lockIDRaw := range lockIDs {
		lockID, ok := lockIDRaw.(string)
		if !ok {
			continue
		}
		if err := dc.lockManager.ReleaseLock(ctx, lockID, agentID); err != nil {
			slog.Error("failed to release lock", "error", lockID, "error", err)
		}
	}
}

func (dc *DistributedCoordinator) updateOperationStatusInternal(op *DistributedOperation, finalStatus string) error {
	now := time.Now()
	op.Status = finalStatus
	op.CompletedAt = &now
	op.UpdatedAt = now
	if err := dc.db.Save(op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}
	return nil
}
