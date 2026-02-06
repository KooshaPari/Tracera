// Package parsers provides parsers functionality.
package parsers

import (
	"context"
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

// GoParser parses Go source files
type GoParser struct {
	projectRoot string
}

// NewGoParser creates a new Go parser
func NewGoParser(projectRoot string) *GoParser {
	return &GoParser{
		projectRoot: projectRoot,
	}
}

// ParseFile parses a Go source file
func (parser *GoParser) ParseFile(ctx context.Context, filePath string, content string) (*codeindex.ParsedFile, error) {
	_ = ctx
	start := time.Now()

	parsedFile := &codeindex.ParsedFile{
		FilePath: filePath,
		Language: codeindex.LanguageGo,
		Entities: make([]*codeindex.ParsedEntity, 0),
		Imports:  make([]codeindex.ImportRef, 0),
		Content:  content,
		Hash:     hashContent(content),
		ParsedAt: time.Now(),
	}

	// Extract module path
	parsedFile.Module = strings.TrimPrefix(filePath, parser.projectRoot)
	parsedFile.Module = strings.TrimPrefix(parsedFile.Module, "/")

	// Extract package name
	packageName := parser.extractPackageName(content)
	if packageName != "" {
		parsedFile.Module = packageName
	}

	// Parse imports
	imports := parser.parseImports(content)
	parsedFile.Imports = imports

	// Parse declarations
	entities := parser.parseDeclarations(content, filePath)
	parsedFile.Entities = entities

	_ = time.Since(start)
	return parsedFile, nil
}

// extractPackageName extracts the package name from the file
func (parser *GoParser) extractPackageName(content string) string {
	packageRegex := regexp.MustCompile(`^package\s+(\w+)`)

	lines := strings.Split(content, "\n")
	for _, line := range lines {
		if matches := packageRegex.FindStringSubmatch(line); matches != nil {
			return matches[1]
		}
	}

	return ""
}

// parseImports extracts import statements from Go file
func (parser *GoParser) parseImports(content string) []codeindex.ImportRef {
	// Match import blocks and single imports
	importBlockRegex := regexp.MustCompile(`(?m)^import\s*\(\s*([\s\S]*?)\s*\)`)
	singleImportRegex := regexp.MustCompile(`(?m)^import\s+(?:"([^"]+)"|'([^']+)')`)
	aliasImportRegex := regexp.MustCompile(`(?m)(?:(\w+)\s+)?(?:"([^"]+)"|'([^']+)')`)

	return parser.parseImportLines(content, importBlockRegex, aliasImportRegex, singleImportRegex)
}

func (parser *GoParser) parseImportLines(
	content string,
	importBlockRegex *regexp.Regexp,
	aliasImportRegex *regexp.Regexp,
	singleImportRegex *regexp.Regexp,
) []codeindex.ImportRef {
	imports := make([]codeindex.ImportRef, 0)
	lines := strings.Split(content, "\n")

	for lineIndex, line := range lines {
		imports = append(
			imports,
			parser.parseImportBlockLine(importBlockRegex, aliasImportRegex, line, lineIndex)...,
		)
		if ref, ok := parseSingleImportLine(singleImportRegex, content, line); ok {
			imports = append(imports, ref)
		}
	}

	return imports
}

func (parser *GoParser) parseImportBlockLine(
	importBlockRegex *regexp.Regexp,
	aliasImportRegex *regexp.Regexp,
	line string,
	lineIndex int,
) []codeindex.ImportRef {
	if matches := importBlockRegex.FindStringSubmatch(line); matches != nil {
		return parseImportBlockLines(aliasImportRegex, matches[1], lineIndex)
	}
	return nil
}

func parseImportBlockLines(
	aliasImportRegex *regexp.Regexp,
	importBlock string,
	lineIndex int,
) []codeindex.ImportRef {
	importLines := strings.Split(importBlock, "\n")
	imports := make([]codeindex.ImportRef, 0, len(importLines))

	for _, importLine := range importLines {
		trimmedLine := strings.TrimSpace(importLine)
		if trimmedLine == "" || strings.HasPrefix(trimmedLine, "//") {
			continue
		}

		if aliasMatches := aliasImportRegex.FindStringSubmatch(trimmedLine); aliasMatches != nil {
			alias := aliasMatches[1]
			path := aliasMatches[2]
			if path == "" {
				path = aliasMatches[3]
			}

			imports = append(imports, codeindex.ImportRef{
				ModulePath: path,
				Alias:      alias,
				Line:       lineIndex + 1,
			})
		}
	}

	return imports
}

func parseSingleImportLine(
	singleImportRegex *regexp.Regexp,
	content string,
	line string,
) (codeindex.ImportRef, bool) {
	matches := singleImportRegex.FindStringSubmatch(line)
	if matches == nil {
		return codeindex.ImportRef{}, false
	}

	path := matches[1]
	if path == "" {
		path = matches[2]
	}

	return codeindex.ImportRef{
		ModulePath: path,
		Line:       strings.Index(content, line) / len(content),
	}, true
}

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
