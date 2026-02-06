package tests

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"

	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestCreateLink(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	e := echo.New()
	linkJSON := `{
		"source_id": "item-1",
		"target_id": "item-2",
		"type": "depends_on"
	}`

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", strings.NewReader(linkJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.CreateLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var link models.Link
	err = json.Unmarshal(rec.Body.Bytes(), &link)
	assert.NoError(t, err)
	assert.NotEmpty(t, link.ID)
	assert.Equal(t, "item-1", link.SourceID)
	assert.Equal(t, "item-2", link.TargetID)
	assert.Equal(t, "depends_on", link.Type)
}

func TestCreateLinkInvalidJSON(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", strings.NewReader("{invalid}"))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.CreateLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestListLinks(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test links
	links := []models.Link{
		{SourceID: "item-1", TargetID: "item-2", Type: "depends_on"},
		{SourceID: "item-2", TargetID: "item-3", Type: "implements"},
		{SourceID: "item-1", TargetID: "item-3", Type: "tests"},
	}
	for _, link := range links {
		db.Create(&link)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []models.Link
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Len(t, result, 3)
}

func TestListLinksFilteredBySource(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test links
	links := []models.Link{
		{SourceID: "item-1", TargetID: "item-2", Type: "depends_on"},
		{SourceID: "item-2", TargetID: "item-3", Type: "implements"},
		{SourceID: "item-1", TargetID: "item-3", Type: "tests"},
	}
	for _, link := range links {
		db.Create(&link)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links?source_id=item-1", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []models.Link
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Len(t, result, 2)
	for _, link := range result {
		assert.Equal(t, "item-1", link.SourceID)
	}
}

func TestListLinksFilteredByTarget(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test links
	links := []models.Link{
		{SourceID: "item-1", TargetID: "item-2", Type: "depends_on"},
		{SourceID: "item-2", TargetID: "item-3", Type: "implements"},
		{SourceID: "item-1", TargetID: "item-3", Type: "tests"},
	}
	for _, link := range links {
		db.Create(&link)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links?target_id=item-3", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []models.Link
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Len(t, result, 2)
	for _, link := range result {
		assert.Equal(t, "item-3", link.TargetID)
	}
}

func TestListLinksFilteredByType(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test links
	links := []models.Link{
		{SourceID: "item-1", TargetID: "item-2", Type: "depends_on"},
		{SourceID: "item-2", TargetID: "item-3", Type: "implements"},
		{SourceID: "item-1", TargetID: "item-3", Type: "depends_on"},
	}
	for _, link := range links {
		db.Create(&link)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links?type=depends_on", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []models.Link
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Len(t, result, 2)
	for _, link := range result {
		assert.Equal(t, "depends_on", link.Type)
	}
}

func TestGetLink(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test link
	link := models.Link{
		ID:       "link-123",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "implements",
	}
	db.Create(&link)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links/link-123", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("link-123")

	err := handler.GetLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result models.Link
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Equal(t, "link-123", result.ID)
	assert.Equal(t, "implements", result.Type)
}

func TestGetLinkNotFound(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links/nonexistent", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("nonexistent")

	err := handler.GetLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func TestUpdateLink(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test link
	link := models.Link{
		ID:       "link-123",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "depends_on",
	}
	db.Create(&link)

	e := echo.New()
	updateJSON := `{"type": "implements"}`
	req := httptest.NewRequest(http.MethodPut, "/api/v1/links/link-123", strings.NewReader(updateJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("link-123")

	err := handler.UpdateLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify the update
	var updated models.Link
	db.First(&updated, "id = ?", "link-123")
	assert.Equal(t, "implements", updated.Type)
}

func TestUpdateLinkWithMetadata(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test link
	link := models.Link{
		ID:       "link-456",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "depends_on",
	}
	db.Create(&link)

	e := echo.New()
	updateJSON := `{"type": "implements", "metadata": {"strength": "high"}}`
	req := httptest.NewRequest(http.MethodPut, "/api/v1/links/link-456", strings.NewReader(updateJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("link-456")

	err := handler.UpdateLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify the update
	var result models.Link
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Equal(t, "implements", result.Type)
}

func TestUpdateLinkInvalidID(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	e := echo.New()
	updateJSON := `{"type": "implements"}`
	req := httptest.NewRequest(http.MethodPut, "/api/v1/links/invalid-id", strings.NewReader(updateJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid-id")

	err := handler.UpdateLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestUpdateLinkMissingType(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test link
	link := models.Link{
		ID:       "link-789",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "depends_on",
	}
	db.Create(&link)

	e := echo.New()
	updateJSON := `{}`
	req := httptest.NewRequest(http.MethodPut, "/api/v1/links/link-789", strings.NewReader(updateJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("link-789")

	err := handler.UpdateLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestUpdateLinkNotFound(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	e := echo.New()
	updateJSON := `{"type": "implements"}`
	req := httptest.NewRequest(http.MethodPut, "/api/v1/links/nonexistent-link", strings.NewReader(updateJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("nonexistent-link")

	err := handler.UpdateLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

func TestUpdateLinkInvalidJSON(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test link
	link := models.Link{
		ID:       "link-999",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "depends_on",
	}
	db.Create(&link)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPut, "/api/v1/links/link-999", strings.NewReader("{invalid}"))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("link-999")

	err := handler.UpdateLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestDeleteLink(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewLinkHandler(db)

	// Create test link
	link := models.Link{
		ID:       "link-123",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "depends_on",
	}
	db.Create(&link)

	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/links/link-123", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("link-123")

	err := handler.DeleteLink(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify the deletion
	var count int64
	db.Model(&models.Link{}).Where("id = ?", "link-123").Count(&count)
	assert.Equal(t, int64(0), count)
}
