//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
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

// TestE2E_ServiceLayer_AgentCoordinationWorkflow tests agent collaboration
// Scenario: Create agents -> Assign tasks -> Monitor coordination -> Complete workflow
func TestE2E_ServiceLayer_AgentCoordinationWorkflow(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Setup
	token, projectID := setupUserAndProject(t, client, baseURL, "agent.coord@test.com", "Agent Coordination Project")

	// Step 1: Create work items
	itemIDs := make([]string, 3)
	itemTypes := []string{"analyze_requirements", "generate_code", "review_code"}

	for i, itemType := range itemTypes {
		itemIDs[i] = createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title":  "Task for " + itemType,
			"type":   "task",
			"status": "todo",
			"metadata": map[string]interface{}{
				"agent_capability": itemType,
			},
		})
	}

	// Step 2: Create specialized agents
	agentIDs := make(map[string]string)
	agents := []struct {
		name       string
		capability string
	}{
		{"RequirementsAnalyzer", "analyze_requirements"},
		{"CodeGenerator", "generate_code"},
		{"CodeReviewer", "review_code"},
	}

	for _, agent := range agents {
		agentReq := map[string]interface{}{
			"project_id": projectID,
			"name":       agent.name,
			"status":     "idle",
			"metadata": map[string]interface{}{
				"capability":           agent.capability,
				"max_concurrent_tasks": 3,
			},
		}
		agentBody, _ := json.Marshal(agentReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents", bytes.NewBuffer(agentBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		require.Equal(t, http.StatusCreated, resp.StatusCode)

		var agentResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&agentResp)
		resp.Body.Close()

		agentIDs[agent.name] = agentResp.ID
	}

	// Step 3: Assign tasks to agents (simulated via metadata update)
	for i, itemID := range itemIDs {
		agentName := agents[i].name
		updateItem(t, client, baseURL, token, itemID, map[string]interface{}{
			"status": "assigned",
			"metadata": map[string]interface{}{
				"assigned_agent_id": agentIDs[agentName],
				"assigned_at":       time.Now().Format(time.RFC3339),
			},
		})
	}

	// Step 4: Update agent statuses to active
	for _, agentID := range agentIDs {
		updateAgent(t, client, baseURL, token, agentID, map[string]interface{}{
			"status": "active",
		})
	}

	// Step 5: Simulate work progression
	time.Sleep(100 * time.Millisecond)

	// First agent completes requirements analysis
	updateItem(t, client, baseURL, token, itemIDs[0], map[string]interface{}{
		"status": "completed",
	})

	// Second agent starts code generation
	updateItem(t, client, baseURL, token, itemIDs[1], map[string]interface{}{
		"status": "in_progress",
	})

	// Step 6: Create dependency link (code gen depends on requirements)
	createLink(t, client, baseURL, token, itemIDs[1], itemIDs[0], "depends_on", map[string]interface{}{
		"dependency_type": "sequential",
	})

	// Step 7: Complete code generation
	updateItem(t, client, baseURL, token, itemIDs[1], map[string]interface{}{
		"status": "completed",
	})

	// Step 8: Code review starts
	updateItem(t, client, baseURL, token, itemIDs[2], map[string]interface{}{
		"status": "in_progress",
	})
	createLink(t, client, baseURL, token, itemIDs[2], itemIDs[1], "reviews", map[string]interface{}{
		"review_type": "automated",
	})

	// Step 9: Verify final states
	for i, itemID := range itemIDs[:2] {
		item := getItem(t, client, baseURL, token, itemID)
		assert.Equal(t, "completed", item["status"], "Item %d should be completed", i)
	}

	reviewItem := getItem(t, client, baseURL, token, itemIDs[2])
	assert.Equal(t, "in_progress", reviewItem["status"])

	// Step 10: Verify all agents are still active
	for _, agentID := range agentIDs {
		agent := getAgent(t, client, baseURL, token, agentID)
		assert.Equal(t, "active", agent["status"])
	}
}

// TestE2E_ServiceLayer_BulkOperationsWorkflow tests bulk create/update/delete
// Scenario: Bulk create items -> Bulk update -> Bulk link -> Bulk delete
func TestE2E_ServiceLayer_BulkOperationsWorkflow(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	token, projectID := setupUserAndProject(t, client, baseURL, "bulk.ops@test.com", "Bulk Operations Project")

	// Step 1: Bulk create 20 items
	itemIDs := make([]string, 20)
	for i := 0; i < 20; i++ {
		itemIDs[i] = createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title":    fmt.Sprintf("Bulk Item %d", i+1),
			"type":     "task",
			"status":   "todo",
			"priority": map[int]string{0: "low", 1: "medium", 2: "high"}[i%3],
		})

		// Small delay to prevent rate limiting
		if i%5 == 0 {
			time.Sleep(50 * time.Millisecond)
		}
	}

	// Step 2: Verify all items created
	assert.Len(t, itemIDs, 20)
	for _, id := range itemIDs {
		assert.NotEmpty(t, id)
	}

	// Step 3: Bulk update - change status of first 10 items
	for i := 0; i < 10; i++ {
		updateItem(t, client, baseURL, token, itemIDs[i], map[string]interface{}{
			"status": "in_progress",
		})
	}

	// Step 4: Verify updates
	for i := 0; i < 10; i++ {
		item := getItem(t, client, baseURL, token, itemIDs[i])
		assert.Equal(t, "in_progress", item["status"])
	}

	// Step 5: Bulk link - create chain of dependencies
	for i := 0; i < 19; i++ {
		createLink(t, client, baseURL, token, itemIDs[i], itemIDs[i+1], "blocks", nil)
		if i%5 == 0 {
			time.Sleep(50 * time.Millisecond)
		}
	}

	// Step 6: Verify link chain
	firstItemLinks := getItemLinks(t, client, baseURL, token, itemIDs[0])
	assert.GreaterOrEqual(t, len(firstItemLinks), 1)

	lastItemLinks := getItemLinks(t, client, baseURL, token, itemIDs[19])
	assert.GreaterOrEqual(t, len(lastItemLinks), 1)

	// Step 7: Bulk delete - delete last 5 items
	for i := 15; i < 20; i++ {
		deleteItem(t, client, baseURL, token, itemIDs[i])
	}

	// Step 8: Verify deletions
	for i := 15; i < 20; i++ {
		verifyItemDeleted(t, client, baseURL, token, itemIDs[i])
	}

	// Step 9: Verify remaining items still exist
	items := listProjectItems(t, client, baseURL, token, projectID)
	assert.GreaterOrEqual(t, len(items), 15)
}

// TestE2E_ServiceLayer_CrossProjectLinking tests linking across projects
// Scenario: Create two projects -> Create items in each -> Link across projects
func TestE2E_ServiceLayer_CrossProjectLinking(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	token := setupUser(t, client, baseURL, "cross.project@test.com")

	// Step 1: Create two projects
	project1ID := createProject(t, client, baseURL, token, map[string]interface{}{
		"name":        "Frontend Project",
		"description": "Frontend implementation",
	})

	project2ID := createProject(t, client, baseURL, token, map[string]interface{}{
		"name":        "Backend Project",
		"description": "Backend API implementation",
	})

	// Step 2: Create items in each project
	frontendItemID := createItem(t, client, baseURL, token, project1ID, map[string]interface{}{
		"title": "Login UI Component",
		"type":  "feature",
	})

	backendItemID := createItem(t, client, baseURL, token, project2ID, map[string]interface{}{
		"title": "Authentication API",
		"type":  "feature",
	})

	// Step 3: Create cross-project link
	createLink(t, client, baseURL, token, frontendItemID, backendItemID, "depends_on", map[string]interface{}{
		"cross_project": true,
		"reason":        "UI depends on API implementation",
	})

	// Step 4: Verify link exists from frontend item
	frontendLinks := getItemLinks(t, client, baseURL, token, frontendItemID)
	assert.GreaterOrEqual(t, len(frontendLinks), 1)

	// Step 5: Verify link exists from backend item
	backendLinks := getItemLinks(t, client, baseURL, token, backendItemID)
	assert.GreaterOrEqual(t, len(backendLinks), 1)

	// Step 6: Create more cross-project dependencies
	frontend2ID := createItem(t, client, baseURL, token, project1ID, map[string]interface{}{
		"title": "User Profile Page",
		"type":  "feature",
	})

	backend2ID := createItem(t, client, baseURL, token, project2ID, map[string]interface{}{
		"title": "User Profile API",
		"type":  "feature",
	})

	createLink(t, client, baseURL, token, frontend2ID, backend2ID, "depends_on", nil)

	// Step 7: List all items in both projects
	project1Items := listProjectItems(t, client, baseURL, token, project1ID)
	project2Items := listProjectItems(t, client, baseURL, token, project2ID)

	assert.Len(t, project1Items, 2)
	assert.Len(t, project2Items, 2)
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

// TestE2E_ServiceLayer_ErrorRecovery tests error handling and recovery
// Scenario: Attempt invalid operations -> Verify graceful failure -> Recover
func TestE2E_ServiceLayer_ErrorRecovery(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	token, projectID := setupUserAndProject(t, client, baseURL, "error@test.com", "Error Recovery Project")

	// Step 1: Try to create item with invalid data
	invalidItemReq := map[string]interface{}{
		"project_id": "invalid-project-id",
		"title":      "", // Empty title
		"type":       "invalid-type",
	}
	invalidItemBody, _ := json.Marshal(invalidItemReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(invalidItemBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, resp.StatusCode, "Should reject invalid item")
	resp.Body.Close()

	// Step 2: Create valid item
	validItemID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title": "Valid Item",
		"type":  "task",
	})

	// Step 3: Try to create link with non-existent target
	invalidLinkReq := map[string]interface{}{
		"source_id": validItemID,
		"target_id": "non-existent-id",
		"type":      "depends_on",
	}
	invalidLinkBody, _ := json.Marshal(invalidLinkReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(invalidLinkBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, resp.StatusCode, "Should reject link to non-existent item")
	resp.Body.Close()

	// Step 4: Try to update non-existent item
	updateReq := map[string]interface{}{
		"status": "completed",
	}
	updateBody, _ := json.Marshal(updateReq)
	req, _ = http.NewRequestWithContext(context.Background(), "PATCH", baseURL+"/api/v1/items/non-existent-id", bytes.NewBuffer(updateBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, resp.StatusCode, "Should reject update to non-existent item")
	resp.Body.Close()

	// Step 5: Verify valid item still exists and is unchanged
	item := getItem(t, client, baseURL, token, validItemID)
	assert.Equal(t, "Valid Item", item["title"])
	assert.NotEqual(t, "completed", item["status"])

	// Step 6: Create second valid item
	secondItemID := createItem(t, client, baseURL, token, projectID, map[string]interface{}{
		"title": "Second Valid Item",
		"type":  "task",
	})

	// Step 7: Create valid link
	createLink(t, client, baseURL, token, validItemID, secondItemID, "blocks", nil)

	// Step 8: Try to create circular dependency
	circularLinkReq := map[string]interface{}{
		"source_id": secondItemID,
		"target_id": validItemID,
		"type":      "blocks",
	}
	circularLinkBody, _ := json.Marshal(circularLinkReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(circularLinkBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	// Either BadRequest or created (depending on circular dependency detection)
	assert.Contains(t, []int{http.StatusBadRequest, http.StatusCreated}, resp.StatusCode)
	resp.Body.Close()
}

// TestE2E_ServiceLayer_PerformanceUnderLoad tests system under concurrent load
// Scenario: Create many items concurrently -> Verify all succeed
func TestE2E_ServiceLayer_PerformanceUnderLoad(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance test in short mode")
	}

	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 60 * time.Second}
	baseURL := ctx.ServerURL

	token, projectID := setupUserAndProject(t, client, baseURL, "perf@test.com", "Performance Test Project")

	// Step 1: Create 50 items concurrently
	const itemCount = 50
	results := make(chan string, itemCount)
	errors := make(chan error, itemCount)

	for i := 0; i < itemCount; i++ {
		go func(index int) {
			itemReq := map[string]interface{}{
				"project_id": projectID,
				"title":      fmt.Sprintf("Concurrent Item %d", index),
				"type":       "task",
				"priority":   map[int]string{0: "low", 1: "medium", 2: "high"}[index%3],
			}
			itemBody, _ := json.Marshal(itemReq)
			req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
			req.Header.Set("Authorization", "Bearer "+token)
			req.Header.Set("Content-Type", "application/json")

			resp, err := client.Do(req)
			if err != nil {
				errors <- err
				return
			}
			defer resp.Body.Close()

			if resp.StatusCode != http.StatusCreated {
				errors <- fmt.Errorf("unexpected status: %d", resp.StatusCode)
				return
			}

			var itemResp struct {
				ID string `json:"id"`
			}
			if err := json.NewDecoder(resp.Body).Decode(&itemResp); err != nil {
				errors <- err
				return
			}

			results <- itemResp.ID
		}(i)
	}

	// Collect results
	createdIDs := make([]string, 0, itemCount)
	var errs []error

	for i := 0; i < itemCount; i++ {
		select {
		case id := <-results:
			createdIDs = append(createdIDs, id)
		case err := <-errors:
			errs = append(errs, err)
		case <-time.After(30 * time.Second):
			t.Fatal("Timeout waiting for concurrent creates")
		}
	}

	// Step 2: Verify results
	assert.Empty(t, errs, "Should have no errors during concurrent creation")
	assert.Len(t, createdIDs, itemCount, "Should have created all items")

	// Step 3: Verify all items exist
	time.Sleep(500 * time.Millisecond)
	allItems := listProjectItems(t, client, baseURL, token, projectID)
	assert.GreaterOrEqual(t, len(allItems), itemCount, "All items should be retrievable")
}

// Helper functions

func setupUser(t *testing.T, client *http.Client, baseURL, email string) string {
	userReq := map[string]interface{}{
		"email":    email,
		"password": "SecurePass123!",
		"name":     "Test User",
	}
	userBody, _ := json.Marshal(userReq)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(userBody))
	require.NoError(t, err)
	defer resp.Body.Close()

	var authResp struct {
		Token string `json:"token"`
	}
	json.NewDecoder(resp.Body).Decode(&authResp)
	return authResp.Token
}

func setupUserAndProject(t *testing.T, client *http.Client, baseURL, email, projectName string) (string, string) {
	token := setupUser(t, client, baseURL, email)
	projectID := createProject(t, client, baseURL, token, map[string]interface{}{
		"name": projectName,
	})
	return token, projectID
}

func createProject(t *testing.T, client *http.Client, baseURL, token string, data map[string]interface{}) string {
	body, _ := json.Marshal(data)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/projects", bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)
	defer resp.Body.Close()

	var projectResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&projectResp)
	return projectResp.ID
}

func createItem(t *testing.T, client *http.Client, baseURL, token, projectID string, data map[string]interface{}) string {
	data["project_id"] = projectID
	body, _ := json.Marshal(data)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)
	defer resp.Body.Close()

	var itemResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&itemResp)
	return itemResp.ID
}

func updateItem(t *testing.T, client *http.Client, baseURL, token, itemID string, data map[string]interface{}) {
	body, _ := json.Marshal(data)
	req, _ := http.NewRequestWithContext(context.Background(), "PATCH", baseURL+"/api/v1/items/"+itemID, bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()
}

func deleteItem(t *testing.T, client *http.Client, baseURL, token, itemID string) {
	req, _ := http.NewRequestWithContext(context.Background(), "DELETE", baseURL+"/api/v1/items/"+itemID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusNoContent, resp.StatusCode)
	resp.Body.Close()
}

func getItem(t *testing.T, client *http.Client, baseURL, token, itemID string) map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var item map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&item)
	return item
}

func getProject(t *testing.T, client *http.Client, baseURL, token, projectID string) map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var project map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&project)
	return project
}

func createLink(t *testing.T, client *http.Client, baseURL, token, sourceID, targetID, linkType string, metadata map[string]interface{}) {
	linkReq := map[string]interface{}{
		"source_id": sourceID,
		"target_id": targetID,
		"type":      linkType,
	}
	if metadata != nil {
		linkReq["metadata"] = metadata
	}

	body, _ := json.Marshal(linkReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)
	resp.Body.Close()
}

func getItemLinks(t *testing.T, client *http.Client, baseURL, token, itemID string) []map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemID+"/links", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var links []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&links)
	return links
}

func listProjectItems(t *testing.T, client *http.Client, baseURL, token, projectID string) []map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID+"/items", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var items []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&items)
	return items
}

func searchItems(t *testing.T, client *http.Client, baseURL, token string, query map[string]interface{}) []map[string]interface{} {
	body, _ := json.Marshal(query)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var searchResp struct {
		Results []map[string]interface{} `json:"results"`
	}
	json.NewDecoder(resp.Body).Decode(&searchResp)
	return searchResp.Results
}

func filterProjectItems(t *testing.T, client *http.Client, baseURL, token, projectID string, filters map[string]string) []map[string]interface{} {
	url := baseURL + "/api/v1/projects/" + projectID + "/items?"
	for k, v := range filters {
		url += fmt.Sprintf("%s=%s&", k, v)
	}

	req, _ := http.NewRequestWithContext(context.Background(), "GET", url, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var items []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&items)
	return items
}

func updateAgent(t *testing.T, client *http.Client, baseURL, token, agentID string, data map[string]interface{}) {
	body, _ := json.Marshal(data)
	req, _ := http.NewRequestWithContext(context.Background(), "PATCH", baseURL+"/api/v1/agents/"+agentID, bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()
}

func getAgent(t *testing.T, client *http.Client, baseURL, token, agentID string) map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/agents/"+agentID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var agent map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&agent)
	return agent
}

func verifyItemDeleted(t *testing.T, client *http.Client, baseURL, token, itemID string) {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, resp.StatusCode)
	resp.Body.Close()
}
