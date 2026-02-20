package parsers

import (
	"regexp"
	"strconv"
	"strings"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

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
