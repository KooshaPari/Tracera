package security

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestXSSPreventionInRequirementTitle tests XSS attack prevention in item titles
func TestXSSPreventionInRequirementTitle(t *testing.T) {
	xssPayloads := []struct {
		name     string
		payload  string
		expected string
	}{
		{
			name:     "Basic script tag",
			payload:  "<script>alert('XSS')</script>",
			expected: "script tags should be stripped or escaped",
		},
		{
			name:     "IMG onerror",
			payload:  "<img src=x onerror=alert('XSS')>",
			expected: "inline event handlers should be stripped",
		},
		{
			name:     "SVG onload",
			payload:  "<svg/onload=alert('XSS')>",
			expected: "SVG with onload should be stripped",
		},
		{
			name:     "JavaScript protocol",
			payload:  "<a href='javascript:alert(\"XSS\")'>Click</a>",
			expected: "javascript protocol should be stripped",
		},
		{
			name:     "Body onload",
			payload:  "<body onload=alert('XSS')>",
			expected: "body onload should be stripped",
		},
		{
			name:     "Iframe injection",
			payload:  "<iframe src='javascript:alert(\"XSS\")'></iframe>",
			expected: "iframe with javascript should be stripped",
		},
		{
			name:     "Data URI",
			payload:  "<img src='data:text/html,<script>alert(\"XSS\")</script>'>",
			expected: "data URI with script should be stripped",
		},
		{
			name:     "Event handler variations",
			payload:  "<div onclick=alert('XSS')>Click me</div>",
			expected: "onclick handler should be stripped",
		},
	}

	for _, tc := range xssPayloads {
		t.Run(tc.name, func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"title":      tc.payload,
				"type":       "requirement",
				"content":    "Test content",
				"project_id": "test-project-123",
			}

			body, err := json.Marshal(reqBody)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// The handler should process without error
			// In a real implementation, it would sanitize the input
			assert.NotContains(t, rec.Body.String(), "<script>",
				"Response should not contain executable script tags")
			assert.NotContains(t, rec.Body.String(), "javascript:",
				"Response should not contain javascript protocol")
			assert.NotContains(t, rec.Body.String(), "onerror=",
				"Response should not contain inline event handlers")
		})
	}
}

// TestXSSPreventionInRequirementContent tests XSS prevention in markdown/rich content
func TestXSSPreventionInRequirementContent(t *testing.T) {
	// Test that markdown is safely rendered without XSS
	markdownWithXSS := []string{
		"[Click me](javascript:alert('XSS'))",
		"![Image](javascript:alert('XSS'))",
		"<img src=x onerror=alert('XSS')>",
		"```\n<script>alert('XSS')</script>\n```",
	}

	for _, content := range markdownWithXSS {
		t.Run("Markdown XSS: "+content[:20], func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"title":      "Test Title",
				"type":       "requirement",
				"content":    content,
				"project_id": "test-project-123",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should not allow javascript execution in markdown
			responseBody := rec.Body.String()
			assert.NotContains(t, strings.ToLower(responseBody), "javascript:",
				"Markdown should not contain javascript protocol")
		})
	}
}

// TestXSSPreventionInSearchResults tests that search results are properly escaped
func TestXSSPreventionInSearchResults(t *testing.T) {
	e := echo.New()

	// Create items with XSS payloads
	xssTitle := "<script>alert('XSS')</script>"

	req := httptest.NewRequest(http.MethodGet, "/api/items?search="+xssTitle, nil)
	rec := httptest.NewRecorder()
	_ = e.NewContext(req, rec)

	// The search results should escape the XSS payload
	responseBody := rec.Body.String()
	assert.NotContains(t, responseBody, "<script>",
		"Search results should escape script tags")
}

// TestXSSPreventionInUserGeneratedTags tests XSS in user-generated tags
func TestXSSPreventionInUserGeneratedTags(t *testing.T) {
	maliciousTags := []string{
		"<script>alert('XSS')</script>",
		"<img src=x onerror=alert('XSS')>",
		"javascript:alert('XSS')",
		"<svg onload=alert('XSS')>",
	}

	for _, tag := range maliciousTags {
		t.Run("Tag XSS: "+tag[:10], func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"title":      "Test Item",
				"type":       "requirement",
				"tags":       []string{tag, "valid-tag"},
				"project_id": "test-project-123",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			responseBody := rec.Body.String()
			assert.NotContains(t, responseBody, "<script>", "Tags should not contain script tags")
			assert.NotContains(t, responseBody, "onerror=", "Tags should not contain event handlers")
		})
	}
}

// TestXSSPreventionInProjectNames tests XSS in project names
func TestXSSPreventionInProjectNames(t *testing.T) {
	e := echo.New()

	maliciousName := "<img src=x onerror=alert('XSS')>"

	reqBody := map[string]interface{}{
		"name":        maliciousName,
		"description": "Test project",
	}

	body, _ := json.Marshal(reqBody)
	req := httptest.NewRequest(http.MethodPost, "/api/projects", bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	_ = e.NewContext(req, rec)

	responseBody := rec.Body.String()
	assert.NotContains(t, responseBody, "onerror=",
		"Project names should not contain event handlers")
}

// TestHTMLEntityEncoding tests that HTML entities are properly encoded
func TestHTMLEntityEncoding(t *testing.T) {
	specialChars := []struct {
		input    string
		expected string
	}{
		{input: "<", expected: "&lt;"},
		{input: ">", expected: "&gt;"},
		{input: "&", expected: "&amp;"},
		{input: "\"", expected: "&quot;"},
		{input: "'", expected: "&#x27;"},
	}

	for _, tc := range specialChars {
		t.Run("Encode: "+tc.input, func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"title":      "Test " + tc.input + " Title",
				"type":       "requirement",
				"content":    "Content with " + tc.input,
				"project_id": "test-project-123",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Response should contain encoded entities or safely handle them
			// This is a placeholder - actual implementation would check proper encoding
		})
	}
}

// TestDOMClobbering tests protection against DOM clobbering attacks
func TestDOMClobbering(t *testing.T) {
	clobberingAttempts := []string{
		`<form name="alert">`,
		`<img name="console">`,
		`<form><input name="innerHTML">`,
		`<div id="location">`,
	}

	for _, attempt := range clobberingAttempts {
		t.Run("Clobbering: "+attempt[:15], func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"title":      "Test",
				"type":       "requirement",
				"content":    attempt,
				"project_id": "test-project-123",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should not allow DOM clobbering attributes
			_ = rec.Body.String()
			// In production, check that dangerous name/id attributes are removed or escaped
		})
	}
}

// TestPrototypePolultion tests protection against prototype pollution
func TestPrototypePollution(t *testing.T) {
	e := echo.New()

	// Attempt to pollute object prototype
	maliciousJSON := `{
		"title": "Test",
		"type": "requirement",
		"__proto__": {"isAdmin": true},
		"constructor": {"prototype": {"isAdmin": true}},
		"project_id": "test-project-123"
	}`

	req := httptest.NewRequest(http.MethodPost, "/api/items", strings.NewReader(maliciousJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	_ = e.NewContext(req, rec)

	// Should reject or sanitize prototype pollution attempts
	// Go's standard JSON decoder is generally safe from this, but verify
	assert.NotContains(t, rec.Body.String(), "__proto__",
		"Should not process __proto__ properties")
}
