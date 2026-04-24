//go:build e2e

package e2e

import (
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

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
