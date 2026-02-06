package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// Test constants
const (
	testProjectID = "test-project"
)

func dropCodeIndexTables(t *testing.T, db *gorm.DB) {
	t.Helper()
	require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{}, &models.CodeEntityRelationship{}))
}

func setupCodeIndexHandlerTest(t *testing.T) (*CodeIndexHandler, *gorm.DB) {
	// Setup database
	db := setupTestDB(t)

	// Auto migrate the models
	if err := db.AutoMigrate(
		&models.CodeEntity{},
		&models.CodeEntityRelationship{},
	); err != nil {
		t.Fatalf("Failed to migrate models: %v", err)
	}

	// CodeIndexHandler now requires CodeIndexService
	// For now, pass nil service - tests will need proper mocks
	handler := &CodeIndexHandler{
		service: nil,
		binder:  &EchoBinder{},
	}

	return handler, db
}

func setupTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	return db
}

func TestIndexCode_Success(t *testing.T) {
	runIndexCodeSuccess(t)
}

func TestIndexCode_InvalidProjectID(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	e := echo.New()
	req := IndexCodeRequest{
		ProjectID: "invalid-uuid",
		FilePath:  "test.go",
		Language:  "go",
	}

	reqBody, _ := json.Marshal(req)
	httpReq := httptest.NewRequest(http.MethodPost, "/api/v1/code/index", bytes.NewReader(reqBody))
	httpReq.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err := handler.IndexCode(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestListEntities_Success(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	projectID := testProjectID

	// Create test entity
	entity := &models.CodeEntity{
		ProjectID:   projectID,
		EntityType:  "function",
		Name:        "test",
		FullName:    "test.test",
		FilePath:    "test.go",
		Language:    "go",
		LineNumber:  1,
		CodeSnippet: "func test() {}",
		IndexedAt:   time.Now(),
	}
	err := db.Create(entity).Error
	require.NoError(t, err)

	e := echo.New()
	httpReq := httptest.NewRequest(http.MethodGet, "/api/v1/code/entities?project_id="+projectID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err = handler.ListEntities(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var response map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &response)
	assert.Equal(t, float64(1), response["count"])
}

func TestListEntities_MissingProjectID(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	e := echo.New()
	httpReq := httptest.NewRequest(http.MethodGet, "/api/v1/code/entities", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err := handler.ListEntities(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestGetEntity_Success(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	entity := &models.CodeEntity{
		ProjectID:   testProjectID,
		EntityType:  "function",
		Name:        "test",
		FullName:    "test.test",
		FilePath:    "test.go",
		Language:    "go",
		LineNumber:  1,
		CodeSnippet: "func test() {}",
		IndexedAt:   time.Now(),
	}
	err := db.Create(entity).Error
	require.NoError(t, err)

	e := echo.New()
	httpReq := httptest.NewRequest(http.MethodGet, "/api/v1/code/entities/"+entity.ID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)
	c.SetParamNames("id")
	c.SetParamValues(entity.ID)

	err = handler.GetEntity(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var response map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &response)
	assert.NotNil(t, response["entity"])
	assert.NotNil(t, response["relationships"])
}

func TestGetEntity_NotFound(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	e := echo.New()
	httpReq := httptest.NewRequest(http.MethodGet, "/api/v1/code/entities/nonexistent-id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)
	c.SetParamNames("id")
	c.SetParamValues("nonexistent-id")

	err := handler.GetEntity(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func TestUpdateEntity_Success(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	entity := &models.CodeEntity{
		ProjectID:   testProjectID,
		EntityType:  "function",
		Name:        "test",
		FullName:    "test.test",
		FilePath:    "test.go",
		Language:    "go",
		LineNumber:  1,
		CodeSnippet: "func test() {}",
		IndexedAt:   time.Now(),
	}
	err := db.Create(entity).Error
	require.NoError(t, err)

	updateReq := struct {
		Description string `json:"description"`
	}{
		Description: "Updated description",
	}

	e := echo.New()
	reqBody, _ := json.Marshal(updateReq)
	httpReq := httptest.NewRequest(http.MethodPut, "/api/v1/code/entities/"+entity.ID, bytes.NewReader(reqBody))
	httpReq.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)
	c.SetParamNames("id")
	c.SetParamValues(entity.ID)

	err = handler.UpdateEntity(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
}

func TestDeleteEntity_Success(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	entity := &models.CodeEntity{
		ProjectID:   testProjectID,
		EntityType:  "function",
		Name:        "test",
		FullName:    "test.test",
		FilePath:    "test.go",
		Language:    "go",
		LineNumber:  1,
		CodeSnippet: "func test() {}",
		IndexedAt:   time.Now(),
	}
	err := db.Create(entity).Error
	require.NoError(t, err)

	e := echo.New()
	httpReq := httptest.NewRequest(http.MethodDelete, "/api/v1/code/entities/"+entity.ID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)
	c.SetParamNames("id")
	c.SetParamValues(entity.ID)

	err = handler.DeleteEntity(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify soft delete
	var deletedEntity models.CodeEntity
	result := db.WithContext(c.Request().Context()).Where("id = ? AND deleted_at IS NOT NULL", entity.ID).First(&deletedEntity)
	assert.NoError(t, result.Error)
}

func TestSearchEntities_Success(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	projectID := testProjectID

	// Create test entities
	entities := []*models.CodeEntity{
		{
			ProjectID:   projectID,
			EntityType:  "function",
			Name:        "getUserByID",
			FullName:    "pkg.getUserByID",
			FilePath:    "user.go",
			Language:    "go",
			LineNumber:  1,
			CodeSnippet: "func getUserByID() {}",
			IndexedAt:   time.Now(),
		},
		{
			ProjectID:   projectID,
			EntityType:  "function",
			Name:        "getUser",
			FullName:    "pkg.getUser",
			FilePath:    "user.go",
			Language:    "go",
			LineNumber:  10,
			CodeSnippet: "func getUser() {}",
			IndexedAt:   time.Now(),
		},
	}

	for _, e := range entities {
		err := db.Create(e).Error
		require.NoError(t, err)
	}

	e := echo.New()
	httpReq := httptest.NewRequest(http.MethodGet, "/api/v1/code/search?project_id="+projectID+"&q=getUser", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err := handler.SearchEntities(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var response map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &response)
	assert.Greater(t, response["count"], float64(0))
}

func TestSearchEntities_MissingQuery(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	e := echo.New()
	httpReq := httptest.NewRequest(http.MethodGet, "/api/v1/code/search?project_id=test-project", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err := handler.SearchEntities(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestGetStats_Success(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	projectID := testProjectID

	// Create test entities
	entities := []*models.CodeEntity{
		{
			ProjectID:   projectID,
			EntityType:  "function",
			Name:        "func1",
			FullName:    "pkg.func1",
			FilePath:    "test.go",
			Language:    "go",
			LineNumber:  1,
			CodeSnippet: "func func1() {}",
			IndexedAt:   time.Now(),
		},
		{
			ProjectID:   projectID,
			EntityType:  "class",
			Name:        "MyClass",
			FullName:    "pkg.MyClass",
			FilePath:    "test.go",
			Language:    "go",
			LineNumber:  10,
			CodeSnippet: "type MyClass struct {}",
			IndexedAt:   time.Now(),
		},
	}

	for _, entity := range entities {
		err := db.Create(entity).Error
		require.NoError(t, err)
	}

	e := echo.New()
	httpReq := httptest.NewRequest(http.MethodGet, "/api/v1/code/stats?project_id="+projectID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err := handler.GetStats(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var stats models.CodeIndexStats
	_ = json.Unmarshal(rec.Body.Bytes(), &stats)
	assert.Equal(t, int64(2), stats.TotalEntities)
	assert.Equal(t, int64(1), stats.EntitiesByType["function"])
	assert.Equal(t, int64(1), stats.EntitiesByType["class"])
}

func TestReindex_Success(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	projectID := testProjectID

	// Create test entity
	entity := &models.CodeEntity{
		ProjectID:   projectID,
		EntityType:  "function",
		Name:        "test",
		FullName:    "test.test",
		FilePath:    "test.go",
		Language:    "go",
		LineNumber:  1,
		CodeSnippet: "func test() {}",
		IndexedAt:   time.Now(),
	}
	err := db.Create(entity).Error
	require.NoError(t, err)

	// Verify entity exists
	var count int64
	db.Model(&models.CodeEntity{}).Where("project_id = ? AND deleted_at IS NULL", projectID).Count(&count)
	assert.Equal(t, int64(1), count)

	e := echo.New()
	reindexReq := struct {
		ProjectID string `json:"project_id"`
	}{
		ProjectID: projectID,
	}

	reqBody, _ := json.Marshal(reindexReq)
	httpReq := httptest.NewRequest(http.MethodPost, "/api/v1/code/reindex", bytes.NewReader(reqBody))
	httpReq.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err = handler.Reindex(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify entities are soft-deleted
	db.Model(&models.CodeEntity{}).Where("project_id = ? AND deleted_at IS NULL", projectID).Count(&count)
	assert.Equal(t, int64(0), count)
}

func TestBatchIndexCode_Success(t *testing.T) {
	runBatchIndexCodeSuccess(t)
}

func runIndexCodeSuccess(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	e := echo.New()
	req := buildIndexCodeSuccessRequest()

	reqBody, _ := json.Marshal(req)
	httpReq := httptest.NewRequest(http.MethodPost, "/api/v1/code/index", bytes.NewReader(reqBody))
	httpReq.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err := handler.IndexCode(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var response map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &response)
	assert.Equal(t, float64(2), response["entity_count"])
}

func runBatchIndexCodeSuccess(t *testing.T) {
	handler, db := setupCodeIndexHandlerTest(t)
	defer dropCodeIndexTables(t, db)

	batchReq := buildBatchIndexCodeSuccessRequest()

	e := echo.New()
	reqBody, _ := json.Marshal(batchReq)
	httpReq := httptest.NewRequest(http.MethodPost, "/api/v1/code/batch-index", bytes.NewReader(reqBody))
	httpReq.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err := handler.BatchIndexCode(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var response map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &response)
	assert.Equal(t, float64(2), response["entity_count"])
	assert.Equal(t, float64(2), response["batch_count"])
}

func buildIndexCodeSuccessRequest() IndexCodeRequest {
	return IndexCodeRequest{
		ProjectID: testProjectID,
		FilePath:  "pkg/main.go",
		Language:  "go",
		Entities: []CodeEntityInput{
			{
				EntityType:    "function",
				Name:          "main",
				FullName:      "main.main",
				Description:   "Entry point",
				LineNumber:    1,
				EndLineNumber: 10,
				ColumnNumber:  1,
				CodeSnippet:   "func main() {",
				Signature:     "func()",
				ReturnType:    "void",
				Parameters:    json.RawMessage("[]"),
				Metadata:      json.RawMessage("{}"),
			},
			{
				EntityType:    "function",
				Name:          "helper",
				FullName:      "main.helper",
				Description:   "Helper function",
				LineNumber:    12,
				EndLineNumber: 20,
				ColumnNumber:  1,
				CodeSnippet:   "func helper() {",
				Signature:     "func()",
				ReturnType:    "void",
				Parameters:    json.RawMessage("[]"),
				Metadata:      json.RawMessage("{}"),
			},
		},
		Relationships: []CodeRelationshipInput{
			{
				SourceEntityName: "main.main",
				TargetEntityName: "main.helper",
				RelationType:     "calls",
				Metadata:         json.RawMessage("{}"),
			},
		},
	}
}

func buildBatchIndexCodeSuccessRequest() struct {
	ProjectID string             `json:"project_id"`
	Batches   []IndexCodeRequest `json:"batches"`
} {
	return struct {
		ProjectID string             `json:"project_id"`
		Batches   []IndexCodeRequest `json:"batches"`
	}{
		ProjectID: testProjectID,
		Batches: []IndexCodeRequest{
			{
				ProjectID: testProjectID,
				FilePath:  "file1.go",
				Language:  "go",
				Entities: []CodeEntityInput{
					{
						EntityType:    "function",
						Name:          "func1",
						FullName:      "pkg.func1",
						LineNumber:    1,
						EndLineNumber: 5,
						ColumnNumber:  1,
						CodeSnippet:   "func func1() {}",
						Parameters:    json.RawMessage("[]"),
						Metadata:      json.RawMessage("{}"),
					},
				},
			},
			{
				ProjectID: testProjectID,
				FilePath:  "file2.go",
				Language:  "go",
				Entities: []CodeEntityInput{
					{
						EntityType:    "function",
						Name:          "func2",
						FullName:      "pkg.func2",
						LineNumber:    1,
						EndLineNumber: 5,
						ColumnNumber:  1,
						CodeSnippet:   "func func2() {}",
						Parameters:    json.RawMessage("[]"),
						Metadata:      json.RawMessage("{}"),
					},
				},
			},
		},
	}
}
