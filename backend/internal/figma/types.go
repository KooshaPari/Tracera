// Package figma contains types and models for Figma integration.
package figma

import (
	"time"
)

// FileMetadata represents Figma file information
type FileMetadata struct {
	Key             string    `json:"key"`
	Name            string    `json:"name"`
	LastModified    time.Time `json:"last_modified"`
	ThumbnailURL    string    `json:"thumbnail_url,omitempty"`
	EditorType      string    `json:"editor_type,omitempty"`
	SharedPluginURL string    `json:"shared_plugin_url,omitempty"`
}

// FileResponse represents the Figma API file endpoint response
type FileResponse struct {
	Name    string                 `json:"name"`
	Role    string                 `json:"role"`
	Version string                 `json:"version"`
	Pages   []PageNode             `json:"pages"`
	Nodes   map[string]interface{} `json:"nodes"`
	Schemas map[string]interface{} `json:"schemas,omitempty"`
}

// PageNode represents a page in a Figma file
type PageNode struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

// Node represents a Figma node (component, frame, etc.)
type Node struct {
	ID                     string                     `json:"id"`
	Name                   string                     `json:"name"`
	Type                   string                     `json:"type"`
	ModifiedAt             time.Time                  `json:"modified_at,omitempty"`
	ParentID               string                     `json:"parent_id,omitempty"`
	PageID                 string                     `json:"page_id,omitempty"`
	Children               []Node                     `json:"children,omitempty"`
	ComponentSetID         string                     `json:"component_set_id,omitempty"`
	IsMainComponent        bool                       `json:"is_main_component"`
	IsComponent            bool                       `json:"is_component"`
	IsAsset                bool                       `json:"is_asset"`
	Description            string                     `json:"description,omitempty"`
	DocumentationLinks     []DocumentationLink        `json:"documentation_links,omitempty"`
	Properties             map[string]interface{}     `json:"properties,omitempty"`
	VariantGroupProperties map[string]VariantProperty `json:"variant_group_properties,omitempty"`
}

// DocumentationLink represents documentation attached to a component
type DocumentationLink struct {
	URI string `json:"uri"`
}

// VariantProperty represents a variant property of a component
type VariantProperty struct {
	Type    string            `json:"type"`
	Default string            `json:"default"`
	Options []string          `json:"options"`
	Values  map[string]string `json:"values,omitempty"`
}

// ImageExportResponse represents the response from Figma's image export endpoint
type ImageExportResponse struct {
	Images map[string]string `json:"images"`
	Err    string            `json:"err,omitempty"`
}

// ExportFormat represents export settings for images
type ExportFormat string

const (
	// ExportFormatJPG exports images as JPEG.
	ExportFormatJPG ExportFormat = "jpg"
	// ExportFormatPNG exports images as PNG.
	ExportFormatPNG ExportFormat = "png"
	// ExportFormatSVG exports images as SVG.
	ExportFormatSVG ExportFormat = "svg"
	// ExportFormatPDF exports images as PDF.
	ExportFormatPDF ExportFormat = "pdf"
)

// ExportSettings represents image export settings
type ExportSettings struct {
	Format               ExportFormat
	Scale                float64
	SVGIncludeID         bool
	SVGSimplifyStroke    bool
	SVGUseAbsoluteBounds bool
	PDFIncludeID         bool
}

// SyncStatus represents the status of a Figma sync
type SyncStatus string

const (
	// SyncStatusUnlinked indicates no sync relationship exists.
	SyncStatusUnlinked SyncStatus = "unlinked"
	// SyncStatusSynced indicates the sync is up to date.
	SyncStatusSynced SyncStatus = "synced"
	// SyncStatusOutdated indicates the sync is behind changes.
	SyncStatusOutdated SyncStatus = "outdated"
	// SyncStatusConflict indicates a sync conflict.
	SyncStatusConflict SyncStatus = "conflict"
	// SyncStatusPending indicates the sync is pending.
	SyncStatusPending SyncStatus = "pending"
)

// SyncDirection represents the direction of synchronization
type SyncDirection string

const (
	// SyncDirectionFigmaToCode syncs from Figma to code.
	SyncDirectionFigmaToCode SyncDirection = "figma_to_code"
	// SyncDirectionCodeToFigma syncs from code to Figma.
	SyncDirectionCodeToFigma SyncDirection = "code_to_figma"
	// SyncDirectionBidirectional syncs in both directions.
	SyncDirectionBidirectional SyncDirection = "bidirectional"
)

// SyncState represents the synchronization state between Figma and code.
type SyncState struct {
	ID                 string                 `json:"id"`
	ProjectID          string                 `json:"project_id"`
	ItemID             *string                `json:"item_id,omitempty"`
	ComponentID        *string                `json:"component_id,omitempty"`
	FileKey            string                 `json:"file_key"`
	PageName           *string                `json:"page_name,omitempty"`
	NodeID             string                 `json:"node_id"`
	NodeName           *string                `json:"node_name,omitempty"`
	FigmaURL           *string                `json:"figma_url,omitempty"`
	NodeType           *string                `json:"node_type,omitempty"`
	SyncStatus         SyncStatus             `json:"sync_status"`
	SyncDirection      *SyncDirection         `json:"sync_direction,omitempty"`
	LastSyncedAt       *time.Time             `json:"last_synced_at,omitempty"`
	FigmaModifiedAt    *time.Time             `json:"figma_modified_at,omitempty"`
	CodeModifiedAt     *time.Time             `json:"code_modified_at,omitempty"`
	FigmaVersion       *string                `json:"figma_version,omitempty"`
	CodeVersion        *string                `json:"code_version,omitempty"`
	SyncMetadata       map[string]interface{} `json:"sync_metadata,omitempty"`
	HasConflict        bool                   `json:"has_conflict"`
	ConflictDetails    *string                `json:"conflict_details,omitempty"`
	CodeConnectEnabled bool                   `json:"code_connect_enabled"`
	CodeConnectURL     *string                `json:"code_connect_url,omitempty"`
	Metadata           map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt          time.Time              `json:"created_at"`
	UpdatedAt          time.Time              `json:"updated_at"`
}

// SyncComparison represents the result of comparing Figma and code versions
type SyncComparison struct {
	NodeID          string
	FigmaModified   time.Time
	CodeModified    time.Time
	IsSynced        bool
	IsOutdated      bool
	HasConflict     bool
	ConflictDetails string
}

// ClientConfig represents configuration for the Figma API client
type ClientConfig struct {
	Token           string
	BaseURL         string
	Timeout         time.Duration
	RateLimit       int
	RateLimitWindow time.Duration
}

// SyncConfig represents configuration for the sync service
type SyncConfig struct {
	Enabled            bool
	IntervalMinutes    int
	ConflictResolution string // "manual", "figma_priority", "code_priority"
	AutoSyncComponents bool
	TrackVariants      bool
	ExportImages       bool
	MaxConcurrentSyncs int
}

// ComponentVariant represents a variant of a component
type ComponentVariant struct {
	ID          string
	Name        string
	Properties  map[string]string
	Description string
}

// LibraryComponent represents a component in the design library
type LibraryComponent struct {
	ID           string
	ProjectID    string
	FigmaNodeID  string
	Name         string
	Description  string
	Category     string
	Variants     []ComponentVariant
	Properties   map[string]interface{}
	ThumbnailURL string
	CreatedAt    time.Time
	UpdatedAt    time.Time
}
