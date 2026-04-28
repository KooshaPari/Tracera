package parsers

import (
	"regexp"
	"strings"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

// parseClassMembers extracts methods and properties from a class
func (parser *TypeScriptParser) parseClassMembers(
	lines []string,
	startLine int,
	endLine int,
	filePath string,
	className string,
) []*codeindex.ParsedEntity {
	members := make([]*codeindex.ParsedEntity, 0)

	methodRegex := regexp.MustCompile(`(?m)^\s+(?:public|private|protected)?\s*(?:async\s+)?(\w+)\s*\(([^)]*)\)`)
	propertyRegex := regexp.MustCompile(`(?m)^\s+(?:public|private|protected)?\s*(\w+)\s*:\s*([^=;]+)(?:=)?`)

	for lineIndex := startLine + 1; lineIndex < endLine && lineIndex < len(lines); lineIndex++ {
		line := lines[lineIndex]

		if matches := methodRegex.FindStringSubmatch(line); matches != nil {
			methodName := matches[1]
			params := matches[2]

			member := &codeindex.ParsedEntity{
				ID:            uuid.New(),
				Name:          methodName,
				QualifiedName: filePath + ":" + className + "." + methodName,
				Type:          codeindex.SymbolTypeMethod,
				Language:      codeindex.LanguageTypeScript,
				FilePath:      filePath,
				StartLine:     lineIndex + 1,
				ParentName:    className,
				IsAsync:       strings.Contains(line, "async"),
				Parameters:    parser.parseParameters(params),
			}
			member.EndLine = parser.findEndLine(lines, lineIndex)
			members = append(members, member)
		}

		if matches := propertyRegex.FindStringSubmatch(line); matches != nil {
			propName := matches[1]
			propType := matches[2]

			member := &codeindex.ParsedEntity{
				ID:            uuid.New(),
				Name:          propName,
				QualifiedName: filePath + ":" + className + "." + propName,
				Type:          codeindex.SymbolTypeProperty,
				Language:      codeindex.LanguageTypeScript,
				FilePath:      filePath,
				StartLine:     lineIndex + 1,
				EndLine:       lineIndex + 1,
				ParentName:    className,
				Metadata: map[string]interface{}{
					"type": propType,
				},
			}
			members = append(members, member)
		}
	}

	return members
}

// parseParameters parses function parameters
func (parser *TypeScriptParser) parseParameters(paramString string) []codeindex.Parameter {
	return parseTypeScriptParameterList(paramString)
}

func parseTypeScriptParameterList(paramString string) []codeindex.Parameter {
	trimmed := strings.TrimSpace(paramString)
	if trimmed == "" {
		return nil
	}

	parts := strings.Split(trimmed, ",")
	params := make([]codeindex.Parameter, 0, len(parts))
	for _, part := range parts {
		param, ok := parseTypeScriptParameterPart(part)
		if ok {
			params = append(params, param)
		}
	}

	return params
}

func parseTypeScriptParameterPart(rawPart string) (codeindex.Parameter, bool) {
	part := strings.TrimSpace(rawPart)
	if part == "" {
		return codeindex.Parameter{}, false
	}

	param := codeindex.Parameter{Name: part}
	param = applyTypeScriptOptional(param)
	param = applyTypeScriptSpread(param)
	param = applyTypeScriptType(param, part)

	return param, true
}

func applyTypeScriptOptional(param codeindex.Parameter) codeindex.Parameter {
	if strings.Contains(param.Name, "?") {
		param.Optional = true
		param.Name = strings.ReplaceAll(param.Name, "?", "")
	}
	return param
}

func applyTypeScriptSpread(param codeindex.Parameter) codeindex.Parameter {
	if strings.Contains(param.Name, "...") {
		param.Spread = true
		param.Name = strings.TrimPrefix(param.Name, "...")
	}
	return param
}

func applyTypeScriptType(param codeindex.Parameter, part string) codeindex.Parameter {
	if !strings.Contains(part, ":") {
		return param
	}

	bits := strings.Split(part, ":")
	param.Name = strings.TrimSpace(bits[0])
	if len(bits) > 1 {
		param.Type = strings.TrimSpace(bits[1])
	}
	return param
}
