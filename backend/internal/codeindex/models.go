// Package codeindex provides enhanced code indexing with canonical concept linking,
// cross-language resolution, call chain analysis, and incremental sync.
package codeindex

import (
	"time"

	"github.com/google/uuid"
)

// SymbolType represents the type of code symbol
type SymbolType string

// SymbolType values identify code symbol kinds.
const (
	SymbolTypeFunction  SymbolType = "function"
	SymbolTypeMethod    SymbolType = "method"
	SymbolTypeClass     SymbolType = "class"
	SymbolTypeInterface SymbolType = "interface"
	SymbolTypeStruct    SymbolType = "struct"
	SymbolTypeType      SymbolType = "type"
	SymbolTypeVariable  SymbolType = "variable"
	SymbolTypeConstant  SymbolType = "constant"
	SymbolTypeEnum      SymbolType = "enum"
	SymbolTypeModule    SymbolType = "module"
	SymbolTypePackage   SymbolType = "package"
	SymbolTypeProperty  SymbolType = "property"
	SymbolTypeParameter SymbolType = "parameter"
	SymbolTypeHandler   SymbolType = "handler"
	SymbolTypeRoute     SymbolType = "route"
	SymbolTypeComponent SymbolType = "component"
	SymbolTypeHook      SymbolType = "hook"
)

// Language represents a programming language
type Language string

// Language values identify supported programming languages.
const (
	LanguageTypeScript Language = "typescript"
	LanguageJavaScript Language = "javascript"
	LanguageGo         Language = "go"
	LanguagePython     Language = "python"
	LanguageRust       Language = "rust"
	LanguageJava       Language = "java"
)

// CodeEntity represents a code symbol with AST-level granularity
type CodeEntity struct {
	ID        uuid.UUID `json:"id"`
	ProjectID uuid.UUID `json:"project_id"`

	// Location
	FilePath    string `json:"file_path"`
	StartLine   int    `json:"start_line"`
	EndLine     int    `json:"end_line"`
	StartColumn int    `json:"start_column,omitempty"`
	EndColumn   int    `json:"end_column,omitempty"`

	// Symbol info
	SymbolName string     `json:"symbol_name"`
	SymbolType SymbolType `json:"symbol_type"`
	Language   Language   `json:"language"`
	Signature  string     `json:"signature,omitempty"`

	// Hierarchy
	ParentID   *uuid.UUID `json:"parent_id,omitempty"`
	ModulePath string     `json:"module_path,omitempty"` // e.g., "internal/handlers"

	// Canonical linking
	CanonicalID *uuid.UUID `json:"canonical_id,omitempty"`

	// Content
	DocComment  string `json:"doc_comment,omitempty"`
	Content     string `json:"content,omitempty"` // Source code
	ContentHash string `json:"content_hash"`      // For change detection

	// Embeddings
	Embedding      []float32 `json:"embedding,omitempty"`
	EmbeddingModel string    `json:"embedding_model,omitempty"`

	// References
	Imports     []ImportRef  `json:"imports,omitempty"`
	Calls       []CallRef    `json:"calls,omitempty"`
	References  []SymbolRef  `json:"references,omitempty"`
	Annotations []Annotation `json:"annotations,omitempty"`

	// Metadata
	Visibility string         `json:"visibility,omitempty"` // public, private, protected
	IsExported bool           `json:"is_exported"`
	IsAsync    bool           `json:"is_async,omitempty"`
	Metadata   map[string]any `json:"metadata,omitempty"`

	// Timestamps
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	IndexedAt time.Time `json:"indexed_at"`
}

// ImportRef represents an import statement
type ImportRef struct {
	ModulePath  string `json:"module_path"`
	ImportName  string `json:"import_name,omitempty"`
	Alias       string `json:"alias,omitempty"`
	IsDefault   bool   `json:"is_default,omitempty"`
	IsNamespace bool   `json:"is_namespace,omitempty"`
	Line        int    `json:"line"`
}

// CallRef represents a function/method call
type CallRef struct {
	TargetName    string     `json:"target_name"`
	TargetID      *uuid.UUID `json:"target_id,omitempty"` // Resolved entity ID
	ModulePath    string     `json:"module_path,omitempty"`
	Line          int        `json:"line"`
	Column        int        `json:"column,omitempty"`
	IsAsync       bool       `json:"is_async,omitempty"`
	ArgumentCount int        `json:"argument_count,omitempty"`
}

// SymbolRef represents a reference to another symbol
type SymbolRef struct {
	SymbolName string     `json:"symbol_name"`
	SymbolID   *uuid.UUID `json:"symbol_id,omitempty"`
	RefType    string     `json:"ref_type"` // usage, extends, implements
	Line       int        `json:"line"`
	Column     int        `json:"column,omitempty"`
}

// Annotation represents a code annotation (e.g., @trace-implements)
type Annotation struct {
	Name  string         `json:"name"`
	Value string         `json:"value,omitempty"`
	Args  map[string]any `json:"args,omitempty"`
	Line  int            `json:"line"`
}

// CallChain represents a chain of function calls (for journey derivation)
type CallChain struct {
	ID         uuid.UUID   `json:"id"`
	ProjectID  uuid.UUID   `json:"project_id"`
	Name       string      `json:"name,omitempty"`
	Type       string      `json:"type"` // user_flow, data_path, api_chain
	EntryPoint uuid.UUID   `json:"entry_point"`
	Steps      []ChainStep `json:"steps"`
	Depth      int         `json:"depth"`
	CrossLang  bool        `json:"cross_lang"` // Crosses language boundaries
	CreatedAt  time.Time   `json:"created_at"`
}

// ChainStep represents a step in a call chain
type ChainStep struct {
	EntityID   uuid.UUID `json:"entity_id"`
	SymbolName string    `json:"symbol_name"`
	FilePath   string    `json:"file_path"`
	Language   Language  `json:"language"`
	Order      int       `json:"order"`
	CallType   string    `json:"call_type"` // direct, async, http, event
}
