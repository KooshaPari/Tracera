package docindex

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestNewParser creates a new parser and validates configuration
func TestNewParser(t *testing.T) {
	parser := NewParser()
	assert.NotNil(t, parser)
	assert.NotNil(t, parser.md)
}

// TestParseSimpleMarkdown parses a simple markdown document
func TestParseSimpleMarkdown(t *testing.T) {
	parser := NewParser()
	content := `# Main Title

This is the introduction.

## Section 1

Content for section 1.

## Section 2

Content for section 2.
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)
	assert.NotNil(t, doc)
	assert.Equal(t, "test.md", doc.FilePath)
	assert.Equal(t, "Main Title", doc.Title)
	assert.Equal(t, content, doc.RawContent)
	assert.NotEmpty(t, doc.Sections)
}

// TestParseWithFrontmatter parses markdown with YAML frontmatter
func TestParseWithFrontmatter(t *testing.T) {
	parser := NewParser()
	content := `---
title: Test Document
author: Test Author
tags: [docs, test]
---

# Introduction

This is the content.
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)
	assert.NotNil(t, doc)
	assert.NotNil(t, doc.Frontmatter)
	assert.Equal(t, "Test Document", doc.Frontmatter["title"])
	assert.Equal(t, "Test Author", doc.Frontmatter["author"])
}

// TestParseNestedSections tests parsing of nested section hierarchy
func TestParseNestedSections(t *testing.T) {
	parser := NewParser()
	content := `# Chapter 1

Content 1.

## Section 1.1

Content 1.1.

### Subsection 1.1.1

Content 1.1.1.

## Section 1.2

Content 1.2.

# Chapter 2

Content 2.
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)
	require.Len(t, doc.Sections, 2)

	// Check first chapter
	chapter1 := doc.Sections[0]
	assert.Equal(t, "Chapter 1", chapter1.Title)
	assert.Equal(t, 1, chapter1.Level)
	assert.Len(t, chapter1.Children, 2)

	// Check nested structure
	section11 := chapter1.Children[0]
	assert.Equal(t, "Section 1.1", section11.Title)
	assert.Equal(t, 2, section11.Level)
	assert.Len(t, section11.Children, 1)

	// Check double nested
	subsection := section11.Children[0]
	assert.Equal(t, "Subsection 1.1.1", subsection.Title)
	assert.Equal(t, 3, subsection.Level)
}

// TestSectionPaths tests that section paths are correctly numbered
func TestSectionPaths(t *testing.T) {
	parser := NewParser()
	content := `# First

## First.One

## First.Two

### First.Two.One

### First.Two.Two

# Second

## Second.One
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)

	// Verify paths
	assert.Equal(t, "1", doc.Sections[0].Path)
	assert.Equal(t, "1.1", doc.Sections[0].Children[0].Path)
	assert.Equal(t, "1.2", doc.Sections[0].Children[1].Path)
	assert.Equal(t, "1.2.1", doc.Sections[0].Children[1].Children[0].Path)
	assert.Equal(t, "1.2.2", doc.Sections[0].Children[1].Children[1].Path)
	assert.Equal(t, "2", doc.Sections[1].Path)
	assert.Equal(t, "2.1", doc.Sections[1].Children[0].Path)
}

// TestExtractCodeRefsInlineCode tests inline code reference extraction
func TestExtractCodeRefsInlineCode(t *testing.T) {
	parser := NewParser()
	// ExtractCodeRefs looks for file paths with extensions
	content := "See main.go or helper.ts files."

	refs := parser.ExtractCodeRefs(content)
	assert.NotEmpty(t, refs)

	fileRefs := filterRefsByType(refs, "file")
	assert.NotEmpty(t, fileRefs)
}

// TestExtractCodeRefsFilePaths tests file path reference extraction
func TestExtractCodeRefsFilePaths(t *testing.T) {
	parser := NewParser()
	content := "Check the file src/main.go or app/components/Button.tsx for examples."

	refs := parser.ExtractCodeRefs(content)
	assert.NotEmpty(t, refs)

	fileRefs := filterRefsByType(refs, "file")
	assert.Len(t, fileRefs, 2)

	assert.Equal(t, "src/main.go", fileRefs[0].FilePath)
	assert.Equal(t, "app/components/Button.tsx", fileRefs[1].FilePath)
}

// TestExtractCodeRefsLanguageDetection tests language detection from file paths
func TestExtractCodeRefsLanguageDetection(t *testing.T) {
	// Test that detectLanguage function works correctly
	tests := []struct {
		filePath string
		expected string
	}{
		{"app.ts", "typescript"},
		{"component.tsx", "typescript"},
		{"script.js", "javascript"},
		{"main.go", "go"},
	}

	for _, test := range tests {
		lang := detectLanguage(test.filePath)
		assert.Equal(t, test.expected, lang, "Language detection failed for: %s", test.filePath)
	}
}

// TestClassifyCodeRef tests code reference classification
func TestClassifyCodeRef(t *testing.T) {
	parser := NewParser()

	tests := []struct {
		code          string
		expectedType  string
		expectedName  string
		minConfidence float64
	}{
		{"myFunction()", "function", "myFunction", 0.8},
		{"MyClass", "class", "MyClass", 0.7},
		{"MY_CONSTANT", "constant", "MY_CONSTANT", 0.75},
		{"myVar", "variable", "myVar", 0.5},
		{"module.util", "package", "module.util", 0.6},
	}

	for _, test := range tests {
		ref := parser.classifyCodeRef(test.code, 0, len(test.code))
		require.NotNil(t, ref, "Failed to classify: %s", test.code)
		assert.Equal(t, test.expectedType, ref.Type, "Type mismatch for: %s", test.code)
		assert.Equal(t, test.expectedName, ref.Name, "Name mismatch for: %s", test.code)
		assert.GreaterOrEqual(t, ref.Confidence, test.minConfidence, "Confidence too low for: %s", test.code)
	}
}

// TestEmptyCodeRef tests handling of empty code references
func TestEmptyCodeRef(t *testing.T) {
	parser := NewParser()
	ref := parser.classifyCodeRef("", 0, 0)
	assert.Nil(t, ref)
}

// TestExtractSectionContent tests content extraction for sections
func TestExtractSectionContent(t *testing.T) {
	parser := NewParser()
	content := `# Main

Introduction paragraph.

## First Section

First section content goes here.
With multiple lines.

## Second Section

Second section content.
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)

	// Check first section content
	first := doc.Sections[0].Children[0]
	assert.Equal(t, "First Section", first.Title)
	assert.NotEmpty(t, first.Content)
	assert.Contains(t, first.Content, "First section content")
}

// TestGetLineNumber tests line number calculation
func TestGetLineNumber(t *testing.T) {
	parser := NewParser()
	content := []byte("line 1\nline 2\nline 3\nline 4")

	tests := []struct {
		offset   int
		expected int
	}{
		{0, 1},
		{7, 2},  // Start of line 2
		{14, 3}, // Start of line 3
		{21, 4}, // Start of line 4
	}

	for _, test := range tests {
		line := parser.getLineNumber(content, test.offset)
		assert.Equal(t, test.expected, line, "Line number incorrect for offset %d", test.offset)
	}
}

// TestComplexMarkdownStructure tests parsing of complex markdown with various elements
func TestComplexMarkdownStructure(t *testing.T) {
	parser := NewParser()
	content := `# Documentation

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

### Prerequisites

- Go 1.21+
- PostgreSQL 14+

### Steps

1. Clone the repo
2. Install dependencies
3. Configure database

## Usage

Code:
package main

func main() {
    fmt.Println("Hello")
}

## Tables

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

## Code References

Check main.go or types.go for implementation.
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)
	assert.Equal(t, "Documentation", doc.Title)

	// Verify document parsed successfully with sections
	assert.NotEmpty(t, doc.Sections)
	assert.NotEmpty(t, doc.RawContent)
}

// TestCodeBlockPreservation tests that code blocks are preserved
func TestCodeBlockPreservation(t *testing.T) {
	parser := NewParser()
	content := `# Example

function greet(name: string): string {
  return "Hello";
}
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)
	assert.Contains(t, doc.RawContent, "function greet")
	assert.Contains(t, doc.RawContent, "Hello")
}

// TestMultipleCodeReferencesPerLine tests extraction of multiple code refs
func TestMultipleCodeReferencesPerLine(t *testing.T) {
	parser := NewParser()
	content := "Import from models.ts and utils.ts."

	refs := parser.ExtractCodeRefs(content)
	// ExtractCodeRefs finds file references
	assert.NotEmpty(t, refs)

	// Should find file references
	fileRefs := filterRefsByType(refs, "file")
	assert.GreaterOrEqual(t, len(fileRefs), 1)
}

// TestEdgeCaseEmptyDocument tests parsing of empty document
func TestEdgeCaseEmptyDocument(t *testing.T) {
	parser := NewParser()
	content := ""

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)
	assert.NotNil(t, doc)
	assert.Empty(t, doc.Title)
	assert.Empty(t, doc.Sections)
}

// TestEdgeCaseOnlyHeadings tests document with only headings
func TestEdgeCaseOnlyHeadings(t *testing.T) {
	parser := NewParser()
	content := `# First
## Sub
# Second
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)
	assert.Len(t, doc.Sections, 2)
	assert.Len(t, doc.Sections[0].Children, 1)
}

// TestFrontmatterWithoutContent tests frontmatter parsing without content
func TestFrontmatterWithoutContent(t *testing.T) {
	parser := NewParser()
	content := `---
title: Only Frontmatter
tags: [test]
---
`

	doc, err := parser.Parse("test.md", []byte(content))
	require.NoError(t, err)
	assert.Equal(t, "Only Frontmatter", doc.Title)
}

func TestHelperFunctions(t *testing.T) {
	refs := []CodeRef{
		{Type: "function", Name: "alpha"},
		{Type: "class", Name: "beta"},
	}
	ref := findRefByType(refs, "class")
	require.NotNil(t, ref)
	assert.Equal(t, "class", ref.Type)

	sections := []*Section{
		{Title: "Intro"},
		{Title: "Usage"},
	}
	section := findSectionByTitle(sections, "Usage")
	require.NotNil(t, section)
	assert.Equal(t, "Usage", section.Title)
}

// Helper functions

func findRefByType(refs []CodeRef, refType string) *CodeRef {
	for i := range refs {
		if refs[i].Type == refType {
			return &refs[i]
		}
	}
	return nil
}

func filterRefsByType(refs []CodeRef, refType string) []CodeRef {
	var filtered []CodeRef
	for _, ref := range refs {
		if ref.Type == refType {
			filtered = append(filtered, ref)
		}
	}
	return filtered
}

func findSectionByTitle(sections []*Section, title string) *Section {
	for _, s := range sections {
		if s.Title == title {
			return s
		}
	}
	return nil
}
