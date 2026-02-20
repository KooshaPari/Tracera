package parsers

import (
	"regexp"
	"strings"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

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
