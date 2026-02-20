// Package docindex provides documentation indexing with section extraction,
// code reference detection, and concept linking for traceability.
package docindex

import (
	"time"

	"github.com/google/uuid"
)

// DocEntityType represents the type of documentation entity
type DocEntityType string

const (
	// DocTypeDocument represents a document entity.
	DocTypeDocument DocEntityType = "document"
	// DocTypeSection represents a section entity.
	DocTypeSection DocEntityType = "section"
	// DocTypeChunk represents a chunk entity.
	DocTypeChunk DocEntityType = "chunk"
)

// DocEntity represents a documentation entity (document, section, or chunk)
type DocEntity struct {
	ID         uuid.UUID     `json:"id"`
	ProjectID  uuid.UUID     `json:"project_id"`
	Type       DocEntityType `json:"type"`
	ParentID   *uuid.UUID    `json:"parent_id,omitempty"`
	DocumentID uuid.UUID     `json:"document_id"` // Root document ID

	// Location
	FilePath    string `json:"file_path"`
	SectionPath string `json:"section_path,omitempty"` // e.g., "1.2.3" for nested sections

	// Content
	Title       string `json:"title"`
	Content     string `json:"content"`
	RawMarkdown string `json:"raw_markdown,omitempty"`

	// Hierarchy
	HeadingLevel int `json:"heading_level,omitempty"` // 1-6 for h1-h6
	ChunkIndex   int `json:"chunk_index,omitempty"`
	StartLine    int `json:"start_line"`
	EndLine      int `json:"end_line"`

	// Extracted references
	CodeRefs      []CodeRef      `json:"code_refs,omitempty"`
	APIRefs       []APIRef       `json:"api_refs,omitempty"`
	InternalLinks []InternalLink `json:"internal_links,omitempty"`

	// Embeddings
	Embedding      []float32 `json:"embedding,omitempty"`
	EmbeddingModel string    `json:"embedding_model,omitempty"`

	// Metadata
	Tags     []string       `json:"tags,omitempty"`
	Metadata map[string]any `json:"metadata,omitempty"`

	// Timestamps
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	IndexedAt time.Time `json:"indexed_at"`
}

// CodeRef represents a reference to code within documentation
type CodeRef struct {
	Type        string  `json:"type"` // file, function, class, variable, package
	Name        string  `json:"name"` // The referenced name
	FilePath    string  `json:"file_path,omitempty"`
	Language    string  `json:"language,omitempty"`
	StartOffset int     `json:"start_offset"` // Character offset in content
	EndOffset   int     `json:"end_offset"`
	Context     string  `json:"context,omitempty"` // Surrounding text
	Confidence  float64 `json:"confidence"`
}

// APIRef represents a reference to an API endpoint
type APIRef struct {
	Method      string `json:"method,omitempty"` // GET, POST, etc.
	Path        string `json:"path"`
	Description string `json:"description,omitempty"`
	StartOffset int    `json:"start_offset"`
	EndOffset   int    `json:"end_offset"`
}

// InternalLink represents a link to another document or section
type InternalLink struct {
	TargetPath  string `json:"target_path"`
	Anchor      string `json:"anchor,omitempty"`
	Text        string `json:"text"`
	StartOffset int    `json:"start_offset"`
	EndOffset   int    `json:"end_offset"`
}

// Section represents a parsed markdown section
type Section struct {
	Title       string     `json:"title"`
	Level       int        `json:"level"`   // Heading level 1-6
	Content     string     `json:"content"` // Text content (without subsections)
	RawMarkdown string     `json:"raw_markdown"`
	StartLine   int        `json:"start_line"`
	EndLine     int        `json:"end_line"`
	Children    []*Section `json:"children,omitempty"`
	Path        string     `json:"path"` // Section path like "1.2.3"
}

// Document represents a parsed markdown document
type Document struct {
	FilePath      string         `json:"file_path"`
	Title         string         `json:"title"`
	Frontmatter   map[string]any `json:"frontmatter,omitempty"`
	Sections      []*Section     `json:"sections"`
	RawContent    string         `json:"raw_content"`
	CodeRefs      []CodeRef      `json:"code_refs"`
	APIRefs       []APIRef       `json:"api_refs"`
	InternalLinks []InternalLink `json:"internal_links"`
}

// IndexRequest represents a request to index documentation
type IndexRequest struct {
	ProjectID          uuid.UUID `json:"project_id"`
	FilePaths          []string  `json:"file_paths,omitempty"` // Specific files to index
	Directory          string    `json:"directory,omitempty"`  // Directory to scan
	Recursive          bool      `json:"recursive"`
	FilePatterns       []string  `json:"file_patterns,omitempty"` // e.g., ["*.md", "*.mdx"]
	ExcludePatterns    []string  `json:"exclude_patterns,omitempty"`
	GenerateEmbeddings bool      `json:"generate_embeddings"`
	ChunkSize          int       `json:"chunk_size,omitempty"` // Max chars per chunk
	ChunkOverlap       int       `json:"chunk_overlap,omitempty"`
}

// IndexResult represents the result of an indexing operation
type IndexResult struct {
	ProjectID        uuid.UUID `json:"project_id"`
	DocumentsIndexed int       `json:"documents_indexed"`
	SectionsCreated  int       `json:"sections_created"`
	ChunksCreated    int       `json:"chunks_created"`
	CodeRefsFound    int       `json:"code_refs_found"`
	APIRefsFound     int       `json:"api_refs_found"`
	Errors           []string  `json:"errors,omitempty"`
	DurationMs       int64     `json:"duration_ms"`
}
