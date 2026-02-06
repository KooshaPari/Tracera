package parsers

import (
	"context"
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

const (
	docCommentLookbackLines = 10
	hashShift               = 5
	startLineOffset         = 2
)

// TypeScriptParser parses TypeScript and JavaScript files
type TypeScriptParser struct {
	projectRoot string
	// In a real implementation, we would use tree-sitter bindings
	// For now, we use regex-based parsing as a foundation
}

// NewTypeScriptParser creates a new TypeScript parser
func NewTypeScriptParser(projectRoot string) *TypeScriptParser {
	return &TypeScriptParser{
		projectRoot: projectRoot,
	}
}

// ParseFile parses a TypeScript/JavaScript file
func (parser *TypeScriptParser) ParseFile(
	ctx context.Context,
	filePath string,
	content string,
) (*codeindex.ParsedFile, error) {
	_ = ctx
	start := time.Now()

	parsedFile := &codeindex.ParsedFile{
		FilePath: filePath,
		Language: codeindex.LanguageTypeScript,
		Entities: make([]*codeindex.ParsedEntity, 0),
		Imports:  make([]codeindex.ImportRef, 0),
		Content:  content,
		Hash:     hashContent(content),
		ParsedAt: time.Now(),
	}

	// Extract module path (relative to project root)
	parsedFile.Module = strings.TrimPrefix(filePath, parser.projectRoot)
	parsedFile.Module = strings.TrimPrefix(parsedFile.Module, "/")

	// Parse imports
	imports := parser.parseImports(content)
	parsedFile.Imports = imports

	// Parse top-level declarations
	entities := parser.parseTopLevelDeclarations(content, filePath)
	parsedFile.Entities = entities

	_ = time.Since(start)
	return parsedFile, nil
}

// parseImports extracts import statements
func (parser *TypeScriptParser) parseImports(content string) []codeindex.ImportRef {
	lines := strings.Split(content, "\n")
	return parser.parseImportsFromLines(lines)
}

func (parser *TypeScriptParser) parseImportsFromLines(lines []string) []codeindex.ImportRef {
	imports := make([]codeindex.ImportRef, 0, len(lines))

	importRegex := regexp.MustCompile(
		`(?m)^import\s+` +
			`(?:{([^}]+)}|(?:\*\s+as\s+(\w+))|(\w+))\s+from\s+` +
			`['"]([^'"]+)['"];?`,
	)
	requireRegex := regexp.MustCompile(
		`(?m)^(?:const|let|var)\s+` +
			`(?:{([^}]+)}|(\w+))\s*=\s*require\(['"]([^'"]+)['"]\)`,
	)

	imports = append(imports, parser.parseESImports(lines, importRegex)...)
	imports = append(imports, parser.parseRequireImports(lines, requireRegex)...)

	return imports
}

func (parser *TypeScriptParser) parseESImports(
	lines []string,
	importRegex *regexp.Regexp,
) []codeindex.ImportRef {
	imports := make([]codeindex.ImportRef, 0)
	for lineNum, line := range lines {
		matches := importRegex.FindStringSubmatch(line)
		if matches == nil {
			continue
		}

		importName, isNamespace, isDefault := parseESImportName(matches)
		importPath := matches[4]

		imports = append(imports, codeindex.ImportRef{
			ModulePath:  importPath,
			ImportName:  importName,
			IsDefault:   isDefault,
			IsNamespace: isNamespace,
			Line:        lineNum + 1,
		})
	}
	return imports
}

func parseESImportName(matches []string) (string, bool, bool) {
	switch {
	case matches[1] != "":
		return matches[1], false, false
	case matches[2] != "":
		return matches[2], true, false
	case matches[3] != "":
		return matches[3], false, true
	default:
		return "", false, false
	}
}

func (parser *TypeScriptParser) parseRequireImports(
	lines []string,
	requireRegex *regexp.Regexp,
) []codeindex.ImportRef {
	imports := make([]codeindex.ImportRef, 0)
	for lineNum, line := range lines {
		matches := requireRegex.FindStringSubmatch(line)
		if matches == nil {
			continue
		}

		importName := matches[1]
		if importName == "" {
			importName = matches[2]
		}

		imports = append(imports, codeindex.ImportRef{
			ModulePath: matches[3],
			ImportName: importName,
			Line:       lineNum + 1,
		})
	}

	return imports
}

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

// extractCallsAndReferences extracts function calls and references from a line
func (parser *TypeScriptParser) extractCallsAndReferences(
	line string,
	lineNum int,
	entities []*codeindex.ParsedEntity,
) {
	// Match function calls: methodName(...) or obj.methodName(...)
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

// extractAnnotations extracts decorator/annotation information
func (parser *TypeScriptParser) extractAnnotations(line string) []codeindex.Annotation {
	// Match decorators: @decorator or @decorator(args)
	decoratorRegex := regexp.MustCompile(`@(\w+)(?:\(([^)]*)\))?`)

	matches := decoratorRegex.FindAllStringSubmatch(line, -1)
	annotations := make([]codeindex.Annotation, 0, len(matches))
	for _, match := range matches {
		name := match[1]
		args := match[2]

		ann := codeindex.Annotation{
			Name:  name,
			Value: args,
		}

		annotations = append(annotations, ann)
	}

	return annotations
}

// attachDocComments attaches documentation comments to entities
func (parser *TypeScriptParser) attachDocComments(lines []string, entities []*codeindex.ParsedEntity) {
	for _, entity := range entities {
		docComment := parser.findDocComment(lines, entity.StartLine)
		if docComment != "" {
			entity.DocComment = docComment
		}
	}
}

func (parser *TypeScriptParser) findDocComment(lines []string, startLine int) string {
	if startLine <= 1 {
		return ""
	}

	lineIdx := startLine - startLineOffset
	if lineIdx < 0 || lineIdx >= len(lines) {
		return ""
	}

	if !strings.Contains(lines[lineIdx], "/**") {
		return ""
	}

	docLines := collectDocLines(lines, lineIdx)
	return strings.Join(docLines, "\n")
}

func collectDocLines(lines []string, lineIdx int) []string {
	docLines := make([]string, 0, docCommentLookbackLines)
	for lineIndex := lineIdx; lineIndex >= 0 && lineIndex > lineIdx-docCommentLookbackLines; lineIndex-- {
		line := lines[lineIndex]
		docLines = append([]string{line}, docLines...)
		if strings.Contains(line, "/**") {
			break
		}
	}
	return docLines
}

// findEndLine finds the end line of a code block (matching braces)
func (parser *TypeScriptParser) findEndLine(lines []string, startLine int) int {
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

// extractEntityContent extracts the source code for an entity
func (parser *TypeScriptParser) extractEntityContent(lines []string, startLine, endLine int) string {
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

func hashContent(content string) string {
	// Simple hash for content (could use crypto/sha256 for better implementation)
	hash := 0
	for _, ch := range content {
		hash = ((hash << hashShift) - hash) + int(ch)
	}
	return strconv.Itoa(hash)
}
