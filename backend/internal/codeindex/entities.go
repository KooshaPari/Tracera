package codeindex

import (
	"time"

	"github.com/google/uuid"
)

// Parser-specific entities for indexing support

// ParsedFile represents a code file after parsing
type ParsedFile struct {
	FilePath string
	Language Language
	Entities []*ParsedEntity
	Imports  []ImportRef
	Module   string
	Content  string
	Hash     string
	ParsedAt time.Time
}

// ParsedEntity represents a parsed code entity with relationships
type ParsedEntity struct {
	ID            uuid.UUID
	Name          string
	QualifiedName string
	Type          SymbolType
	Language      Language
	FilePath      string
	StartLine     int
	EndLine       int
	StartColumn   int
	EndColumn     int
	Signature     string
	DocComment    string
	Content       string
	Visibility    string
	IsExported    bool
	IsAsync       bool
	ParentName    string // For nested entities (methods, nested classes, etc.)
	Annotations   []Annotation
	Calls         []ParsedCall
	References    []ParsedReference
	Properties    []*ParsedEntity // For classes: fields and methods
	Parameters    []Parameter
	ReturnType    string
	Metadata      map[string]interface{}
}

// ParsedCall represents a function/method call found in code
type ParsedCall struct {
	TargetName    string
	TargetID      *uuid.UUID
	ModulePath    string
	Line          int
	Column        int
	IsAsync       bool
	ArgumentCount int
	Arguments     []string // Argument expressions
}

// ParsedReference represents a reference to a symbol (variable, type, etc.)
type ParsedReference struct {
	SymbolName string
	SymbolID   *uuid.UUID
	RefType    string // "usage", "definition", "import", etc.
	Line       int
	Column     int
}

// Parameter represents a function/method parameter
type Parameter struct {
	Name     string
	Type     string
	Optional bool
	Default  string
	Spread   bool // For variadic parameters
}

// ImportResolution tracks resolved imports across files
type ImportResolution struct {
	ImportRef     ImportRef
	ResolvedPath  string     // Canonical file path
	ResolvedID    *uuid.UUID // Code entity ID if available
	Language      Language
	IsLocal       bool // true for local imports, false for external
	PackageName   string
	ExportedNames []string // What names does this module export?
}

// CrossFileReference tracks a reference from one file to another
type CrossFileReference struct {
	SourceFile    string
	SourceEntity  *uuid.UUID
	SourceLine    int
	TargetFile    string
	TargetEntity  *uuid.UUID
	TargetName    string
	ReferenceType string // "calls", "uses", "extends", "implements", etc.
}

// CallChainResolution tracks a resolved call chain across files
type CallChainResolution struct {
	EntryPoint    *ParsedEntity
	Steps         []*ChainStepResolved
	Depth         int
	CrossLanguage bool
	CircularRefs  []string // Detected circular references
}

// ChainStepResolved represents a resolved step in a call chain
type ChainStepResolved struct {
	Entity    *ParsedEntity
	FilePath  string
	Language  Language
	Order     int
	CallType  string // "direct", "indirect", "async", "callback", etc.
	Arguments []string
}

// SymbolTable maps symbol names to entities for reference resolution
type SymbolTable struct {
	FilePath    string
	Exports     map[string]*ParsedEntity // name -> entity
	Locals      map[string]*ParsedEntity
	Imports     map[string]ImportResolution
	ParentTable *SymbolTable // For nested scopes
}

// IndexingResult contains the result of indexing a file
type IndexingResult struct {
	FilePath      string
	Success       bool
	ParsedFile    *ParsedFile
	Errors        []string
	Warnings      []string
	DurationMs    int64
	EntitiesCount int
	ImportsCount  int
}

// BatchIndexResult contains results from batch indexing
type BatchIndexResult struct {
	TotalFiles      int
	SuccessfulFiles int
	FailedFiles     int
	Results         []*IndexingResult
	DurationMs      int64
	EntitiesAdded   int
	ImportsAdded    int
}
