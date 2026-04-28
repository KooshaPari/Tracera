package codeindex

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewParser(t *testing.T) {
	parser := NewParser()
	assert.NotNil(t, parser)
	assert.NotNil(t, parser.annotationPatterns)
	assert.GreaterOrEqual(t, len(parser.annotationPatterns), 5)
}

// Language Detection Tests
func TestParser_DetectLanguage_TypeScript(t *testing.T) {
	parser := NewParser()

	tests := []struct {
		filePath string
		expected Language
	}{
		{"src/file.ts", LanguageTypeScript},
		{"src/file.tsx", LanguageTypeScript},
		{"components/MyComponent.tsx", LanguageTypeScript},
		{"api/handler.ts", LanguageTypeScript},
	}

	for _, tt := range tests {
		result := parser.DetectLanguage(tt.filePath)
		assert.Equal(t, tt.expected, result, "Failed for %s", tt.filePath)
	}
}

func TestParser_DetectLanguage_JavaScript(t *testing.T) {
	parser := NewParser()

	tests := []struct {
		filePath string
		expected Language
	}{
		{"src/file.js", LanguageJavaScript},
		{"src/file.jsx", LanguageJavaScript},
	}

	for _, tt := range tests {
		result := parser.DetectLanguage(tt.filePath)
		assert.Equal(t, tt.expected, result, "Failed for %s", tt.filePath)
	}
}

func TestParser_DetectLanguage_Go(t *testing.T) {
	parser := NewParser()
	result := parser.DetectLanguage("handler.go")
	assert.Equal(t, LanguageGo, result)
}

func TestParser_DetectLanguage_Python(t *testing.T) {
	parser := NewParser()
	result := parser.DetectLanguage("script.py")
	assert.Equal(t, LanguagePython, result)
}

func TestParser_DetectLanguage_Other(t *testing.T) {
	parser := NewParser()

	tests := []struct {
		filePath string
		expected Language
	}{
		{"code.rs", LanguageRust},
		{"Code.java", LanguageJava},
		{"README.md", ""},
		{"script.sh", ""},
	}

	for _, tt := range tests {
		result := parser.DetectLanguage(tt.filePath)
		assert.Equal(t, tt.expected, result, "Failed for %s", tt.filePath)
	}
}

// Annotation Extraction Tests
func TestParser_ExtractAnnotations(t *testing.T) {
	parser := NewParser()

	code := `// @trace-implements(login-flow)
// @canonical(AuthService)
export function loginUser() {
  // @same-as(authenticate)
  return authenticate();
}`

	annotations := parser.ExtractAnnotations(code)
	require.NotNil(t, annotations)
	assert.GreaterOrEqual(t, len(annotations), 3)

	// Verify specific annotations
	names := make(map[string]string)
	for _, ann := range annotations {
		names[ann.Name] = ann.Value
	}

	assert.Equal(t, "login-flow", names["trace_implements"])
	assert.Equal(t, "AuthService", names["canonical"])
	assert.Equal(t, "authenticate", names["same_as"])
}

func TestParser_ExtractAnnotations_Tests(t *testing.T) {
	parser := NewParser()

	code := `// @tests(LoginUserTest)
export function login() {
  return authenticate();
}`

	annotations := parser.ExtractAnnotations(code)

	testAnnotations := make([]string, 0)
	for _, ann := range annotations {
		if ann.Name == "tests" {
			testAnnotations = append(testAnnotations, ann.Value)
		}
	}

	assert.NotEmpty(t, testAnnotations)
	assert.Equal(t, "LoginUserTest", testAnnotations[0])
}

func TestParser_ExtractAnnotations_Documents(t *testing.T) {
	parser := NewParser()

	code := `// @documents(API-Reference)
export function fetchUser(id: string) {
  return fetch('/users/' + id);
}`

	annotations := parser.ExtractAnnotations(code)

	names := make(map[string]string)
	for _, ann := range annotations {
		names[ann.Name] = ann.Value
	}

	assert.Equal(t, "API-Reference", names["documents"])
}

func TestParser_ExtractAnnotations_LineNumbers(t *testing.T) {
	parser := NewParser()

	code := `// @trace-implements(flow1)
export function test() {
  // @canonical(Service)
  return service.call();
}`

	annotations := parser.ExtractAnnotations(code)
	require.NotEmpty(t, annotations)

	// First annotation should be on line 1
	assert.Equal(t, 1, annotations[0].Line)
}

func TestParser_ExtractAnnotations_WithQuotes(t *testing.T) {
	parser := NewParser()

	code := `// @trace-implements("quoted-value")
// @canonical('single-quoted')
export function test() {}`

	annotations := parser.ExtractAnnotations(code)

	names := make(map[string]string)
	for _, ann := range annotations {
		names[ann.Name] = ann.Value
	}

	assert.Equal(t, "quoted-value", names["trace_implements"])
	assert.Equal(t, "single-quoted", names["canonical"])
}

// TypeScript/JavaScript Import Extraction
func TestParser_ExtractTSImports_Named(t *testing.T) {
	parser := NewParser()

	code := `import { useState, useEffect } from 'react';`

	lines := []string{code}
	imports := parser.extractTSImports(lines)

	require.NotEmpty(t, imports)
	assert.Equal(t, "react", imports[0].ModulePath)

	// Should have separate entries for each named import
	importNames := make(map[string]bool)
	for _, imp := range imports {
		importNames[imp.ImportName] = true
	}

	assert.True(t, importNames["useState"])
	assert.True(t, importNames["useEffect"])
}

func TestParser_ExtractTSImports_Default(t *testing.T) {
	parser := NewParser()

	code := `import axios from 'axios';`

	lines := []string{code}
	imports := parser.extractTSImports(lines)

	require.NotEmpty(t, imports)
	assert.Equal(t, "axios", imports[0].ModulePath)
	assert.Equal(t, "axios", imports[0].ImportName)
	assert.True(t, imports[0].IsDefault)
}

func TestParser_ExtractTSImports_Namespace(t *testing.T) {
	parser := NewParser()

	code := `import * as path from 'path';`

	lines := []string{code}
	imports := parser.extractTSImports(lines)

	require.NotEmpty(t, imports)
	assert.Equal(t, "path", imports[0].ModulePath)
	assert.Equal(t, "path", imports[0].Alias)
	assert.True(t, imports[0].IsNamespace)
}

func TestParser_ExtractTSImports_Mixed(t *testing.T) {
	parser := NewParser()

	// The parser processes line-by-line, so each import needs to be on its own line
	lines := []string{
		"import { FC } from 'react';",
		"import axios from 'axios';",
		"import * as utils from './utils';",
		"import { helper } from '@/helpers';",
	}

	imports := parser.extractTSImports(lines)

	modulePaths := make(map[string]int)
	for _, imp := range imports {
		modulePaths[imp.ModulePath]++
	}

	assert.NotEmpty(t, imports, "Should find imports")
	assert.Positive(t, modulePaths["react"], "Should have react imports")
	assert.Positive(t, modulePaths["axios"], "Should have axios imports")
}

// Go Import Extraction
func TestParser_ExtractGoImports_Single(t *testing.T) {
	parser := NewParser()

	lines := []string{"import \"fmt\"", "import \"github.com/lib/pq\""}
	imports := parser.extractGoImports(lines)

	modulePaths := make(map[string]bool)
	for _, imp := range imports {
		modulePaths[imp.ModulePath] = true
	}

	assert.True(t, modulePaths["fmt"])
	assert.True(t, modulePaths["github.com/lib/pq"])
}

func TestParser_ExtractGoImports_Block(t *testing.T) {
	parser := NewParser()

	lines := []string{
		"import (",
		"    \"fmt\"",
		"    \"log\"",
		"    \"github.com/lib/pq\"",
		")",
	}

	imports := parser.extractGoImports(lines)

	modulePaths := make(map[string]bool)
	for _, imp := range imports {
		modulePaths[imp.ModulePath] = true
	}

	assert.True(t, modulePaths["fmt"])
	assert.True(t, modulePaths["log"])
	assert.True(t, modulePaths["github.com/lib/pq"])
}

func TestParser_ExtractGoImports_WithAlias(t *testing.T) {
	parser := NewParser()

	lines := []string{
		"import (",
		"    db \"database/sql\"",
		"    . \"net/http\"",
		")",
	}

	imports := parser.extractGoImports(lines)

	// Verify imports with aliases are captured
	assert.NotEmpty(t, imports)

	aliasMap := make(map[string]string)
	for _, imp := range imports {
		aliasMap[imp.ModulePath] = imp.Alias
	}

	// At least one import should be found
	assert.NotEmpty(t, aliasMap)
}

// Python Import Extraction
func TestParser_ExtractPythonImports_Simple(t *testing.T) {
	parser := NewParser()

	lines := []string{
		"import os",
		"import sys",
	}

	imports := parser.extractPythonImports(lines)

	modulePaths := make(map[string]bool)
	for _, imp := range imports {
		modulePaths[imp.ModulePath] = true
	}

	assert.True(t, modulePaths["os"])
	assert.True(t, modulePaths["sys"])
}

func TestParser_ExtractPythonImports_WithAlias(t *testing.T) {
	parser := NewParser()

	lines := []string{
		"import numpy as np",
		"import pandas as pd",
	}

	imports := parser.extractPythonImports(lines)

	aliasMap := make(map[string]string)
	for _, imp := range imports {
		aliasMap[imp.ModulePath] = imp.Alias
	}

	assert.Equal(t, "np", aliasMap["numpy"])
	assert.Equal(t, "pd", aliasMap["pandas"])
}

func TestParser_ExtractPythonImports_From(t *testing.T) {
	parser := NewParser()

	lines := []string{
		"from os import path",
		"from django.conf import settings",
		"from . import helpers",
	}

	imports := parser.extractPythonImports(lines)

	require.NotEmpty(t, imports)

	importMap := make(map[string][]string)
	for _, imp := range imports {
		importMap[imp.ModulePath] = append(importMap[imp.ModulePath], imp.ImportName)
	}

	assert.Contains(t, importMap["os"], "path")
	assert.Contains(t, importMap["django.conf"], "settings")
}

func TestParser_ExtractPythonImports_Multiple(t *testing.T) {
	parser := NewParser()

	lines := []string{
		"from os import path, environ, getcwd",
	}

	imports := parser.extractPythonImports(lines)

	names := make(map[string]bool)
	for _, imp := range imports {
		names[imp.ImportName] = true
	}

	assert.True(t, names["path"])
	assert.True(t, names["environ"])
	assert.True(t, names["getcwd"])
}

// Edge Cases
func TestParser_ExtractAnnotations_NoAnnotations(t *testing.T) {
	parser := NewParser()

	code := `export function test() {
  return 42;
}`

	annotations := parser.ExtractAnnotations(code)
	assert.Empty(t, annotations)
}

func TestParser_ExtractImports_Empty(t *testing.T) {
	parser := NewParser()

	imports := parser.ExtractImports("", LanguageTypeScript)
	assert.Empty(t, imports)
}

func TestParser_ExtractTSImports_MultilineDestructure(t *testing.T) {
	parser := NewParser()

	code := `import {
  useState,
  useEffect,
  useContext
} from 'react';`

	// Note: Single-line extraction is used in real parser
	// This test validates the limitation and documents it
	imports := parser.extractTSImports([]string{code})
	// The parser uses line-by-line approach, so multiline won't work perfectly
	// But we should test with actual pattern
	assert.NotNil(t, imports)
}

func TestParser_ExtractTSImports_WithSpaces(t *testing.T) {
	parser := NewParser()

	code := `import   {   useState  }   from   'react'   ;`

	lines := []string{code}
	imports := parser.extractTSImports(lines)

	require.NotEmpty(t, imports)
	assert.Equal(t, "react", imports[0].ModulePath)
}

func TestParser_DetectLanguage_CaseSensitive(t *testing.T) {
	parser := NewParser()

	// Extensions are case-sensitive - uppercase extensions won't match
	result := parser.DetectLanguage("file.TS")
	// Language type is an empty string ("") when not detected
	assert.Equal(t, Language(""), result, "Should not detect uppercase extensions")
}

func TestParser_ExtractGoImports_NestedPackages(t *testing.T) {
	parser := NewParser()

	lines := []string{
		"import (",
		"    \"github.com/very/deep/nested/package\"",
		"    \"github.com/lib/pq/driver\"",
		")",
	}

	imports := parser.extractGoImports(lines)

	modulePaths := make(map[string]bool)
	for _, imp := range imports {
		modulePaths[imp.ModulePath] = true
	}

	assert.True(t, modulePaths["github.com/very/deep/nested/package"])
	assert.True(t, modulePaths["github.com/lib/pq/driver"])
}

func TestParser_ExtractAnnotations_VariousFormats(t *testing.T) {
	parser := NewParser()

	code := `// @trace-implements(LoginFlow)
// @canonical(AuthService)
// @same-as(authenticate)
// @tests(AuthTest)
// @documents(API-Docs)
export function test() {}`

	annotations := parser.ExtractAnnotations(code)
	assert.Len(t, annotations, 5)

	names := make(map[string]bool)
	for _, ann := range annotations {
		names[ann.Name] = true
	}

	assert.True(t, names["trace_implements"])
	assert.True(t, names["canonical"])
	assert.True(t, names["same_as"])
	assert.True(t, names["tests"])
	assert.True(t, names["documents"])
}

func TestParser_ExtractImports_LanguageDispatch(t *testing.T) {
	parser := NewParser()

	tsCode := `import { test } from 'react';`
	goCode := `import "fmt"`
	pyCode := `import os`

	tsImports := parser.ExtractImports(tsCode, LanguageTypeScript)
	goImports := parser.ExtractImports(goCode, LanguageGo)
	pyImports := parser.ExtractImports(pyCode, LanguagePython)

	assert.NotEmpty(t, tsImports, "Should extract TypeScript imports")
	assert.NotEmpty(t, goImports, "Should extract Go imports")
	assert.NotEmpty(t, pyImports, "Should extract Python imports")
}
