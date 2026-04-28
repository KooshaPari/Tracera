package parsers

import (
	"fmt"
	"regexp"
	"strings"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

// parseDeclarations parses function and type declarations
func (parser *GoParser) parseDeclarations(content string, filePath string) []*codeindex.ParsedEntity {
	lines := strings.Split(content, "\n")
	return parser.parseDeclarationsFromLines(lines, filePath)
}

func (parser *GoParser) parseDeclarationsFromLines(
	lines []string,
	filePath string,
) []*codeindex.ParsedEntity {
	entities := make([]*codeindex.ParsedEntity, 0)

	// Regex patterns for Go declarations
	functionRegex := regexp.MustCompile(
		`^func\s+` +
			`(?:\((\w+|\*\w+)\s+(\*?\w+)\)\s+)?` +
			`(\w+)\s*\(([^)]*)\)(?:\s*\(([^)]*)\))?`,
	)
	structRegex := regexp.MustCompile(`^type\s+(\w+)\s+struct`)
	interfaceRegex := regexp.MustCompile(`^type\s+(\w+)\s+interface`)
	constRegex := regexp.MustCompile(`^const\s+(\w+)\s*(?:=|\s)`)
	varRegex := regexp.MustCompile(`^var\s+(\w+)\s*(?:=|\s)`)

	for lineNum, line := range lines {
		trimmedLine := strings.TrimSpace(line)
		if shouldSkipGoLine(trimmedLine) {
			continue
		}

		entities = append(
			entities,
			parser.parseDeclarationLine(
				trimmedLine,
				lineNum,
				lines,
				filePath,
				functionRegex,
				structRegex,
				interfaceRegex,
				constRegex,
				varRegex,
			)...,
		)

		// Extract function calls and references
		parser.extractGoCallsAndReferences(trimmedLine, lineNum, entities)
	}

	return entities
}

func shouldSkipGoLine(trimmedLine string) bool {
	return trimmedLine == "" || strings.HasPrefix(trimmedLine, "//")
}

func (parser *GoParser) parseDeclarationLine(
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
	functionRegex *regexp.Regexp,
	structRegex *regexp.Regexp,
	interfaceRegex *regexp.Regexp,
	constRegex *regexp.Regexp,
	varRegex *regexp.Regexp,
) []*codeindex.ParsedEntity {
	entities := make([]*codeindex.ParsedEntity, 0, 5)

	functionEntity := parser.parseFunctionDeclaration(
		functionRegex,
		trimmedLine,
		lineNum,
		lines,
		filePath,
	)
	if functionEntity != nil {
		entities = append(entities, functionEntity)
	}

	structEntity := parser.parseStructDeclaration(
		structRegex,
		trimmedLine,
		lineNum,
		lines,
		filePath,
	)
	if structEntity != nil {
		entities = append(entities, structEntity)
	}
	entity := parser.parseInterfaceDeclaration(
		interfaceRegex,
		trimmedLine,
		lineNum,
		lines,
		filePath,
	)
	if entity != nil {
		entities = append(entities, entity)
	}
	if entity := parser.parseConstDeclaration(constRegex, trimmedLine, lineNum, lines, filePath); entity != nil {
		entities = append(entities, entity)
	}
	if entity := parser.parseVarDeclaration(varRegex, trimmedLine, lineNum, lines, filePath); entity != nil {
		entities = append(entities, entity)
	}

	return entities
}

func (parser *GoParser) parseFunctionDeclaration(
	re *regexp.Regexp,
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return nil
	}

	receiver := matches[1]
	receiverType := matches[2]
	name := matches[3]
	params := matches[4]
	returnTypes := matches[5]

	entityType := codeindex.SymbolTypeFunction
	if receiver != "" {
		entityType = codeindex.SymbolTypeMethod
	}

	parentName := ""
	if receiverType != "" {
		parentName = strings.TrimPrefix(receiverType, "*")
	}

	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          entityType,
		Language:      codeindex.LanguageGo,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		ParentName:    parentName,
		IsExported:    startsWithUppercase(name),
		Parameters:    parser.parseGoParameters(params),
		Signature:     fmt.Sprintf("%s(%s)", name, params),
		Metadata: map[string]interface{}{
			"return_types": returnTypes,
		},
	}

	if receiver != "" {
		entity.Metadata["receiver"] = receiver
		entity.Metadata["receiver_type"] = receiverType
	}

	parser.finalizeBlockEntity(entity, lines, lineNum)
	return entity
}

func (parser *GoParser) parseStructDeclaration(
	re *regexp.Regexp,
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return nil
	}

	name := matches[1]
	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeStruct,
		Language:      codeindex.LanguageGo,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsExported:    startsWithUppercase(name),
	}

	parser.finalizeBlockEntity(entity, lines, lineNum)
	entity.Properties = parser.parseStructFields(lines, lineNum, entity.EndLine, filePath, name)
	return entity
}

func (parser *GoParser) parseInterfaceDeclaration(
	re *regexp.Regexp,
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return nil
	}

	name := matches[1]
	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeInterface,
		Language:      codeindex.LanguageGo,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsExported:    startsWithUppercase(name),
	}

	parser.finalizeBlockEntity(entity, lines, lineNum)
	entity.Properties = parser.parseInterfaceMethods(lines, lineNum, entity.EndLine, filePath, name)
	return entity
}

func (parser *GoParser) parseConstDeclaration(
	re *regexp.Regexp,
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return nil
	}

	name := matches[1]
	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeConstant,
		Language:      codeindex.LanguageGo,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		EndLine:       lineNum + 1,
		IsExported:    startsWithUppercase(name),
		DocComment:    parser.extractGoDocComment(lines, lineNum),
		Content:       trimmedLine,
	}
	return entity
}

func (parser *GoParser) parseVarDeclaration(
	re *regexp.Regexp,
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return nil
	}

	name := matches[1]
	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          name,
		QualifiedName: filePath + ":" + name,
		Type:          codeindex.SymbolTypeVariable,
		Language:      codeindex.LanguageGo,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		EndLine:       lineNum + 1,
		IsExported:    startsWithUppercase(name),
		DocComment:    parser.extractGoDocComment(lines, lineNum),
		Content:       trimmedLine,
	}
	return entity
}

func (parser *GoParser) finalizeBlockEntity(entity *codeindex.ParsedEntity, lines []string, lineNum int) {
	entity.EndLine = parser.findEndLine(lines, lineNum)
	entity.Content = parser.extractEntityContent(lines, lineNum, entity.EndLine)
	entity.DocComment = parser.extractGoDocComment(lines, lineNum)
}

// parseStructFields extracts struct fields
func (parser *GoParser) parseStructFields(
	lines []string,
	startLine int,
	endLine int,
	filePath string,
	structName string,
) []*codeindex.ParsedEntity {
	fields := make([]*codeindex.ParsedEntity, 0)
	fieldRegex := regexp.MustCompile("^(\\w+)\\s+([^\\s]+)(?:\\s+`([^`]+)`)?") // match field name, type, optional tags

	for lineIndex := startLine + 1; lineIndex < endLine && lineIndex < len(lines); lineIndex++ {
		line := strings.TrimSpace(lines[lineIndex])

		if line == "" || strings.HasPrefix(line, "//") {
			continue
		}

		if matches := fieldRegex.FindStringSubmatch(line); matches != nil {
			fieldName := matches[1]
			fieldType := matches[2]
			tags := matches[3]

			field := &codeindex.ParsedEntity{
				ID:            uuid.New(),
				Name:          fieldName,
				QualifiedName: filePath + ":" + structName + "." + fieldName,
				Type:          codeindex.SymbolTypeProperty,
				Language:      codeindex.LanguageGo,
				FilePath:      filePath,
				StartLine:     lineIndex + 1,
				EndLine:       lineIndex + 1,
				ParentName:    structName,
				IsExported:    startsWithUppercase(fieldName),
				Metadata: map[string]interface{}{
					"type": fieldType,
					"tags": tags,
				},
			}

			fields = append(fields, field)
		}
	}

	return fields
}

// parseInterfaceMethods extracts interface methods
func (parser *GoParser) parseInterfaceMethods(
	lines []string,
	startLine int,
	endLine int,
	filePath string,
	interfaceName string,
) []*codeindex.ParsedEntity {
	methods := make([]*codeindex.ParsedEntity, 0)
	methodRegex := regexp.MustCompile(`^(\w+)\s*\(([^)]*)\)(?:\s*\(([^)]*)\))?`)

	for lineIndex := startLine + 1; lineIndex < endLine && lineIndex < len(lines); lineIndex++ {
		line := strings.TrimSpace(lines[lineIndex])

		if line == "" || strings.HasPrefix(line, "//") {
			continue
		}

		if matches := methodRegex.FindStringSubmatch(line); matches != nil {
			methodName := matches[1]
			params := matches[2]
			returnTypes := matches[3]

			method := &codeindex.ParsedEntity{
				ID:            uuid.New(),
				Name:          methodName,
				QualifiedName: filePath + ":" + interfaceName + "." + methodName,
				Type:          codeindex.SymbolTypeMethod,
				Language:      codeindex.LanguageGo,
				FilePath:      filePath,
				StartLine:     lineIndex + 1,
				EndLine:       lineIndex + 1,
				ParentName:    interfaceName,
				IsExported:    startsWithUppercase(methodName),
				Parameters:    parser.parseGoParameters(params),
				Signature:     fmt.Sprintf("%s(%s)", methodName, params),
				Metadata: map[string]interface{}{
					"return_types": returnTypes,
				},
			}

			methods = append(methods, method)
		}
	}

	return methods
}
