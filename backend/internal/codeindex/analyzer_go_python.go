package codeindex

import (
	"regexp"
	"strings"
)

const (
	matchMinCountGoMethod = 4
	matchMinCountType     = 3
	matchMinCountDefault  = 2
)

// extractGoSymbols extracts Go symbols
func (extractor *Analyzer) extractGoSymbols(content string) []SymbolInfo {
	var symbols []SymbolInfo
	lines := strings.Split(content, "\n")

	funcPattern := regexp.MustCompile(`^func\s+(?:\((\w+)\s+\*?(\w+)\)\s+)?(\w+)\s*\(`)
	typePattern := regexp.MustCompile(`^type\s+(\w+)\s+(struct|interface)`)
	constPattern := regexp.MustCompile(`^(?:const|var)\s+(\w+)`)

	for lineNum, line := range lines {
		trimmed := strings.TrimSpace(line)

		if extractor.appendGoFuncSymbol(&symbols, funcPattern, trimmed, lineNum) {
			continue
		}
		if extractor.appendGoTypeSymbol(&symbols, typePattern, trimmed, lineNum) {
			continue
		}
		extractor.appendGoConstSymbol(&symbols, constPattern, trimmed, lineNum)
	}

	return symbols
}

func (analyzer *Analyzer) appendGoFuncSymbol(
	symbols *[]SymbolInfo,
	pattern *regexp.Regexp,
	trimmed string,
	lineNum int,
) bool {
	matches := pattern.FindStringSubmatch(trimmed)
	if len(matches) < matchMinCountGoMethod {
		return false
	}

	name := matches[3]
	symType := SymbolTypeFunction
	var parentName string

	if matches[2] != "" {
		symType = SymbolTypeMethod
		parentName = matches[2]
	}

	// Check if it's a handler (common patterns)
	if strings.HasSuffix(name, "Handler") || strings.HasPrefix(name, "Handle") {
		symType = SymbolTypeHandler
	}

	*symbols = append(*symbols, SymbolInfo{
		Name:       name,
		Type:       symType,
		StartLine:  lineNum + 1,
		IsExported: name[0] >= 'A' && name[0] <= 'Z',
		ParentName: parentName,
	})
	return true
}

func (analyzer *Analyzer) appendGoTypeSymbol(
	symbols *[]SymbolInfo,
	pattern *regexp.Regexp,
	trimmed string,
	lineNum int,
) bool {
	matches := pattern.FindStringSubmatch(trimmed)
	if len(matches) < matchMinCountType {
		return false
	}

	name := matches[1]
	symType := SymbolTypeStruct
	if matches[2] == "interface" {
		symType = SymbolTypeInterface
	}

	*symbols = append(*symbols, SymbolInfo{
		Name:       name,
		Type:       symType,
		StartLine:  lineNum + 1,
		IsExported: name[0] >= 'A' && name[0] <= 'Z',
	})
	return true
}

func (analyzer *Analyzer) appendGoConstSymbol(
	symbols *[]SymbolInfo,
	pattern *regexp.Regexp,
	trimmed string,
	lineNum int,
) {
	matches := pattern.FindStringSubmatch(trimmed)
	if len(matches) < matchMinCountDefault {
		return
	}
	name := matches[1]
	*symbols = append(*symbols, SymbolInfo{
		Name:       name,
		Type:       SymbolTypeConstant,
		StartLine:  lineNum + 1,
		IsExported: name[0] >= 'A' && name[0] <= 'Z',
	})
}

// extractGoCalls extracts function calls from Go code
func (analyzer *Analyzer) extractGoCalls(content string) []CallRef {
	var calls []CallRef
	lines := strings.Split(content, "\n")
	callPattern := regexp.MustCompile(`(\w+(?:\.\w+)*)\s*\(`)

	for lineNum, line := range lines {
		if analyzer.shouldSkipGoLine(line) {
			continue
		}
		calls = append(calls, analyzer.processGoLineMatches(line, lineNum, callPattern)...)
	}

	return calls
}

func (analyzer *Analyzer) shouldSkipGoLine(line string) bool {
	return strings.HasPrefix(strings.TrimSpace(line), "func ")
}

func (analyzer *Analyzer) processGoLineMatches(line string, lineNum int, pattern *regexp.Regexp) []CallRef {
	var calls []CallRef
	matches := pattern.FindAllStringSubmatch(line, -1)
	for _, match := range matches {
		if len(match) < matchMinCountDefault {
			continue
		}
		name := match[1]
		if isGoKeyword(name) {
			continue
		}
		calls = append(calls, CallRef{
			TargetName: name,
			Line:       lineNum + 1,
		})
	}
	return calls
}

func isGoKeyword(name string) bool {
	keywords := map[string]bool{
		"if": true, "else": true, "for": true, "range": true, "switch": true,
		"case": true, "return": true, "go": true, "defer": true, "select": true,
		"func": true, "type": true, "struct": true, "interface": true,
		"make": true, "new": true, "append": true, "len": true, "cap": true,
		"panic": true, "recover": true, "close": true, "delete": true,
	}
	return keywords[name]
}

// extractPythonSymbols extracts Python symbols
func (analyzer *Analyzer) extractPythonSymbols(content string) []SymbolInfo {
	var symbols []SymbolInfo
	lines := strings.Split(content, "\n")

	funcPattern := regexp.MustCompile(`^(?:async\s+)?def\s+(\w+)\s*\(`)
	classPattern := regexp.MustCompile(`^class\s+(\w+)`)

	for lineNum, line := range lines {
		trimmed := strings.TrimSpace(line)
		isAsync := strings.HasPrefix(trimmed, "async")

		if matches := funcPattern.FindStringSubmatch(trimmed); len(matches) >= matchMinCountDefault {
			name := matches[1]
			symType := SymbolTypeFunction

			// Check for handler patterns
			if strings.HasSuffix(name, "_handler") || strings.HasPrefix(name, "handle_") {
				symType = SymbolTypeHandler
			}

			symbols = append(symbols, SymbolInfo{
				Name:       name,
				Type:       symType,
				StartLine:  lineNum + 1,
				IsExported: !strings.HasPrefix(name, "_"),
				IsAsync:    isAsync,
			})
		} else if matches := classPattern.FindStringSubmatch(trimmed); len(matches) >= matchMinCountDefault {
			symbols = append(symbols, SymbolInfo{
				Name:       matches[1],
				Type:       SymbolTypeClass,
				StartLine:  lineNum + 1,
				IsExported: !strings.HasPrefix(matches[1], "_"),
			})
		}
	}

	return symbols
}

// extractPythonCalls extracts function calls from Python code
func (analyzer *Analyzer) extractPythonCalls(content string) []CallRef {
	var calls []CallRef
	lines := strings.Split(content, "\n")
	callPattern := regexp.MustCompile(`(?:await\s+)?(\w+(?:\.\w+)*)\s*\(`)

	for lineNum, line := range lines {
		if analyzer.shouldSkipPythonLine(line) {
			continue
		}
		calls = append(calls, analyzer.processPythonLineMatches(line, lineNum, callPattern)...)
	}

	return calls
}

func (analyzer *Analyzer) shouldSkipPythonLine(line string) bool {
	return strings.Contains(line, "def ")
}

func (analyzer *Analyzer) processPythonLineMatches(line string, lineNum int, pattern *regexp.Regexp) []CallRef {
	var calls []CallRef
	matches := pattern.FindAllStringSubmatch(line, -1)
	for _, match := range matches {
		if len(match) < matchMinCountDefault {
			continue
		}
		name := match[1]
		if isPythonKeyword(name) {
			continue
		}
		calls = append(calls, CallRef{
			TargetName: name,
			Line:       lineNum + 1,
			IsAsync:    strings.Contains(line, "await"),
		})
	}
	return calls
}

func isPythonKeyword(name string) bool {
	keywords := map[string]bool{
		"if": true, "else": true, "elif": true, "for": true, "while": true,
		"try": true, "except": true, "finally": true, "with": true, "as": true,
		"return": true, "yield": true, "raise": true, "pass": true, "break": true,
		"continue": true, "import": true, "from": true, "class": true, "def": true,
		"lambda": true, "and": true, "or": true, "not": true, "in": true, "is": true,
		"print": true, "len": true, "range": true, "list": true, "dict": true,
		"str": true, "int": true, "float": true, "bool": true, "type": true,
	}
	return keywords[name]
}
