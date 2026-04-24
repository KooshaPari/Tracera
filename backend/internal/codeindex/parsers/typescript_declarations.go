package parsers

import (
	"fmt"
	"regexp"
	"strings"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

// parseTopLevelDeclarations extracts function, class, interface, and type declarations
func (parser *TypeScriptParser) parseTopLevelDeclarations(content string, filePath string) []*codeindex.ParsedEntity {
	lines := strings.Split(content, "\n")

	// Function declarations: function name(...) or const name = (...) =>
	functionRegex := regexp.MustCompile(`(?m)^(?:export\s+)?(async\s+)?function\s+(\w+)\s*\(([^)]*)\)`)
	arrowFunctionRegex := regexp.MustCompile(
		`(?m)^(?:const|let|var)\s+(\w+)\s*:\s*(?:AsyncFunctionComponent|React\.FC)?` +
			`\s*=\s*(?:async\s+)?\(([^)]*)\)\s*(?:=>|{)`,
	)

	// Class declarations
	classRegex := regexp.MustCompile(
		`(?m)^(?:export\s+)?(abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?`,
	)

	// Interface declarations
	interfaceRegex := regexp.MustCompile(`(?m)^(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+([^{]+))?`)

	// Type declarations
	typeRegex := regexp.MustCompile(`(?m)^(?:export\s+)?type\s+(\w+)\s*=`)

	return parser.parseTopLevelDeclarationsFromLines(
		lines,
		filePath,
		functionRegex,
		arrowFunctionRegex,
		classRegex,
		interfaceRegex,
		typeRegex,
	)
}

func (parser *TypeScriptParser) parseTopLevelDeclarationsFromLines(
	lines []string,
	filePath string,
	functionRegex *regexp.Regexp,
	arrowFunctionRegex *regexp.Regexp,
	classRegex *regexp.Regexp,
	interfaceRegex *regexp.Regexp,
	typeRegex *regexp.Regexp,
) []*codeindex.ParsedEntity {
	entities := make([]*codeindex.ParsedEntity, 0)
	for lineNum, line := range lines {
		trimmedLine := strings.TrimSpace(line)
		if shouldSkipTypeScriptLine(trimmedLine) {
			continue
		}

		entities = append(
			entities,
			parser.parseTopLevelLine(
				line,
				lineNum,
				lines,
				filePath,
				functionRegex,
				arrowFunctionRegex,
				classRegex,
				interfaceRegex,
				typeRegex,
			)...,
		)

		// Extract calls and references
		parser.extractCallsAndReferences(line, lineNum, entities)
	}

	// Extract doc comments
	parser.attachDocComments(lines, entities)

	return entities
}

func shouldSkipTypeScriptLine(trimmedLine string) bool {
	return trimmedLine == "" || strings.HasPrefix(trimmedLine, "//")
}

func (parser *TypeScriptParser) parseTopLevelLine(
	line string,
	lineNum int,
	lines []string,
	filePath string,
	functionRegex *regexp.Regexp,
	arrowFunctionRegex *regexp.Regexp,
	classRegex *regexp.Regexp,
	interfaceRegex *regexp.Regexp,
	typeRegex *regexp.Regexp,
) []*codeindex.ParsedEntity {
	entities := make([]*codeindex.ParsedEntity, 0, 5)

	if entity := parser.parseFunctionDeclaration(functionRegex, line, lineNum, lines, filePath); entity != nil {
		entities = append(entities, entity)
	}

	arrowEntity := parser.parseArrowFunctionDeclaration(
		arrowFunctionRegex,
		line,
		lineNum,
		lines,
		filePath,
	)
	if arrowEntity != nil {
		entities = append(entities, arrowEntity)
	}

	if entity := parser.parseClassDeclaration(classRegex, line, lineNum, lines, filePath); entity != nil {
		entities = append(entities, entity)
	}
	if entity := parser.parseInterfaceDeclaration(interfaceRegex, line, lineNum, lines, filePath); entity != nil {
		entities = append(entities, entity)
	}
	if entity := parser.parseTypeDeclaration(typeRegex, line, lineNum, lines, filePath); entity != nil {
		entities = append(entities, entity)
	}

	return entities
}

func (parser *TypeScriptParser) parseFunctionDeclaration(
	re *regexp.Regexp,
	line string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(line)
	if matches == nil {
		return nil
	}

	isAsync := matches[1] != ""
	name := matches[2]
	params := matches[3]

	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeFunction,
		Language:      codeindex.LanguageTypeScript,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsAsync:       isAsync,
		IsExported:    strings.Contains(line, "export"),
		Parameters:    parser.parseParameters(params),
		Annotations:   parser.extractAnnotations(line),
		Signature:     fmt.Sprintf("%s(%s)", name, params),
	}

	parser.finalizeEntity(entity, lines, lineNum)
	return entity
}

func (parser *TypeScriptParser) parseArrowFunctionDeclaration(
	re *regexp.Regexp,
	line string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(line)
	if matches == nil {
		return nil
	}

	name := matches[1]
	params := matches[2]

	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeComponent,
		Language:      codeindex.LanguageTypeScript,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsAsync:       strings.Contains(line, "async"),
		IsExported:    false,
		Parameters:    parser.parseParameters(params),
		Annotations:   parser.extractAnnotations(line),
		Signature:     fmt.Sprintf("%s(%s)", name, params),
	}

	parser.finalizeEntity(entity, lines, lineNum)
	return entity
}

func (parser *TypeScriptParser) parseClassDeclaration(
	re *regexp.Regexp,
	line string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(line)
	if matches == nil {
		return nil
	}

	name := matches[2]
	extends := matches[3]

	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeClass,
		Language:      codeindex.LanguageTypeScript,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsExported:    strings.Contains(line, "export"),
		Annotations:   parser.extractAnnotations(line),
	}
	if extends != "" {
		entity.Metadata = map[string]interface{}{
			"extends": extends,
		}
	}

	parser.finalizeEntity(entity, lines, lineNum)
	entity.Properties = parser.parseClassMembers(lines, lineNum, entity.EndLine, filePath, name)
	return entity
}

func (parser *TypeScriptParser) parseInterfaceDeclaration(
	re *regexp.Regexp,
	line string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(line)
	if matches == nil {
		return nil
	}

	name := matches[1]
	extends := matches[2]

	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeInterface,
		Language:      codeindex.LanguageTypeScript,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsExported:    strings.Contains(line, "export"),
		Annotations:   parser.extractAnnotations(line),
	}
	if extends != "" {
		entity.Metadata = map[string]interface{}{
			"extends": extends,
		}
	}

	parser.finalizeEntity(entity, lines, lineNum)
	return entity
}

func (parser *TypeScriptParser) parseTypeDeclaration(
	re *regexp.Regexp,
	line string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(line)
	if matches == nil {
		return nil
	}

	name := matches[1]

	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeType,
		Language:      codeindex.LanguageTypeScript,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsExported:    strings.Contains(line, "export"),
		Annotations:   parser.extractAnnotations(line),
	}

	parser.finalizeEntity(entity, lines, lineNum)
	return entity
}

func (parser *TypeScriptParser) finalizeEntity(entity *codeindex.ParsedEntity, lines []string, lineNum int) {
	entity.EndLine = parser.findEndLine(lines, lineNum)
	entity.Content = parser.extractEntityContent(lines, lineNum, entity.EndLine)
}
