package parsers

import (
	"regexp"
	"strings"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

// parseGoParameters parses Go function parameters
func (parser *GoParser) parseGoParameters(paramString string) []codeindex.Parameter {
	return parseGoParameterList(paramString)
}

func parseGoParameterList(paramString string) []codeindex.Parameter {
	trimmed := strings.TrimSpace(paramString)
	if trimmed == "" {
		return nil
	}

	parts := strings.Split(trimmed, ",")
	params := make([]codeindex.Parameter, 0, len(parts))
	for _, part := range parts {
		param, ok := parseGoParameterPart(part)
		if ok {
			params = append(params, param)
		}
	}

	return params
}

func parseGoParameterPart(rawPart string) (codeindex.Parameter, bool) {
	part := strings.TrimSpace(rawPart)
	if part == "" {
		return codeindex.Parameter{}, false
	}

	bits := strings.Fields(part)
	if len(bits) == 0 {
		return codeindex.Parameter{}, false
	}

	name, paramType := parseGoParameterNameAndType(bits)
	spread := strings.HasPrefix(paramType, "...")
	if spread {
		paramType = strings.TrimPrefix(paramType, "...")
	}

	return codeindex.Parameter{
		Name:   name,
		Type:   paramType,
		Spread: spread,
	}, true
}

func parseGoParameterNameAndType(bits []string) (string, string) {
	if len(bits) == 1 {
		return "", bits[0]
	}

	return bits[0], strings.Join(bits[1:], " ")
}

// extractGoCallsAndReferences extracts function calls from a line
func (parser *GoParser) extractGoCallsAndReferences(line string, lineNum int, entities []*codeindex.ParsedEntity) {
	// Match function calls: name(...) or obj.name(...)
	callRegex := regexp.MustCompile(`(\w+)\s*\(`)

	matches := callRegex.FindAllStringSubmatchIndex(line, -1)
	for _, match := range matches {
		startIdx := match[2]
		endIdx := match[3]
		if startIdx >= 0 && endIdx >= 0 && startIdx < len(line) && endIdx <= len(line) {
			targetName := line[startIdx:endIdx]

			call := codeindex.ParsedCall{
				TargetName: targetName,
				Line:       lineNum + 1,
				Column:     startIdx,
			}

			if len(entities) > 0 {
				entities[len(entities)-1].Calls = append(entities[len(entities)-1].Calls, call)
			}
		}
	}
}

// extractGoDocComment extracts the documentation comment for a Go declaration
func (parser *GoParser) extractGoDocComment(lines []string, lineNum int) string {
	if lineNum == 0 {
		return ""
	}

	docLines := make([]string, 0)

	// Look backwards for comment lines
	for lineIndex := lineNum - 1; lineIndex >= 0; lineIndex-- {
		line := strings.TrimSpace(lines[lineIndex])

		if strings.HasPrefix(line, "//") {
			docLines = append([]string{line}, docLines...)
			continue
		}
		break
	}

	return strings.Join(docLines, "\n")
}

// findEndLine finds the end line of a Go block
func (parser *GoParser) findEndLine(lines []string, startLine int) int {
	braceCount := 0
	foundOpening := false

	for lineIndex := startLine; lineIndex < len(lines); lineIndex++ {
		line := lines[lineIndex]
		for _, ch := range line {
			switch ch {
			case '{':
				braceCount++
				foundOpening = true
			case '}':
				braceCount--
				if foundOpening && braceCount == 0 {
					return lineIndex + 1
				}
			}
		}
	}

	return startLine + 1
}

// extractEntityContent extracts source code for an entity
func (parser *GoParser) extractEntityContent(lines []string, startLine, endLine int) string {
	if endLine > len(lines) {
		endLine = len(lines)
	}
	if startLine < 0 {
		startLine = 0
	}
	if startLine >= endLine {
		return ""
	}

	return strings.Join(lines[startLine:endLine], "\n")
}

// startsWithUppercase checks if a string starts with uppercase (exported in Go)
func startsWithUppercase(s string) bool {
	if len(s) == 0 {
		return false
	}
	return s[0] >= 'A' && s[0] <= 'Z'
}
