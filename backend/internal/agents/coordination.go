// Package agents provides coordination primitives for agent collaboration.
package agents

import (
	"context"
	"database/sql/driver"
	"encoding/json"
	"errors"
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

const defaultLockCleanupInterval = 30 * time.Second

// Resolution status constants
const (
	resolutionStatusPending  = "pending"
	resolutionStatusResolved = "resolved"
	resolutionStatusFailed   = "failed"
)

// LockType represents the type of lock
type LockType string

const (
	// LockTypeOptimistic uses version-based locking.
	LockTypeOptimistic LockType = "optimistic"
	// LockTypePessimistic uses exclusive locking.
	LockTypePessimistic LockType = "pessimistic"
)

// ConflictResolutionStrategy defines how conflicts should be resolved
type ConflictResolutionStrategy string

const (
	// ResolutionLastWriteWins resolves conflicts by taking the most recent update.
	ResolutionLastWriteWins ConflictResolutionStrategy = "last_write_wins"
	// ResolutionAgentPriority resolves conflicts by preferring higher priority agents.
	ResolutionAgentPriority ConflictResolutionStrategy = "agent_priority"
	// ResolutionManual requires manual intervention to resolve conflicts.
	ResolutionManual ConflictResolutionStrategy = "manual"
	// ResolutionMerge attempts to merge changes when resolving conflicts.
	ResolutionMerge ConflictResolutionStrategy = "merge"
	// ResolutionFirstWins resolves conflicts by preferring the first lock holder.
	ResolutionFirstWins ConflictResolutionStrategy = "first_wins"
)

// AgentLock represents a lock on an item by an agent
type AgentLock struct {
	ID        string    `json:"id" gorm:"primaryKey"`
	ItemID    string    `json:"item_id" gorm:"index:idx_lock_item"`
	ItemType  string    `json:"item_type"`
	AgentID   string    `json:"agent_id" gorm:"index:idx_lock_agent"`
	LockType  LockType  `json:"lock_type"`
	Version   int64     `json:"version"`
	ExpireAt  time.Time `json:"expire_at" gorm:"index:idx_lock_expire"`
	Metadata  JSONMap   `json:"metadata" gorm:"type:jsonb"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// AgentTeam represents a team of agents with role-based access
type AgentTeam struct {
	ID          string              `json:"id" gorm:"primaryKey"`
	ProjectID   string              `json:"project_id" gorm:"index:idx_team_project"`
	Name        string              `json:"name"`
	Description string              `json:"description"`
	Roles       map[string]TeamRole `json:"roles" gorm:"serializer:json"`
	Metadata    JSONMap             `json:"metadata" gorm:"type:jsonb"`
	CreatedAt   time.Time           `json:"created_at"`
	UpdatedAt   time.Time           `json:"updated_at"`
}

// JSONMap persists map[string]interface{} as JSON for sqlite/mysql/postgres.
type JSONMap map[string]interface{}

// Value persists map[string]interface{} as JSON for sqlite/mysql/postgres.
func (m JSONMap) Value() (driver.Value, error) {
	if m == nil {
		return []byte("{}"), nil
	}
	b, err := json.Marshal(map[string]interface{}(m))
	if err != nil {
		return nil, err
	}
	return b, nil
}

func (m *JSONMap) Scan(value interface{}) error {
	if m == nil {
		return errors.New("JSONMap: Scan on nil receiver")
	}

	if value == nil {
		*m = JSONMap{}
		return nil
	}

	var data []byte
	switch v := value.(type) {
	case []byte:
		data = v
	case string:
		data = []byte(v)
	default:
		return fmt.Errorf("JSONMap: unsupported Scan type %T", value)
	}

	if len(data) == 0 {
		*m = JSONMap{}
		return nil
	}

	var out map[string]interface{}
	if err := json.Unmarshal(data, &out); err != nil {
		return err
	}
	*m = JSONMap(out)
	return nil
}

// JSONStringArray is a custom type for []string that works with SQLite
type JSONStringArray []string

func (a JSONStringArray) Value() (driver.Value, error) {
	if a == nil {
		return []byte("[]"), nil
	}
	b, err := json.Marshal([]string(a))
	if err != nil {
		return nil, err
	}
	return b, nil
}

func (a *JSONStringArray) Scan(value interface{}) error {
	if a == nil {
		return errors.New("JSONStringArray: Scan on nil receiver")
	}

	if value == nil {
		*a = JSONStringArray{}
		return nil
	}

	var data []byte
	switch v := value.(type) {
	case []byte:
		data = v
	case string:
		data = []byte(v)
	default:
		return fmt.Errorf("JSONStringArray: unsupported Scan type %T", value)
	}

	if len(data) == 0 {
		*a = JSONStringArray{}
		return nil
	}

	var out []string
	if err := json.Unmarshal(data, &out); err != nil {
		return err
	}
	*a = JSONStringArray(out)
	return nil
}

// TeamRole defines permissions for a role
type TeamRole struct {
	Name        string   `json:"name"`
	Permissions []string `json:"permissions"` // read, write, delete, lock, unlock
	Priority    int      `json:"priority"`    // Higher number = higher priority
}

// AgentTeamMembership links agents to teams with roles
type AgentTeamMembership struct {
	ID        string    `json:"id" gorm:"primaryKey"`
	TeamID    string    `json:"team_id" gorm:"index:idx_membership_team"`
	AgentID   string    `json:"agent_id" gorm:"index:idx_membership_agent"`
	RoleName  string    `json:"role_name"`
	JoinedAt  time.Time `json:"joined_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// ItemVersion tracks version history for conflict detection
type ItemVersion struct {
	ID           string    `json:"id" gorm:"primaryKey"`
	ItemID       string    `json:"item_id" gorm:"index:idx_version_item"`
	Version      int64     `json:"version"`
	AgentID      string    `json:"agent_id"`
	Changes      JSONMap   `json:"changes" gorm:"type:jsonb"`
	PreviousHash string    `json:"previous_hash"`
	CurrentHash  string    `json:"current_hash" gorm:"index:idx_version_hash"`
	CreatedAt    time.Time `json:"created_at"`
}

// ConflictRecord tracks detected conflicts
type ConflictRecord struct {
	ID                string   `json:"id" gorm:"primaryKey"`
	ItemID            string   `json:"item_id" gorm:"index:idx_conflict_item"`
	ConflictingAgents []string `json:"conflicting_agents" gorm:"type:jsonb"`
	// concurrent_modification, version_mismatch, lock_timeout
	ConflictType       string                     `json:"conflict_type"`
	ResolutionStrategy ConflictResolutionStrategy `json:"resolution_strategy"`
	// pending, resolved, failed
	ResolutionStatus string     `json:"resolution_status"`
	ConflictData     JSONMap    `json:"conflict_data" gorm:"type:jsonb"`
	ResolvedBy       string     `json:"resolved_by,omitempty"`
	ResolvedAt       *time.Time `json:"resolved_at,omitempty"`
	CreatedAt        time.Time  `json:"created_at"`
	UpdatedAt        time.Time  `json:"updated_at"`
}

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
	_ context.Context,
	itemID,
	itemType,
	agentID string,
	lockType LockType,
) (*AgentLock, error) {
	lm.mu.Lock()
	defer lm.mu.Unlock()

	// Check if item is already locked
	existingLock, exists := lm.activeLocks[itemID]
	if exists {
		if existingLock.AgentID == agentID {
			// Same agent, refresh the lock
			existingLock.ExpireAt = time.Now().Add(lm.lockTimeout)
			if err := lm.db.Save(existingLock).Error; err != nil {
				return nil, fmt.Errorf("failed to refresh lock: %w", err)
			}
			return existingLock, nil
		}

		// Check if lock has expired
		if time.Now().Before(existingLock.ExpireAt) {
			return nil, fmt.Errorf(
				"item %s is locked by agent %s until %v",
				itemID,
				existingLock.AgentID,
				existingLock.ExpireAt,
			)
		}
	}

	// Get current version
	var currentVersion int64 = 1
	if lockType == LockTypeOptimistic {
		var lastVersion ItemVersion
		err := lm.db.Where("item_id = ?", itemID).Order("version DESC").First(&lastVersion).Error
		if err == nil {
			currentVersion = lastVersion.Version + 1
		}
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

// ReleaseLock releases a lock on an item
func (lm *LockManager) ReleaseLock(_ context.Context, lockID, agentID string) error {
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

	if err == gorm.ErrRecordNotFound {
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

// TeamManager manages agent teams and roles
type TeamManager struct {
	db *gorm.DB
	mu sync.RWMutex
}

// NewTeamManager creates a new team manager
func NewTeamManager(db *gorm.DB) *TeamManager {
	return &TeamManager{
		db: db,
	}
}

// CreateTeam creates a new agent team
func (tm *TeamManager) CreateTeam(_ context.Context, team *AgentTeam) error {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	if team.ID == "" {
		team.ID = uuid.New().String()
	}
	team.CreatedAt = time.Now()
	team.UpdatedAt = time.Now()

	if err := tm.db.Create(team).Error; err != nil {
		return fmt.Errorf("failed to create team: %w", err)
	}

	return nil
}

// AddTeamMember adds an agent to a team with a role
func (tm *TeamManager) AddTeamMember(_ context.Context, teamID, agentID, roleName string) error {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	// Verify team exists
	var team AgentTeam
	if err := tm.db.First(&team, "id = ?", teamID).Error; err != nil {
		return fmt.Errorf("team not found: %w", err)
	}

	// Verify role exists in team
	if _, exists := team.Roles[roleName]; !exists {
		return fmt.Errorf("role %s not found in team", roleName)
	}

	membership := &AgentTeamMembership{
		ID:        uuid.New().String(),
		TeamID:    teamID,
		AgentID:   agentID,
		RoleName:  roleName,
		JoinedAt:  time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := tm.db.Create(membership).Error; err != nil {
		return fmt.Errorf("failed to add team member: %w", err)
	}

	return nil
}

// GetAgentPermissions returns the permissions for an agent based on their team roles
func (tm *TeamManager) GetAgentPermissions(_ context.Context, agentID string) ([]string, int, error) {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	memberships, err := tm.fetchMemberships(agentID)
	if err != nil {
		return nil, 0, err
	}

	permissionSet, maxPriority := tm.collectPermissions(memberships)
	return permissionsFromSet(permissionSet), maxPriority, nil
}

func (tm *TeamManager) fetchMemberships(agentID string) ([]AgentTeamMembership, error) {
	var memberships []AgentTeamMembership
	if err := tm.db.Where("agent_id = ?", agentID).Find(&memberships).Error; err != nil {
		return nil, fmt.Errorf("failed to get memberships: %w", err)
	}
	return memberships, nil
}

func (tm *TeamManager) collectPermissions(memberships []AgentTeamMembership) (map[string]bool, int) {
	permissionSet := make(map[string]bool)
	maxPriority := 0

	for _, membership := range memberships {
		team, err := tm.fetchTeam(membership.TeamID)
		if err != nil {
			continue
		}
		role, exists := team.Roles[membership.RoleName]
		if !exists {
			continue
		}
		for _, perm := range role.Permissions {
			permissionSet[perm] = true
		}
		if role.Priority > maxPriority {
			maxPriority = role.Priority
		}
	}

	return permissionSet, maxPriority
}

func (tm *TeamManager) fetchTeam(teamID string) (*AgentTeam, error) {
	var team AgentTeam
	if err := tm.db.First(&team, "id = ?", teamID).Error; err != nil {
		return nil, err
	}
	return &team, nil
}

func permissionsFromSet(permissionSet map[string]bool) []string {
	permissions := make([]string, 0, len(permissionSet))
	for perm := range permissionSet {
		permissions = append(permissions, perm)
	}
	return permissions
}

// HasPermission checks if an agent has a specific permission
func (tm *TeamManager) HasPermission(ctx context.Context, agentID, permission string) (bool, error) {
	permissions, _, err := tm.GetAgentPermissions(ctx, agentID)
	if err != nil {
		return false, err
	}

	for _, perm := range permissions {
		if perm == permission || perm == "*" {
			return true, nil
		}
	}

	return false, nil
}
