// Package parsers provides parsers functionality.
package parsers

import (
	"context"
	"regexp"
	"strings"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

// GoParser parses Go source files
type GoParser struct {
	projectRoot string
}

// NewGoParser creates a new Go parser
func NewGoParser(projectRoot string) *GoParser {
	return &GoParser{
		projectRoot: projectRoot,
	}
}

// ParseFile parses a Go source file
func (parser *GoParser) ParseFile(ctx context.Context, filePath string, content string) (*codeindex.ParsedFile, error) {
	_ = ctx
	start := time.Now()

	parsedFile := &codeindex.ParsedFile{
		FilePath: filePath,
		Language: codeindex.LanguageGo,
		Entities: make([]*codeindex.ParsedEntity, 0),
		Imports:  make([]codeindex.ImportRef, 0),
		Content:  content,
		Hash:     hashContent(content),
		ParsedAt: time.Now(),
	}

	// Extract module path
	parsedFile.Module = strings.TrimPrefix(filePath, parser.projectRoot)
	parsedFile.Module = strings.TrimPrefix(parsedFile.Module, "/")

	// Extract package name
	packageName := parser.extractPackageName(content)
	if packageName != "" {
		parsedFile.Module = packageName
	}

	// Parse imports
	imports := parser.parseImports(content)
	parsedFile.Imports = imports

	// Parse declarations
	entities := parser.parseDeclarations(content, filePath)
	parsedFile.Entities = entities

	_ = time.Since(start)
	return parsedFile, nil
}

// extractPackageName extracts the package name from the file
func (parser *GoParser) extractPackageName(content string) string {
	packageRegex := regexp.MustCompile(`^package\s+(\w+)`)

	lines := strings.Split(content, "\n")
	for _, line := range lines {
		if matches := packageRegex.FindStringSubmatch(line); matches != nil {
			return matches[1]
		}
	}

	return ""
}
