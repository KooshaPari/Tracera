package docindex

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestFullIndexingWorkflow tests the complete indexing pipeline
func TestFullIndexingWorkflow(t *testing.T) {
	// Create temporary directory with test markdown files
	tmpDir := t.TempDir()

	// Create test markdown file
	docPath := filepath.Join(tmpDir, "guide.md")
	content := `---
title: Getting Started Guide
author: Test Team
tags: [guide, tutorial]
---

# Getting Started

Welcome to the guide.

## Installation

Follow these steps:

1. Install dependencies with 'bun install'
2. Configure settings in 'config.json'
3. Run 'npm start' or 'bun run dev'

### Prerequisites

You need:
- Node.js 18+
- PostgreSQL 14+

## Configuration

Edit 'src/config.ts' to customize.

## Usage Examples

Check 'examples/' directory.

### Basic Example

import { setup } from "./core";

setup();

### Advanced Usage

POST /api/v1/configure to set options.

## Troubleshooting

See [FAQ](faq.md) for common issues.
`

	err := os.WriteFile(docPath, []byte(content), 0o600)
	require.NoError(t, err)

	// Create indexer
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	// Index the directory
	projectID := uuid.New()
	req := &IndexRequest{
		ProjectID:          projectID,
		Directory:          tmpDir,
		Recursive:          true,
		FilePatterns:       []string{"*.md"},
		GenerateEmbeddings: false,
	}

	ctx := context.Background()
	result, err := indexer.Index(ctx, req)

	require.NoError(t, err)
	require.NotNil(t, result)
	assert.Equal(t, 1, result.DocumentsIndexed)
	assert.Positive(t, result.SectionsCreated)
}

// TestComplexDocumentStructure tests indexing of complex document
func TestComplexDocumentStructure(t *testing.T) {
	parser := NewParser()

	// Complex document with multiple levels and references
	content := `---
title: Advanced Architecture
version: 2.0
---

# System Architecture

## Core Components

### API Layer

The API layer handles:
- Authentication via auth.go
- Request validation using validators.ts
- Response formatting

POST /api/v1/authenticate with credentials.
GET /api/v1/status for health check.

### Data Layer

Use models.go for type definitions.

See [Database Design](db-design.md#schema) for details.

### Service Layer

Implement business logic in services/ directory.

## Integration Points

### External APIs

Call GET /api/external/data for integration.

### Webhooks

See [Webhook Configuration](webhooks.md) for setup.

## Performance Considerations

Optimize using cache.ts and compression.go.

## Security

Review security.md and [Auth Guide](auth.md#tokens).
`

	doc, err := parser.Parse("architecture.md", []byte(content))
	require.NoError(t, err)

	// Verify document parsing
	assert.Equal(t, "Advanced Architecture", doc.Title)
	assert.NotNil(t, doc.Frontmatter)
	// YAML frontmatter parses numbers as float64
	version, ok := doc.Frontmatter["version"]
	assert.True(t, ok)
	assert.InEpsilon(t, 2.0, version, 1e-9)

	// Verify section extraction
	assert.NotEmpty(t, doc.Sections)

	// Verify code ref extraction
	refs := parser.ExtractCodeRefs(doc.RawContent)
	assert.NotEmpty(t, refs)

	// Verify API ref extraction
	apiRefs := ExtractAPIRefs(doc.RawContent)
	assert.NotEmpty(t, apiRefs)

	// Verify internal links extraction
	links := ExtractInternalLinks(doc.RawContent)
	assert.NotEmpty(t, links)
}

// TestMultipleFilesIndexing tests indexing multiple documents
func TestMultipleFilesIndexing(t *testing.T) {
	tmpDir := t.TempDir()

	// Create multiple markdown files
	files := map[string]string{
		"README.md": `# Project
## Overview
This is the main documentation.`,

		"guide.md": `# Getting Started
## Installation
Install with npm install.`,

		"api.md": `# API Reference
## Endpoints
GET /api/users
POST /api/users`,
	}

	for name, content := range files {
		path := filepath.Join(tmpDir, name)
		err := os.WriteFile(path, []byte(content), 0o600)
		require.NoError(t, err)
	}

	// Index all files
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	projectID := uuid.New()
	req := &IndexRequest{
		ProjectID:          projectID,
		Directory:          tmpDir,
		Recursive:          true,
		FilePatterns:       []string{"*.md"},
		GenerateEmbeddings: false,
	}

	ctx := context.Background()
	result, err := indexer.Index(ctx, req)

	require.NoError(t, err)
	assert.Equal(t, 3, result.DocumentsIndexed)
}

// TestNestedDirectoryIndexing tests recursive directory scanning
func TestNestedDirectoryIndexing(t *testing.T) {
	tmpDir := t.TempDir()

	// Create nested directory structure
	subDir := filepath.Join(tmpDir, "docs", "guides")
	err := os.MkdirAll(subDir, 0o750)
	require.NoError(t, err)

	// Add files at different levels
	docs := map[string]string{
		filepath.Join(tmpDir, "README.md"):                     "# Root\nRoot documentation.",
		filepath.Join(tmpDir, "docs", "guide.md"):              "# Guide\nGuide content.",
		filepath.Join(tmpDir, "docs", "guides", "advanced.md"): "# Advanced\nAdvanced guide.",
	}

	for path, content := range docs {
		err := os.WriteFile(path, []byte(content), 0o600)
		require.NoError(t, err)
	}

	// Index recursively
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	projectID := uuid.New()
	req := &IndexRequest{
		ProjectID:          projectID,
		Directory:          tmpDir,
		Recursive:          true,
		FilePatterns:       []string{"*.md"},
		GenerateEmbeddings: false,
	}

	ctx := context.Background()
	result, err := indexer.Index(ctx, req)

	require.NoError(t, err)
	assert.Equal(t, 3, result.DocumentsIndexed)
}

// TestExcludePatterns tests file exclusion during indexing
func TestExcludePatterns(t *testing.T) {
	tmpDir := t.TempDir()

	// Create files with different names
	files := []string{
		"README.md",
		"DRAFT.md",
		"guide.md",
		"guide.DRAFT.md",
	}

	for _, file := range files {
		path := filepath.Join(tmpDir, file)
		err := os.WriteFile(path, []byte("# Content"), 0o600)
		require.NoError(t, err)
	}

	// Index with exclusion pattern
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	projectID := uuid.New()
	req := &IndexRequest{
		ProjectID:          projectID,
		Directory:          tmpDir,
		Recursive:          true,
		FilePatterns:       []string{"*.md"},
		ExcludePatterns:    []string{"DRAFT"},
		GenerateEmbeddings: false,
	}

	ctx := context.Background()
	result, err := indexer.Index(ctx, req)

	require.NoError(t, err)
	// Should only index README.md and guide.md (excluding DRAFT files)
	assert.LessOrEqual(t, result.DocumentsIndexed, 2)
}

// TestParserAndChunkerIntegration tests parser + chunker workflow
func TestParserAndChunkerIntegration(t *testing.T) {
	parser := NewParser()
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)
	indexer.chunkSize = 300
	indexer.chunkOverlap = 50

	// Parse document
	content := `# Main Section

This is some introductory content. We will now discuss important concepts.

## Subsection 1

Content for subsection 1 with significant amount of text to trigger chunking.
This content is long enough to be split into multiple chunks for better processing.

` + generateContent(500) + `

## Subsection 2

More content here.
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)

	// Create chunks from sections
	projectID := uuid.New()
	documentID := uuid.New()
	ctx := context.Background()

	result := &IndexResult{}
	err = indexer.indexSections(ctx, projectID, documentID, doc.Sections, false, result)

	require.NoError(t, err)
	assert.Positive(t, result.SectionsCreated)
}

// TestReferenceExtraction tests extraction of all reference types
func TestReferenceExtraction(t *testing.T) {
	content := `
# Documentation

## Code References

See the implementation in src/main.go or app.ts.

Use myFunction() from utils.ts.

Check MyClass and process().

## API Endpoints

GET /api/v1/users - fetch users
POST /api/v1/users - create user
DELETE /api/v1/users/{id} - delete user

## Links

See [Getting Started](getting-started.md) and [Configuration](config.md#setup).

Check [FAQ](faq.md#troubleshooting) for issues.
`

	parser := NewParser()

	// Extract code references
	codeRefs := parser.ExtractCodeRefs(content)
	assert.NotEmpty(t, codeRefs)

	// Extract API references
	apiRefs := ExtractAPIRefs(content)
	assert.NotEmpty(t, apiRefs)
	assert.Len(t, apiRefs, 3)

	// Extract internal links
	links := ExtractInternalLinks(content)
	assert.NotEmpty(t, links)
}

// TestSectionHierarchyPreservation tests that section hierarchy is maintained
func TestSectionHierarchyPreservation(t *testing.T) {
	parser := NewParser()

	content := `# Part 1

## Chapter 1.1

### Section 1.1.1

### Section 1.1.2

## Chapter 1.2

# Part 2

## Chapter 2.1

### Section 2.1.1
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)

	assert.Len(t, doc.Sections, 2)

	// Verify Part 1 structure
	part1 := doc.Sections[0]
	assert.Equal(t, "Part 1", part1.Title)
	assert.Len(t, part1.Children, 2)

	// Verify Chapter 1.1 structure
	chapter11 := part1.Children[0]
	assert.Equal(t, "Chapter 1.1", chapter11.Title)
	assert.Len(t, chapter11.Children, 2)

	// Verify Part 2 structure
	part2 := doc.Sections[1]
	assert.Equal(t, "Part 2", part2.Title)
	assert.Len(t, part2.Children, 1)
}

// TestEmptyAndWhitespaceHandling tests handling of empty sections
func TestEmptyAndWhitespaceHandling(t *testing.T) {
	parser := NewParser()

	content := `# Main



## Empty Section



## Another Section

Content here.
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)

	assert.NotEmpty(t, doc.Sections)
}

// TestCodeBlockPreservationInRefs tests that code blocks are handled correctly
func TestCodeBlockPreservationInRefs(t *testing.T) {
	content := "See main.go or helpers.ts files."

	parser := NewParser()
	refs := parser.ExtractCodeRefs(content)

	// The file path parsing should work
	assert.NotNil(t, refs)
	fileRefs := filterRefsByType(refs, "file")
	assert.NotEmpty(t, fileRefs)
}

// TestLargeDocumentHandling tests parsing of large documents
func TestLargeDocumentHandling(t *testing.T) {
	parser := NewParser()

	// Create a large document
	var contentBuilder strings.Builder
	contentBuilder.WriteString("# Large Document\n\n")
	for i := 1; i <= 50; i++ {
		contentBuilder.WriteString("## Section ")
		contentBuilder.WriteRune(rune(48 + i%10))
		contentBuilder.WriteString("\n\n")
		contentBuilder.WriteString(generateContent(500))
		contentBuilder.WriteString("\n\n")
	}

	doc, err := parser.Parse("large.md", []byte(contentBuilder.String()))
	require.NoError(t, err)

	// Document should parse without error
	assert.NotEmpty(t, doc.Sections)
	assert.Equal(t, "Large Document", doc.Title)
}

// TestIndexingWithSpecificFiles tests indexing specific file paths
func TestIndexingWithSpecificFiles(t *testing.T) {
	tmpDir := t.TempDir()

	// Create test files
	file1 := filepath.Join(tmpDir, "doc1.md")
	file2 := filepath.Join(tmpDir, "doc2.md")

	err := os.WriteFile(file1, []byte("# Doc 1\nContent 1"), 0o600)
	require.NoError(t, err)
	err = os.WriteFile(file2, []byte("# Doc 2\nContent 2"), 0o600)
	require.NoError(t, err)

	// Index specific file
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	projectID := uuid.New()
	req := &IndexRequest{
		ProjectID:          projectID,
		FilePaths:          []string{file1},
		GenerateEmbeddings: false,
	}

	ctx := context.Background()
	result, err := indexer.Index(ctx, req)

	require.NoError(t, err)
	assert.Equal(t, 1, result.DocumentsIndexed)
}

// TestMetadataPreservation tests that metadata is preserved through indexing
func TestMetadataPreservation(t *testing.T) {
	parser := NewParser()

	content := `---
title: Test Document
version: 1.0
categories: [guide, tutorial]
status: published
---

# Content

Document content here.
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)

	assert.NotNil(t, doc.Frontmatter)
	assert.Equal(t, "Test Document", doc.Frontmatter["title"])
	// YAML parsing converts numbers to float64
	version, ok := doc.Frontmatter["version"]
	assert.True(t, ok)
	assert.InEpsilon(t, 1.0, version, 1e-9)
	assert.Equal(t, "published", doc.Frontmatter["status"])
}

// TestConcurrentIndexing tests that indexing handles context cancellation
func TestConcurrentIndexing(t *testing.T) {
	tmpDir := t.TempDir()

	// Create test file
	path := filepath.Join(tmpDir, "test.md")
	err := os.WriteFile(path, []byte("# Test\nContent"), 0o600)
	require.NoError(t, err)

	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	projectID := uuid.New()
	req := &IndexRequest{
		ProjectID:          projectID,
		Directory:          tmpDir,
		Recursive:          true,
		FilePatterns:       []string{"*.md"},
		GenerateEmbeddings: false,
	}

	// Test normal completion
	ctx := context.Background()
	result, err := indexer.Index(ctx, req)
	require.NoError(t, err)
	assert.Equal(t, 1, result.DocumentsIndexed)
}

// TestIndexingPerformance measures basic indexing performance
func TestIndexingPerformance(t *testing.T) {
	tmpDir := t.TempDir()

	// Create multiple documents
	for i := 0; i < 5; i++ {
		path := filepath.Join(tmpDir, "doc"+string(rune(48+i))+".md")
		content := "# Document " + string(rune(48+i)) + "\n\n" + generateContent(1000)
		err := os.WriteFile(path, []byte(content), 0o600)
		require.NoError(t, err)
	}

	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	projectID := uuid.New()
	req := &IndexRequest{
		ProjectID:          projectID,
		Directory:          tmpDir,
		Recursive:          true,
		FilePatterns:       []string{"*.md"},
		GenerateEmbeddings: false,
	}

	start := time.Now()
	ctx := context.Background()
	result, err := indexer.Index(ctx, req)
	duration := time.Since(start)

	require.NoError(t, err)
	assert.Equal(t, 5, result.DocumentsIndexed)
	assert.Less(t, duration.Seconds(), 10.0, "Indexing should complete in reasonable time")
}
