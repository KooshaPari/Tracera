package tests

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/models"
)

// setupTestPool creates a test database pool
// Note: Requires PostgreSQL to be running
func setupTestPool(t *testing.T) *pgxpool.Pool {
	ctx := context.Background()
	pool, err := pgxpool.New(ctx, "postgresql://postgres:password@localhost:5432/tracertm_test")
	assert.NoError(t, err)
	return pool
}

// TestCreateItem tests item creation with sqlc
func TestCreateItem(t *testing.T) {
	t.Skip("Requires PostgreSQL database - run with: go test -run TestCreateItem")

	pool := setupTestPool(t)
	defer func() {
		pool.Close()
	}()

	handler := handlers.NewItemHandler(pool)

	e := echo.New()
	itemJSON := `{
		"project_id": "550e8400-e29b-41d4-a716-446655440000",
		"title": "Test Item",
		"description": "Test Description",
		"type": "feature",
		"status": "open",
		"priority": 3
	}`

	req := httptest.NewRequest(http.MethodPost, "/api/v1/items", strings.NewReader(itemJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.CreateItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var item db.Item
	err = json.Unmarshal(rec.Body.Bytes(), &item)
	assert.NoError(t, err)
	assert.NotEmpty(t, item.ID)
}

func TestCreateItemInvalidJSON(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewItemHandler(db)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/items", strings.NewReader("{invalid json}"))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.CreateItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestListItems(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewItemHandler(db)

	// Create test items
	items := []models.Item{
		{ProjectID: "project-1", Title: "Item 1", Type: "feature", Status: "open", Priority: models.PriorityHigh},
		{ProjectID: "project-1", Title: "Item 2", Type: "bug", Status: "open", Priority: models.PriorityMedium},
		{ProjectID: "project-2", Title: "Item 3", Type: "task", Status: "done", Priority: models.PriorityLow},
	}
	for _, item := range items {
		db.Create(&item)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListItems(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []models.Item
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Len(t, result, 3)
}

func TestListItemsFilteredByProject(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewItemHandler(db)

	// Create test items
	items := []models.Item{
		{ProjectID: "project-1", Title: "Item 1", Type: "feature", Status: "open", Priority: models.PriorityHigh},
		{ProjectID: "project-1", Title: "Item 2", Type: "bug", Status: "open", Priority: models.PriorityMedium},
		{ProjectID: "project-2", Title: "Item 3", Type: "task", Status: "done", Priority: models.PriorityLow},
	}
	for _, item := range items {
		db.Create(&item)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items?project_id=project-1", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListItems(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []models.Item
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Len(t, result, 2)
	for _, item := range result {
		assert.Equal(t, "project-1", item.ProjectID)
	}
}

func TestGetItem(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewItemHandler(db)

	// Create test item
	item := models.Item{
		ID:        "item-123",
		ProjectID: "project-1",
		Title:     "Test Item",
		Type:      "feature",
		Status:    "open",
		Priority:  models.PriorityHigh,
	}
	db.Create(&item)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items/item-123", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("item-123")

	err := handler.GetItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result models.Item
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Equal(t, "item-123", result.ID)
	assert.Equal(t, "Test Item", result.Title)
}

func TestGetItemNotFound(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewItemHandler(db)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items/nonexistent", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("nonexistent")

	err := handler.GetItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func TestUpdateItem(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewItemHandler(db)

	// Create test item
	item := models.Item{
		ID:        "item-123",
		ProjectID: "project-1",
		Title:     "Original Title",
		Type:      "feature",
		Status:    "open",
		Priority:  models.PriorityHigh,
	}
	db.Create(&item)

	e := echo.New()
	updateJSON := `{"title": "Updated Title", "status": "in_progress"}`
	req := httptest.NewRequest(http.MethodPut, "/api/v1/items/item-123", strings.NewReader(updateJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("item-123")

	err := handler.UpdateItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify the update
	var updated models.Item
	db.First(&updated, "id = ?", "item-123")
	assert.Equal(t, "Updated Title", updated.Title)
}

func TestDeleteItem(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewItemHandler(db)

	// Create test item
	item := models.Item{
		ID:        "item-123",
		ProjectID: "project-1",
		Title:     "To Delete",
		Type:      "feature",
		Status:    "open",
		Priority:  models.PriorityHigh,
	}
	db.Create(&item)

	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/items/item-123", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("item-123")

	err := handler.DeleteItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify the deletion
	var count int64
	db.Model(&models.Item{}).Where("id = ?", "item-123").Count(&count)
	assert.Equal(t, int64(0), count)
}
