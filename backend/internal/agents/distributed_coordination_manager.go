package agents

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// DistributedCoordinator manages distributed operations across multiple agents
type DistributedCoordinator struct {
	db               *gorm.DB
	lockManager      *LockManager
	conflictDetector *ConflictDetector
	teamManager      *TeamManager
	mu               sync.RWMutex
	operations       map[string]*DistributedOperation
}

// NewDistributedCoordinator creates a new distributed coordinator
func NewDistributedCoordinator(
	db *gorm.DB,
	lockManager *LockManager,
	conflictDetector *ConflictDetector,
	teamManager *TeamManager,
) *DistributedCoordinator {
	return &DistributedCoordinator{
		db:               db,
		lockManager:      lockManager,
		conflictDetector: conflictDetector,
		teamManager:      teamManager,
		operations:       make(map[string]*DistributedOperation),
	}
}

// CreateDistributedOperation creates a new distributed operation
func (dc *DistributedCoordinator) CreateDistributedOperation(_ context.Context, op *DistributedOperation) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	if op.ID == "" {
		op.ID = uuid.New().String()
	}
	op.Status = string(TaskStatusPending)
	op.CreatedAt = time.Now()
	op.UpdatedAt = time.Now()

	if err := dc.db.Create(op).Error; err != nil {
		return fmt.Errorf("failed to create operation: %w", err)
	}

	dc.operations[op.ID] = op
	return nil
}

// checkOperationCompletion checks if an operation is complete
func (dc *DistributedCoordinator) checkOperationCompletion(_ context.Context, operationID string) error {
	var participants []OperationParticipant
	if err := dc.db.Where("operation_id = ?", operationID).Find(&participants).Error; err != nil {
		return fmt.Errorf("failed to get participants: %w", err)
	}

	allCompleted, anyFailed := dc.assessParticipantsStatus(participants)

	if !allCompleted {
		return nil // Operation still in progress
	}

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return fmt.Errorf("operation not found: %w", err)
	}

	now := time.Now()
	if anyFailed {
		op.Status = string(TaskStatusFailed)
	} else {
		op.Status = string(TaskStatusCompleted)
	}
	op.CompletedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(&op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}

	delete(dc.operations, operationID)
	return nil
}

func (dc *DistributedCoordinator) assessParticipantsStatus(participants []OperationParticipant) (bool, bool) {
	allCompleted := true
	anyFailed := false

	for _, p := range participants {
		if p.Status != string(TaskStatusCompleted) && p.Status != string(TaskStatusFailed) {
			allCompleted = false
		}
		if p.Status == string(TaskStatusFailed) {
			anyFailed = true
		}
	}
	return allCompleted, anyFailed
}

// CompleteOperation marks a distributed operation as completed
func (dc *DistributedCoordinator) CompleteOperation(_ context.Context, operationID string) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return fmt.Errorf("operation not found: %w", err)
	}

	now := time.Now()
	op.Status = string(TaskStatusCompleted)
	op.CompletedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(&op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}

	dc.operations[operationID] = &op
	return nil
}

// UpdateOperationStatus updates the status of a distributed operation
func (dc *DistributedCoordinator) UpdateOperationStatus(_ context.Context, operationID string, status string) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return fmt.Errorf("operation not found: %w", err)
	}

	op.Status = status
	op.UpdatedAt = time.Now()

	if err := dc.db.Save(&op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}

	dc.operations[operationID] = &op
	return nil
}
