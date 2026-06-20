package codeindex

import (
	"regexp"
	"strings"
)

const (
	matchMinCountAnnotation   = 2
	matchMinCountImport       = 3
	matchMinCountSimpleImport = 2
)

// Parser provides language-agnostic code parsing utilities
type Parser struct {
	annotationPatterns map[string]*regexp.Regexp
}

// NewParser creates a new code parser
func NewParser() *Parser {
	return &Parser{
		annotationPatterns: map[string]*regexp.Regexp{
			"trace_implements": regexp.MustCompile(`@trace-implements\s*\(\s*["']?([^"'\s)]+)["']?\s*\)`),
			"canonical":        regexp.MustCompile(`@canonical\s*\(\s*["']?([^"'\s)]+)["']?\s*\)`),
			"same_as":          regexp.MustCompile(`@same-as\s*\(\s*["']?([^"'\s)]+)["']?\s*\)`),
			"tests":            regexp.MustCompile(`@tests\s*\(\s*["']?([^"'\s)]+)["']?\s*\)`),
			"documents":        regexp.MustCompile(`@documents\s*\(\s*["']?([^"'\s)]+)["']?\s*\)`),
		},
	}
}

// DetectLanguage detects the programming language from file extension
func (parser *Parser) DetectLanguage(filePath string) Language {
	switch {
	case strings.HasSuffix(filePath, ".ts"), strings.HasSuffix(filePath, ".tsx"):
		return LanguageTypeScript
	case strings.HasSuffix(filePath, ".js"), strings.HasSuffix(filePath, ".jsx"):
		return LanguageJavaScript
	case strings.HasSuffix(filePath, ".go"):
		return LanguageGo
	case strings.HasSuffix(filePath, ".py"):
		return LanguagePython
	case strings.HasSuffix(filePath, ".rs"):
		return LanguageRust
	case strings.HasSuffix(filePath, ".java"):
		return LanguageJava
	default:
		return ""
	}
}

// ExtractAnnotations extracts traceability annotations from code/comments
func (parser *Parser) ExtractAnnotations(content string) []Annotation {
	var annotations []Annotation
	lines := strings.Split(content, "\n")

	for lineNum, line := range lines {
		for name, pattern := range parser.annotationPatterns {
			matches := pattern.FindAllStringSubmatch(line, -1)
			for _, match := range matches {
				if len(match) >= matchMinCountAnnotation {
					annotations = append(annotations, Annotation{
						Name:  name,
						Value: match[1],
						Line:  lineNum + 1,
					})
				}
			}
		}
	}

	return annotations
}

// ExtractImports extracts import statements from code
func (parser *Parser) ExtractImports(content string, lang Language) []ImportRef {
	var imports []ImportRef
	lines := strings.Split(content, "\n")

	switch lang {
	case LanguageTypeScript, LanguageJavaScript:
		imports = parser.extractTSImports(lines)
	case LanguageGo:
		imports = parser.extractGoImports(lines)
	case LanguagePython:
		imports = parser.extractPythonImports(lines)
	case LanguageRust, LanguageJava:
		// No-op: import extraction not implemented for these languages yet.
	}

	return imports
}

// extractTSImports extracts TypeScript/JavaScript imports
func (parser *Parser) extractTSImports(lines []string) []ImportRef {
	// Pattern: import { X } from 'module'
	namedImport := regexp.MustCompile(`import\s+\{([^}]+)\}\s+from\s+['"]([^'"]+)['"]`)
	// Pattern: import X from 'module'
	defaultImport := regexp.MustCompile(`import\s+(\w+)\s+from\s+['"]([^'"]+)['"]`)
	// Pattern: import * as X from 'module'
	namespaceImport := regexp.MustCompile(`import\s+\*\s+as\s+(\w+)\s+from\s+['"]([^'"]+)['"]`)

	matchers := tsImportMatchers{
		named:     namedImport,
		def:       defaultImport,
		namespace: namespaceImport,
	}

	imports := make([]ImportRef, 0, len(lines))
	for lineNum, line := range lines {
		imports = append(imports, parser.extractTSImportLine(lineNum+1, line, matchers)...)
	}

	return imports
}

type tsImportMatchers struct {
	named     *regexp.Regexp
	def       *regexp.Regexp
	namespace *regexp.Regexp
}

func (parser *Parser) extractTSImportLine(lineNum int, line string, matchers tsImportMatchers) []ImportRef {
	if matches := matchers.namespace.FindStringSubmatch(line); len(matches) >= matchMinCountImport {
		return []ImportRef{
			{
				ModulePath:  matches[2],
				Alias:       matches[1],
				IsNamespace: true,
				Line:        lineNum,
			},
		}
	}
	if matches := matchers.def.FindStringSubmatch(line); len(matches) >= matchMinCountImport {
		return []ImportRef{
			{
				ModulePath: matches[2],
				ImportName: matches[1],
				IsDefault:  true,
				Line:       lineNum,
			},
		}
	}
	if matches := matchers.named.FindStringSubmatch(line); len(matches) >= matchMinCountImport {
		return buildNamedTSImports(matches[2], matches[1], lineNum)
	}

	return nil
}

func buildNamedTSImports(modulePath, namesCSV string, lineNum int) []ImportRef {
	names := strings.Split(namesCSV, ",")
	imports := make([]ImportRef, 0, len(names))
	for _, name := range names {
		trimmed := strings.TrimSpace(name)
		if trimmed == "" {
			continue
		}
		imports = append(imports, ImportRef{
			ModulePath: modulePath,
			ImportName: trimmed,
			Line:       lineNum,
		})
	}
	return imports
}

// extractGoImports extracts Go imports
func (parser *Parser) extractGoImports(lines []string) []ImportRef {
	inImportBlock := false

	singleImport := regexp.MustCompile(`import\s+(?:(\w+)\s+)?["']([^"']+)["']`)
	blockImport := regexp.MustCompile(`^\s*(?:(\w+)\s+)?["']([^"']+)["']`)

	matchers := goImportMatchers{
		single: singleImport,
		block:  blockImport,
	}

	var imports []ImportRef
	for lineNum, line := range lines {
		trimmed := strings.TrimSpace(line)

		var consumed bool
		inImportBlock, consumed = updateGoImportBlockState(trimmed, inImportBlock)
		if consumed {
			continue
		}

		if ref, ok := parseGoImportLine(lineNum+1, line, inImportBlock, matchers); ok {
			imports = append(imports, ref)
		}
	}

	return imports
}

type goImportMatchers struct {
	single *regexp.Regexp
	block  *regexp.Regexp
}

func updateGoImportBlockState(trimmedLine string, inImportBlock bool) (bool, bool) {
	if strings.HasPrefix(trimmedLine, "import (") {
		return true, true
	}
	if inImportBlock && trimmedLine == ")" {
		return false, true
	}
	return inImportBlock, false
}

func parseGoImportLine(lineNum int, line string, inImportBlock bool, matchers goImportMatchers) (ImportRef, bool) {
	if inImportBlock {
		matches := matchers.block.FindStringSubmatch(line)
		if len(matches) >= matchMinCountImport {
			return ImportRef{
				ModulePath: matches[2],
				Alias:      matches[1],
				Line:       lineNum,
			}, true
		}
		return ImportRef{}, false
	}

	matches := matchers.single.FindStringSubmatch(line)
	if len(matches) >= matchMinCountImport {
		return ImportRef{
			ModulePath: matches[2],
			Alias:      matches[1],
			Line:       lineNum,
		}, true
	}

	return ImportRef{}, false
}

// extractPythonImports extracts Python imports
func (parser *Parser) extractPythonImports(lines []string) []ImportRef {
	var imports []ImportRef

	fromImport := regexp.MustCompile(`from\s+(\S+)\s+import\s+(.+)`)
	simpleImport := regexp.MustCompile(`^import\s+(\S+)(?:\s+as\s+(\w+))?`)

	for lineNum, line := range lines {
		if matches := fromImport.FindStringSubmatch(line); len(matches) >= matchMinCountImport {
			names := strings.Split(matches[2], ",")
			for _, name := range names {
				name = strings.TrimSpace(name)
				if name != "" {
					imports = append(imports, ImportRef{
						ModulePath: matches[1],
						ImportName: name,
						Line:       lineNum + 1,
					})
				}
			}
		} else if matches := simpleImport.FindStringSubmatch(line); len(matches) >= matchMinCountSimpleImport {
			imports = append(imports, ImportRef{
				ModulePath: matches[1],
				Alias:      matches[2],
				Line:       lineNum + 1,
			})
		}
	}

	return imports
}
