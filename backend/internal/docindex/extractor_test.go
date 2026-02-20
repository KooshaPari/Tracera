package docindex

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestExtractAPIRefsWithMethods tests extraction of API refs with HTTP methods
func TestExtractAPIRefsWithMethods(t *testing.T) {
	tests := []struct {
		name     string
		content  string
		expected int
		methods  []string
	}{
		{
			name:     "single GET request",
			content:  "Call GET /api/users to fetch users.",
			expected: 1,
			methods:  []string{"GET"},
		},
		{
			name:     "multiple HTTP methods",
			content:  "Use GET /api/users, POST /api/users, DELETE /api/users/123.",
			expected: 3,
			methods:  []string{"GET", "POST", "DELETE"},
		},
		{
			name:     "lowercase methods",
			content:  "get /api/items or post /api/items",
			expected: 2,
			methods:  []string{"GET", "POST"},
		},
		{
			name:     "all HTTP methods",
			content:  "GET /api/a PUT /api/b PATCH /api/c DELETE /api/d HEAD /api/e OPTIONS /api/f",
			expected: 6,
			methods:  []string{"GET", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			refs := ExtractAPIRefs(test.content)
			assert.Len(t, refs, test.expected, "Expected %d API refs", test.expected)

			for i, ref := range refs {
				if i < len(test.methods) {
					assert.Equal(t, test.methods[i], ref.Method)
				}
			}
		})
	}
}

// TestExtractAPIRefsPathPatterns tests extraction of API paths
func TestExtractAPIRefsPathPatterns(t *testing.T) {
	tests := []struct {
		name     string
		content  string
		expected []string
	}{
		{
			name:     "simple paths",
			content:  "GET /api/v1/users and POST /api/v1/items",
			expected: []string{"/api/v1/users", "/api/v1/items"},
		},
		{
			name:     "paths with parameters",
			content:  "GET /api/v1/users/{id} and PATCH /api/v1/items/{itemId}/status",
			expected: []string{"/api/v1/users/{id}", "/api/v1/items/{itemId}/status"},
		},
		{
			name:     "paths with query-like segments",
			content:  "POST /api/v2/search:execute",
			expected: []string{"/api/v2/search:execute"},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			refs := ExtractAPIRefs(test.content)
			assert.Len(t, refs, len(test.expected))

			for i, ref := range refs {
				if i < len(test.expected) {
					assert.Equal(t, test.expected[i], ref.Path)
				}
			}
		})
	}
}

// TestExtractAPIRefsNoExternalLinks tests that external URLs are not captured
func TestExtractAPIRefsNoExternalLinks(t *testing.T) {
	content := `Check out http://example.com or https://api.external.com for details.
But use GET /api/internal/data instead.`

	refs := ExtractAPIRefs(content)
	// Should capture internal API endpoints (not external URLs)
	for _, ref := range refs {
		assert.False(t, isExternalURL(ref.Path))
	}
}

// TestExtractInternalLinks tests extraction of markdown links
func TestExtractInternalLinks(t *testing.T) {
	tests := []struct {
		name          string
		content       string
		expectedCount int
		expectedText  []string
	}{
		{
			name:          "single link",
			content:       "See [documentation](docs/guide.md) for details.",
			expectedCount: 1,
			expectedText:  []string{"documentation"},
		},
		{
			name:          "multiple links",
			content:       "Check [guide](guide.md) and [reference](api/ref.md).",
			expectedCount: 2,
			expectedText:  []string{"guide", "reference"},
		},
		{
			name:          "links with anchors",
			content:       "See [section](docs.md#getting-started) and [api](api.md#endpoints)",
			expectedCount: 2,
			expectedText:  []string{"section", "api"},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			links := ExtractInternalLinks(test.content)
			assert.Len(t, links, test.expectedCount)

			for i, link := range links {
				if i < len(test.expectedText) {
					assert.Equal(t, test.expectedText[i], link.Text)
				}
			}
		})
	}
}

// TestExtractInternalLinksWithAnchors tests anchor extraction from links
func TestExtractInternalLinksWithAnchors(t *testing.T) {
	content := `[Getting Started](docs.md#getting-started) and [API Reference](api/reference.md#endpoints)`

	links := ExtractInternalLinks(content)
	assert.Len(t, links, 2)

	assert.Equal(t, "docs.md", links[0].TargetPath)
	assert.Equal(t, "getting-started", links[0].Anchor)

	assert.Equal(t, "api/reference.md", links[1].TargetPath)
	assert.Equal(t, "endpoints", links[1].Anchor)
}

// TestExtractInternalLinksNoExternalLinks tests that external links are excluded
func TestExtractInternalLinksNoExternalLinks(t *testing.T) {
	content := `[Google](https://google.com) and [Guide](guide.md) and [External](http://external.com)`

	links := ExtractInternalLinks(content)
	assert.Len(t, links, 1)
	assert.Equal(t, "guide.md", links[0].TargetPath)
}

// TestExtractInternalLinksOffsets tests offset calculation
func TestExtractInternalLinksOffsets(t *testing.T) {
	content := "See [guide](guide.md) for details."
	links := ExtractInternalLinks(content)

	require.Len(t, links, 1)
	link := links[0]

	// Verify offsets point to the link
	linkText := content[link.StartOffset:link.EndOffset]
	assert.Contains(t, linkText, "guide")
	assert.Contains(t, linkText, "guide.md")
}

// TestIsFilePath tests file path detection
func TestIsFilePath(t *testing.T) {
	tests := []struct {
		path     string
		expected bool
	}{
		{"main.go", true},
		{"app.tsx", true},
		{"style.css", true},
		{"config.json", true},
		{"src/main.ts", true},
		{"src/main.go", true},
		{"document.md", true},
		{"data.yaml", true},
		{"settings.yml", true},
		{"random_text", false},
		{"no_extension", false},
		{"file.unknown", false},
	}

	for _, test := range tests {
		result := isFilePath(test.path)
		assert.Equal(t, test.expected, result, "isFilePath(%s) should return %v", test.path, test.expected)
	}
}

// TestDetectLanguage tests language detection from file paths
func TestDetectLanguage(t *testing.T) {
	tests := []struct {
		path     string
		expected string
	}{
		{"main.go", "go"},
		{"app.ts", "typescript"},
		{"component.tsx", "typescript"},
		{"script.js", "javascript"},
		{"component.jsx", "javascript"},
		{"script.py", "python"},
		{"README.md", "markdown"},
		{"guide.mdx", "markdown"},
		{"config.json", ""},
		{"style.css", ""},
		{"unknown.xyz", ""},
	}

	for _, test := range tests {
		result := detectLanguage(test.path)
		assert.Equal(t, test.expected, result, "detectLanguage(%s) should return %s", test.path, test.expected)
	}
}

// TestIsPascalCase tests PascalCase detection
func TestIsPascalCase(t *testing.T) {
	tests := []struct {
		text     string
		expected bool
	}{
		{"MyClass", true},
		{"UserService", true},
		{"HTMLElement", true},
		{"myVar", false},
		{"MY_CONST", false},
		{"my-element", false},
		{"", false},
		{"a", false},
		{"_private", false},
	}

	for _, test := range tests {
		result := isPascalCase(test.text)
		assert.Equal(t, test.expected, result, "isPascalCase(%s) should return %v", test.text, test.expected)
	}
}

// TestIsCamelCase tests camelCase detection
func TestIsCamelCase(t *testing.T) {
	tests := []struct {
		text     string
		expected bool
	}{
		{"myVar", true},
		{"getUserName", true},
		{"validateInput", true},
		{"MyClass", false},
		{"my_var", false},
		{"MY_CONST", false},
		{"", false},
		{"A", false},
	}

	for _, test := range tests {
		result := isCamelCase(test.text)
		assert.Equal(t, test.expected, result, "isCamelCase(%s) should return %v", test.text, test.expected)
	}
}

// TestIsSnakeCase tests snake_case detection
func TestIsSnakeCase(t *testing.T) {
	tests := []struct {
		text     string
		expected bool
	}{
		{"my_var", true},
		{"user_name", true},
		{"get_user_data", true},
		{"MY_VAR", false}, // This is UPPER_SNAKE_CASE
		{"myVar", false},
		{"my-var", false},
		{"a", false},
		{"_private", true},
		{"", false},
	}

	for _, test := range tests {
		result := isSnakeCase(test.text)
		assert.Equal(t, test.expected, result, "isSnakeCase(%s) should return %v", test.text, test.expected)
	}
}

// TestIsUpperSnakeCase tests UPPER_SNAKE_CASE detection
func TestIsUpperSnakeCase(t *testing.T) {
	tests := []struct {
		text     string
		expected bool
	}{
		{"MY_CONST", true},
		{"MAX_BUFFER_SIZE", true},
		{"DEBUG_MODE", true},
		{"my_var", false},
		{"MyClass", false},
		{"MIXED_Case", false},
		{"A", false},
		{"", false},
	}

	for _, test := range tests {
		result := isUpperSnakeCase(test.text)
		assert.Equal(t, test.expected, result, "isUpperSnakeCase(%s) should return %v", test.text, test.expected)
	}
}

// TestIsCommonWord tests common word detection
func TestIsCommonWord(t *testing.T) {
	commonWords := []string{"The", "This", "That", "Note", "Warning", "Error", "Info", "True", "False", "None"}
	notCommonWords := []string{"MyClass", "Custom", "Function", "myVar", "debug_log"}

	for _, word := range commonWords {
		assert.True(t, isCommonWord(word), "Expected %s to be common", word)
	}

	for _, word := range notCommonWords {
		assert.False(t, isCommonWord(word), "Expected %s to NOT be common", word)
	}
}

// TestClassifyCodeRefPascalCase tests PascalCase classification
func TestClassifyCodeRefPascalCase(t *testing.T) {
	parser := NewParser()
	refs := []struct {
		code     string
		expected string
	}{
		{"UserService", "class"},
		{"Component", "class"},
		{"HTMLParser", "class"},
	}

	for _, r := range refs {
		ref := parser.classifyCodeRef(r.code, 0, len(r.code))
		require.NotNil(t, ref)
		assert.Equal(t, r.expected, ref.Type)
	}
}

// TestClassifyCodeRefCamelCase tests camelCase classification
func TestClassifyCodeRefCamelCase(t *testing.T) {
	parser := NewParser()
	refs := []struct {
		code     string
		expected string
	}{
		{"getUserName", "variable"},
		{"validateInput", "variable"},
		{"processData", "variable"},
	}

	for _, r := range refs {
		ref := parser.classifyCodeRef(r.code, 0, len(r.code))
		require.NotNil(t, ref)
		assert.Equal(t, r.expected, ref.Type)
	}
}

// TestClassifyCodeRefSnakeCase tests snake_case classification
func TestClassifyCodeRefSnakeCase(t *testing.T) {
	parser := NewParser()
	refs := []struct {
		code     string
		expected string
	}{
		{"get_user", "variable"},
		{"my_function", "variable"},
		{"user_data", "variable"},
	}

	for _, r := range refs {
		ref := parser.classifyCodeRef(r.code, 0, len(r.code))
		require.NotNil(t, ref)
		assert.Equal(t, r.expected, ref.Type)
	}
}

// TestClassifyCodeRefFunctionCall tests function call classification
func TestClassifyCodeRefFunctionCall(t *testing.T) {
	parser := NewParser()
	refs := []struct {
		code     string
		expected string
	}{
		{"myFunction()", "function"},
		{"process(arg1, arg2)", "function"},
		{"getValue()", "function"},
	}

	for _, r := range refs {
		ref := parser.classifyCodeRef(r.code, 0, len(r.code))
		require.NotNil(t, ref)
		assert.Equal(t, r.expected, ref.Type)
	}
}

// TestClassifyCodeRefPackage tests package/module classification
func TestClassifyCodeRefPackage(t *testing.T) {
	parser := NewParser()
	refs := []struct {
		code     string
		expected string
	}{
		{"module.function", "package"},
		{"pkg.Class", "package"},
		{"app.config", "package"},
	}

	for _, r := range refs {
		ref := parser.classifyCodeRef(r.code, 0, len(r.code))
		require.NotNil(t, ref)
		assert.Equal(t, r.expected, ref.Type)
	}
}

// TestExtractAPIRefsComplexPaths tests complex API paths
func TestExtractAPIRefsComplexPaths(t *testing.T) {
	content := `
GET /api/v1/users/{userId}/projects/{projectId}/items
POST /api/v2/data:import
PATCH /api/v1/config:update
DELETE /api/v3/resources/{id}/children
`

	refs := ExtractAPIRefs(content)
	assert.GreaterOrEqual(t, len(refs), 3)
}

// TestExtractInternalLinksComplexPaths tests complex link paths
func TestExtractInternalLinksComplexPaths(t *testing.T) {
	content := `
[Main Doc](../../docs/README.md)
[Section](docs/guide/getting-started.md#installation)
[External](/api/reference.md#list)
`

	links := ExtractInternalLinks(content)
	assert.Len(t, links, 3)
}

// Helper function
func isExternalURL(path string) bool {
	return len(path) > 4 && (path[:7] == "http://" || path[:8] == "https://")
}
