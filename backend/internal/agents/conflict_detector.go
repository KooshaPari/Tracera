package agents

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// ConflictDetector detects and manages conflicts
type ConflictDetector struct {
	db          *gorm.DB
	lockManager *LockManager
	mu          sync.RWMutex
}

// NewConflictDetector creates a new conflict detector
func NewConflictDetector(db *gorm.DB, lockManager *LockManager) *ConflictDetector {
	return &ConflictDetector{
		db:          db,
		lockManager: lockManager,
	}
}

// DetectConflict checks for conflicts when multiple agents modify the same item
func (cd *ConflictDetector) DetectConflict(
	ctx context.Context,
	itemID string,
	agentID string,
	expectedVersion int64,
) (*ConflictRecord, error) {
	cd.mu.Lock()
	defer cd.mu.Unlock()

	// Check for active locks by other agents
	locks, err := cd.lockManager.GetActiveLocks(ctx, "", itemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get locks: %w", err)
	}

	conflictingAgents := extractConflictingAgents(locks, agentID)
	if conflict := cd.buildVersionConflict(itemID, agentID, expectedVersion, conflictingAgents); conflict != nil {
		return cd.createConflictRecord(conflict)
	}
	if conflict := buildConcurrentConflict(itemID, agentID, conflictingAgents); conflict != nil {
		return cd.createConflictRecord(conflict)
	}

	return nil, nil // No conflict
}

func extractConflictingAgents(locks []AgentLock, agentID string) []string {
	var conflictingAgents []string
	for _, lock := range locks {
		if lock.AgentID != agentID {
			conflictingAgents = append(conflictingAgents, lock.AgentID)
		}
	}
	return conflictingAgents
}

func (cd *ConflictDetector) buildVersionConflict(
	itemID string,
	agentID string,
	expectedVersion int64,
	conflictingAgents []string,
) *ConflictRecord {
	var lastVersion ItemVersion
	if err := cd.db.Where("item_id = ?", itemID).Order("version DESC").First(&lastVersion).Error; err != nil {
		return nil
	}
	if lastVersion.Version == expectedVersion-1 {
		return nil
	}
	if lastVersion.AgentID != agentID {
		conflictingAgents = append(conflictingAgents, lastVersion.AgentID)
	}
	return &ConflictRecord{
		ID:                 uuid.New().String(),
		ItemID:             itemID,
		ConflictingAgents:  conflictingAgents,
		ConflictType:       "version_mismatch",
		ResolutionStrategy: ResolutionLastWriteWins,
		ResolutionStatus:   resolutionStatusPending,
		ConflictData: map[string]interface{}{
			"expected_version": expectedVersion,
			"current_version":  lastVersion.Version,
			"current_agent":    agentID,
			"last_agent":       lastVersion.AgentID,
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
}

func buildConcurrentConflict(itemID string, agentID string, conflictingAgents []string) *ConflictRecord {
	if len(conflictingAgents) == 0 {
		return nil
	}
	return &ConflictRecord{
		ID:                 uuid.New().String(),
		ItemID:             itemID,
		ConflictingAgents:  conflictingAgents,
		ConflictType:       "concurrent_modification",
		ResolutionStrategy: ResolutionFirstWins,
		ResolutionStatus:   resolutionStatusPending,
		ConflictData: map[string]interface{}{
			"current_agent":      agentID,
			"conflicting_agents": conflictingAgents,
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
}

func (cd *ConflictDetector) createConflictRecord(conflict *ConflictRecord) (*ConflictRecord, error) {
	if err := cd.db.Create(conflict).Error; err != nil {
		return nil, fmt.Errorf("failed to create conflict record: %w", err)
	}

	return conflict, nil
}

// ResolveConflict resolves a conflict based on the strategy
func (cd *ConflictDetector) ResolveConflict(
	_ context.Context,
	conflictID string,
	resolverAgentID string,
	strategy ConflictResolutionStrategy,
	resolution map[string]interface{},
) error {
	cd.mu.Lock()
	defer cd.mu.Unlock()

	var conflict ConflictRecord
	if err := cd.db.First(&conflict, "id = ?", conflictID).Error; err != nil {
		return fmt.Errorf("conflict not found: %w", err)
	}

	if conflict.ResolutionStatus != resolutionStatusPending {
		return errors.New("conflict already resolved")
	}

	now := time.Now()
	conflict.ResolutionStrategy = strategy
	conflict.ResolutionStatus = "resolved"
	conflict.ResolvedBy = resolverAgentID
	conflict.ResolvedAt = &now
	conflict.ConflictData["resolution"] = resolution
	conflict.UpdatedAt = now

	if err := cd.db.Save(&conflict).Error; err != nil {
		return fmt.Errorf("failed to update conflict: %w", err)
	}

	return nil
}

// GetPendingConflicts returns all pending conflicts for an item or agent
func (cd *ConflictDetector) GetPendingConflicts(_ context.Context, itemID, agentID string) ([]ConflictRecord, error) {
	var conflicts []ConflictRecord
	query := cd.db.Where("resolution_status = ?", resolutionStatusPending)

	if itemID != "" {
		query = query.Where("item_id = ?", itemID)
	}
	if agentID != "" {
		query = query.Where("conflicting_agents @> ?", fmt.Sprintf(`["%s"]`, agentID))
	}

	if err := query.Find(&conflicts).Error; err != nil {
		return nil, fmt.Errorf("failed to get conflicts: %w", err)
	}

	return conflicts, nil
}
