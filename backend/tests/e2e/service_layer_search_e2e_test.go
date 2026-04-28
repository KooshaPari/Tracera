//go:build e2e

package e2e

import (
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// TestE2E_ServiceLayer_SearchAndFilter tests search functionality
// Scenario: Create diverse items -> Search with filters -> Verify results
func TestE2E_ServiceLayer_SearchAndFilter(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	token, projectID := setupUserAndProject(t, client, baseURL, "search@test.com", "Search Test Project")

	// Step 1: Create items with different characteristics
	createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title":    "Authentication Module",
		"type":     "feature",
		"priority": 3,
		"status":   "in_progress",
	})

	createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title":    "Login Bug Fix",
		"type":     "bug",
		"priority": 4,
		"status":   "todo",
	})

	createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title":    "User Authentication API",
		"type":     "task",
		"priority": 3,
		"status":   "completed",
	})

	createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title":    "Database Migration",
		"type":     "task",
		"priority": 1,
		"status":   "todo",
	})

	createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title":    "Update Authentication Documentation",
		"type":     "documentation",
		"priority": 2,
		"status":   "in_progress",
	})

	// Wait for indexing
	time.Sleep(500 * time.Millisecond)

	// Step 2: Search for "authentication"
	results := searchItems(t, client, baseURL, token, map[string]interface{}{
		"query":      "authentication",
		"project_id": projectID,
	})
	assert.GreaterOrEqual(t, len(results), 3, "Should find at least 3 items with 'authentication'")

	// Step 3: Filter by type
	taskItems := filterProjectItems(t, client, baseURL, token, projectID, map[string]string{
		"type": "task",
	})
	assert.GreaterOrEqual(t, len(taskItems), 2, "Should have at least 2 tasks")

	// Step 4: Filter by status
	todoItems := filterProjectItems(t, client, baseURL, token, projectID, map[string]string{
		"status": "todo",
	})
	assert.GreaterOrEqual(t, len(todoItems), 2, "Should have at least 2 todo items")

	// Step 5: Filter by priority
	highPriorityItems := filterProjectItems(t, client, baseURL, token, projectID, map[string]string{
		"priority": 3,
	})
	assert.GreaterOrEqual(t, len(highPriorityItems), 2, "Should have at least 2 high priority items")
}
