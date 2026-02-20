//go:build e2e

package e2e

import (
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// TestE2E_ServiceLayer_ProjectItemCreationWorkflow tests project to item creation
// Scenario: Create project -> Add multiple item types -> Verify hierarchy
func TestE2E_ServiceLayer_ProjectItemCreationWorkflow(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Setup: Create user
	token := setupUser(t, client, baseURL, "project.creator@test.com")

	// Step 1: Create project with metadata
	projectReq := map[string]interface{}{
		"name":        "E-Commerce Platform",
		"description": "Complete e-commerce solution",
		"metadata": map[string]interface{}{
			"budget":    "100000",
			"timeline":  "6 months",
			"team_size": 5,
		},
	}
	projectID := createProject(t, client, baseURL, token, projectReq)

	// Step 2: Create epic-level items
	epicIDs := make(map[string]string)
	epics := []struct {
		title    string
		priority string
	}{
		{"Product Catalog System", "high"},
		{"Shopping Cart & Checkout", "high"},
		{"User Account Management", "medium"},
		{"Payment Integration", "high"},
		{"Order Management", "medium"},
	}

	for _, epic := range epics {
		epicIDs[epic.title] = createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title":    epic.title,
			"type":     "epic",
			"priority": epic.priority,
			"status":   "planned",
		})
	}

	// Step 3: Create features for first epic
	catalogEpicID := epicIDs["Product Catalog System"]
	featureIDs := make([]string, 0)

	features := []string{
		"Product listing page",
		"Product search functionality",
		"Product detail view",
		"Category navigation",
	}

	for _, featureTitle := range features {
		featureID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title":  featureTitle,
			"type":   "feature",
			"status": "todo",
		})
		featureIDs = append(featureIDs, featureID)

		// Link feature to epic
		createLink(t, client, baseURL, token, featureID, catalogEpicID, "part_of", nil)
	}

	// Step 4: Create tasks for first feature
	listingFeatureID := featureIDs[0]
	taskTitles := []string{
		"Design product card component",
		"Implement grid layout",
		"Add pagination",
		"Optimize image loading",
	}

	for _, taskTitle := range taskTitles {
		taskID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title":  taskTitle,
			"type":   "task",
			"status": "todo",
		})

		// Link task to feature
		createLink(t, client, baseURL, token, taskID, listingFeatureID, "implements", nil)
	}

	// Step 5: Verify project hierarchy
	projectDetails := getProject(t, client, baseURL, token, projectID)

	// Should have items created
	items := listProjectItems(t, client, baseURL, token, projectID)
	assert.GreaterOrEqual(t, len(items), 13, "Project should have 5 epics + 4 features + 4 tasks")

	// Step 6: Verify epic has correct children
	epicLinks := getItemLinks(t, client, baseURL, token, catalogEpicID)
	featureCount := 0
	for _, link := range epicLinks {
		if link["type"] == "part_of" {
			featureCount++
		}
	}
	assert.Equal(t, 4, featureCount, "Epic should have 4 features")

	// Step 7: Verify metadata preserved
	assert.Equal(t, "E-Commerce Platform", projectDetails["name"])
	metadata := projectDetails["metadata"].(map[string]interface{})
	assert.Equal(t, "100000", metadata["budget"])
}

// TestE2E_ServiceLayer_ComplexGraphTraversal tests deep item hierarchies
// Scenario: Create deep hierarchy -> Traverse -> Verify relationships
func TestE2E_ServiceLayer_ComplexGraphTraversal(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	token, projectID := setupUserAndProject(t, client, baseURL, "graph@test.com", "Graph Traversal Project")

	// Step 1: Create 4-level hierarchy (Epic -> Feature -> Task -> Subtask)
	epicID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title": "Major Initiative",
		"type":  "epic",
	})

	// Create 3 features under epic
	featureIDs := make([]string, 3)
	for i := 0; i < 3; i++ {
		featureIDs[i] = createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title": fmt.Sprintf("Feature %d", i+1),
			"type":  "feature",
		})
		createLink(t, client, baseURL, token, featureIDs[i], epicID, "part_of", nil)
	}

	// Create 2 tasks under each feature
	taskIDs := make([]string, 0)
	for _, featureID := range featureIDs {
		for j := 0; j < 2; j++ {
			taskID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
				"title": fmt.Sprintf("Task for feature %s-%d", featureID[:8], j+1),
				"type":  "task",
			})
			taskIDs = append(taskIDs, taskID)
			createLink(t, client, baseURL, token, taskID, featureID, "implements", nil)
		}
	}

	// Create subtasks under first task
	subtaskIDs := make([]string, 2)
	for i := 0; i < 2; i++ {
		subtaskIDs[i] = createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title": fmt.Sprintf("Subtask %d", i+1),
			"type":  "subtask",
		})
		createLink(t, client, baseURL, token, subtaskIDs[i], taskIDs[0], "part_of", nil)
	}

	// Step 2: Verify hierarchy depth
	epicLinks := getItemLinks(t, client, baseURL, token, epicID)
	assert.GreaterOrEqual(t, len(epicLinks), 3, "Epic should have 3 features")

	// Step 3: Verify feature has tasks
	feature1Links := getItemLinks(t, client, baseURL, token, featureIDs[0])
	assert.GreaterOrEqual(t, len(feature1Links), 2, "Feature should have at least 2 tasks")

	// Step 4: Verify task has subtasks
	task1Links := getItemLinks(t, client, baseURL, token, taskIDs[0])
	assert.GreaterOrEqual(t, len(task1Links), 2, "Task should have at least 2 subtasks")

	// Step 5: Total item count verification
	allItems := listProjectItems(t, client, baseURL, token, projectID)
	assert.GreaterOrEqual(t, len(allItems), 12, "Should have epic + 3 features + 6 tasks + 2 subtasks")
}
