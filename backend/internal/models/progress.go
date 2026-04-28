package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// Milestone represents a project milestone with hierarchical structure
type Milestone struct {
	ID          string         `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ProjectID   string         `gorm:"column:project_id;type:uuid;not null;index:idx_milestones_project_id" json:"project_id"`
	ParentID    *string        `gorm:"column:parent_id;type:uuid;index:idx_milestones_parent_id" json:"parent_id,omitempty"`
	Name        string         `gorm:"column:name;size:255;not null" json:"name"`
	Slug        string         `gorm:"column:slug;size:255;not null;index:idx_milestones_slug,composite:project_id" json:"slug"`
	Description *string        `gorm:"column:description;type:text" json:"description,omitempty"`
	Objective   *string        `gorm:"column:objective;type:text" json:"objective,omitempty"`
	StartDate   *time.Time     `gorm:"column:start_date" json:"start_date,omitempty"`
	TargetDate  time.Time      `gorm:"column:target_date;not null;index:idx_milestones_target_date" json:"target_date"`
	ActualDate  *time.Time     `gorm:"column:actual_date" json:"actual_date,omitempty"`
	Status      string         `gorm:"column:status;size:50;not null;default:'not_started';index:idx_milestones_status" json:"status"`
	Health      string         `gorm:"column:health;size:20;not null;default:'unknown'" json:"health"`
	RiskScore   int            `gorm:"column:risk_score;not null;default:0" json:"risk_score"`
	RiskFactors datatypes.JSON `gorm:"column:risk_factors;type:jsonb;default:'[]'" json:"risk_factors"`
	OwnerID     *string        `gorm:"column:owner_id;type:uuid;index:idx_milestones_owner_id" json:"owner_id,omitempty"`
	Tags        datatypes.JSON `gorm:"column:tags;type:jsonb;default:'[]'" json:"tags"`
	Metadata    datatypes.JSON `gorm:"column:metadata;type:jsonb;default:'{}'" json:"metadata"`
	CreatedAt   time.Time      `gorm:"column:created_at;not null;default:now()" json:"created_at"`
	UpdatedAt   time.Time      `gorm:"column:updated_at;not null;default:now()" json:"updated_at"`
	DeletedAt   *time.Time     `gorm:"column:deleted_at;index" json:"deleted_at,omitempty"`

	// Relationships (not in SQL but for GORM)
	Project  *Project    `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
	Parent   *Milestone  `gorm:"foreignKey:ParentID;references:ID" json:"parent,omitempty"`
	Owner    *Profile    `gorm:"foreignKey:OwnerID;references:ID" json:"owner,omitempty"`
	Children []Milestone `gorm:"foreignKey:ParentID;references:ID" json:"children,omitempty"`
	Items    []Item      `gorm:"many2many:milestone_items" json:"items,omitempty"`
}

// TableName specifies the table name for Milestone
func (Milestone) TableName() string {
	return "milestones"
}

// BeforeCreate hook to generate UUID
func (m *Milestone) BeforeCreate(_ *gorm.DB) error {
	if m.ID == "" {
		m.ID = uuid.New().String()
	}
	return nil
}

// MilestoneItem represents the join table between milestones and items
type MilestoneItem struct {
	MilestoneID string    `gorm:"column:milestone_id;primaryKey;type:uuid" json:"milestone_id"`
	ItemID      string    `gorm:"column:item_id;primaryKey;type:uuid;index:idx_milestone_items_item_id" json:"item_id"`
	CreatedAt   time.Time `gorm:"column:created_at;not null;default:now()" json:"created_at"`

	// Relationships
	Milestone *Milestone `gorm:"foreignKey:MilestoneID;references:ID" json:"milestone,omitempty"`
	Item      *Item      `gorm:"foreignKey:ItemID;references:ID" json:"item,omitempty"`
}

// TableName specifies the table name for MilestoneItem
func (MilestoneItem) TableName() string {
	return "milestone_items"
}

// Sprint represents an agile sprint
type Sprint struct {
	ID              string         `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ProjectID       string         `gorm:"column:project_id;type:uuid;not null;index:idx_sprints_project_id" json:"project_id"`
	Name            string         `gorm:"column:name;size:255;not null" json:"name"`
	Slug            string         `gorm:"column:slug;size:255;not null;index:idx_sprints_slug,composite:project_id" json:"slug"`
	Goal            *string        `gorm:"column:goal;type:text" json:"goal,omitempty"`
	StartDate       time.Time      `gorm:"column:start_date;not null;index:idx_sprints_start_date" json:"start_date"`
	EndDate         time.Time      `gorm:"column:end_date;not null" json:"end_date"`
	Status          string         `gorm:"column:status;size:50;not null;default:'planning';index:idx_sprints_status" json:"status"`
	Health          string         `gorm:"column:health;size:20;not null;default:'unknown'" json:"health"`
	PlannedCapacity *int           `gorm:"column:planned_capacity" json:"planned_capacity,omitempty"`
	ActualCapacity  *int           `gorm:"column:actual_capacity" json:"actual_capacity,omitempty"`
	PlannedPoints   int            `gorm:"column:planned_points;not null;default:0" json:"planned_points"`
	CompletedPoints int            `gorm:"column:completed_points;not null;default:0" json:"completed_points"`
	RemainingPoints int            `gorm:"column:remaining_points;not null;default:0" json:"remaining_points"`
	AddedPoints     int            `gorm:"column:added_points;not null;default:0" json:"added_points"`
	RemovedPoints   int            `gorm:"column:removed_points;not null;default:0" json:"removed_points"`
	Metadata        datatypes.JSON `gorm:"column:metadata;type:jsonb;default:'{}'" json:"metadata"`
	CreatedAt       time.Time      `gorm:"column:created_at;not null;default:now()" json:"created_at"`
	UpdatedAt       time.Time      `gorm:"column:updated_at;not null;default:now()" json:"updated_at"`
	CompletedAt     *time.Time     `gorm:"column:completed_at" json:"completed_at,omitempty"`
	DeletedAt       *time.Time     `gorm:"column:deleted_at;index" json:"deleted_at,omitempty"`

	// Relationships
	Project      *Project       `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
	Items        []Item         `gorm:"many2many:sprint_items" json:"items,omitempty"`
	BurndownData []BurndownData `gorm:"foreignKey:SprintID;references:ID" json:"burndown_data,omitempty"`
}

// TableName specifies the table name for Sprint
func (Sprint) TableName() string {
	return "sprints"
}

// BeforeCreate hook to generate UUID
func (s *Sprint) BeforeCreate(_ *gorm.DB) error {
	if s.ID == "" {
		s.ID = uuid.New().String()
	}
	return nil
}

// SprintItem represents the join table between sprints and items
type SprintItem struct {
	SprintID  string    `gorm:"column:sprint_id;primaryKey;type:uuid" json:"sprint_id"`
	ItemID    string    `gorm:"column:item_id;primaryKey;type:uuid;index:idx_sprint_items_item_id" json:"item_id"`
	CreatedAt time.Time `gorm:"column:created_at;not null;default:now()" json:"created_at"`

	// Relationships
	Sprint *Sprint `gorm:"foreignKey:SprintID;references:ID" json:"sprint,omitempty"`
	Item   *Item   `gorm:"foreignKey:ItemID;references:ID" json:"item,omitempty"`
}

// TableName specifies the table name for SprintItem
func (SprintItem) TableName() string {
	return "sprint_items"
}

// BurndownData represents daily burndown data for a sprint
type BurndownData struct {
	ID              string    `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	SprintID        string    `gorm:"column:sprint_id;type:uuid;not null;index:idx_bd_sprint" json:"sprint_id"`
	RecordedDate    time.Time `gorm:"column:recorded_date;not null" json:"recorded_date"`
	RemainingPoints int       `gorm:"column:remaining_points;not null" json:"remaining_points"`
	IdealPoints     int       `gorm:"column:ideal_points;not null" json:"ideal_points"`
	CompletedPoints int       `gorm:"column:completed_points;not null" json:"completed_points"`
	AddedPoints     *int      `gorm:"column:added_points;default:0" json:"added_points,omitempty"`
	CreatedAt       time.Time `gorm:"column:created_at;not null;default:now()" json:"created_at"`

	// Relationships
	Sprint *Sprint `gorm:"foreignKey:SprintID;references:ID" json:"sprint,omitempty"`
}

// TableName specifies the table name for BurndownData
func (BurndownData) TableName() string {
	return "burndown_data"
}

// BeforeCreate hook to generate UUID
func (b *BurndownData) BeforeCreate(_ *gorm.DB) error {
	if b.ID == "" {
		b.ID = uuid.New().String()
	}
	return nil
}

// ProgressSnapshot represents a point-in-time snapshot of project metrics
type ProgressSnapshot struct {
	ID           string         `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ProjectID    string         `gorm:"column:project_id;type:uuid;not null;index:idx_ps_proj" json:"project_id"`
	SnapshotDate time.Time      `gorm:"column:snapshot_date;not null;index:idx_ps_date" json:"snapshot_date"`
	Metrics      datatypes.JSON `gorm:"column:metrics;type:jsonb;not null" json:"metrics"`
	CreatedAt    time.Time      `gorm:"column:created_at;not null;default:now()" json:"created_at"`

	// Relationships
	Project *Project `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
}

// TableName specifies the table name for ProgressSnapshot
func (ProgressSnapshot) TableName() string {
	return "progress_snapshots"
}

// BeforeCreate hook to generate UUID
func (p *ProgressSnapshot) BeforeCreate(_ *gorm.DB) error {
	if p.ID == "" {
		p.ID = uuid.New().String()
	}
	return nil
}

// VelocityHistory represents historical velocity data for a project
type VelocityHistory struct {
	ID              string    `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ProjectID       string    `gorm:"column:project_id;type:uuid;not null;index:idx_vh_proj" json:"project_id"`
	PeriodStart     time.Time `gorm:"column:period_start;not null" json:"period_start"`
	PeriodEnd       time.Time `gorm:"column:period_end;not null" json:"period_end"`
	PeriodLabel     string    `gorm:"column:period_label;size:255;not null" json:"period_label"`
	PlannedPoints   int       `gorm:"column:planned_points;not null" json:"planned_points"`
	CompletedPoints int       `gorm:"column:completed_points;not null" json:"completed_points"`
	Velocity        int       `gorm:"column:velocity;not null" json:"velocity"`
	CreatedAt       time.Time `gorm:"column:created_at;not null;default:now()" json:"created_at"`

	// Relationships
	Project *Project `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
}

// TableName specifies the table name for VelocityHistory
func (VelocityHistory) TableName() string {
	return "velocity_history"
}

// BeforeCreate hook to generate UUID
func (v *VelocityHistory) BeforeCreate(_ *gorm.DB) error {
	if v.ID == "" {
		v.ID = uuid.New().String()
	}
	return nil
}

// MilestoneDependency represents dependencies between milestones
type MilestoneDependency struct {
	DependentID      string    `gorm:"column:dependent_id;primaryKey;type:uuid" json:"dependent_id"`
	DependencyID     string    `gorm:"column:dependency_id;primaryKey;type:uuid;index:idx_md_dep" json:"dependency_id"`
	RelationshipType string    `gorm:"column:relationship_type;size:50;not null" json:"relationship_type"`
	CreatedAt        time.Time `gorm:"column:created_at;not null;default:now()" json:"created_at"`

	// Relationships
	Dependent  *Milestone `gorm:"foreignKey:DependentID;references:ID" json:"dependent,omitempty"`
	Dependency *Milestone `gorm:"foreignKey:DependencyID;references:ID" json:"dependency,omitempty"`
}

// TableName specifies the table name for MilestoneDependency
func (MilestoneDependency) TableName() string {
	return "milestone_dependencies"
}
