package models

import (
	"time"

	"github.com/google/uuid"
	"github.com/lib/pq"
	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// Documentation represents a parsed documentation entry
type Documentation struct {
	ID        string  `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	ProjectID string  `gorm:"type:uuid;not null;index:idx_documentation_project_id" json:"project_id"`
	Title     string  `gorm:"size:512;not null" json:"title"`
	Slug      *string `gorm:"size:512;index:idx_documentation_slug,composite:project_slug" json:"slug,omitempty"`
	// Format: markdown, rst, html, plaintext
	Format          string         `gorm:"size:50;not null;index:idx_documentation_format" json:"format"`
	Content         string         `gorm:"type:text;not null" json:"content"`
	Summary         *string        `gorm:"type:text" json:"summary,omitempty"`
	ParsedStructure datatypes.JSON `gorm:"type:jsonb;default:'{}'" json:"parsed_structure"`
	Tags            pq.StringArray `gorm:"type:text[];default:'{}';index:idx_documentation_tags,type:gin" json:"tags"`
	Version         int            `gorm:"default:1" json:"version"`
	SourceURL       *string        `gorm:"type:text" json:"source_url,omitempty"`                                    // if parsed from URL
	FilePath        *string        `gorm:"type:text" json:"file_path,omitempty"`                                     // if parsed from file
	FullTextSearch  *string        `gorm:"type:tsvector;index:idx_documentation_full_text_search,type:gin" json:"-"` // for full-text search
	Metadata        datatypes.JSON `gorm:"type:jsonb;default:'{}'" json:"metadata"`
	CreatedBy       *string        `gorm:"type:uuid" json:"created_by,omitempty"`
	CreatedAt       time.Time      `gorm:"not null;default:now();index:idx_documentation_created_at" json:"created_at"`
	UpdatedAt       time.Time      `gorm:"not null;default:now()" json:"updated_at"`
	DeletedAt       *time.Time     `json:"deleted_at,omitempty"`
}

// BeforeCreate hook to generate UUID
func (d *Documentation) BeforeCreate(_ *gorm.DB) error {
	if d.ID == "" {
		d.ID = uuid.New().String()
	}
	return nil
}

// DocumentationSection represents a section extracted from documentation
type DocumentationSection struct {
	ID            string         `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	DocID         string         `gorm:"type:uuid;not null;index:idx_documentation_sections_doc_id" json:"doc_id"`
	Level         int            `gorm:"not null;index:idx_documentation_sections_level" json:"level"` // heading level (1-6 for markdown)
	Title         string         `gorm:"size:512;not null" json:"title"`
	Content       *string        `gorm:"type:text" json:"content,omitempty"`
	SectionNumber *string        `gorm:"size:50" json:"section_number,omitempty"` // like "1.2.3" for hierarchical structure
	Position      *int           `json:"position,omitempty"`                      // position within document
	CodeBlocks    pq.StringArray `gorm:"type:text[]" json:"code_blocks"`
	Links         pq.StringArray `gorm:"type:text[]" json:"links"` // links found in this section
	Metadata      datatypes.JSON `gorm:"type:jsonb;default:'{}'" json:"metadata"`
	CreatedAt     time.Time      `gorm:"not null;default:now()" json:"created_at"`
}

// BeforeCreate hook to generate UUID
func (ds *DocumentationSection) BeforeCreate(_ *gorm.DB) error {
	if ds.ID == "" {
		ds.ID = uuid.New().String()
	}
	return nil
}

// DocumentationLink represents a link between documentation entries or to external resources
type DocumentationLink struct {
	ID           string  `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	SourceDocID  string  `gorm:"type:uuid;not null;index:idx_documentation_links_source" json:"source_doc_id"`
	TargetDocID  *string `gorm:"type:uuid;index:idx_documentation_links_target_doc" json:"target_doc_id,omitempty"`
	TargetItemID *string `gorm:"type:uuid;index:idx_documentation_links_target_item" json:"target_item_id,omitempty"`
	// LinkType: references, seeAlso, relatedTo, implements, etc.
	LinkType    *string   `gorm:"size:50;index:idx_documentation_links_type" json:"link_type,omitempty"`
	URL         *string   `gorm:"type:text" json:"url,omitempty"`
	Title       *string   `gorm:"type:text" json:"title,omitempty"`
	Description *string   `gorm:"type:text" json:"description,omitempty"`
	CreatedAt   time.Time `gorm:"not null;default:now()" json:"created_at"`
}

// BeforeCreate hook to generate UUID
func (dl *DocumentationLink) BeforeCreate(_ *gorm.DB) error {
	if dl.ID == "" {
		dl.ID = uuid.New().String()
	}
	return nil
}

// DocumentationSearchIndex represents an entry in the documentation search index
type DocumentationSearchIndex struct {
	ID             string    `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	DocID          string    `gorm:"type:uuid;not null;index:idx_documentation_search_index_doc_id" json:"doc_id"`
	DocTitle       *string   `gorm:"size:512" json:"doc_title,omitempty"`
	SectionTitle   *string   `gorm:"size:512" json:"section_title,omitempty"`
	ContentSnippet *string   `gorm:"type:text" json:"content_snippet,omitempty"`
	SearchVector   *string   `gorm:"type:tsvector;index:idx_documentation_search_index_search,type:gin" json:"-"`
	Rank           float64   `gorm:"default:0.5" json:"rank"`
	CreatedAt      time.Time `gorm:"not null;default:now()" json:"created_at"`
}

// BeforeCreate hook to generate UUID
func (dsi *DocumentationSearchIndex) BeforeCreate(_ *gorm.DB) error {
	if dsi.ID == "" {
		dsi.ID = uuid.New().String()
	}
	return nil
}

// DocumentationVersion represents a version of documentation for version tracking
type DocumentationVersion struct {
	ID            string    `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	DocID         string    `gorm:"type:uuid;not null;index:idx_dv_doc;uniqueIndex:idx_dv_uniq,composite:dv" json:"doc_id"`
	VersionNumber int       `gorm:"not null;uniqueIndex:idx_dv_uniq,composite:dv;index:idx_dv_num,composite:dv_sort" json:"version_number"`
	Content       string    `gorm:"type:text;not null" json:"content"`
	ChangeSummary *string   `gorm:"type:text" json:"change_summary,omitempty"`
	ChangedBy     *string   `gorm:"type:uuid" json:"changed_by,omitempty"`
	CreatedAt     time.Time `gorm:"not null;default:now()" json:"created_at"`
}

// BeforeCreate hook to generate UUID
func (dv *DocumentationVersion) BeforeCreate(_ *gorm.DB) error {
	if dv.ID == "" {
		dv.ID = uuid.New().String()
	}
	return nil
}
