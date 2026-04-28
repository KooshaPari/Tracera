package agents

import (
	"time"
)

// Distributed operation status constants
const (
	statusInProgress = "in_progress"
	statusReady      = "ready"
	statusWorking    = "working"
	statusResolved   = "resolved"
)

// DistributedOperation represents a coordinated operation across multiple agents
type DistributedOperation struct {
	ID             string          `json:"id" gorm:"primaryKey"`
	ProjectID      string          `json:"project_id" gorm:"index:idx_operation_project"`
	Type           string          `json:"type"`   // batch_update, coordinated_analysis, multi_agent_task
	Status         string          `json:"status"` // pending, in_progress, completed, failed
	ParticipantIDs JSONStringArray `json:"participant_i_ds" gorm:"type:text"`
	CoordinatorID  string          `json:"coordinator_id"`
	TargetItems    JSONStringArray `json:"target_items" gorm:"type:text"`
	OperationData  JSONMap         `json:"operation_data" gorm:"type:text"`
	StartedAt      *time.Time      `json:"started_at,omitempty"`
	CompletedAt    *time.Time      `json:"completed_at,omitempty"`
	CreatedAt      time.Time       `json:"created_at"`
	UpdatedAt      time.Time       `json:"updated_at"`
}

// OperationParticipant tracks individual agent participation in distributed operations
type OperationParticipant struct {
	ID            string          `json:"id" gorm:"primaryKey"`
	OperationID   string          `json:"operation_id" gorm:"index:idx_participant_operation"`
	AgentID       string          `json:"agent_id" gorm:"index:idx_participant_agent"`
	Status        string          `json:"status"` // ready, working, completed, failed
	AssignedItems JSONStringArray `json:"assigned_items" gorm:"type:text"`
	Result        JSONMap         `json:"result" gorm:"type:text"`
	Error         string          `json:"error,omitempty"`
	StartedAt     *time.Time      `json:"started_at,omitempty"`
	CompletedAt   *time.Time      `json:"completed_at,omitempty"`
	CreatedAt     time.Time       `json:"created_at"`
	UpdatedAt     time.Time       `json:"updated_at"`
}
