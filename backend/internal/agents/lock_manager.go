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

// LockManager handles lock acquisition and release
type LockManager struct {
	db              *gorm.DB
	mu              sync.RWMutex
	activeLocks     map[string]*AgentLock // itemID -> lock
	lockTimeout     time.Duration
	cleanupInterval time.Duration
	ctx             context.Context
	cancel          context.CancelFunc
	wg              sync.WaitGroup
}

// NewLockManager creates a new lock manager
func NewLockManager(db *gorm.DB, lockTimeout time.Duration) *LockManager {
	ctx, cancel := context.WithCancel(context.Background())

	lm := &LockManager{
		db:              db,
		activeLocks:     make(map[string]*AgentLock),
		lockTimeout:     lockTimeout,
		cleanupInterval: defaultLockCleanupInterval,
		ctx:             ctx,
		cancel:          cancel,
	}

	// Start cleanup goroutine
	lm.wg.Add(1)
	go lm.cleanupExpiredLocks()

	return lm
}

// AcquireLock attempts to acquire a lock on an item
func (lm *LockManager) AcquireLock(
	ctx context.Context,
	itemID,
	itemType,
	agentID string,
	lockType LockType,
) (*AgentLock, error) {
	lm.mu.Lock()
	defer lm.mu.Unlock()

	// Check if item is already locked
	if existingLock, exists := lm.activeLocks[itemID]; exists {
		refreshed, err := lm.tryRefreshExistingLock(existingLock, agentID)
		if refreshed || err != nil {
			return existingLock, err
		}
	}

	// Get current version for optimistic locking
	currentVersion, err := lm.resolveVersion(itemID, lockType)
	if err != nil {
		return nil, err
	}

	// Create new lock
	lock := &AgentLock{
		ID:        uuid.New().String(),
		ItemID:    itemID,
		ItemType:  itemType,
		AgentID:   agentID,
		LockType:  lockType,
		Version:   currentVersion,
		ExpireAt:  time.Now().Add(lm.lockTimeout),
		Metadata:  make(map[string]interface{}),
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Save to database
	if err := lm.db.Create(lock).Error; err != nil {
		return nil, fmt.Errorf("failed to create lock: %w", err)
	}

	// Store in memory
	lm.activeLocks[itemID] = lock

	return lock, nil
}

func (lm *LockManager) tryRefreshExistingLock(existingLock *AgentLock, agentID string) (bool, error) {
	if existingLock.AgentID == agentID {
		// Same agent, refresh the lock
		existingLock.ExpireAt = time.Now().Add(lm.lockTimeout)
		if err := lm.db.Save(existingLock).Error; err != nil {
			return true, fmt.Errorf("failed to refresh lock: %w", err)
		}
		return true, nil
	}

	// Check if lock has expired
	if time.Now().Before(existingLock.ExpireAt) {
		return false, fmt.Errorf(
			"item %s is locked by agent %s until %v",
			existingLock.ItemID,
			existingLock.AgentID,
			existingLock.ExpireAt,
		)
	}
	return false, nil
}

func (lm *LockManager) resolveVersion(itemID string, lockType LockType) (int64, error) {
	var currentVersion int64 = 1
	if lockType == LockTypeOptimistic {
		var lastVersion ItemVersion
		err := lm.db.Where("item_id = ?", itemID).Order("version DESC").First(&lastVersion).Error
		if err == nil {
			currentVersion = lastVersion.Version + 1
		}
	}
	return currentVersion, nil
}

// ReleaseLock releases a lock on an item
func (lm *LockManager) ReleaseLock(ctx context.Context, lockID, agentID string) error {
	lm.mu.Lock()
	defer lm.mu.Unlock()

	var lock AgentLock
	if err := lm.db.First(&lock, "id = ?", lockID).Error; err != nil {
		return fmt.Errorf("lock not found: %w", err)
	}

	if lock.AgentID != agentID {
		return fmt.Errorf("lock %s is owned by agent %s, not %s", lockID, lock.AgentID, agentID)
	}

	// Delete from database
	if err := lm.db.Delete(&lock).Error; err != nil {
		return fmt.Errorf("failed to delete lock: %w", err)
	}

	// Remove from memory
	delete(lm.activeLocks, lock.ItemID)

	return nil
}

// ValidateVersion checks if the version is valid for optimistic locking
func (lm *LockManager) ValidateVersion(_ context.Context, itemID string, expectedVersion int64) error {
	var lastVersion ItemVersion
	err := lm.db.Where("item_id = ?", itemID).Order("version DESC").First(&lastVersion).Error

	if errors.Is(err, gorm.ErrRecordNotFound) {
		// No versions exist, this is the first one
		if expectedVersion == 1 {
			return nil
		}
		return fmt.Errorf("version mismatch: expected 1 for new item, got %d", expectedVersion)
	}

	if err != nil {
		return fmt.Errorf("failed to get last version: %w", err)
	}

	if lastVersion.Version != expectedVersion-1 {
		return fmt.Errorf("version mismatch: expected %d, current is %d", expectedVersion-1, lastVersion.Version)
	}

	return nil
}

// RecordVersion records a new version after successful update
func (lm *LockManager) RecordVersion(
	_ context.Context,
	itemID,
	agentID string,
	version int64,
	changes map[string]interface{},
	previousHash,
	currentHash string,
) error {
	itemVersion := &ItemVersion{
		ID:           uuid.New().String(),
		ItemID:       itemID,
		Version:      version,
		AgentID:      agentID,
		Changes:      changes,
		PreviousHash: previousHash,
		CurrentHash:  currentHash,
		CreatedAt:    time.Now(),
	}

	if err := lm.db.Create(itemVersion).Error; err != nil {
		return fmt.Errorf("failed to record version: %w", err)
	}

	return nil
}

// cleanupExpiredLocks periodically removes expired locks
func (lm *LockManager) cleanupExpiredLocks() {
	defer lm.wg.Done()

	ticker := time.NewTicker(lm.cleanupInterval)
	defer ticker.Stop()

	for {
		select {
		case <-lm.ctx.Done():
			return
		case <-ticker.C:
			lm.performCleanup()
		}
	}
}

// performCleanup removes expired locks
func (lm *LockManager) performCleanup() {
	lm.mu.Lock()
	defer lm.mu.Unlock()

	now := time.Now()
	var expiredLockIDs []string

	// Find expired locks in memory
	for itemID, lock := range lm.activeLocks {
		if now.After(lock.ExpireAt) {
			expiredLockIDs = append(expiredLockIDs, lock.ID)
			delete(lm.activeLocks, itemID)
		}
	}

	// Delete from database
	if len(expiredLockIDs) > 0 {
		lm.db.Where("id IN ?", expiredLockIDs).Delete(&AgentLock{})
	}

	// Also cleanup any expired locks from database that weren't in memory
	lm.db.Where("expire_at < ?", now).Delete(&AgentLock{})
}

// GetActiveLocks returns all active locks for an agent or item
func (lm *LockManager) GetActiveLocks(_ context.Context, agentID, itemID string) ([]AgentLock, error) {
	var locks []AgentLock
	query := lm.db.Where("expire_at > ?", time.Now())

	if agentID != "" {
		query = query.Where("agent_id = ?", agentID)
	}
	if itemID != "" {
		query = query.Where("item_id = ?", itemID)
	}

	if err := query.Find(&locks).Error; err != nil {
		return nil, fmt.Errorf("failed to get locks: %w", err)
	}

	return locks, nil
}

// Shutdown gracefully shuts down the lock manager
func (lm *LockManager) Shutdown() {
	lm.cancel()
	lm.wg.Wait()
}
