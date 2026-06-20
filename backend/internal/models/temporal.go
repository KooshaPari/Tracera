package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// VersionBranch represents a version control branch for managing parallel development
type VersionBranch struct {
	ID          string  `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ProjectID   string  `gorm:"column:project_id;type:uuid;not null" json:"project_id"`
	Name        string  `gorm:"column:name;size:255;not null" json:"name"`
	Slug        string  `gorm:"column:slug;size:255;not null" json:"slug"`
	Description *string `gorm:"column:description;type:text" json:"description,omitempty"`
	// BranchType: main, release, feature, experiment, hotfix, archive
	BranchType     string  `gorm:"column:branch_type;size:50;not null;default:'feature'" json:"branch_type"`
	ParentBranchID *string `gorm:"column:parent_branch_id;type:uuid" json:"parent_branch_id,omitempty"`
	BaseVersionID  *string `gorm:"column:base_version_id;type:uuid" json:"base_version_id,omitempty"`
	// Status: active, review, merged, abandoned, archived
	Status       string         `gorm:"column:status;size:50;not null;default:'active'" json:"status"`
	IsDefault    bool           `gorm:"column:is_default;not null;default:false" json:"is_default"`
	IsProtected  bool           `gorm:"column:is_protected;not null;default:false" json:"is_protected"`
	MergedAt     *time.Time     `gorm:"column:merged_at" json:"merged_at,omitempty"`
	MergedInto   *string        `gorm:"column:merged_into;type:uuid" json:"merged_into,omitempty"`
	MergedBy     *string        `gorm:"column:merged_by;size:255" json:"merged_by,omitempty"`
	VersionCount int            `gorm:"column:version_count;not null;default:0" json:"version_count"`
	ItemCount    int            `gorm:"column:item_count;not null;default:0" json:"item_count"`
	Metadata     datatypes.JSON `gorm:"column:metadata;type:jsonb;default:'{}'" json:"metadata"`
	CreatedBy    string         `gorm:"column:created_by;size:255;not null" json:"created_by"`
	CreatedAt    time.Time      `gorm:"column:created_at;not null;autoCreateTime" json:"created_at"`
	UpdatedAt    time.Time      `gorm:"column:updated_at;not null;autoUpdateTime" json:"updated_at"`

	// Relationships
	Project      *Project       `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
	ParentBranch *VersionBranch `gorm:"foreignKey:ParentBranchID;references:ID" json:"parent_branch,omitempty"`
}

// TableName overrides GORM table name
func (VersionBranch) TableName() string {
	return "version_branches"
}

// BeforeCreate generates UUID for ID if not set
func (vb *VersionBranch) BeforeCreate(_ *gorm.DB) error {
	if vb.ID == "" {
		vb.ID = uuid.New().String()
	}
	return nil
}

// Version represents a snapshot/commit in a version branch
type Version struct {
	ID              string  `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	BranchID        string  `gorm:"column:branch_id;type:uuid;not null" json:"branch_id"`
	ProjectID       string  `gorm:"column:project_id;type:uuid;not null" json:"project_id"`
	VersionNumber   int     `gorm:"column:version_number;not null" json:"version_number"`
	ParentVersionID *string `gorm:"column:parent_version_id;type:uuid" json:"parent_version_id,omitempty"`
	SnapshotID      *string `gorm:"column:snapshot_id;type:uuid" json:"snapshot_id,omitempty"`
	ChangesetID     *string `gorm:"column:changeset_id;type:uuid" json:"changeset_id,omitempty"`
	Tag             *string `gorm:"column:tag;size:255" json:"tag,omitempty"`
	Message         string  `gorm:"column:message;type:text;not null" json:"message"`
	ItemCount       int     `gorm:"column:item_count;not null;default:0" json:"item_count"`
	ChangeCount     int     `gorm:"column:change_count;not null;default:0" json:"change_count"`
	// Status: draft, pending_review, approved, rejected, superseded
	Status          string         `gorm:"column:status;size:50;not null;default:'draft'" json:"status"`
	ApprovedBy      *string        `gorm:"column:approved_by;size:255" json:"approved_by,omitempty"`
	ApprovedAt      *time.Time     `gorm:"column:approved_at" json:"approved_at,omitempty"`
	RejectionReason *string        `gorm:"column:rejection_reason;type:text" json:"rejection_reason,omitempty"`
	Metadata        datatypes.JSON `gorm:"column:metadata;type:jsonb;default:'{}'" json:"metadata"`
	CreatedBy       string         `gorm:"column:created_by;size:255;not null" json:"created_by"`
	CreatedAt       time.Time      `gorm:"column:created_at;not null;autoCreateTime" json:"created_at"`

	// Relationships
	Branch        *VersionBranch `gorm:"foreignKey:BranchID;references:ID" json:"branch,omitempty"`
	Project       *Project       `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
	ParentVersion *Version       `gorm:"foreignKey:ParentVersionID;references:ID" json:"parent_version,omitempty"`
}

// TableName overrides GORM table name
func (Version) TableName() string {
	return "versions"
}

// BeforeCreate generates UUID for ID if not set
func (v *Version) BeforeCreate(_ *gorm.DB) error {
	if v.ID == "" {
		v.ID = uuid.New().String()
	}
	return nil
}

// ItemVersion represents a snapshot of an item at a specific version
type ItemVersion struct {
	ID                      string         `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ItemID                  string         `gorm:"column:item_id;type:uuid;not null" json:"item_id"`
	VersionID               string         `gorm:"column:version_id;type:uuid;not null" json:"version_id"`
	BranchID                string         `gorm:"column:branch_id;type:uuid;not null" json:"branch_id"`
	ProjectID               string         `gorm:"column:project_id;type:uuid;not null" json:"project_id"`
	State                   datatypes.JSON `gorm:"column:state;type:jsonb;not null" json:"state"`
	Lifecycle               *string        `gorm:"column:lifecycle;size:50" json:"lifecycle,omitempty"`
	IntroducedInVersionID   *string        `gorm:"column:introduced_in_version_id;type:uuid" json:"introduced_in_version_id,omitempty"`
	LastModifiedInVersionID *string        `gorm:"type:uuid" json:"last_modified_in_version_id,omitempty"`
	CreatedAt               time.Time      `gorm:"column:created_at;not null;autoCreateTime" json:"created_at"`

	// Relationships
	Item    *Item          `gorm:"foreignKey:ItemID;references:ID" json:"item,omitempty"`
	Version *Version       `gorm:"foreignKey:VersionID;references:ID" json:"version,omitempty"`
	Branch  *VersionBranch `gorm:"foreignKey:BranchID;references:ID" json:"branch,omitempty"`
	Project *Project       `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
}

// TableName overrides GORM table name
func (ItemVersion) TableName() string {
	return "item_versions"
}

// BeforeCreate generates UUID for ID if not set
func (iv *ItemVersion) BeforeCreate(_ *gorm.DB) error {
	if iv.ID == "" {
		iv.ID = uuid.New().String()
	}
	return nil
}

// ItemAlternative represents alternative implementations or design choices for an item
type ItemAlternative struct {
	ID                string `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ProjectID         string `gorm:"column:project_id;type:uuid;not null" json:"project_id"`
	BaseItemID        string `gorm:"column:base_item_id;type:uuid;not null" json:"base_item_id"`
	AlternativeItemID string `gorm:"column:alternative_item_id;type:uuid;not null" json:"alternative_item_id"`
	// Relationship: alternative_to, supersedes, experiment_of
	Relationship string         `gorm:"column:relationship;size:100;not null" json:"relationship"`
	Description  *string        `gorm:"column:description;type:text" json:"description,omitempty"`
	IsChosen     bool           `gorm:"column:is_chosen;not null;default:false" json:"is_chosen"`
	ChosenAt     *time.Time     `gorm:"column:chosen_at" json:"chosen_at,omitempty"`
	ChosenBy     *string        `gorm:"column:chosen_by;size:255" json:"chosen_by,omitempty"`
	ChosenReason *string        `gorm:"column:chosen_reason;type:text" json:"chosen_reason,omitempty"`
	Metrics      datatypes.JSON `gorm:"column:metrics;type:jsonb;default:'{}'" json:"metrics"`
	CreatedAt    time.Time      `gorm:"column:created_at;not null;autoCreateTime" json:"created_at"`
	UpdatedAt    time.Time      `gorm:"column:updated_at;not null;autoUpdateTime" json:"updated_at"`

	// Relationships
	Project         *Project `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
	BaseItem        *Item    `gorm:"foreignKey:BaseItemID;references:ID" json:"base_item,omitempty"`
	AlternativeItem *Item    `gorm:"foreignKey:AlternativeItemID;references:ID" json:"alternative_item,omitempty"`
}

// TableName overrides GORM table name
func (ItemAlternative) TableName() string {
	return "item_alternatives"
}

// BeforeCreate generates UUID for ID if not set
func (ia *ItemAlternative) BeforeCreate(_ *gorm.DB) error {
	if ia.ID == "" {
		ia.ID = uuid.New().String()
	}
	return nil
}

// MergeRequest represents a request to merge one branch into another
type MergeRequest struct {
	ID              string  `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ProjectID       string  `gorm:"column:project_id;type:uuid;not null" json:"project_id"`
	SourceBranchID  string  `gorm:"column:source_branch_id;type:uuid;not null" json:"source_branch_id"`
	TargetBranchID  string  `gorm:"column:target_branch_id;type:uuid;not null" json:"target_branch_id"`
	SourceVersionID string  `gorm:"column:source_version_id;type:uuid;not null" json:"source_version_id"`
	BaseVersionID   *string `gorm:"column:base_version_id;type:uuid" json:"base_version_id,omitempty"`
	// Status: open, approved, merged, closed, conflict
	Status      string         `gorm:"column:status;size:50;not null;default:'open'" json:"status"`
	Title       string         `gorm:"column:title;size:255;not null" json:"title"`
	Description *string        `gorm:"column:description;type:text" json:"description,omitempty"`
	Diff        datatypes.JSON `gorm:"column:diff;type:jsonb;default:'{}'" json:"diff"`
	Conflicts   datatypes.JSON `gorm:"column:conflicts;type:jsonb;default:'[]'" json:"conflicts"`
	Reviewers   datatypes.JSON `gorm:"column:reviewers;type:jsonb;default:'[]'" json:"reviewers"`
	ApprovedBy  datatypes.JSON `gorm:"column:approved_by;type:jsonb;default:'[]'" json:"approved_by"`
	CreatedBy   string         `gorm:"column:created_by;size:255;not null" json:"created_by"`
	CreatedAt   time.Time      `gorm:"column:created_at;not null;autoCreateTime" json:"created_at"`
	MergedAt    *time.Time     `gorm:"column:merged_at" json:"merged_at,omitempty"`
	MergedBy    *string        `gorm:"column:merged_by;size:255" json:"merged_by,omitempty"`
	ClosedAt    *time.Time     `gorm:"column:closed_at" json:"closed_at,omitempty"`
	UpdatedAt   time.Time      `gorm:"column:updated_at;not null;autoUpdateTime" json:"updated_at"`

	// Relationships
	Project       *Project       `gorm:"foreignKey:ProjectID;references:ID" json:"project,omitempty"`
	SourceBranch  *VersionBranch `gorm:"foreignKey:SourceBranchID;references:ID" json:"source_branch,omitempty"`
	TargetBranch  *VersionBranch `gorm:"foreignKey:TargetBranchID;references:ID" json:"target_branch,omitempty"`
	SourceVersion *Version       `gorm:"foreignKey:SourceVersionID;references:ID" json:"source_version,omitempty"`
	BaseVersion   *Version       `gorm:"foreignKey:BaseVersionID;references:ID" json:"base_version,omitempty"`
}

// TableName overrides GORM table name
func (MergeRequest) TableName() string {
	return "merge_requests"
}

// BeforeCreate generates UUID for ID if not set
func (mr *MergeRequest) BeforeCreate(_ *gorm.DB) error {
	if mr.ID == "" {
		mr.ID = uuid.New().String()
	}
	return nil
}
