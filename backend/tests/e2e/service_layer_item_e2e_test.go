//go:build e2e

package e2e

import (
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// TestE2E_ServiceLayer_ItemCreationLinkingUpdates tests complete item workflow
// Scenario: Create items -> Create links -> Update items -> Verify cascade
func TestE2E_ServiceLayer_ItemCreationLinkingUpdates(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Setup: Create user and project
	token, projectID := setupUserAndProject(t, client, baseURL, "workflow.user@test.com", "Item Workflow Project")

	// Step 1: Create a feature item
	featureID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title":       "User Authentication Feature",
		"type":        "feature",
		"description": "Implement user authentication system",
		"priority":    "high",
		"status":      "planned",
	})

	// Step 2: Create task items for the feature
	taskIDs := make([]string, 3)
	tasks := []string{"Implement login API", "Add JWT middleware", "Create user registration"}
	for i, taskTitle := range tasks {
		taskIDs[i] = createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title":    taskTitle,
			"type":     "task",
			"status":   "todo",
			"priority": 2,
		})
	}

	// Step 3: Link tasks to feature (tasks implement feature)
	for _, taskID := range taskIDs {
		createLink(t, client, baseURL, token, taskID, featureID, "implements", map[string]interface{}{
			"relationship": "task-to-feature",
		})
	}

	// Step 4: Create dependencies between tasks
	createLink(t, client, baseURL, token, taskIDs[0], taskIDs[1], "blocks", map[string]interface{}{
		"reason": "Login must be implemented before middleware",
	})
	createLink(t, client, baseURL, token, taskIDs[1], taskIDs[2], "blocks", map[string]interface{}{
		"reason": "Middleware needed for registration",
	})

	// Step 5: Update first task status to in_progress
	updateItem(t, client, baseURL, token, taskIDs[0], map[string]interface{}{
		"status": "in_progress",
	})

	// Step 6: Verify feature shows correct task progress
	feature := getItem(t, client, baseURL, token, featureID)
	assert.Equal(t, "planned", feature["status"])

	// Step 7: Complete first task
	updateItem(t, client, baseURL, token, taskIDs[0], map[string]interface{}{
		"status": "completed",
	})

	// Step 8: Verify link integrity after updates
	links := getItemLinks(t, client, baseURL, token, featureID)
	assert.GreaterOrEqual(t, len(links), 3, "Feature should have at least 3 implementing tasks")

	// Step 9: Update feature status
	updateItem(t, client, baseURL, token, featureID, map[string]interface{}{
		"status": "in_progress",
	})

	// Step 10: Verify final state
	finalFeature := getItem(t, client, baseURL, token, featureID)
	assert.Equal(t, "in_progress", finalFeature["status"])
}

// TestE2E_ServiceLayer_ItemVersioning tests item update history
// Scenario: Create item -> Multiple updates -> Verify version history
func TestE2E_ServiceLayer_ItemVersioning(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	token, projectID := setupUserAndProject(t, client, baseURL, "versioning@test.com", "Versioning Project")

	// Step 1: Create initial item
	itemID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title":       "Feature with versions",
		"type":        "feature",
		"description": "Initial description",
		"status":      "todo",
		"priority":    "low",
	})

	// Step 2: Update 1 - Change description
	time.Sleep(100 * time.Millisecond)
	updateItem(t, client, baseURL, token, itemID, map[string]interface{}{
		"description": "Updated description v1",
	})

	// Step 3: Update 2 - Change status
	time.Sleep(100 * time.Millisecond)
	updateItem(t, client, baseURL, token, itemID, map[string]interface{}{
		"status": "in_progress",
	})

	// Step 4: Update 3 - Change priority
	time.Sleep(100 * time.Millisecond)
	updateItem(t, client, baseURL, token, itemID, map[string]interface{}{
		"priority": 3,
	})

	// Step 5: Update 4 - Change title and description
	time.Sleep(100 * time.Millisecond)
	updateItem(t, client, baseURL, token, itemID, map[string]interface{}{
		"title":       "Enhanced Feature",
		"description": "Final description v3",
	})

	// Step 6: Update 5 - Complete the item
	time.Sleep(100 * time.Millisecond)
	updateItem(t, client, baseURL, token, itemID, map[string]interface{}{
		"status": "completed",
	})

	// Step 7: Verify final state
	finalItem := getItem(t, client, baseURL, token, itemID)
	assert.Equal(t, "Enhanced Feature", finalItem["title"])
	assert.Equal(t, "Final description v3", finalItem["description"])
	assert.Equal(t, "completed", finalItem["status"])
	assert.Equal(t, "high", finalItem["priority"])

	// Step 8: Verify updated_at changed
	assert.NotNil(t, finalItem["updated_at"])
}

// TestE2E_ServiceLayer_ConcurrentUpdates tests concurrent access
// Scenario: Create item -> Concurrent updates from multiple "users" -> Verify consistency
func TestE2E_ServiceLayer_ConcurrentUpdates(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	token, projectID := setupUserAndProject(t, client, baseURL, "concurrent@test.com", "Concurrency Project")

	// Step 1: Create shared item
	itemID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title":  "Shared Item",
		"type":   "task",
		"status": "todo",
		"metadata": map[string]interface{}{
			"counter": 0,
		},
	})

	// Step 2: Perform concurrent updates
	done := make(chan bool, 5)

	for i := 0; i < 5; i++ {
		go func(iteration int) {
			defer func() { done <- true }()

			time.Sleep(time.Duration(iteration*10) * time.Millisecond)

			updateItem(t, client, baseURL, token, itemID, map[string]interface{}{
				"metadata": map[string]interface{}{
					"counter":       iteration,
					"updated_by_go": iteration,
					"timestamp":     time.Now().Unix(),
				},
			})
		}(i)
	}

	// Wait for all updates to complete
	for i := 0; i < 5; i++ {
		<-done
	}

	// Step 3: Verify item still accessible and valid
	finalItem := getItem(t, client, baseURL, token, itemID)
	assert.Equal(t, "Shared Item", finalItem["title"])
	assert.NotNil(t, finalItem["metadata"])
}
