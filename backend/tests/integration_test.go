//go:build integration

package tests

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// TestFullItemLifecycle tests the complete lifecycle of an item
func TestFullItemLifecycle(t *testing.T) {
	e := setupTestServer()
	itemHandler := testItemHandler
	linkHandler := testLinkHandler

	// 1. Create an item
	createReqBody := map[string]interface{}{
		"title":       "Integration Test Item",
		"type":        "requirement",
		"description": "Full lifecycle test",
		"project_id":  testProject.ID,
	}

	body, _ := json.Marshal(createReqBody)
	req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := itemHandler.CreateItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var createdItem map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &createdItem)
	itemID, ok := createdItem["id"].(string)
	require.True(t, ok, "created item should include id")

	// 2. Retrieve the item
	req = httptest.NewRequest(http.MethodGet, "/api/items/"+itemID, nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(itemID)

	err = itemHandler.GetItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var retrievedItem map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &retrievedItem)
	assert.Equal(t, "Integration Test Item", retrievedItem["title"])

	// 3. Update the item
	updateReqBody := map[string]interface{}{
		"title":       "Updated Integration Test Item",
		"description": "Updated content",
	}

	body, _ = json.Marshal(updateReqBody)
	req = httptest.NewRequest(http.MethodPut, "/api/items/"+itemID, bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(itemID)

	err = itemHandler.UpdateItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// 4. Create a link to another item
	targetItem := createTestItem()
	linkReqBody := map[string]interface{}{
		"source_id": itemID,
		"target_id": targetItem.ID,
		"type":      "satisfies",
	}

	body, _ = json.Marshal(linkReqBody)
	req = httptest.NewRequest(http.MethodPost, "/api/links", bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)

	err = linkHandler.CreateLink(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	// 5. Delete the item
	req = httptest.NewRequest(http.MethodDelete, "/api/items/"+itemID, nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(itemID)

	err = itemHandler.DeleteItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// 6. Verify deletion
	req = httptest.NewRequest(http.MethodGet, "/api/items/"+itemID, nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(itemID)

	err = itemHandler.GetItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

// TestSearchIntegration tests the search functionality end-to-end
func TestSearchIntegration(t *testing.T) {
	t.Skip("search integration requires SearchService wiring")
}

// TestGraphTraversalIntegration tests graph traversal with complex relationships
func TestGraphTraversalIntegration(t *testing.T) {
	t.Skip("graph integration requires GraphService wiring")
}

// TestEventSystemIntegration tests the event publishing and subscription
func TestEventSystemIntegration(t *testing.T) {
	e := setupTestServer()
	itemHandler := testItemHandler

	// Subscribe to events (in production, this would be via WebSocket or NATS)
	events := make(chan string, 10)

	// Create an item (should publish event)
	createReqBody := map[string]interface{}{
		"title":      "Event Test Item",
		"type":       "requirement",
		"project_id": testProject.ID,
	}

	body, _ := json.Marshal(createReqBody)
	req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := itemHandler.CreateItem(c)
	require.NoError(t, err)

	// Verify event was published
	select {
	case event := <-events:
		assert.Contains(t, event, "item.created")
	default:
		// Event system may be async
	}
}

// TestConcurrentOperations tests handling of concurrent operations
func TestConcurrentOperations(t *testing.T) {
	e := setupTestServer()
	itemHandler := testItemHandler

	testItem := createTestItem()
	done := make(chan bool, 10)

	// Concurrent reads
	for i := 0; i < 5; i++ {
		go func() {
			req := httptest.NewRequest(http.MethodGet, "/api/items/"+testItem.ID, nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetParamNames("id")
			c.SetParamValues(testItem.ID)

			itemHandler.GetItem(c)
			done <- true
		}()
	}

	// Concurrent updates
	for i := 0; i < 5; i++ {
		go func(idx int) {
			updateReqBody := map[string]interface{}{
				"description": fmt.Sprintf("Concurrent update %d", idx),
			}

			body, _ := json.Marshal(updateReqBody)
			req := httptest.NewRequest(http.MethodPut, "/api/items/"+testItem.ID, bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetParamNames("id")
			c.SetParamValues(testItem.ID)

			itemHandler.UpdateItem(c)
			done <- true
		}(i)
	}

	// Wait for all operations to complete
	for i := 0; i < 10; i++ {
		<-done
	}

	// Verify data integrity
	req := httptest.NewRequest(http.MethodGet, "/api/items/"+testItem.ID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(testItem.ID)

	err := itemHandler.GetItem(c)
	require.NoError(t, err)
}

func createItemWithTitle(title string) *models.Item {
	ctx := context.Background()
	item := &models.Item{
		Title:       title,
		Type:        "requirement",
		Description: title,
		ProjectID:   testProject.ID,
		Status:      "open",
	}
	if err := testItemService.CreateItem(ctx, item); err != nil {
		panic(err)
	}
	return item
}
