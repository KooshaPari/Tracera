package agents

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// DistributedOperation represents a coordinated operation across multiple agents
type DistributedOperation struct {
	ID             string                 `json:"id" gorm:"primaryKey"`
	ProjectID      string                 `json:"project_id" gorm:"index:idx_operation_project"`
	Type           string                 `json:"type"`   // batch_update, coordinated_analysis, multi_agent_task
	Status         string                 `json:"status"` // pending, in_progress, completed, failed
	ParticipantIDs []string               `json:"participant_ids" gorm:"type:jsonb"`
	CoordinatorID  string                 `json:"coordinator_id"`
	TargetItems    []string               `json:"target_items" gorm:"type:jsonb"`
	OperationData  map[string]interface{} `json:"operation_data" gorm:"type:jsonb"`
	StartedAt      *time.Time             `json:"started_at,omitempty"`
	CompletedAt    *time.Time             `json:"completed_at,omitempty"`
	CreatedAt      time.Time              `json:"created_at"`
	UpdatedAt      time.Time              `json:"updated_at"`
}

// OperationParticipant tracks individual agent participation in distributed operations
type OperationParticipant struct {
	ID            string                 `json:"id" gorm:"primaryKey"`
	OperationID   string                 `json:"operation_id" gorm:"index:idx_participant_operation"`
	AgentID       string                 `json:"agent_id" gorm:"index:idx_participant_agent"`
	Status        string                 `json:"status"` // ready, working, completed, failed
	AssignedItems []string               `json:"assigned_items" gorm:"type:jsonb"`
	Result        map[string]interface{} `json:"result" gorm:"type:jsonb"`
	Error         string                 `json:"error,omitempty"`
	StartedAt     *time.Time             `json:"started_at,omitempty"`
	CompletedAt   *time.Time             `json:"completed_at,omitempty"`
	CreatedAt     time.Time              `json:"created_at"`
	UpdatedAt     time.Time              `json:"updated_at"`
}

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
func NewDistributedCoordinator(db *gorm.DB, lockManager *LockManager, conflictDetector *ConflictDetector, teamManager *TeamManager) *DistributedCoordinator {
	return &DistributedCoordinator{
		db:               db,
		lockManager:      lockManager,
		conflictDetector: conflictDetector,
		teamManager:      teamManager,
		operations:       make(map[string]*DistributedOperation),
	}
}

// CreateDistributedOperation creates a new distributed operation
func (dc *DistributedCoordinator) CreateDistributedOperation(ctx context.Context, op *DistributedOperation) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	if op.ID == "" {
		op.ID = uuid.New().String()
	}
	op.Status = "pending"
	op.CreatedAt = time.Now()
	op.UpdatedAt = time.Now()

	if err := dc.db.Create(op).Error; err != nil {
		return fmt.Errorf("failed to create operation: %w", err)
	}

	dc.operations[op.ID] = op
	return nil
}

// AssignOperationToAgents assigns parts of an operation to multiple agents
func (dc *DistributedCoordinator) AssignOperationToAgents(ctx context.Context, operationID string, agentAssignments map[string][]string) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return fmt.Errorf("operation not found: %w", err)
	}

	if op.Status != "pending" {
		return fmt.Errorf("operation is not in pending status")
	}

	// Create participant records
	for agentID, items := range agentAssignments {
		participant := &OperationParticipant{
			ID:            uuid.New().String(),
			OperationID:   operationID,
			AgentID:       agentID,
			Status:        "ready",
			AssignedItems: items,
			Result:        make(map[string]interface{}),
			CreatedAt:     time.Now(),
			UpdatedAt:     time.Now(),
		}

		if err := dc.db.Create(participant).Error; err != nil {
			return fmt.Errorf("failed to create participant: %w", err)
		}
	}

	// Update operation status
	now := time.Now()
	op.Status = "in_progress"
	op.StartedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(&op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}

	dc.operations[operationID] = &op
	return nil
}

// StartParticipation marks an agent as starting work on their part of the operation
func (dc *DistributedCoordinator) StartParticipation(ctx context.Context, operationID, agentID string) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var participant OperationParticipant
	if err := dc.db.Where("operation_id = ? AND agent_id = ?", operationID, agentID).First(&participant).Error; err != nil {
		return fmt.Errorf("participant not found: %w", err)
	}

	if participant.Status != "ready" {
		return fmt.Errorf("participant is not in ready status")
	}

	now := time.Now()
	participant.Status = "working"
	participant.StartedAt = &now
	participant.UpdatedAt = now

	if err := dc.db.Save(&participant).Error; err != nil {
		return fmt.Errorf("failed to update participant: %w", err)
	}

	return nil
}

// CompleteParticipation marks an agent's part of the operation as complete
func (dc *DistributedCoordinator) CompleteParticipation(ctx context.Context, operationID, agentID string, result map[string]interface{}) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var participant OperationParticipant
	if err := dc.db.Where("operation_id = ? AND agent_id = ?", operationID, agentID).First(&participant).Error; err != nil {
		return fmt.Errorf("participant not found: %w", err)
	}

	now := time.Now()
	participant.Status = "completed"
	participant.Result = result
	participant.CompletedAt = &now
	participant.UpdatedAt = now

	if err := dc.db.Save(&participant).Error; err != nil {
		return fmt.Errorf("failed to update participant: %w", err)
	}

	// Check if all participants are done
	return dc.checkOperationCompletion(ctx, operationID)
}

// FailParticipation marks an agent's part of the operation as failed
func (dc *DistributedCoordinator) FailParticipation(ctx context.Context, operationID, agentID string, errorMsg string) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var participant OperationParticipant
	if err := dc.db.Where("operation_id = ? AND agent_id = ?", operationID, agentID).First(&participant).Error; err != nil {
		return fmt.Errorf("participant not found: %w", err)
	}

	now := time.Now()
	participant.Status = "failed"
	participant.Error = errorMsg
	participant.CompletedAt = &now
	participant.UpdatedAt = now

	if err := dc.db.Save(&participant).Error; err != nil {
		return fmt.Errorf("failed to update participant: %w", err)
	}

	// Check if operation should be marked as failed
	return dc.checkOperationCompletion(ctx, operationID)
}

// checkOperationCompletion checks if an operation is complete
func (dc *DistributedCoordinator) checkOperationCompletion(ctx context.Context, operationID string) error {
	var participants []OperationParticipant
	if err := dc.db.Where("operation_id = ?", operationID).Find(&participants).Error; err != nil {
		return fmt.Errorf("failed to get participants: %w", err)
	}

	allCompleted := true
	anyFailed := false

	for _, p := range participants {
		if p.Status != "completed" && p.Status != "failed" {
			allCompleted = false
		}
		if p.Status == "failed" {
			anyFailed = true
		}
	}

	if !allCompleted {
		return nil // Operation still in progress
	}

	// All participants are done, update operation
	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return fmt.Errorf("operation not found: %w", err)
	}

	now := time.Now()
	if anyFailed {
		op.Status = "failed"
	} else {
		op.Status = "completed"
	}
	op.CompletedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(&op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}

	delete(dc.operations, operationID)
	return nil
}

// GetOperationStatus returns the status of a distributed operation
func (dc *DistributedCoordinator) GetOperationStatus(ctx context.Context, operationID string) (*DistributedOperation, []OperationParticipant, error) {
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

// CoordinatedUpdate performs a coordinated update across multiple items with conflict detection
func (dc *DistributedCoordinator) CoordinatedUpdate(ctx context.Context, projectID string, updates map[string]map[string]interface{}, coordinatorAgentID string) (*DistributedOperation, error) {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	// Create operation
	itemIDs := make([]string, 0, len(updates))
	for itemID := range updates {
		itemIDs = append(itemIDs, itemID)
	}

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

	// Acquire locks on all items
	locks := make([]*AgentLock, 0, len(itemIDs))
	for _, itemID := range itemIDs {
		lock, err := dc.lockManager.AcquireLock(ctx, itemID, "item", coordinatorAgentID, LockTypePessimistic)
		if err != nil {
			// Release acquired locks on failure
			for _, l := range locks {
				dc.lockManager.ReleaseLock(ctx, l.ID, coordinatorAgentID)
			}
			return nil, fmt.Errorf("failed to acquire lock for item %s: %w", itemID, err)
		}
		locks = append(locks, lock)
	}

	// Detect conflicts
	for itemID := range updates {
		conflict, err := dc.conflictDetector.DetectConflict(ctx, itemID, coordinatorAgentID, 1)
		if err != nil {
			// Release locks on error
			for _, l := range locks {
				dc.lockManager.ReleaseLock(ctx, l.ID, coordinatorAgentID)
			}
			return nil, fmt.Errorf("conflict detection failed for item %s: %w", itemID, err)
		}

		if conflict != nil {
			// Release locks and return conflict
			for _, l := range locks {
				dc.lockManager.ReleaseLock(ctx, l.ID, coordinatorAgentID)
			}
			return nil, fmt.Errorf("conflict detected for item %s: %v", itemID, conflict)
		}
	}

	now := time.Now()
	op.Status = "in_progress"
	op.StartedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(op).Error; err != nil {
		// Release locks on error
		for _, l := range locks {
			dc.lockManager.ReleaseLock(ctx, l.ID, coordinatorAgentID)
		}
		return nil, fmt.Errorf("failed to update operation: %w", err)
	}

	dc.operations[op.ID] = op

	// Store locks in operation data for later release
	lockIDs := make([]string, len(locks))
	for i, l := range locks {
		lockIDs[i] = l.ID
	}
	op.OperationData["lock_ids"] = lockIDs

	return op, nil
}

// finalizeOperation is the internal implementation for completing or cancelling operations
func (dc *DistributedCoordinator) finalizeOperation(ctx context.Context, operationID string, agentID string, finalStatus string, actionName string) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return fmt.Errorf("operation not found: %w", err)
	}

	if op.CoordinatorID != agentID {
		return fmt.Errorf("only coordinator can %s the operation", actionName)
	}

	// Release all locks
	if lockIDsRaw, exists := op.OperationData["lock_ids"]; exists {
		if lockIDs, ok := lockIDsRaw.([]interface{}); ok {
			for _, lockIDRaw := range lockIDs {
				if lockID, ok := lockIDRaw.(string); ok {
					dc.lockManager.ReleaseLock(ctx, lockID, agentID)
				}
			}
		}
	}

	// Update operation status
	now := time.Now()
	op.Status = finalStatus
	op.CompletedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(&op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}

	delete(dc.operations, operationID)
	return nil
}

// CompleteCoordinatedUpdate completes a coordinated update and releases locks
func (dc *DistributedCoordinator) CompleteCoordinatedUpdate(ctx context.Context, operationID string, coordinatorAgentID string) error {
	return dc.finalizeOperation(ctx, operationID, coordinatorAgentID, "completed", "complete")
}

// GetAgentOperations returns all operations an agent is participating in
func (dc *DistributedCoordinator) GetAgentOperations(ctx context.Context, agentID string, status string) ([]DistributedOperation, error) {
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

// CancelOperation cancels a distributed operation and releases all locks
func (dc *DistributedCoordinator) CancelOperation(ctx context.Context, operationID string, cancellerAgentID string) error {
	return dc.finalizeOperation(ctx, operationID, cancellerAgentID, "cancelled", "cancel")
}

// GetDistributedOperation retrieves a distributed operation by ID
func (dc *DistributedCoordinator) GetDistributedOperation(ctx context.Context, operationID string) (*DistributedOperation, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return nil, fmt.Errorf("operation not found: %w", err)
	}

	return &op, nil
}

// ListOperations lists all distributed operations with optional filtering
func (dc *DistributedCoordinator) ListOperations(ctx context.Context, projectID string, statusFilter string) ([]DistributedOperation, error) {
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

// CompleteOperation marks a distributed operation as completed
func (dc *DistributedCoordinator) CompleteOperation(ctx context.Context, operationID string) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var op DistributedOperation
	if err := dc.db.First(&op, "id = ?", operationID).Error; err != nil {
		return fmt.Errorf("operation not found: %w", err)
	}

	now := time.Now()
	op.Status = "completed"
	op.CompletedAt = &now
	op.UpdatedAt = now

	if err := dc.db.Save(&op).Error; err != nil {
		return fmt.Errorf("failed to update operation: %w", err)
	}

	dc.operations[operationID] = &op
	return nil
}

// UpdateOperationStatus updates the status of a distributed operation
func (dc *DistributedCoordinator) UpdateOperationStatus(ctx context.Context, operationID string, status string) error {
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

// GetParticipantStatus returns the status of a participant in a distributed operation
func (dc *DistributedCoordinator) GetParticipantStatus(ctx context.Context, operationID string, agentID string) (*OperationParticipant, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	var participant OperationParticipant
	if err := dc.db.Where("operation_id = ? AND agent_id = ?", operationID, agentID).First(&participant).Error; err != nil {
		return nil, fmt.Errorf("participant not found: %w", err)
	}

	return &participant, nil
}

// SubmitParticipantResult submits a result from a participant in a distributed operation
func (dc *DistributedCoordinator) SubmitParticipantResult(ctx context.Context, operationID string, agentID string, result map[string]interface{}) error {
	dc.mu.Lock()
	defer dc.mu.Unlock()

	var participant OperationParticipant
	if err := dc.db.Where("operation_id = ? AND agent_id = ?", operationID, agentID).First(&participant).Error; err != nil {
		return fmt.Errorf("participant not found: %w", err)
	}

	now := time.Now()
	participant.Status = "completed"
	participant.Result = result
	participant.CompletedAt = &now
	participant.UpdatedAt = now

	if err := dc.db.Save(&participant).Error; err != nil {
		return fmt.Errorf("failed to update participant: %w", err)
	}

	return dc.checkOperationCompletion(ctx, operationID)
}

// GetOperationResults returns aggregated results from a distributed operation
func (dc *DistributedCoordinator) GetOperationResults(ctx context.Context, operationID string) (map[string]interface{}, error) {
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

	participantsMap := results["participants"].(map[string]interface{})
	for _, p := range participants {
		participantsMap[p.AgentID] = map[string]interface{}{
			"status": p.Status,
			"result": p.Result,
			"error":  p.Error,
		}
	}

	return results, nil
}
