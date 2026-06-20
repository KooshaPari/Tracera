// FR-1.1: Create Item - Backend API Tests
// Linked to: FR-1.1, ADR-3 (Backend), ADR-12 (API Design), ARU-2 (Backend Architecture)

package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test Group 1: Basic Item Creation (AC-1 to AC-10)

// Test 1.1.1: User can enter item title (1-255 characters)
// Linked to: AC-1, Validation Rule 1
func TestCreateItem_ValidTitle_1Character(t *testing.T) {
	router := setupTestRouter()
	
	payload := map[string]interface{}{
		"title": "A",
		"type":  "REQUIREMENT",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusCreated, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "A", response["title"])
}

// Test 1.1.2: User can enter item title (255 characters)
// Linked to: AC-1, Validation Rule 1
func TestCreateItem_ValidTitle_255Characters(t *testing.T) {
	router := setupTestRouter()
	
	title := ""
	for i := 0; i < 255; i++ {
		title += "A"
	}
	
	payload := map[string]interface{}{
		"title": title,
		"type":  "REQUIREMENT",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusCreated, w.Code)
}

// Test 1.1.3: Should reject empty title
// Linked to: Validation Rule 1, Error Scenario 1
func TestCreateItem_EmptyTitle_Error(t *testing.T) {
	router := setupTestRouter()
	
	payload := map[string]interface{}{
		"title": "",
		"type":  "REQUIREMENT",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "VALIDATION_ERROR", response["error_code"])
	assert.Contains(t, response["message"], "title is required")
}

// Test 1.1.4: Should reject title > 255 characters
// Linked to: Validation Rule 1, Error Scenario 1
func TestCreateItem_TitleTooLong_Error(t *testing.T) {
	router := setupTestRouter()
	
	title := ""
	for i := 0; i < 256; i++ {
		title += "A"
	}
	
	payload := map[string]interface{}{
		"title": title,
		"type":  "REQUIREMENT",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "VALIDATION_ERROR", response["error_code"])
}

// Test 1.1.5: User can select item type from 8 types
// Linked to: AC-2, Validation Rule 2
func TestCreateItem_ValidTypes(t *testing.T) {
	router := setupTestRouter()
	
	types := []string{"REQUIREMENT", "DESIGN", "IMPLEMENTATION", "TEST", 
		"DEPLOYMENT", "DOCUMENTATION", "RESEARCH", "SPIKE"}
	
	for _, itemType := range types {
		payload := map[string]interface{}{
			"title": "Test Item",
			"type":  itemType,
		}
		
		body, _ := json.Marshal(payload)
		req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer test-token")
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusCreated, w.Code, "Failed for type: "+itemType)
	}
}

// Test 1.1.6: Should reject invalid item type
// Linked to: Validation Rule 2, Error Scenario 2
func TestCreateItem_InvalidType_Error(t *testing.T) {
	router := setupTestRouter()
	
	payload := map[string]interface{}{
		"title": "Test Item",
		"type":  "INVALID_TYPE",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "VALIDATION_ERROR", response["error_code"])
}

// Test 1.1.7: User can enter description (0-5000 characters, markdown)
// Linked to: AC-3
func TestCreateItem_ValidDescription(t *testing.T) {
	router := setupTestRouter()
	
	description := "# Title\n\n**Bold** and *italic*\n\n- List item"
	
	payload := map[string]interface{}{
		"title":       "Test Item",
		"type":        "REQUIREMENT",
		"description": description,
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusCreated, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, description, response["description"])
}

// Test 1.1.8: Should reject description > 5000 characters
// Linked to: Validation Rule 3, Error Scenario 3
func TestCreateItem_DescriptionTooLong_Error(t *testing.T) {
	router := setupTestRouter()
	
	description := ""
	for i := 0; i < 5001; i++ {
		description += "A"
	}
	
	payload := map[string]interface{}{
		"title":       "Test Item",
		"type":        "REQUIREMENT",
		"description": description,
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
}

// Test 1.1.9: User can add tags (0-20 tags)
// Linked to: AC-4
func TestCreateItem_ValidTags(t *testing.T) {
	router := setupTestRouter()
	
	tags := []string{"urgent", "backend", "frontend"}
	
	payload := map[string]interface{}{
		"title": "Test Item",
		"type":  "REQUIREMENT",
		"tags":  tags,
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusCreated, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, tags, response["tags"])
}

// Test 1.1.10: Should reject > 20 tags
// Linked to: Validation Rule 8, Error Scenario 8
func TestCreateItem_TooManyTags_Error(t *testing.T) {
	router := setupTestRouter()
	
	tags := make([]string, 21)
	for i := 0; i < 21; i++ {
		tags[i] = "tag" + string(rune(i))
	}
	
	payload := map[string]interface{}{
		"title": "Test Item",
		"type":  "REQUIREMENT",
		"tags":  tags,
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
}

// Test 1.1.11: User can set priority
// Linked to: AC-5
func TestCreateItem_ValidPriorities(t *testing.T) {
	router := setupTestRouter()
	
	priorities := []string{"LOW", "MEDIUM", "HIGH", "CRITICAL"}
	
	for _, priority := range priorities {
		payload := map[string]interface{}{
			"title":    "Test Item",
			"type":     "REQUIREMENT",
			"priority": priority,
		}
		
		body, _ := json.Marshal(payload)
		req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer test-token")
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusCreated, w.Code, "Failed for priority: "+priority)
	}
}

// Test 1.1.12: Item created with DRAFT status
// Linked to: AC-6, Story US-1.1
func TestCreateItem_DraftStatus(t *testing.T) {
	router := setupTestRouter()
	
	payload := map[string]interface{}{
		"title": "Test Item",
		"type":  "REQUIREMENT",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusCreated, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "DRAFT", response["status"])
}

// Test 1.1.13: Item assigned unique UUID
// Linked to: AC-6
func TestCreateItem_UniqueID(t *testing.T) {
	router := setupTestRouter()
	
	payload := map[string]interface{}{
		"title": "Test Item",
		"type":  "REQUIREMENT",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	
	id := response["id"].(string)
	assert.NotEmpty(t, id)
	assert.Len(t, id, 36) // UUID v4 length
}

// PERFORMANCE TESTS

// Test 1.1.P1: Response time < 100ms
// Linked to: Performance Requirement 1
func TestCreateItem_ResponseTime_LessThan100ms(t *testing.T) {
	router := setupTestRouter()
	
	payload := map[string]interface{}{
		"title": "Test Item",
		"type":  "REQUIREMENT",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer test-token")
	
	start := time.Now()
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	elapsed := time.Since(start)
	
	assert.Equal(t, http.StatusCreated, w.Code)
	assert.Less(t, elapsed, 100*time.Millisecond)
}

// Test 1.1.P2: Database write < 50ms
// Linked to: Performance Requirement 2
func TestCreateItem_DatabaseWrite_LessThan50ms(t *testing.T) {
	// This test would measure database write time
	// Implementation depends on database setup
}

// AUTHORIZATION TESTS

// Test 1.1.A1: Unauthorized user cannot create item
// Linked to: Authorization Rule 1, Error Scenario 4
func TestCreateItem_Unauthorized_Error(t *testing.T) {
	router := setupTestRouter()
	
	payload := map[string]interface{}{
		"title": "Test Item",
		"type":  "REQUIREMENT",
	}
	
	body, _ := json.Marshal(payload)
	req := httptest.NewRequest("POST", "/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	// No Authorization header
	
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

// TOTAL TESTS: 15+ tests for FR-1.1 backend


