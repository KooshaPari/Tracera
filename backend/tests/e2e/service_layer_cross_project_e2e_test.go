//go:build e2e

package e2e

import (
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

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
