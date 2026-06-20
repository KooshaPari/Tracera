package docindex

import (
	"time"

	"github.com/google/uuid"
)

// DocumentEntityType represents the hierarchical types of documentation entities
type DocumentEntityType string

const (
	// EntityTypeDocumentRoot represents a document root entity.
	EntityTypeDocumentRoot DocumentEntityType = "doc_root"
	// EntityTypeDocSection represents a document section entity.
	EntityTypeDocSection DocumentEntityType = "doc_section"
	// EntityTypeDocChunk represents a document chunk entity.
	EntityTypeDocChunk DocumentEntityType = "doc_chunk"
)

// DocumentEntity represents a structured document node in the documentation hierarchy
// This extends the base DocEntity with hierarchical relationships
type DocumentEntity struct {
	ID uuid.UUID `json:"id"`

	// Project context
	ProjectID uuid.UUID `json:"project_id"`

	// Hierarchy
	Type       DocumentEntityType `json:"type"`        // doc_root, doc_section, doc_chunk
	ParentID   *uuid.UUID         `json:"parent_id"`   // Parent section/chunk ID
	DocumentID uuid.UUID          `json:"document_id"` // Root document reference

	// Location metadata
	FilePath    string `json:"file_path"`
	SectionPath string `json:"section_path,omitempty"` // e.g., "1.2.3" for nested sections
	HeadingID   string `json:"heading_id,omitempty"`   // Auto-generated ID from heading

	// Content
	Title       string `json:"title"`
	Content     string `json:"content"`
	RawMarkdown string `json:"raw_markdown,omitempty"`

	// Hierarchy metadata
	HeadingLevel int `json:"heading_level,omitempty"` // 1-6 for h1-h6
	ChunkIndex   int `json:"chunk_index,omitempty"`   // Order within parent section
	StartLine    int `json:"start_line"`
	EndLine      int `json:"end_line"`

	// Extracted references and concepts
	CodeReferences  []CodeReference  `json:"code_references,omitempty"`
	APIReferences   []APIReference   `json:"api_references,omitempty"`
	ConceptLinks    []ConceptLink    `json:"concept_links,omitempty"`
	RelatedEntities []EntityRelation `json:"related_entities,omitempty"`

	// Semantic information
	Summary        string    `json:"summary,omitempty"` // AI-generated summary
	Keywords       []string  `json:"keywords,omitempty"`
	Topics         []string  `json:"topics,omitempty"`
	Embedding      []float32 `json:"embedding,omitempty"`
	EmbeddingModel string    `json:"embedding_model,omitempty"`

	// Quality metrics
	TextLength     int     `json:"text_length"`
	WordCount      int     `json:"word_count"`
	CodeBlockCount int     `json:"code_block_count"`
	TableCount     int     `json:"table_count"`
	LinkCount      int     `json:"link_count"`
	Quality        float64 `json:"quality"` // 0.0-1.0 quality score

	// Status and lifecycle
	IsPublished bool   `json:"is_published"`
	IsOutdated  bool   `json:"is_outdated"`
	Status      string `json:"status"` // draft, review, published, deprecated
	Version     int    `json:"version"`

	// Metadata
	Tags         []string       `json:"tags,omitempty"`
	Metadata     map[string]any `json:"metadata,omitempty"`
	CustomFields map[string]any `json:"custom_fields,omitempty"`

	// Timestamps
	CreatedAt   time.Time  `json:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at"`
	IndexedAt   time.Time  `json:"indexed_at"`
	PublishedAt *time.Time `json:"published_at,omitempty"`
}

// CodeReference represents a reference to a code entity
type CodeReference struct {
	ID             uuid.UUID  `json:"id"`
	ReferenceType  string     `json:"reference_type"`  // file, function, class, constant, etc.
	ReferencedName string     `json:"referenced_name"` // The name of what's referenced
	FilePath       string     `json:"file_path,omitempty"`
	Language       string     `json:"language,omitempty"`
	LineNumber     int        `json:"line_number,omitempty"`
	ColumnNumber   int        `json:"column_number,omitempty"`
	StartOffset    int        `json:"start_offset"` // Char offset in document content
	EndOffset      int        `json:"end_offset"`
	Context        string     `json:"context,omitempty"`        // Surrounding text for context
	Confidence     float64    `json:"confidence"`               // 0.0-1.0 confidence level
	CodeEntityID   *uuid.UUID `json:"code_entity_id,omitempty"` // Link to actual code entity
}

// APIReference represents a reference to an API endpoint
type APIReference struct {
	ID           uuid.UUID       `json:"id"`
	Method       string          `json:"method,omitempty"` // GET, POST, PUT, PATCH, DELETE, etc.
	Path         string          `json:"path"`
	Version      string          `json:"version,omitempty"` // API version like v1, v2
	Description  string          `json:"description,omitempty"`
	StartOffset  int             `json:"start_offset"`
	EndOffset    int             `json:"end_offset"`
	Confidence   float64         `json:"confidence"`
	RequestBody  *RequestSchema  `json:"request_body,omitempty"`
	ResponseBody *ResponseSchema `json:"response_body,omitempty"`
}

// RequestSchema represents the request schema of an API endpoint
type RequestSchema struct {
	ContentType string         `json:"content_type"`
	Schema      map[string]any `json:"schema,omitempty"`
	Example     string         `json:"example,omitempty"`
}

// ResponseSchema represents the response schema of an API endpoint
type ResponseSchema struct {
	ContentType string         `json:"content_type"`
	StatusCode  int            `json:"status_code"`
	Schema      map[string]any `json:"schema,omitempty"`
	Example     string         `json:"example,omitempty"`
}

// ConceptLink represents a link from a document entity to a business concept
type ConceptLink struct {
	ID           uuid.UUID   `json:"id"`
	ConceptID    uuid.UUID   `json:"concept_id"` // Reference to BusinessTerm
	ConceptName  string      `json:"concept_name"`
	ConceptType  ConceptType `json:"concept_type"`
	StartOffset  int         `json:"start_offset"`
	EndOffset    int         `json:"end_offset"`
	Confidence   float64     `json:"confidence"`
	RelationType string      `json:"relation_type"` // defines, implements, describes, etc.
}

// EntityRelation represents a relationship between document entities
type EntityRelation struct {
	ID             uuid.UUID          `json:"id"`
	TargetEntityID uuid.UUID          `json:"target_entity_id"`
	TargetType     DocumentEntityType `json:"target_type"`
	RelationType   string             `json:"relation_type"` // parent, child, related, referenced_by, etc.
	Confidence     float64            `json:"confidence"`
	Evidence       string             `json:"evidence,omitempty"`
}

// DocumentHierarchy represents the hierarchical structure of a document
type DocumentHierarchy struct {
	ID        uuid.UUID         `json:"id"`
	RootID    uuid.UUID         `json:"root_id"`
	Sections  []DocumentSection `json:"sections"`
	Depth     int               `json:"depth"`
	NodeCount int               `json:"node_count"`
}

// DocumentSection represents a section node in the document hierarchy
type DocumentSection struct {
	ID            uuid.UUID         `json:"id"`
	Title         string            `json:"title"`
	Level         int               `json:"level"`
	Path          string            `json:"path"`
	SectionID     string            `json:"section_id"`
	Content       string            `json:"content"`
	ContentLength int               `json:"content_length"`
	Chunks        []DocumentChunk   `json:"chunks,omitempty"`
	Children      []DocumentSection `json:"children,omitempty"`
	ParentID      *uuid.UUID        `json:"parent_id,omitempty"`
}

// DocumentChunk represents a chunk of content within a section
type DocumentChunk struct {
	ID          uuid.UUID       `json:"id"`
	SectionID   uuid.UUID       `json:"section_id"`
	ChunkIndex  int             `json:"chunk_index"`
	Type        string          `json:"type"` // paragraph, code_block, table, list, definition
	Content     string          `json:"content"`
	TextLength  int             `json:"text_length"`
	WordCount   int             `json:"word_count"`
	CodeRefs    []CodeReference `json:"code_refs,omitempty"`
	ConceptRefs []ConceptLink   `json:"concept_refs,omitempty"`
	Embedding   []float32       `json:"embedding,omitempty"`
}

// DocumentStats represents statistical information about a document
type DocumentStats struct {
	DocumentID          uuid.UUID `json:"document_id"`
	TotalSections       int       `json:"total_sections"`
	TotalChunks         int       `json:"total_chunks"`
	TotalWords          int       `json:"total_words"`
	TotalChars          int       `json:"total_chars"`
	AverageHeadingLevel float64   `json:"average_heading_level"`
	CodeReferences      int       `json:"code_references"`
	APIReferences       int       `json:"api_references"`
	ConceptMentions     int       `json:"concept_mentions"`
	UniqueCodeEntities  int       `json:"unique_code_entities"`
	UniqueConcepts      int       `json:"unique_concepts"`
	AverageChunkSize    int       `json:"average_chunk_size"`
	MaxChunkSize        int       `json:"max_chunk_size"`
	MinChunkSize        int       `json:"min_chunk_size"`
	Quality             float64   `json:"quality"`      // 0.0-1.0
	Completeness        float64   `json:"completeness"` // 0.0-1.0
	LastAnalyzed        time.Time `json:"last_analyzed"`
}

// DocumentDiff represents changes between document versions
type DocumentDiff struct {
	ID                uuid.UUID `json:"id"`
	DocumentID        uuid.UUID `json:"document_id"`
	OldVersion        int       `json:"old_version"`
	NewVersion        int       `json:"new_version"`
	ChangedAt         time.Time `json:"changed_at"`
	AddedSections     int       `json:"added_sections"`
	RemovedSections   int       `json:"removed_sections"`
	ModifiedSections  int       `json:"modified_sections"`
	AddedChunks       int       `json:"added_chunks"`
	RemovedChunks     int       `json:"removed_chunks"`
	ChangeDescription string    `json:"change_description"`
}

// Helper functions

// GetDepth returns the depth of this entity in the hierarchy
func (de *DocumentEntity) GetDepth() int {
	switch de.Type {
	case EntityTypeDocumentRoot:
		return 0
	case EntityTypeDocSection:
		return de.HeadingLevel
	case EntityTypeDocChunk:
		return de.HeadingLevel + 1
	default:
		return 0
	}
}

// IsLeaf returns true if this entity has no children
func (de *DocumentEntity) IsLeaf() bool {
	return de.Type == EntityTypeDocChunk
}

// IsRoot returns true if this is a document root
func (de *DocumentEntity) IsRoot() bool {
	return de.Type == EntityTypeDocumentRoot
}

// GetHierarchyPath returns the full path in the document hierarchy
func (de *DocumentEntity) GetHierarchyPath() string {
	if de.SectionPath != "" {
		return de.SectionPath
	}
	if de.HeadingID != "" {
		return de.HeadingID
	}
	return de.ID.String()
}

// ValidateEntityType validates that the entity type is valid
func ValidateEntityType(et DocumentEntityType) bool {
	switch et {
	case EntityTypeDocumentRoot, EntityTypeDocSection, EntityTypeDocChunk:
		return true
	default:
		return false
	}
}

// EntityTypeFromDocType converts DocEntityType to DocumentEntityType
func EntityTypeFromDocType(dt DocEntityType) DocumentEntityType {
	switch dt {
	case DocTypeDocument:
		return EntityTypeDocumentRoot
	case DocTypeSection:
		return EntityTypeDocSection
	case DocTypeChunk:
		return EntityTypeDocChunk
	default:
		return EntityTypeDocumentRoot
	}
}
