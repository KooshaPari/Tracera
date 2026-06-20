package codeindex

import (
	"crypto/sha256"
	"encoding/hex"
	"regexp"
	"strings"
)

// Analyzer provides code analysis for symbol extraction
type Analyzer struct {
	parser *Parser
}

const matchMinCount = 2

// NewAnalyzer creates a new code analyzer
func NewAnalyzer() *Analyzer {
	return &Analyzer{
		parser: NewParser(),
	}
}

// AnalyzeFile analyzes a source file and extracts code entities
func (analyzer *Analyzer) AnalyzeFile(filePath string, content string) (*FileAnalysis, error) {
	lang := analyzer.parser.DetectLanguage(filePath)
	if lang == "" {
		return nil, nil // Unsupported language
	}

	analysis := &FileAnalysis{
		FilePath:    filePath,
		Language:    lang,
		ContentHash: analyzer.hashContent(content),
		Imports:     analyzer.parser.ExtractImports(content, lang),
		Annotations: analyzer.parser.ExtractAnnotations(content),
		Symbols:     make([]SymbolInfo, 0),
		Calls:       make([]CallRef, 0),
	}

	// Extract symbols based on language
	switch lang {
	case LanguageTypeScript, LanguageJavaScript:
		analysis.Symbols = analyzer.extractTSSymbols(content)
		analysis.Calls = analyzer.extractTSCalls(content)
	case LanguageGo:
		analysis.Symbols = analyzer.extractGoSymbols(content)
		analysis.Calls = analyzer.extractGoCalls(content)
	case LanguagePython:
		analysis.Symbols = analyzer.extractPythonSymbols(content)
		analysis.Calls = analyzer.extractPythonCalls(content)
	case LanguageRust, LanguageJava:
		// Symbol/call extraction not yet implemented for these languages.
		// Leave empty to avoid partial/incorrect analysis.
	}

	return analysis, nil
}

// FileAnalysis represents the analysis result for a file
type FileAnalysis struct {
	FilePath    string       `json:"file_path"`
	Language    Language     `json:"language"`
	ContentHash string       `json:"content_hash"`
	Imports     []ImportRef  `json:"imports"`
	Annotations []Annotation `json:"annotations"`
	Symbols     []SymbolInfo `json:"symbols"`
	Calls       []CallRef    `json:"calls"`
}

// SymbolInfo represents extracted symbol information
type SymbolInfo struct {
	Name       string     `json:"name"`
	Type       SymbolType `json:"type"`
	Signature  string     `json:"signature,omitempty"`
	DocComment string     `json:"doc_comment,omitempty"`
	StartLine  int        `json:"start_line"`
	EndLine    int        `json:"end_line"`
	IsExported bool       `json:"is_exported"`
	IsAsync    bool       `json:"is_async,omitempty"`
	ParentName string     `json:"parent_name,omitempty"`
}

var (
	tsFuncPattern  = regexp.MustCompile(`^(?:export\s+)?(?:async\s+)?function\s+(\w+)`)
	tsArrowPattern = regexp.MustCompile(
		`^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>`,
	)
	tsClassPattern     = regexp.MustCompile(`^(?:export\s+)?(?:abstract\s+)?class\s+(\w+)`)
	tsInterfacePattern = regexp.MustCompile(`^(?:export\s+)?interface\s+(\w+)`)
	tsTypePattern      = regexp.MustCompile(`^(?:export\s+)?type\s+(\w+)`)
	tsConstPattern     = regexp.MustCompile(`^(?:export\s+)?const\s+(\w+)\s*=`)
	tsComponentPattern = regexp.MustCompile(
		`^(?:export\s+)?(?:const|function)\s+([A-Z]\w+).*(?:React\.FC|JSX\.Element|=>)`,
	)
)

func (a *Analyzer) hashContent(content string) string {
	hash := sha256.Sum256([]byte(content))
	return hex.EncodeToString(hash[:])
}

// extractTSSymbols extracts TypeScript/JavaScript symbols
func (a *Analyzer) extractTSSymbols(content string) []SymbolInfo {
	var symbols []SymbolInfo
	lines := strings.Split(content, "\n")

	for lineNum, line := range lines {
		trimmed := strings.TrimSpace(line)
		if symbol, ok := matchTSSymbol(trimmed, lineNum+1); ok {
			symbols = append(symbols, symbol)
		}
	}

	return symbols
}

func matchTSSymbol(trimmed string, lineNum int) (SymbolInfo, bool) {
	isExported := strings.HasPrefix(trimmed, "export")
	isAsync := strings.Contains(trimmed, "async")

	if symbol, ok := matchTSSymbolRegex(
		trimmed,
		tsComponentPattern,
		SymbolTypeComponent,
		lineNum,
		isExported,
		false,
	); ok {
		return symbol, true
	}
	if symbol, ok := matchTSSymbolRegex(trimmed, tsFuncPattern, SymbolTypeFunction, lineNum, isExported, isAsync); ok {
		return symbol, true
	}
	if symbol, ok := matchTSSymbolRegex(trimmed, tsArrowPattern, SymbolTypeFunction, lineNum, isExported, isAsync); ok {
		return symbol, true
	}
	if symbol, ok := matchTSSymbolRegex(trimmed, tsClassPattern, SymbolTypeClass, lineNum, isExported, false); ok {
		return symbol, true
	}
	if symbol, ok := matchTSSymbolRegex(
		trimmed,
		tsInterfacePattern,
		SymbolTypeInterface,
		lineNum,
		isExported,
		false,
	); ok {
		return symbol, true
	}
	if symbol, ok := matchTSSymbolRegex(trimmed, tsTypePattern, SymbolTypeType, lineNum, isExported, false); ok {
		return symbol, true
	}
	if symbol, ok := matchTSConstSymbol(trimmed, lineNum, isExported); ok {
		return symbol, true
	}

	return SymbolInfo{}, false
}

func matchTSSymbolRegex(
	trimmed string,
	re *regexp.Regexp,
	symType SymbolType,
	lineNum int,
	isExported bool,
	isAsync bool,
) (SymbolInfo, bool) {
	matches := re.FindStringSubmatch(trimmed)
	if len(matches) < matchMinCount {
		return SymbolInfo{}, false
	}
	return SymbolInfo{
		Name:       matches[1],
		Type:       symType,
		StartLine:  lineNum,
		IsExported: isExported,
		IsAsync:    isAsync,
	}, true
}

func matchTSConstSymbol(trimmed string, lineNum int, isExported bool) (SymbolInfo, bool) {
	matches := tsConstPattern.FindStringSubmatch(trimmed)
	if len(matches) < matchMinCount {
		return SymbolInfo{}, false
	}
	name, symType := classifyTSConstant(matches[1])
	return SymbolInfo{
		Name:       name,
		Type:       symType,
		StartLine:  lineNum,
		IsExported: isExported,
	}, true
}

func classifyTSConstant(name string) (string, SymbolType) {
	symType := SymbolTypeConstant
	if strings.HasPrefix(name, "use") && len(name) > 3 && name[3] >= 'A' && name[3] <= 'Z' {
		symType = SymbolTypeHook
	}
	return name, symType
}

// extractTSCalls extracts function calls from TypeScript/JavaScript
func (a *Analyzer) extractTSCalls(content string) []CallRef {
	var calls []CallRef
	lines := strings.Split(content, "\n")

	callPattern := regexp.MustCompile(`(?:await\s+)?(\w+(?:\.\w+)*)\s*\(`)

	for lineNum, line := range lines {
		matches := callPattern.FindAllStringSubmatch(line, -1)
		for _, match := range matches {
			if len(match) >= matchMinCount {
				name := match[1]
				// Skip common keywords
				if isKeyword(name) {
					continue
				}
				calls = append(calls, CallRef{
					TargetName: name,
					Line:       lineNum + 1,
					IsAsync:    strings.Contains(line, "await"),
				})
			}
		}
	}

	return calls
}

func isKeyword(name string) bool {
	keywords := map[string]bool{
		"if": true, "else": true, "for": true, "while": true, "switch": true,
		"case": true, "return": true, "throw": true, "try": true, "catch": true,
		"finally": true, "new": true, "typeof": true, "instanceof": true,
		"function": true, "class": true, "import": true, "export": true,
	}
	return keywords[name]
}
