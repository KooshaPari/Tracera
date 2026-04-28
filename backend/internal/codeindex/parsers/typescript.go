package parsers

import (
	"context"
	"strings"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

const (
	docCommentLookbackLines = 10
	hashShift               = 5
	startLineOffset         = 2
)

// TypeScriptParser parses TypeScript and JavaScript files
type TypeScriptParser struct {
	projectRoot string
	// In a real implementation, we would use tree-sitter bindings
	// For now, we use regex-based parsing as a foundation
}

// NewTypeScriptParser creates a new TypeScript parser
func NewTypeScriptParser(projectRoot string) *TypeScriptParser {
	return &TypeScriptParser{
		projectRoot: projectRoot,
	}
}

// ParseFile parses a TypeScript/JavaScript file
func (parser *TypeScriptParser) ParseFile(
	ctx context.Context,
	filePath string,
	content string,
) (*codeindex.ParsedFile, error) {
	_ = ctx
	start := time.Now()

	parsedFile := &codeindex.ParsedFile{
		FilePath: filePath,
		Language: codeindex.LanguageTypeScript,
		Entities: make([]*codeindex.ParsedEntity, 0),
		Imports:  make([]codeindex.ImportRef, 0),
		Content:  content,
		Hash:     hashContent(content),
		ParsedAt: time.Now(),
	}

	// Extract module path (relative to project root)
	parsedFile.Module = strings.TrimPrefix(filePath, parser.projectRoot)
	parsedFile.Module = strings.TrimPrefix(parsedFile.Module, "/")

	// Parse imports
	imports := parser.parseImports(content)
	parsedFile.Imports = imports

	// Parse top-level declarations
	entities := parser.parseTopLevelDeclarations(content, filePath)
	parsedFile.Entities = entities

	_ = time.Since(start)
	return parsedFile, nil
}
