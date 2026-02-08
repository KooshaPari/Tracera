package parsers

import (
	"regexp"
	"strings"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

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
