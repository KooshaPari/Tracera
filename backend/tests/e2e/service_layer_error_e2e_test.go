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
