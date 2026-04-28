package agents

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"github.com/google/uuid"
)

// CoordinatedUpdate performs a coordinated update across multiple items with conflict detection
func (dc *DistributedCoordinator) CoordinatedUpdate(
	ctx context.Context,
	projectID string,
	updates map[string]map[string]interface{},
	coordinatorAgentID string,
) (*DistributedOperation, error) {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	itemIDs := buildItemIDs(updates)

	op, err := dc.createOperation(projectID, coordinatorAgentID, updates, itemIDs)
	if err != nil {
		return nil, err
	}

	locks, err := dc.acquireLocks(ctx, itemIDs, coordinatorAgentID)
	if err != nil {
		return nil, err
	}

	if err := dc.ensureNoConflicts(ctx, updates, coordinatorAgentID, locks); err != nil {
		return nil, err
	}

	if err := dc.startOperation(ctx, op, locks, coordinatorAgentID); err != nil {
		return nil, err
	}

	return op, nil
}

func buildItemIDs(updates map[string]map[string]interface{}) []string {
	itemIDs := make([]string, 0, len(updates))
	for itemID := range updates {
		itemIDs = append(itemIDs, itemID)
	}
	return itemIDs
}

func (dc *DistributedCoordinator) createOperation(
	projectID string,
	coordinatorAgentID string,
	updates map[string]map[string]interface{},
	itemIDs []string,
) (*DistributedOperation, error) {
	op := &DistributedOperation{
		ID:             uuid.New().String(),
		ProjectID:      projectID,
		Type:           "batch_update",
		Status:         "pending",
		ParticipantIDs: []string{coordinatorAgentID},
		CoordinatorID:  coordinatorAgentID,
		TargetItems:    itemIDs,
		OperationData: map[string]interface{}{
			"updates": updates,
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := dc.db.Create(op).Error; err != nil {
		return nil, fmt.Errorf("failed to create operation: %w", err)
	}

	return op, nil
}

func (dc *DistributedCoordinator) acquireLocks(
	ctx context.Context,
	itemIDs []string,
	coordinatorAgentID string,
) ([]*AgentLock, error) {
	locks := make([]*AgentLock, 0, len(itemIDs))
	for _, itemID := range itemIDs {
		lock, err := dc.lockManager.AcquireLock(ctx, itemID, "item", coordinatorAgentID, LockTypePessimistic)
		if err != nil {
			dc.releaseLocks(ctx, locks, coordinatorAgentID)
			return nil, fmt.Errorf("failed to acquire lock for item %s: %w", itemID, err)
		}
		locks = append(locks, lock)
	}

	return locks, nil
}

func (dc *DistributedCoordinator) ensureNoConflicts(
	ctx context.Context,
	updates map[string]map[string]interface{},
	coordinatorAgentID string,
	locks []*AgentLock,
) error {
	for itemID := range updates {
		conflict, err := dc.conflictDetector.DetectConflict(ctx, itemID, coordinatorAgentID, 1)
		if err != nil {
			dc.releaseLocks(ctx, locks, coordinatorAgentID)
			return fmt.Errorf("conflict detection failed for item %s: %w", itemID, err)
		}

		if conflict != nil {
			dc.releaseLocks(ctx, locks, coordinatorAgentID)
			return fmt.Errorf("conflict detected for item %s: %v", itemID, conflict)
		}
	}

	return nil
}

func (dc *DistributedCoordinator) startOperation(
	ctx context.Context,
	op *DistributedOperation,
	locks []*AgentLock,
	coordinatorAgentID string,
) error {
	now := time.Now()
	op.Status = statusInProgress
	op.StartedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(op).Error; err != nil {
		dc.releaseLocks(ctx, locks, coordinatorAgentID)
		return fmt.Errorf("failed to update operation: %w", err)
	}

	dc.operations[op.ID] = op
	op.OperationData["lock_ids"] = lockIDsFromLocks(locks)

	return nil
}

func (dc *DistributedCoordinator) releaseLocks(ctx context.Context, locks []*AgentLock, coordinatorAgentID string) {
	for _, lock := range locks {
		if err := dc.lockManager.ReleaseLock(ctx, lock.ID, coordinatorAgentID); err != nil {
			slog.Error("failed to release lock", "error", lock.ID, "error", err)
		}
	}
}

func lockIDsFromLocks(locks []*AgentLock) []string {
	lockIDs := make([]string, len(locks))
	for i, lock := range locks {
		lockIDs[i] = lock.ID
	}
	return lockIDs
}

// CompleteCoordinatedUpdate completes a coordinated update and releases locks
func (dc *DistributedCoordinator) CompleteCoordinatedUpdate(
	ctx context.Context,
	operationID string,
	coordinatorAgentID string,
) error {
	return dc.finalizeOperation(ctx, operationID, coordinatorAgentID, string(TaskStatusCompleted), "complete")
}

// CancelOperation cancels a distributed operation and releases all locks
func (dc *DistributedCoordinator) CancelOperation(
	ctx context.Context,
	operationID string,
	cancellerAgentID string,
) error {
	return dc.finalizeOperation(ctx, operationID, cancellerAgentID, "cancelled", "cancel")
}
