package docindex

import (
	"regexp"
	"strings"
)

const (
	codeRefConfidenceBase     = 0.7
	codeRefConfidenceFile     = 0.9
	codeRefConfidenceFunction = 0.85
	codeRefConfidenceClass    = 0.75
	codeRefConfidenceConstant = 0.8
	codeRefConfidencePackage  = 0.7
	codeRefConfidenceVariable = 0.6
	codeRefConfidenceGeneric  = 0.5
	codeRefPartsMin           = 2
	minIdentifierLength       = 2
)

// classifyCodeRef classifies an inline code reference
func (p *Parser) classifyCodeRef(code string, start, end int) *CodeRef {
	code = strings.TrimSpace(code)
	if code == "" {
		return nil
	}

	ref := &CodeRef{
		Name:        code,
		StartOffset: start,
		EndOffset:   end,
		Confidence:  codeRefConfidenceBase,
	}

	// Detect file paths
	if strings.Contains(code, "/") || strings.Contains(code, "\\") {
		if isFilePath(code) {
			ref.Type = "file"
			ref.FilePath = code
			ref.Confidence = codeRefConfidenceFile
			ref.Language = detectLanguage(code)
			return ref
		}
	}

	// Detect function calls
	if strings.HasSuffix(code, "()") || strings.Contains(code, "(") {
		ref.Type = "function"
		ref.Name = strings.Split(code, "(")[0]
		ref.Confidence = codeRefConfidenceFunction
		return ref
	}

	// Detect class/type names (PascalCase)
	if isPascalCase(code) && !isCommonWord(code) {
		ref.Type = "class"
		ref.Confidence = codeRefConfidenceClass
		return ref
	}

	// Detect constants (UPPER_SNAKE_CASE)
	if isUpperSnakeCase(code) {
		ref.Type = "constant"
		ref.Confidence = codeRefConfidenceConstant
		return ref
	}

	// Detect package/module references
	if strings.Contains(code, ".") && !strings.Contains(code, " ") {
		parts := strings.Split(code, ".")
		if len(parts) >= codeRefPartsMin {
			ref.Type = "package"
			ref.Confidence = codeRefConfidencePackage
			return ref
		}
	}

	// Detect variable names (camelCase or snake_case)
	if isCamelCase(code) || isSnakeCase(code) {
		ref.Type = "variable"
		ref.Confidence = codeRefConfidenceVariable
		return ref
	}

	// Generic code reference
	ref.Type = "code"
	ref.Confidence = codeRefConfidenceGeneric
	return ref
}

// ExtractAPIRefs extracts API endpoint references from content
func ExtractAPIRefs(content string) []APIRef {
	var refs []APIRef

	// Pattern for HTTP methods with paths
	httpPattern := regexp.MustCompile(`(?i)(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/[a-zA-Z0-9/_\-{}:]+)`)
	matches := httpPattern.FindAllStringSubmatchIndex(content, -1)
	for _, match := range matches {
		method := strings.ToUpper(content[match[2]:match[3]])
		path := content[match[4]:match[5]]
		refs = append(refs, APIRef{
			Method:      method,
			Path:        path,
			StartOffset: match[0],
			EndOffset:   match[1],
		})
	}

	// Pattern for API paths without explicit method
	pathPattern := regexp.MustCompile(`(?:^|[\s"'])(/api/v[0-9]+/[a-zA-Z0-9/_\-{}:]+)`)
	matches = pathPattern.FindAllStringSubmatchIndex(content, -1)
	for _, match := range matches {
		path := content[match[2]:match[3]]
		// Check if already captured
		duplicate := false
		for _, existing := range refs {
			if existing.Path == path {
				duplicate = true
				break
			}
		}
		if !duplicate {
			refs = append(refs, APIRef{
				Path:        path,
				StartOffset: match[2],
				EndOffset:   match[3],
			})
		}
	}

	return refs
}

// ExtractInternalLinks extracts links to other documents
func ExtractInternalLinks(content string) []InternalLink {
	var links []InternalLink

	// Markdown link pattern: [text](path)
	linkPattern := regexp.MustCompile(`\[([^\]]+)\]\(([^)]+)\)`)
	matches := linkPattern.FindAllStringSubmatchIndex(content, -1)
	for _, match := range matches {
		text := content[match[2]:match[3]]
		target := content[match[4]:match[5]]

		// Skip external links
		if strings.HasPrefix(target, "http://") || strings.HasPrefix(target, "https://") {
			continue
		}

		link := InternalLink{
			Text:        text,
			StartOffset: match[0],
			EndOffset:   match[1],
		}

		// Parse anchor
		if idx := strings.Index(target, "#"); idx != -1 {
			link.TargetPath = target[:idx]
			link.Anchor = target[idx+1:]
		} else {
			link.TargetPath = target
		}

		links = append(links, link)
	}

	return links
}

// Helper functions

func isFilePath(s string) bool {
	extensions := []string{".ts", ".tsx", ".js", ".jsx", ".go", ".py", ".md", ".json", ".yaml", ".yml", ".css", ".scss", ".html"}
	for _, ext := range extensions {
		if strings.HasSuffix(s, ext) {
			return true
		}
	}
	return false
}

func detectLanguage(path string) string {
	switch {
	case strings.HasSuffix(path, ".ts"), strings.HasSuffix(path, ".tsx"):
		return "typescript"
	case strings.HasSuffix(path, ".js"), strings.HasSuffix(path, ".jsx"):
		return "javascript"
	case strings.HasSuffix(path, ".go"):
		return "go"
	case strings.HasSuffix(path, ".py"):
		return "python"
	case strings.HasSuffix(path, ".md"), strings.HasSuffix(path, ".mdx"):
		return "markdown"
	default:
		return ""
	}
}

func isPascalCase(s string) bool {
	if len(s) < minIdentifierLength {
		return false
	}
	return s[0] >= 'A' && s[0] <= 'Z' && !strings.Contains(s, "_") && !strings.Contains(s, "-")
}

func isCamelCase(s string) bool {
	if len(s) < minIdentifierLength {
		return false
	}
	return s[0] >= 'a' && s[0] <= 'z' && !strings.Contains(s, "_") && !strings.Contains(s, "-")
}

func isSnakeCase(s string) bool {
	return strings.Contains(s, "_") && !strings.Contains(s, " ") && s == strings.ToLower(s)
}

func isUpperSnakeCase(s string) bool {
	return strings.Contains(s, "_") && s == strings.ToUpper(s)
}

func isCommonWord(s string) bool {
	common := map[string]bool{
		"The": true, "This": true, "That": true, "These": true, "Those": true,
		"Note": true, "Warning": true, "Error": true, "Info": true, "Debug": true,
		"True": true, "False": true, "None": true, "Null": true,
	}
	return common[s]
}
