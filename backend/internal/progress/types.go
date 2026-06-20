package progress

import (
	"database/sql/driver"
	"encoding/json"
	"fmt"
	"time"

	"github.com/google/uuid"
)

// MilestoneStatus represents the status of a milestone
type MilestoneStatus string

const (
	// MilestoneNotStarted indicates a milestone that has not started.
	MilestoneNotStarted MilestoneStatus = "not_started"
	// MilestoneInProgress indicates a milestone currently in progress.
	MilestoneInProgress MilestoneStatus = "in_progress"
	// MilestoneAtRisk indicates a milestone that is at risk.
	MilestoneAtRisk MilestoneStatus = "at_risk"
	// MilestoneBlocked indicates a milestone that is blocked.
	MilestoneBlocked MilestoneStatus = "blocked"
	// MilestoneCompleted indicates a milestone that is completed.
	MilestoneCompleted MilestoneStatus = "completed"
	// MilestoneCancelled indicates a milestone that is cancelled.
	MilestoneCancelled MilestoneStatus = "cancelled"
)

// HealthStatus represents the health of a milestone or sprint
type HealthStatus string

const (
	// HealthGreen indicates healthy status.
	HealthGreen HealthStatus = "green"
	// HealthYellow indicates a warning status.
	HealthYellow HealthStatus = "yellow"
	// HealthRed indicates unhealthy status.
	HealthRed HealthStatus = "red"
	// HealthUnknown indicates unknown status.
	HealthUnknown HealthStatus = "unknown"
)

// SprintStatus represents the status of a sprint
type SprintStatus string

const (
	// SprintPlanning indicates the sprint is in planning.
	SprintPlanning SprintStatus = "planning"
	// SprintActive indicates the sprint is active.
	SprintActive SprintStatus = "active"
	// SprintCompleted indicates the sprint is completed.
	SprintCompleted SprintStatus = "completed"
	// SprintCancelled indicates the sprint is cancelled.
	SprintCancelled SprintStatus = "cancelled"
)

// RiskFactor represents a risk affecting a milestone
type RiskFactor struct {
	Type                 string     `json:"type"`
	Severity             string     `json:"severity"`
	Description          string     `json:"description"`
	ItemID               *uuid.UUID `json:"item_id,omitempty"`
	MitigationSuggestion *string    `json:"mitigation_suggestion,omitempty"`
}

// Milestone represents a milestone in a project
type Milestone struct {
	ID          uuid.UUID       `db:"id"`
	ProjectID   uuid.UUID       `db:"project_id"`
	ParentID    *uuid.UUID      `db:"parent_id"`
	Name        string          `db:"name"`
	Slug        string          `db:"slug"`
	Description *string         `db:"description"`
	Objective   *string         `db:"objective"`
	StartDate   *time.Time      `db:"start_date"`
	TargetDate  time.Time       `db:"target_date"`
	ActualDate  *time.Time      `db:"actual_date"`
	Status      MilestoneStatus `db:"status"`
	Health      HealthStatus    `db:"health"`
	RiskScore   int             `db:"risk_score"`
	RiskFactors []RiskFactor    `db:"risk_factors"`
	OwnerID     *uuid.UUID      `db:"owner_id"`
	Tags        []string        `db:"tags"`
	Metadata    json.RawMessage `db:"metadata"`
	CreatedAt   time.Time       `db:"created_at"`
	UpdatedAt   time.Time       `db:"updated_at"`
	DeletedAt   *time.Time      `db:"deleted_at"`
}

// MilestoneProgress represents progress metrics for a milestone
type MilestoneProgress struct {
	TotalItems      int `json:"total_items"`
	CompletedItems  int `json:"completed_items"`
	InProgressItems int `json:"in_progress_items"`
	BlockedItems    int `json:"blocked_items"`
	NotStartedItems int `json:"not_started_items"`
	Percentage      int `json:"percentage"`
}

// Sprint represents a time-boxed work period
type Sprint struct {
	ID              uuid.UUID       `db:"id"`
	ProjectID       uuid.UUID       `db:"project_id"`
	Name            string          `db:"name"`
	Slug            string          `db:"slug"`
	Goal            *string         `db:"goal"`
	StartDate       time.Time       `db:"start_date"`
	EndDate         time.Time       `db:"end_date"`
	Status          SprintStatus    `db:"status"`
	Health          HealthStatus    `db:"health"`
	PlannedCapacity *int            `db:"planned_capacity"`
	ActualCapacity  *int            `db:"actual_capacity"`
	PlannedPoints   int             `db:"planned_points"`
	CompletedPoints int             `db:"completed_points"`
	RemainingPoints int             `db:"remaining_points"`
	AddedPoints     int             `db:"added_points"`
	RemovedPoints   int             `db:"removed_points"`
	Metadata        json.RawMessage `db:"metadata"`
	CreatedAt       time.Time       `db:"created_at"`
	UpdatedAt       time.Time       `db:"updated_at"`
	CompletedAt     *time.Time      `db:"completed_at"`
	DeletedAt       *time.Time      `db:"deleted_at"`
}

// BurndownDataPoint represents a single data point in a burndown chart
type BurndownDataPoint struct {
	RecordedDate    time.Time `db:"recorded_date"`
	RemainingPoints int       `db:"remaining_points"`
	IdealPoints     int       `db:"ideal_points"`
	CompletedPoints int       `db:"completed_points"`
	AddedPoints     int       `db:"added_points"`
}

// Snapshot represents a point-in-time snapshot of project progress.
type Snapshot struct {
	ID           uuid.UUID       `db:"id"`
	ProjectID    uuid.UUID       `db:"project_id"`
	SnapshotDate time.Time       `db:"snapshot_date"`
	Metrics      json.RawMessage `db:"metrics"`
	CreatedAt    time.Time       `db:"created_at"`
}

// ProjectMetrics contains all metrics for a project at a point in time
type ProjectMetrics struct {
	TotalItems        int            `json:"total_items"`
	ByStatus          map[string]int `json:"by_status"`
	ByPriority        map[string]int `json:"by_priority"`
	ByType            map[string]int `json:"by_type"`
	ByLifecycle       map[string]int `json:"by_lifecycle"`
	CompletedThisWeek int            `json:"completed_this_week"`
	CompletedLastWeek int            `json:"completed_last_week"`
	Velocity          float64        `json:"velocity"`
	BlockedCount      int            `json:"blocked_count"`
	AtRiskCount       int            `json:"at_risk_count"`
	OverdueCount      int            `json:"overdue_count"`
	TestCoverage      *float64       `json:"test_coverage"`
	DocCoverage       *float64       `json:"doc_coverage"`
	TraceCoverage     *float64       `json:"trace_coverage"`
	AverageCycleTime  *int           `json:"average_cycle_time"`
	AverageLeadTime   *int           `json:"average_lead_time"`
}

// VelocityDataPoint represents velocity data for a period
type VelocityDataPoint struct {
	PeriodStart     time.Time `db:"period_start"`
	PeriodEnd       time.Time `db:"period_end"`
	PeriodLabel     string    `db:"period_label"`
	PlannedPoints   int       `db:"planned_points"`
	CompletedPoints int       `db:"completed_points"`
	Velocity        int       `db:"velocity"`
}

// CreateMilestoneRequest is the request to create a milestone
type CreateMilestoneRequest struct {
	Name        string     `json:"name" validate:"required,min=1,max=255"`
	Slug        string     `json:"slug" validate:"required,min=1,max=255"`
	Description *string    `json:"description"`
	Objective   *string    `json:"objective"`
	StartDate   *time.Time `json:"start_date"`
	TargetDate  time.Time  `json:"target_date" validate:"required"`
	ParentID    *uuid.UUID `json:"parent_id"`
	OwnerID     *uuid.UUID `json:"owner_id"`
}

// UpdateMilestoneRequest is the request to update a milestone
type UpdateMilestoneRequest struct {
	Name        *string          `json:"name"`
	Slug        *string          `json:"slug"`
	Description *string          `json:"description"`
	Objective   *string          `json:"objective"`
	StartDate   *time.Time       `json:"start_date"`
	TargetDate  *time.Time       `json:"target_date"`
	Status      *MilestoneStatus `json:"status"`
	Health      *HealthStatus    `json:"health"`
	RiskScore   *int             `json:"risk_score"`
	OwnerID     *uuid.UUID       `json:"owner_id"`
}

// CreateSprintRequest is the request to create a sprint
type CreateSprintRequest struct {
	Name            string    `json:"name" validate:"required,min=1,max=255"`
	Slug            string    `json:"slug" validate:"required,min=1,max=255"`
	Goal            *string   `json:"goal"`
	StartDate       time.Time `json:"start_date" validate:"required"`
	EndDate         time.Time `json:"end_date" validate:"required"`
	PlannedCapacity *int      `json:"planned_capacity"`
	ActualCapacity  *int      `json:"actual_capacity"`
}

// UpdateSprintRequest is the request to update a sprint
type UpdateSprintRequest struct {
	Name            *string       `json:"name"`
	Slug            *string       `json:"slug"`
	Goal            *string       `json:"goal"`
	Status          *SprintStatus `json:"status"`
	Health          *HealthStatus `json:"health"`
	PlannedCapacity *int          `json:"planned_capacity"`
	ActualCapacity  *int          `json:"actual_capacity"`
	PlannedPoints   *int          `json:"planned_points"`
	CompletedPoints *int          `json:"completed_points"`
}

// RiskFactorSlice is a named type for RiskFactor slice for database operations
type RiskFactorSlice []RiskFactor

// Scan implements sql.Scanner interface for RiskFactor slice
func (rf *RiskFactorSlice) Scan(value interface{}) error {
	if value == nil {
		*rf = RiskFactorSlice{}
		return nil
	}
	b, ok := value.([]byte)
	if !ok {
		return fmt.Errorf("RiskFactorSlice.Scan: expected []byte, got %T", value)
	}
	return json.Unmarshal(b, rf)
}

// Value implements driver.Valuer interface for RiskFactor slice
func (rf RiskFactorSlice) Value() (driver.Value, error) {
	return json.Marshal(rf)
}

// StringSlice is a named type for string slice for database operations
type StringSlice []string

// Scan implements sql.Scanner interface for string slice
func (ss *StringSlice) Scan(value interface{}) error {
	if value == nil {
		*ss = StringSlice{}
		return nil
	}
	b, ok := value.([]byte)
	if !ok {
		return fmt.Errorf("StringSlice.Scan: expected []byte, got %T", value)
	}
	return json.Unmarshal(b, ss)
}

// Value implements driver.Valuer interface for string slice
func (ss StringSlice) Value() (driver.Value, error) {
	return json.Marshal(ss)
}
