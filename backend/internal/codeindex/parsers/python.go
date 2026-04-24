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

// PythonParser parses Python source files
type PythonParser struct {
	projectRoot string
}

// NewPythonParser creates a new Python parser
func NewPythonParser(projectRoot string) *PythonParser {
	return &PythonParser{
		projectRoot: projectRoot,
	}
}

// ParseFile parses a Python source file
func (parser *PythonParser) ParseFile(
	ctx context.Context,
	filePath string,
	content string,
) (*codeindex.ParsedFile, error) {
	_ = ctx
	start := time.Now()

	parsedFile := &codeindex.ParsedFile{
		FilePath: filePath,
		Language: codeindex.LanguagePython,
		Entities: make([]*codeindex.ParsedEntity, 0),
		Imports:  make([]codeindex.ImportRef, 0),
		Content:  content,
		Hash:     hashContent(content),
		ParsedAt: time.Now(),
	}

	// Extract module path
	parsedFile.Module = strings.TrimPrefix(filePath, parser.projectRoot)
	parsedFile.Module = strings.TrimPrefix(parsedFile.Module, "/")
	parsedFile.Module = strings.TrimSuffix(parsedFile.Module, ".py")

	// Parse imports
	imports := parser.parseImports(content)
	parsedFile.Imports = imports

	// Parse declarations
	entities := parser.parseDeclarations(content, filePath)
	parsedFile.Entities = entities

	_ = time.Since(start)
	return parsedFile, nil
}

// parseImports extracts import statements from Python file
func (parser *PythonParser) parseImports(content string) []codeindex.ImportRef {
	return parsePythonImports(content)
}

func parsePythonImports(content string) []codeindex.ImportRef {
	imports := make([]codeindex.ImportRef, 0)
	lines := strings.Split(content, "\n")

	// Match: import module or import module as alias
	importRegex := regexp.MustCompile(`^import\s+([\w.]+)(?:\s+as\s+(\w+))?`)
	// Match: from module import name or from module import name as alias
	fromImportRegex := regexp.MustCompile(`^from\s+([\w.]+)\s+import\s+(.+)`)

	for lineNum, line := range lines {
		trimmedLine := strings.TrimSpace(line)

		if ref, ok := parsePythonStandardImport(importRegex, trimmedLine, lineNum); ok {
			imports = append(imports, ref)
		}

		imports = append(
			imports,
			parsePythonFromImport(fromImportRegex, trimmedLine, lineNum)...,
		)
	}

	return imports
}

func parsePythonStandardImport(
	importRegex *regexp.Regexp,
	trimmedLine string,
	lineNum int,
) (codeindex.ImportRef, bool) {
	matches := importRegex.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return codeindex.ImportRef{}, false
	}

	modulePath := matches[1]
	alias := matches[2]

	return codeindex.ImportRef{
		ModulePath: modulePath,
		ImportName: modulePath,
		Alias:      alias,
		Line:       lineNum + 1,
	}, true
}

func parsePythonFromImport(
	fromImportRegex *regexp.Regexp,
	trimmedLine string,
	lineNum int,
) []codeindex.ImportRef {
	matches := fromImportRegex.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return nil
	}

	modulePath := matches[1]
	importNames := matches[2]

	return parsePythonImportNames(modulePath, importNames, lineNum)
}

func parsePythonImportNames(
	modulePath string,
	importNames string,
	lineNum int,
) []codeindex.ImportRef {
	namesParts := strings.Split(importNames, ",")
	imports := make([]codeindex.ImportRef, 0, len(namesParts))

	for _, namePart := range namesParts {
		namePart = strings.TrimSpace(namePart)
		if namePart == "" || namePart == "*" {
			continue
		}

		importName, alias := parsePythonImportAlias(namePart)
		imports = append(imports, codeindex.ImportRef{
			ModulePath: modulePath,
			ImportName: importName,
			Alias:      alias,
			Line:       lineNum + 1,
		})
	}

	return imports
}

func parsePythonImportAlias(namePart string) (string, string) {
	if strings.Contains(namePart, " as ") {
		parts := strings.Split(namePart, " as ")
		return strings.TrimSpace(parts[0]), strings.TrimSpace(parts[1])
	}
	return namePart, ""
}

// parseDeclarations parses function and class declarations
func (parser *PythonParser) parseDeclarations(content string, filePath string) []*codeindex.ParsedEntity {
	lines := strings.Split(content, "\n")
	return parser.parseDeclarationsFromLines(lines, filePath)
}

func (parser *PythonParser) parseDeclarationsFromLines(
	lines []string,
	filePath string,
) []*codeindex.ParsedEntity {
	entities := make([]*codeindex.ParsedEntity, 0)

	// Regex patterns for Python declarations
	functionRegex := regexp.MustCompile(`^(async\s+)?def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:`)
	classRegex := regexp.MustCompile(`^class\s+(\w+)(?:\(([^)]*)\))?:`)
	decoratorRegex := regexp.MustCompile(`^@(\w+(?:\.\w+)*)(?:\(([^)]*)\))?`)

	var decorators []codeindex.Annotation

	for lineNum, line := range lines {
		trimmedLine := strings.TrimSpace(line)

		// Skip empty lines and comments
		if shouldSkipPythonLine(trimmedLine) {
			continue
		}

		var handled bool
		decorators, handled = parser.parseDecorator(decoratorRegex, trimmedLine, decorators)
		if handled {
			continue
		}

		lineEntities, nextDecorators := parser.parseDeclarationLine(
			trimmedLine,
			lineNum,
			lines,
			filePath,
			decorators,
			functionRegex,
			classRegex,
		)
		if len(lineEntities) > 0 {
			entities = append(entities, lineEntities...)
		}
		decorators = nextDecorators

		// Extract function calls and references
		parser.extractPythonCallsAndReferences(trimmedLine, lineNum, entities)
	}

	return entities
}

func shouldSkipPythonLine(trimmedLine string) bool {
	return trimmedLine == "" || strings.HasPrefix(trimmedLine, "#")
}

func (parser *PythonParser) parseDeclarationLine(
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
	decorators []codeindex.Annotation,
	functionRegex *regexp.Regexp,
	classRegex *regexp.Regexp,
) ([]*codeindex.ParsedEntity, []codeindex.Annotation) {
	entities := make([]*codeindex.ParsedEntity, 0, 2)

	if entity := parser.parseFunctionDeclaration(
		functionRegex,
		trimmedLine,
		lineNum,
		lines,
		filePath,
		decorators,
	); entity != nil {
		entities = append(entities, entity)
		decorators = nil
	}

	if entity := parser.parseClassDeclaration(
		classRegex,
		trimmedLine,
		lineNum,
		lines,
		filePath,
		decorators,
	); entity != nil {
		entities = append(entities, entity)
		decorators = nil
	}

	if !isDecoratorOrDefinition(trimmedLine) {
		decorators = parser.resetDecoratorsIfNeeded(decorators, lineNum, lines)
	}

	return entities, decorators
}

func isDecoratorOrDefinition(trimmedLine string) bool {
	return strings.HasPrefix(trimmedLine, "@") ||
		strings.HasPrefix(trimmedLine, "def ") ||
		strings.HasPrefix(trimmedLine, "class ") ||
		strings.HasPrefix(trimmedLine, "async def ")
}

func (parser *PythonParser) parseDecorator(
	re *regexp.Regexp,
	trimmedLine string,
	decorators []codeindex.Annotation,
) ([]codeindex.Annotation, bool) {
	matches := re.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return decorators, false
	}
	ann := codeindex.Annotation{
		Name:  matches[1],
		Value: matches[2],
	}
	return append(decorators, ann), true
}

func (parser *PythonParser) parseFunctionDeclaration(
	re *regexp.Regexp,
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
	decorators []codeindex.Annotation,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return nil
	}

	isAsync := matches[1] != ""
	funcName := matches[2]
	params := matches[3]
	returnType := matches[4]

	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          funcName,
		QualifiedName: filePath + ":" + funcName,
		Type:          codeindex.SymbolTypeFunction,
		Language:      codeindex.LanguagePython,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsAsync:       isAsync,
		IsExported:    !strings.HasPrefix(funcName, "_"),
		Parameters:    parser.parsePythonParameters(params),
		Annotations:   decorators,
		Signature:     fmt.Sprintf("%s(%s)", funcName, params),
	}

	if returnType != "" {
		entity.ReturnType = strings.TrimSpace(returnType)
	}

	parser.finalizePythonEntity(entity, lines, lineNum)
	return entity
}

func (parser *PythonParser) parseClassDeclaration(
	re *regexp.Regexp,
	trimmedLine string,
	lineNum int,
	lines []string,
	filePath string,
	decorators []codeindex.Annotation,
) *codeindex.ParsedEntity {
	matches := re.FindStringSubmatch(trimmedLine)
	if matches == nil {
		return nil
	}

	className := matches[1]
	bases := matches[2]

	entity := &codeindex.ParsedEntity{
		ID:            uuid.New(),
		Name:          className,
		QualifiedName: filePath + ":" + className,
		Type:          codeindex.SymbolTypeClass,
		Language:      codeindex.LanguagePython,
		FilePath:      filePath,
		StartLine:     lineNum + 1,
		IsExported:    !strings.HasPrefix(className, "_"),
		Annotations:   decorators,
	}

	if bases != "" {
		entity.Metadata = map[string]interface{}{
			"bases": bases,
		}
	}

	parser.finalizePythonEntity(entity, lines, lineNum)
	entity.Properties = parser.parseClassMethods(lines, lineNum, entity.EndLine, filePath, className)
	return entity
}

func (parser *PythonParser) finalizePythonEntity(entity *codeindex.ParsedEntity, lines []string, lineNum int) {
	entity.EndLine = parser.findEndLineByIndentation(lines, lineNum)
	entity.Content = parser.extractEntityContent(lines, lineNum, entity.EndLine)
	entity.DocComment = parser.extractPythonDocstring(lines, lineNum)
}

func (parser *PythonParser) resetDecoratorsIfNeeded(
	decorators []codeindex.Annotation,
	lineNum int,
	lines []string,
) []codeindex.Annotation {
	if len(decorators) == 0 || lineNum == 0 {
		return decorators
	}
	prevLine := strings.TrimSpace(lines[lineNum-1])
	if strings.HasPrefix(prevLine, "@") {
		return decorators
	}
	return nil
}

// parseClassMethods extracts methods from a class
func (parser *PythonParser) parseClassMethods(
	lines []string,
	startLine int,
	endLine int,
	filePath string,
	className string,
) []*codeindex.ParsedEntity {
	methods := make([]*codeindex.ParsedEntity, 0)
	functionRegex := regexp.MustCompile(`^(async\s+)?def\s+(\w+)\s*\(([^)]*)\)`)

	baseIndentation := parser.getIndentation(lines[startLine])

	for lineIndex := startLine + 1; lineIndex < endLine && lineIndex < len(lines); lineIndex++ {
		line := lines[lineIndex]
		trimmedLine := strings.TrimSpace(line)

		if trimmedLine == "" || strings.HasPrefix(trimmedLine, "#") {
			continue
		}

		currentIndentation := parser.getIndentation(line)
		if currentIndentation <= baseIndentation {
			break
		}

		if matches := functionRegex.FindStringSubmatch(trimmedLine); matches != nil {
			isAsync := matches[1] != ""
			methodName := matches[2]
			params := matches[3]

			method := &codeindex.ParsedEntity{
				ID:            uuid.New(),
				Name:          methodName,
				QualifiedName: filePath + ":" + className + "." + methodName,
				Type:          codeindex.SymbolTypeMethod,
				Language:      codeindex.LanguagePython,
				FilePath:      filePath,
				StartLine:     lineIndex + 1,
				ParentName:    className,
				IsAsync:       isAsync,
				IsExported:    !strings.HasPrefix(methodName, "_"),
				Parameters:    parser.parsePythonParameters(params),
				Signature:     fmt.Sprintf("%s(%s)", methodName, params),
			}

			method.EndLine = parser.findEndLineByIndentation(lines, lineIndex)
			method.DocComment = parser.extractPythonDocstring(lines, lineIndex)

			methods = append(methods, method)
		}
	}

	return methods
}

// parsePythonParameters parses Python function parameters
func (parser *PythonParser) parsePythonParameters(paramString string) []codeindex.Parameter {
	return parsePythonParameterList(paramString)
}

func parsePythonParameterList(paramString string) []codeindex.Parameter {
	trimmed := strings.TrimSpace(paramString)
	if trimmed == "" {
		return nil
	}

	parts := strings.Split(trimmed, ",")
	params := make([]codeindex.Parameter, 0, len(parts))
	for _, part := range parts {
		param, ok := parsePythonParameterPart(part)
		if ok {
			params = append(params, param)
		}
	}

	return params
}

func parsePythonParameterPart(rawPart string) (codeindex.Parameter, bool) {
	part := strings.TrimSpace(rawPart)
	if part == "" {
		return codeindex.Parameter{}, false
	}

	spread, varargs, normalized := normalizePythonParam(part)
	paramName, paramType := splitPythonParam(normalized)

	return codeindex.Parameter{
		Name:     paramName,
		Type:     paramType,
		Optional: strings.Contains(normalized, "="),
		Spread:   spread || varargs,
	}, true
}

func normalizePythonParam(part string) (bool, bool, string) {
	spread := strings.HasPrefix(part, "*")
	varargs := strings.HasPrefix(part, "**")

	if spread || varargs {
		trimmed := strings.TrimPrefix(part, "*")
		trimmed = strings.TrimPrefix(trimmed, "*")
		return spread, varargs, trimmed
	}

	return spread, varargs, part
}

func splitPythonParam(part string) (string, string) {
	if !strings.Contains(part, ":") {
		return part, ""
	}

	bits := strings.Split(part, ":")
	paramName := strings.TrimSpace(bits[0])
	rest := strings.Join(bits[1:], ":")

	return paramName, parsePythonParamType(rest)
}

func parsePythonParamType(typedPart string) string {
	if strings.Contains(typedPart, "=") {
		typeBits := strings.Split(typedPart, "=")
		return strings.TrimSpace(typeBits[0])
	}
	return strings.TrimSpace(typedPart)
}

// extractPythonCallsAndReferences extracts function calls
func (parser *PythonParser) extractPythonCallsAndReferences(
	line string,
	lineNum int,
	entities []*codeindex.ParsedEntity,
) {
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

// extractPythonDocstring extracts the docstring for a Python declaration
func (parser *PythonParser) extractPythonDocstring(lines []string, lineNum int) string {
	if lineNum >= len(lines)-1 {
		return ""
	}

	nextLine := strings.TrimSpace(lines[lineNum+1])

	quote := detectPythonDocstringQuote(nextLine)
	if quote == "" {
		return ""
	}

	return collectPythonDocstring(lines, lineNum+1, quote)
}

func detectPythonDocstringQuote(line string) string {
	if strings.HasPrefix(line, `"""`) {
		return `"""`
	}
	if strings.HasPrefix(line, `'''`) {
		return `'''`
	}
	return ""
}

func collectPythonDocstring(lines []string, startLine int, quote string) string {
	docLines := make([]string, 0)
	startFound := false

	for lineIndex := startLine; lineIndex < len(lines); lineIndex++ {
		line := lines[lineIndex]

		if strings.Contains(line, quote) {
			docLines = append(docLines, line)
			if startFound {
				break
			}
			startFound = true
			continue
		}

		if startFound {
			docLines = append(docLines, line)
		}
	}

	return strings.Join(docLines, "\n")
}

// findEndLineByIndentation finds the end line by tracking Python indentation
func (parser *PythonParser) findEndLineByIndentation(lines []string, startLine int) int {
	if startLine >= len(lines) {
		return startLine + 1
	}

	baseIndentation := parser.getIndentation(lines[startLine])

	for lineIndex := startLine + 1; lineIndex < len(lines); lineIndex++ {
		line := lines[lineIndex]
		trimmedLine := strings.TrimSpace(line)

		// Empty lines don't count
		if trimmedLine == "" {
			continue
		}

		currentIndentation := parser.getIndentation(line)

		// If we find a line with same or less indentation, we've hit the end
		if currentIndentation <= baseIndentation {
			return lineIndex
		}
	}

	return len(lines)
}

// getIndentation returns the indentation level (number of spaces)
func (parser *PythonParser) getIndentation(line string) int {
	count := 0
	for _, ch := range line {
		switch ch {
		case ' ':
			count++
		case '\t':
			count += 4
		default:
			return count
		}
	}
	return count
}

// extractEntityContent extracts source code for an entity
func (parser *PythonParser) extractEntityContent(lines []string, startLine, endLine int) string {
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
