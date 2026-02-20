package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// Priority constants for items
type Priority int32

// Priority levels for items
const (
	PriorityLow      Priority = 1
	PriorityMedium   Priority = 2
	PriorityHigh     Priority = 3
	PriorityCritical Priority = 4
)

// PriorityLabel returns a string label for stats/display (e.g. 1 -> "low").
func PriorityLabel(p Priority) string {
	switch p {
	case PriorityLow:
		return "low"
	case PriorityMedium:
		return "medium"
	case PriorityHigh:
		return "high"
	case PriorityCritical:
		return "critical"
	default:
		return ""
	}
}

// Item represents a requirement/feature/task in the system
type Item struct {
	ID          string         `gorm:"primaryKey" json:"id"`
	ProjectID   string         `json:"project_id"`
	Title       string         `json:"title"`
	Description string         `json:"description"`
	Type        string         `json:"type"` // feature, task, bug, etc.
	Status      string         `json:"status"`
	Priority    Priority       `gorm:"column:priority;default:50" json:"priority"`
	PositionX   *float64       `gorm:"column:position_x" json:"position_x,omitempty"` // X coordinate for graph layout
	PositionY   *float64       `gorm:"column:position_y" json:"position_y,omitempty"` // Y coordinate for graph layout
	Metadata    datatypes.JSON `json:"metadata"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   *time.Time     `json:"deleted_at,omitempty"`
}

// Link represents a relationship between items
type Link struct {
	ID        string         `gorm:"primaryKey" json:"id"`
	SourceID  string         `json:"source_id"`
	TargetID  string         `json:"target_id"`
	Type      string         `json:"type"` // depends_on, implements, tests, etc.
	Metadata  datatypes.JSON `json:"metadata"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
}

// Project represents a project
type Project struct {
	ID          string         `gorm:"primaryKey" json:"id"`
	Name        string         `json:"name"`
	Description string         `json:"description"`
	Metadata    datatypes.JSON `json:"metadata"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   *time.Time     `json:"deleted_at,omitempty"`
}

// Agent represents an AI agent
type Agent struct {
	ID             string         `gorm:"column:id;primaryKey;type:uuid" json:"id"`
	ProjectID      string         `gorm:"column:project_id;type:uuid;not null" json:"project_id"`
	Name           string         `gorm:"column:name;size:255;not null" json:"name"`
	Status         string         `gorm:"column:status;size:50;default:'active'" json:"status"` // active, idle, error
	Metadata       datatypes.JSON `gorm:"column:metadata;type:jsonb;default:'{}'" json:"metadata"`
	LastActivityAt *time.Time     `gorm:"column:last_activity_at" json:"last_activity_at,omitempty"`
	CreatedAt      time.Time      `gorm:"column:created_at;autoCreateTime" json:"created_at"`
	UpdatedAt      time.Time      `gorm:"column:updated_at;autoUpdateTime" json:"updated_at"`
	DeletedAt      *time.Time     `gorm:"column:deleted_at" json:"deleted_at,omitempty"`
}

// BeforeCreate hook to generate UUID (signature must be BeforeCreate(*gorm.DB) error for GORM)
func (i *Item) BeforeCreate(_ *gorm.DB) error {
	if i.ID == "" {
		i.ID = uuid.New().String()
	}
	return nil
}

// BeforeCreate generates a UUID for Link.ID if not set.
func (l *Link) BeforeCreate(_ *gorm.DB) error {
	if l.ID == "" {
		l.ID = uuid.New().String()
	}
	return nil
}

// BeforeCreate generates a UUID for Project.ID if not set.
func (p *Project) BeforeCreate(_ *gorm.DB) error {
	if p.ID == "" {
		p.ID = uuid.New().String()
	}
	return nil
}

// BeforeCreate generates a UUID for Agent.ID if not set.
func (a *Agent) BeforeCreate(_ *gorm.DB) error {
	if a.ID == "" {
		a.ID = uuid.New().String()
	}
	return nil
}

// View represents a view configuration for displaying items
type View struct {
	ID        string    `gorm:"primaryKey" json:"id"`
	ProjectID string    `json:"project_id"`
	Name      string    `json:"name"`
	Type      string    `json:"type"`   // kanban, timeline, matrix, graph
	Config    string    `json:"config"` // JSON configuration
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// BeforeCreate generates a UUID for View.ID if not set.
func (v *View) BeforeCreate(_ *gorm.DB) error {
	if v.ID == "" {
		v.ID = uuid.New().String()
	}
	return nil
}

// ViewStats contains statistics for a view
type ViewStats struct {
	ViewID    string    `json:"view_id"`
	ItemCount int64     `json:"item_count"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Profile represents a user profile synced from WorkOS (public.profiles)
// Owned by GORM: schema is created/updated via AutoMigrate, not Alembic.
type Profile struct {
	ID           string         `gorm:"column:id;primaryKey" json:"id"`
	AuthID       *string        `gorm:"column:auth_id" json:"auth_id,omitempty"`
	WorkosUserID string         `gorm:"column:workos_user_id;uniqueIndex;not null" json:"workos_user_id"`
	WorkosOrgID  string         `gorm:"column:workos_org_id" json:"workos_org_id"`
	Email        string         `gorm:"column:email;not null" json:"email"`
	FullName     string         `gorm:"column:full_name" json:"full_name"`
	AvatarURL    string         `gorm:"column:avatar_url" json:"avatar_url"`
	WorkosIDs    datatypes.JSON `gorm:"column:workos_ids" json:"workos_ids,omitempty"`
	Metadata     datatypes.JSON `gorm:"column:metadata" json:"metadata,omitempty"`
	CreatedAt    time.Time      `gorm:"column:created_at;autoCreateTime" json:"created_at"`
	UpdatedAt    time.Time      `gorm:"column:updated_at;autoUpdateTime" json:"updated_at"`
	DeletedAt    *time.Time     `gorm:"column:deleted_at;index" json:"deleted_at,omitempty"`
}

// TableName overrides GORM table name to public.profiles
func (Profile) TableName() string {
	return "profiles"
}

// BeforeCreate generates UUID for ID if not set
func (p *Profile) BeforeCreate(_ *gorm.DB) error {
	if p.ID == "" {
		p.ID = uuid.New().String()
	}
	return nil
}
