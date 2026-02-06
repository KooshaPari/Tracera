package storybook

import (
	"encoding/json"
	"time"
)

// Config holds configuration for Storybook client.
type Config struct {
	BaseURL        string
	TimeoutSeconds int
	MaxRetries     int
}

// StoriesResponse represents the structure of stories.json from Storybook.
type StoriesResponse struct {
	V        int                   `json:"v"`
	Stories  map[string]StoryEntry `json:"stories"`
	Docs     map[string]DocsEntry  `json:"docs"`
	Metadata Metadata              `json:"_meta"`
}

// StoryEntry represents a single story in the Storybook index.
type StoryEntry struct {
	ID               string                 `json:"id"`
	Title            string                 `json:"title"`
	Name             string                 `json:"name"`
	ImportPath       string                 `json:"importPath"`
	Args             map[string]interface{} `json:"args"`
	ArgTypes         map[string]ArgType     `json:"argTypes"`
	Parameters       map[string]interface{} `json:"parameters"`
	Globals          map[string]interface{} `json:"globals"`
	Tags             []string               `json:"tags"`
	ComponentID      string                 `json:"component_id"`
	SourceCodeSource string                 `json:"source_code_source"`
}

// DocsEntry represents a docs entry in Storybook.
type DocsEntry struct {
	ID         string                 `json:"id"`
	Title      string                 `json:"title"`
	ImportPath string                 `json:"importPath"`
	Parameters map[string]interface{} `json:"parameters"`
}

// ArgType represents an argument type definition from Storybook.
type ArgType struct {
	Name         string      `json:"name"`
	Type         *TypeInfo   `json:"type"`
	Description  string      `json:"description"`
	Required     bool        `json:"required"`
	DefaultValue interface{} `json:"defaultValue"`
	Control      *Control    `json:"control"`
	Options      []string    `json:"options"`
	Table        *TableInfo  `json:"table"`
}

// TypeInfo represents the type information for an arg.
type TypeInfo struct {
	Name      string        `json:"name"`
	Required  bool          `json:"required"`
	Value     string        `json:"value"`
	Of        []interface{} `json:"of"`
	Signature *Signature    `json:"signature"`
}

// Signature represents function signature information.
type Signature struct {
	Name   string `json:"name"`
	Type   string `json:"type"`
	Params []struct {
		Name string `json:"name"`
		Type string `json:"type"`
	} `json:"params"`
	Return string `json:"return"`
}

// Control represents the control configuration for an arg.
type Control struct {
	Type string      `json:"type"`
	Min  interface{} `json:"min"`
	Max  interface{} `json:"max"`
	Step interface{} `json:"step"`
}

// TableInfo represents table information for documentation.
type TableInfo struct {
	Type         *TypeInfo   `json:"type"`
	DefaultValue interface{} `json:"defaultValue"`
	Summary      string      `json:"summary"`
	Detail       string      `json:"detail"`
	Category     string      `json:"category"`
	Disable      bool        `json:"disable"`
}

// Metadata represents metadata about the Storybook instance.
type Metadata struct {
	ConfigDir        string                     `json:"configDir"`
	StoriesDir       string                     `json:"storiesDir"`
	OutputDir        string                     `json:"outputDir"`
	CustomDir        string                     `json:"customDir"`
	Version          string                     `json:"version"`
	GeneratedAt      int64                      `json:"generatedAt"`
	HasCustomDir     bool                       `json:"hasCustomDir"`
	HasStaticDir     bool                       `json:"hasStaticDir"`
	HasDocumentation bool                       `json:"hasDocumentation"`
	WallFileNames    []string                   `json:"wallFileNames"`
	Refs             map[string]json.RawMessage `json:"refs"`
}

// LibraryComponent represents a component in the library.
type LibraryComponent struct {
	ID            string          `json:"id" gorm:"primaryKey"`
	ProjectID     string          `json:"project_id" gorm:"index"`
	Name          string          `json:"name" gorm:"index"`
	Title         string          `json:"title"`
	Description   string          `json:"description"`
	Category      string          `json:"category"`
	SourceFile    string          `json:"source_file"`
	StorybookPath string          `json:"storybook_path"`
	Props         json.RawMessage `json:"props"`
	Variants      json.RawMessage `json:"variants"`
	Dependencies  json.RawMessage `json:"dependencies"`
	Screenshots   json.RawMessage `json:"screenshots"`
	Documentation string          `json:"documentation"`
	Tags          json.RawMessage `json:"tags"`
	Metadata      json.RawMessage `json:"metadata"`
	LastSyncedAt  time.Time       `json:"last_synced_at"`
	CreatedAt     time.Time       `json:"created_at"`
	UpdatedAt     time.Time       `json:"updated_at"`
}

// ComponentVariant represents a single variant of a component.
type ComponentVariant struct {
	ID            string                 `json:"id"`
	ComponentID   string                 `json:"component_id"`
	Name          string                 `json:"name"`
	Title         string                 `json:"title"`
	StorybookID   string                 `json:"storybook_id"`
	Args          map[string]interface{} `json:"args"`
	ScreenshotURL string                 `json:"screenshot_url"`
	Description   string                 `json:"description"`
	CreatedAt     time.Time              `json:"created_at"`
	UpdatedAt     time.Time              `json:"updated_at"`
}

// PropSchema represents the schema for a component prop.
type PropSchema struct {
	Name         string      `json:"name"`
	Type         string      `json:"type"`
	Description  string      `json:"description"`
	Required     bool        `json:"required"`
	DefaultValue interface{} `json:"default_value"`
	Options      []string    `json:"options"`
	Category     string      `json:"category"`
}

// ComponentExtraction holds extracted component information.
type ComponentExtraction struct {
	ComponentName string             `json:"component_name"`
	Title         string             `json:"title"`
	Description   string             `json:"description"`
	Props         []PropSchema       `json:"props"`
	Variants      []ComponentVariant `json:"variants"`
	Dependencies  []string           `json:"dependencies"`
	Category      string             `json:"category"`
	SourceFile    string             `json:"source_file"`
	StorybookPath string             `json:"storybook_path"`
	Tags          []string           `json:"tags"`
	ExportedAt    time.Time          `json:"exported_at"`
}

// SyncResult holds the result of a sync operation.
type SyncResult struct {
	TotalStories      int                `json:"total_stories"`
	CreatedComponents int                `json:"created_components"`
	UpdatedComponents int                `json:"updated_components"`
	FailedComponents  int                `json:"failed_components"`
	Components        []LibraryComponent `json:"components"`
	Errors            []SyncError        `json:"errors"`
	StartTime         time.Time          `json:"start_time"`
	EndTime           time.Time          `json:"end_time"`
}

// SyncError represents an error encountered during sync.
type SyncError struct {
	ComponentName string    `json:"component_name"`
	Message       string    `json:"message"`
	Timestamp     time.Time `json:"timestamp"`
}

// ComponentLibraryIndexRequest is the request to index components from Storybook.
type ComponentLibraryIndexRequest struct {
	ProjectID          string   `json:"project_id"`
	StorybookBaseURL   string   `json:"storybook_base_url"`
	IncludeScreenshots bool     `json:"include_screenshots"`
	Categories         []string `json:"categories"`
	Tags               []string `json:"tags"`
}
