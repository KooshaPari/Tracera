// Package agents provides coordination primitives for agent collaboration.
package agents

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
	"fmt"
	"time"
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
func (jm JSONMap) Value() (driver.Value, error) {
	if jm == nil {
		return []byte("{}"), nil
	}
	b, err := json.Marshal(map[string]interface{}(jm))
	if err != nil {
		return nil, err
	}
	return b, nil
}

// Scan implements the sql.Scanner interface for JSONMap.
func (jm *JSONMap) Scan(value interface{}) error {
	if jm == nil {
		return errors.New("JSONMap: Scan on nil receiver")
	}

	if value == nil {
		*jm = JSONMap{}
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
		*jm = JSONMap{}
		return nil
	}

	var out map[string]interface{}
	if err := json.Unmarshal(data, &out); err != nil {
		return err
	}
	*jm = JSONMap(out)
	return nil
}

// JSONStringArray is a custom type for []string that works with SQLite
type JSONStringArray []string

// Value implements the driver.Valuer interface for JSONStringArray.
func (jsa JSONStringArray) Value() (driver.Value, error) {
	if jsa == nil {
		return []byte("[]"), nil
	}
	b, err := json.Marshal([]string(jsa))
	if err != nil {
		return nil, err
	}
	return b, nil
}

// Scan implements the sql.Scanner interface for JSONStringArray.
func (jsa *JSONStringArray) Scan(value interface{}) error {
	if jsa == nil {
		return errors.New("JSONStringArray: Scan on nil receiver")
	}

	if value == nil {
		*jsa = JSONStringArray{}
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
		*jsa = JSONStringArray{}
		return nil
	}

	var out []string
	if err := json.Unmarshal(data, &out); err != nil {
		return err
	}
	*jsa = JSONStringArray(out)
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
