package equivalence

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type equivalenceHandlerTestEnv struct {
	e            *echo.Echo
	handler      *Handler
	repo         *MockRepository
	projectID    uuid.UUID
	sourceItemID uuid.UUID
	userID       uuid.UUID
}

func newEquivalenceHandlerTestEnv() *equivalenceHandlerTestEnv {
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	api := e.Group("/api/v1")
	handler.RegisterRoutes(api)

	return &equivalenceHandlerTestEnv{
		e:            e,
		handler:      handler,
		repo:         mockRepo,
		projectID:    uuid.New(),
		sourceItemID: uuid.New(),
		userID:       uuid.New(),
	}
}

// TestEquivalenceHandlerEndpoints tests various equivalence handler endpoints
func TestEquivalenceHandlerEndpoints(t *testing.T) {
	env := newEquivalenceHandlerTestEnv()
	runListEquivalencesEndpointTests(t, env)
	runDetectEquivalencesEndpointTests(t, env)
	runListProjectConceptsEndpointTests(t, env)
}

func runListEquivalencesEndpointTests(t *testing.T, env *equivalenceHandlerTestEnv) {
	t.Run("list equivalences - missing project_id", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/equivalences", nil)
		rec := httptest.NewRecorder()
		c := env.e.NewContext(req, rec)

		err := env.handler.ListEquivalences(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("list equivalences - valid request", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/equivalences?project_id="+env.projectID.String(), nil)
		rec := httptest.NewRecorder()
		c := env.e.NewContext(req, rec)

		err := env.handler.ListEquivalences(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp ListEquivalencesResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.Equal(t, int64(0), resp.Total)
		assert.False(t, resp.HasMore)
	})
}

func runDetectEquivalencesEndpointTests(t *testing.T, env *equivalenceHandlerTestEnv) {
	t.Run("detect equivalences - invalid body", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/detect", bytes.NewReader([]byte("invalid")))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()
		c := env.e.NewContext(req, rec)

		err := env.handler.DetectEquivalences(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("detect equivalences - valid request", func(t *testing.T) {
		body := DetectionRequest{
			ProjectID:     env.projectID,
			SourceItemID:  env.sourceItemID,
			MinConfidence: 0.5,
			MaxResults:    10,
		}
		bodyBytes, err := json.Marshal(body)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/detect", bytes.NewReader(bodyBytes))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()
		c := env.e.NewContext(req, rec)

		err = env.handler.DetectEquivalences(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp []Suggestion
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.NotNil(t, resp)
	})
}

func runListProjectConceptsEndpointTests(t *testing.T, env *equivalenceHandlerTestEnv) {
	t.Run("list project concepts - invalid project ID", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/invalid/concepts", nil)
		rec := httptest.NewRecorder()
		c := env.e.NewContext(req, rec)
		c.SetParamNames("projectId")
		c.SetParamValues("invalid")

		err := env.handler.ListProjectConcepts(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("list project concepts - valid project ID", func(t *testing.T) {
		path := "/api/v1/projects/" + env.projectID.String() + "/concepts"
		req := httptest.NewRequest(http.MethodGet, path, nil)
		rec := httptest.NewRecorder()
		c := env.e.NewContext(req, rec)
		c.SetParamNames("projectId")
		c.SetParamValues(env.projectID.String())

		err := env.handler.ListProjectConcepts(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp []CanonicalConcept
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.Equal(t, 0, len(resp))
	})
}

// TestCreateProjectConcept tests the POST /projects/:projectId/concepts endpoint
func TestCreateProjectConcept(t *testing.T) {
	env := newEquivalenceHandlerTestEnv()
	runCreateProjectConceptCases(t, env)
}

func runCreateProjectConceptCases(t *testing.T, env *equivalenceHandlerTestEnv) {
	runCreateProjectConceptInvalidProjectID(t, env)
	runCreateProjectConceptMissingName(t, env)
	runCreateProjectConceptUnauthorized(t, env)
	runCreateProjectConceptAuthorized(t, env)
}

func runCreateProjectConceptInvalidProjectID(t *testing.T, env *equivalenceHandlerTestEnv) {
	t.Run("invalid project ID", func(t *testing.T) {
		body := CreateCanonicalConceptRequest{
			ProjectID:   env.projectID,
			Name:        "Test Concept",
			Description: "A test concept",
		}
		c, rec := makeProjectConceptContext(t, env, "invalid", body)

		err := env.handler.CreateProjectConcept(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func runCreateProjectConceptMissingName(t *testing.T, env *equivalenceHandlerTestEnv) {
	t.Run("missing name", func(t *testing.T) {
		body := CreateCanonicalConceptRequest{
			ProjectID: env.projectID,
			Name:      "",
		}
		c, rec := makeProjectConceptContext(t, env, env.projectID.String(), body)

		err := env.handler.CreateProjectConcept(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func runCreateProjectConceptUnauthorized(t *testing.T, env *equivalenceHandlerTestEnv) {
	t.Run("valid request without user authentication", func(t *testing.T) {
		body := CreateCanonicalConceptRequest{
			ProjectID:   env.projectID,
			Name:        "Test Concept",
			Description: "A test concept",
			Domain:      "system",
			Category:    "entity",
		}
		c, rec := makeProjectConceptContext(t, env, env.projectID.String(), body)

		err := env.handler.CreateProjectConcept(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})
}

func runCreateProjectConceptAuthorized(t *testing.T, env *equivalenceHandlerTestEnv) {
	t.Run("valid request with user authentication", func(t *testing.T) {
		body := CreateCanonicalConceptRequest{
			ProjectID:   env.projectID,
			Name:        "Test Concept",
			Description: "A test concept",
			Domain:      "system",
			Category:    "entity",
		}
		c, rec := makeProjectConceptContext(t, env, env.projectID.String(), body)
		c.Set("user_id", env.userID)

		err := env.handler.CreateProjectConcept(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusCreated, rec.Code)

		var resp CreateCanonicalConceptResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.Equal(t, "Test Concept", resp.Concept.Name)
		assert.Equal(t, env.projectID, resp.Concept.ProjectID)
		assert.NotZero(t, resp.CreatedAt)
	})
}

func makeProjectConceptContext(
	t *testing.T,
	env *equivalenceHandlerTestEnv,
	projectID string,
	body CreateCanonicalConceptRequest,
) (echo.Context, *httptest.ResponseRecorder) {
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	req := httptest.NewRequest(
		http.MethodPost,
		"/api/v1/projects/"+projectID+"/concepts",
		bytes.NewReader(bodyBytes),
	)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := env.e.NewContext(req, rec)
	c.SetParamNames("projectId")
	c.SetParamValues(projectID)

	return c, rec
}

// TestProjectScopedConceptEndpointsBackwardCompatibility tests that both
// the old /equivalences/concepts and new /projects/:projectId/concepts endpoints work together
func TestProjectScopedConceptEndpointsBackwardCompatibility(t *testing.T) {
	env := newEquivalenceHandlerTestEnv()
	createdConceptID := createBackwardCompatibleConcept(t, env)
	oldList := listConceptsOldEndpoint(t, env)
	newList := listConceptsProjectEndpoint(t, env)

	assert.Greater(t, len(oldList), 0)
	assert.Equal(t, createdConceptID, oldList[0].ID)
	assert.Equal(t, len(oldList), len(newList))
	assert.Equal(t, newList[0].ID, createdConceptID)
}

func createBackwardCompatibleConcept(t *testing.T, env *equivalenceHandlerTestEnv) uuid.UUID {
	conceptReq := CreateCanonicalConceptRequest{
		ProjectID:   env.projectID,
		Name:        "Backward Compatible Concept",
		Description: "Created via project-scoped endpoint",
		Domain:      "system",
		Category:    "entity",
	}
	body, err := json.Marshal(conceptReq)
	require.NoError(t, err)

	req := httptest.NewRequest(
		http.MethodPost,
		"/api/v1/projects/"+env.projectID.String()+"/concepts",
		bytes.NewReader(body),
	)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := env.e.NewContext(req, rec)
	c.SetParamNames("projectId")
	c.SetParamValues(env.projectID.String())
	c.Set("user_id", env.userID)

	err = env.handler.CreateProjectConcept(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var createResp CreateCanonicalConceptResponse
	err = json.Unmarshal(rec.Body.Bytes(), &createResp)
	require.NoError(t, err)
	return createResp.Concept.ID
}

func listConceptsOldEndpoint(t *testing.T, env *equivalenceHandlerTestEnv) []CanonicalConcept {
	req := httptest.NewRequest(
		http.MethodGet,
		"/api/v1/equivalences/concepts?project_id="+env.projectID.String(),
		nil,
	)
	rec := httptest.NewRecorder()
	c := env.e.NewContext(req, rec)

	err := env.handler.GetCanonicalConcepts(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp []CanonicalConcept
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	return resp
}

func listConceptsProjectEndpoint(t *testing.T, env *equivalenceHandlerTestEnv) []CanonicalConcept {
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+env.projectID.String()+"/concepts", nil)
	rec := httptest.NewRecorder()
	c := env.e.NewContext(req, rec)
	c.SetParamNames("projectId")
	c.SetParamValues(env.projectID.String())

	err := env.handler.ListProjectConcepts(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp []CanonicalConcept
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	return resp
}

// TestGetSuggestions tests the GET /equivalences/suggestions endpoint
func TestGetSuggestions(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	projectID := uuid.New()

	// Test case: invalid project_id
	req := httptest.NewRequest(http.MethodGet, "/api/v1/equivalences/suggestions?project_id=invalid", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.GetSuggestions(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid request
	req = httptest.NewRequest(http.MethodGet, "/api/v1/equivalences/suggestions?project_id="+projectID.String(), nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)

	err = handler.GetSuggestions(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
}

// TestConfirmSuggestion tests the POST /equivalences/suggestions/:id/confirm endpoint
func TestConfirmSuggestion(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	suggestionID := uuid.New()
	userID := uuid.New()

	// Create a mock suggestion
	mockSuggestion := &Suggestion{
		ID:            suggestionID,
		ProjectID:     uuid.New(),
		SourceItemID:  uuid.New(),
		TargetItemID:  uuid.New(),
		Confidence:    0.8,
		SuggestedType: "same_as",
		CreatedAt:     time.Now(),
	}
	require.NoError(t, mockRepo.SaveSuggestion(context.TODO(), mockSuggestion))

	// Test case: invalid suggestion id
	req := httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/suggestions/invalid/confirm", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid")

	err := handler.ConfirmSuggestion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid confirmation
	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/suggestions/"+suggestionID.String()+"/confirm",
		bytes.NewReader([]byte(`{}`)))
	req.Header.Set("Content-Type", "application/json")
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(suggestionID.String())
	c.Set("user_id", userID)

	err = handler.ConfirmSuggestion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp Link
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.NotEqual(t, uuid.Nil, resp.ID)
	assert.Equal(t, StatusConfirmed, resp.Status)
}

// TestRejectSuggestion tests the POST /equivalences/suggestions/:id/reject endpoint
func TestRejectSuggestion(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	suggestionID := uuid.New()

	// Test case: invalid suggestion id
	req := httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/suggestions/invalid/reject", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid")

	err := handler.RejectSuggestion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid rejection
	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/suggestions/"+suggestionID.String()+"/reject", nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(suggestionID.String())

	err = handler.RejectSuggestion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNoContent, rec.Code)
}

// TestBulkConfirmEquivalences tests the POST /equivalences/bulk-confirm endpoint
func TestBulkConfirmEquivalences(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	userID := uuid.New()
	suggestionID := uuid.New()

	// Create a mock suggestion
	mockSuggestion := &Suggestion{
		ID:            suggestionID,
		ProjectID:     uuid.New(),
		SourceItemID:  uuid.New(),
		TargetItemID:  uuid.New(),
		Confidence:    0.8,
		SuggestedType: "same_as",
		CreatedAt:     time.Now(),
	}
	require.NoError(t, mockRepo.SaveSuggestion(context.TODO(), mockSuggestion))

	// Test case: empty equivalence_ids
	req := httptest.NewRequest(
		http.MethodPost,
		"/api/v1/equivalences/bulk-confirm",
		bytes.NewReader([]byte(`{"equivalence_ids":[]}`)),
	)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.BulkConfirmEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid bulk confirmation
	bulkReq := BulkConfirmRequest{
		EquivalenceIDs: []uuid.UUID{suggestionID},
	}
	body, err := json.Marshal(bulkReq)
	require.NoError(t, err)

	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/bulk-confirm", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.Set("user_id", userID)

	err = handler.BulkConfirmEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp BulkConfirmResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Greater(t, resp.Confirmed, 0)
}

// TestBulkRejectEquivalences tests the POST /equivalences/bulk-reject endpoint
func TestBulkRejectEquivalences(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	userID := uuid.New()
	suggestionID := uuid.New()

	// Test case: empty equivalence_ids
	req := httptest.NewRequest(
		http.MethodPost,
		"/api/v1/equivalences/bulk-reject",
		bytes.NewReader([]byte(`{"equivalence_ids":[]}`)),
	)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.BulkRejectEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid bulk rejection
	bulkReq := BulkRejectRequest{
		EquivalenceIDs: []uuid.UUID{suggestionID},
	}
	body, err := json.Marshal(bulkReq)
	require.NoError(t, err)

	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/bulk-reject", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.Set("user_id", userID)

	err = handler.BulkRejectEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp BulkRejectResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
}

// TestCreateCanonicalConcept tests the POST /equivalences/concepts endpoint
func TestCreateCanonicalConcept(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	projectID := uuid.New()
	userID := uuid.New()

	// Test case: missing name
	req := httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/concepts",
		bytes.NewReader([]byte(`{"project_id":"`+projectID.String()+`"}`)))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.CreateCanonicalConcept(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid creation
	conceptReq := CreateCanonicalConceptRequest{
		ProjectID:   projectID,
		Name:        "Test Concept",
		Description: "A test canonical concept",
	}
	body, err := json.Marshal(conceptReq)
	require.NoError(t, err)

	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/concepts", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.Set("user_id", userID)

	err = handler.CreateCanonicalConcept(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var resp CreateCanonicalConceptResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.NotEqual(t, uuid.Nil, resp.Concept.ID)
	assert.Equal(t, "Test Concept", resp.Concept.Name)
}

// TestGetCanonicalConcepts tests the GET /equivalences/concepts endpoint
func TestGetCanonicalConcepts(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	projectID := uuid.New()

	// Test case: invalid project_id
	req := httptest.NewRequest(http.MethodGet, "/api/v1/equivalences/concepts?project_id=invalid", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.GetCanonicalConcepts(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid request
	req = httptest.NewRequest(http.MethodGet, "/api/v1/equivalences/concepts?project_id="+projectID.String(), nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)

	err = handler.GetCanonicalConcepts(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
}

// TestGetConceptProjections tests the GET /equivalences/concepts/:id/projections endpoint
func TestGetConceptProjections(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	conceptID := uuid.New()

	// Test case: invalid concept id
	req := httptest.NewRequest(http.MethodGet, "/api/v1/equivalences/concepts/invalid/projections", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid")

	err := handler.GetConceptProjections(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid request with concept
	concept := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: uuid.New(),
		Name:      "Test Concept",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		Version:   1,
	}
	require.NoError(t, mockRepo.SaveConcept(context.Background(), concept))

	req = httptest.NewRequest(http.MethodGet, "/api/v1/equivalences/concepts/"+conceptID.String()+"/projections", nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(conceptID.String())

	err = handler.GetConceptProjections(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp GetProjectionsResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Equal(t, conceptID, resp.ConceptID)
}

// TestListProjectEquivalences tests the GET /projects/:projectId/equivalences endpoint
func TestListProjectEquivalences(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	projectID := uuid.New()

	// Test case: invalid project id
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/invalid/equivalences", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("projectId")
	c.SetParamValues("invalid")

	err := handler.ListProjectEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid request
	req = httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+projectID.String()+"/equivalences", nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("projectId")
	c.SetParamValues(projectID.String())

	err = handler.ListProjectEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp ListEquivalencesResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Equal(t, int64(0), resp.Total)
}

// TestDetectProjectEquivalences tests the POST /projects/:projectId/equivalences/detect endpoint
func TestDetectProjectEquivalences(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	projectID := uuid.New()
	sourceItemID := uuid.New()

	// Test case: invalid project id
	req := httptest.NewRequest(http.MethodPost, "/api/v1/projects/invalid/equivalences/detect", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("projectId")
	c.SetParamValues("invalid")

	err := handler.DetectProjectEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid detection
	detectionReq := DetectionRequest{
		ProjectID:     projectID,
		SourceItemID:  sourceItemID,
		MinConfidence: 0.5,
		MaxResults:    10,
	}
	body, err := json.Marshal(detectionReq)
	require.NoError(t, err)

	req = httptest.NewRequest(http.MethodPost, "/api/v1/projects/"+projectID.String()+"/equivalences/detect",
		bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("projectId")
	c.SetParamValues(projectID.String())

	err = handler.DetectProjectEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp interface{}
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
}

// TestCreateCanonicalProjection tests the POST /equivalences/concepts/:id/projections endpoint
func TestCreateCanonicalProjection(t *testing.T) {
	env := newEquivalenceHandlerTestEnv()
	conceptID := uuid.New()
	itemID := uuid.New()

	seedCanonicalConcept(t, env, conceptID)
	runCreateCanonicalProjectionCases(t, env, conceptID, itemID)
}

func seedCanonicalConcept(t *testing.T, env *equivalenceHandlerTestEnv, conceptID uuid.UUID) {
	concept := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: env.projectID,
		Name:      "Test Concept",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, env.repo.SaveConcept(context.Background(), concept))
}

func runCreateCanonicalProjectionCases(t *testing.T, env *equivalenceHandlerTestEnv, conceptID, itemID uuid.UUID) {
	t.Run("invalid concept ID", func(t *testing.T) {
		reqBody := CreateCanonicalProjectionRequest{
			ItemID:      itemID,
			Perspective: "code",
			Confidence:  0.9,
		}
		c, rec := makeProjectionContext(t, env, "invalid", reqBody)

		err := env.handler.CreateCanonicalProjection(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("missing item_id", func(t *testing.T) {
		reqBody := CreateCanonicalProjectionRequest{
			ItemID: uuid.Nil,
		}
		c, rec := makeProjectionContext(t, env, conceptID.String(), reqBody)

		err := env.handler.CreateCanonicalProjection(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("unauthorized (no user context)", func(t *testing.T) {
		reqBody := CreateCanonicalProjectionRequest{
			ItemID:      itemID,
			Perspective: "code",
			Confidence:  0.9,
		}
		c, rec := makeProjectionContext(t, env, conceptID.String(), reqBody)

		err := env.handler.CreateCanonicalProjection(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})

	t.Run("successful creation with user context", func(t *testing.T) {
		reqBody := CreateCanonicalProjectionRequest{
			ItemID:      itemID,
			Perspective: "code",
			Confidence:  0.9,
		}
		c, rec := makeProjectionContext(t, env, conceptID.String(), reqBody)
		c.Set("user_id", env.userID)

		err := env.handler.CreateCanonicalProjection(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusCreated, rec.Code)

		var resp CreateCanonicalProjectionResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.Equal(t, itemID, resp.Projection.ItemID)
		assert.Equal(t, conceptID, resp.Projection.CanonicalID)
		assert.Equal(t, "code", resp.Projection.Perspective)
		assert.Equal(t, 0.9, resp.Projection.Confidence)
		assert.NotEmpty(t, resp.Message)
		assert.False(t, resp.CreatedAt.IsZero())
	})
}

func makeProjectionContext(
	t *testing.T,
	env *equivalenceHandlerTestEnv,
	conceptID string,
	body CreateCanonicalProjectionRequest,
) (echo.Context, *httptest.ResponseRecorder) {
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	req := httptest.NewRequest(
		http.MethodPost,
		"/api/v1/equivalences/concepts/"+conceptID+"/projections",
		bytes.NewReader(bodyBytes),
	)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := env.e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(conceptID)

	return c, rec
}

func seedCanonicalProjection(t *testing.T, env *equivalenceHandlerTestEnv, projectionID, conceptID, itemID uuid.UUID) {
	projection := &CanonicalProjection{
		ID:          projectionID,
		ProjectID:   env.projectID,
		CanonicalID: conceptID,
		ItemID:      itemID,
		Perspective: "code",
		Confidence:  0.9,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	require.NoError(t, env.repo.SaveProjection(context.Background(), projection))
}

func runDeleteCanonicalProjectionCases(
	t *testing.T,
	env *equivalenceHandlerTestEnv,
	conceptID uuid.UUID,
	projectionID uuid.UUID,
) {
	t.Run("invalid concept ID", func(t *testing.T) {
		c, rec := makeDeleteProjectionContext(env, "invalid", projectionID.String())
		err := env.handler.DeleteCanonicalProjection(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("invalid projection ID", func(t *testing.T) {
		c, rec := makeDeleteProjectionContext(env, conceptID.String(), "invalid")
		err := env.handler.DeleteCanonicalProjection(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("projection not found", func(t *testing.T) {
		notFoundProjectionID := uuid.New()
		c, rec := makeDeleteProjectionContext(
			env,
			conceptID.String(),
			notFoundProjectionID.String(),
		)
		err := env.handler.DeleteCanonicalProjection(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusNotFound, rec.Code)
	})

	t.Run("successful deletion", func(t *testing.T) {
		c, rec := makeDeleteProjectionContext(env, conceptID.String(), projectionID.String())
		err := env.handler.DeleteCanonicalProjection(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusNoContent, rec.Code)

		deletedProjection, err := env.repo.GetProjection(context.Background(), projectionID)
		assert.Error(t, err)
		assert.Nil(t, deletedProjection)
	})
}

func makeDeleteProjectionContext(
	env *equivalenceHandlerTestEnv,
	conceptID string,
	projectionID string,
) (echo.Context, *httptest.ResponseRecorder) {
	req := httptest.NewRequest(
		http.MethodDelete,
		"/api/v1/equivalences/concepts/"+conceptID+"/projections/"+projectionID,
		nil,
	)
	rec := httptest.NewRecorder()
	c := env.e.NewContext(req, rec)
	c.SetParamNames("conceptId", "projectionId")
	c.SetParamValues(conceptID, projectionID)
	return c, rec
}

func seedCanonicalConceptWithDetails(
	t *testing.T,
	env *equivalenceHandlerTestEnv,
	conceptID uuid.UUID,
	name string,
	domain string,
) {
	concept := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: env.projectID,
		Name:      name,
		Domain:    domain,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, env.repo.SaveConcept(context.Background(), concept))
}

func createCanonicalProjectionForConcept(
	t *testing.T,
	env *equivalenceHandlerTestEnv,
	conceptID uuid.UUID,
	itemID uuid.UUID,
	perspective string,
	role string,
	confidence float64,
	source StrategyType,
) uuid.UUID {
	reqBody := CreateCanonicalProjectionRequest{
		ItemID:      itemID,
		Perspective: perspective,
		Role:        role,
		Confidence:  confidence,
		Source:      source,
	}
	bodyBytes, err := json.Marshal(reqBody)
	require.NoError(t, err)

	req := httptest.NewRequest(
		http.MethodPost,
		"/api/v1/equivalences/concepts/"+conceptID.String()+"/projections",
		bytes.NewReader(bodyBytes),
	)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := env.e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(conceptID.String())
	c.Set("user_id", env.userID)

	err = env.handler.CreateCanonicalProjection(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var resp CreateCanonicalProjectionResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Equal(t, itemID, resp.Projection.ItemID)

	return resp.Projection.ID
}

func deleteCanonicalProjectionForConcept(
	t *testing.T,
	env *equivalenceHandlerTestEnv,
	conceptID uuid.UUID,
	projectionID uuid.UUID,
) {
	req := httptest.NewRequest(
		http.MethodDelete,
		"/api/v1/equivalences/concepts/"+conceptID.String()+"/projections/"+projectionID.String(),
		nil,
	)
	rec := httptest.NewRecorder()
	c := env.e.NewContext(req, rec)
	c.SetParamNames("conceptId", "projectionId")
	c.SetParamValues(conceptID.String(), projectionID.String())

	err := env.handler.DeleteCanonicalProjection(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNoContent, rec.Code)
}

func assertProjectionCount(t *testing.T, env *equivalenceHandlerTestEnv, conceptID uuid.UUID, expected int) {
	projections, err := env.repo.GetProjectionsByConcept(context.Background(), conceptID)
	require.NoError(t, err)
	assert.Equal(t, expected, len(projections))
}

func assertProjectionRemaining(t *testing.T, env *equivalenceHandlerTestEnv, conceptID, projectionID uuid.UUID) {
	projections, err := env.repo.GetProjectionsByConcept(context.Background(), conceptID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(projections))
	assert.Equal(t, projectionID, projections[0].ID)
}

// TestDeleteCanonicalProjection tests the DELETE /equivalences/concepts/:conceptId/projections/:projectionId endpoint
func TestDeleteCanonicalProjection(t *testing.T) {
	env := newEquivalenceHandlerTestEnv()
	conceptID := uuid.New()
	itemID := uuid.New()
	projectionID := uuid.New()

	seedCanonicalConcept(t, env, conceptID)
	seedCanonicalProjection(t, env, projectionID, conceptID, itemID)
	runDeleteCanonicalProjectionCases(t, env, conceptID, projectionID)
}

// TestDeleteCanonicalProjection_WrongConcept tests deletion with mismatched concept ID
func TestDeleteCanonicalProjection_WrongConcept(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	projectID := uuid.New()
	conceptID1 := uuid.New()
	conceptID2 := uuid.New()
	itemID := uuid.New()
	projectionID := uuid.New()

	// Create two canonical concepts
	concept1 := &CanonicalConcept{
		ID:        conceptID1,
		ProjectID: projectID,
		Name:      "Test Concept 1",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, mockRepo.SaveConcept(context.Background(), concept1))

	concept2 := &CanonicalConcept{
		ID:        conceptID2,
		ProjectID: projectID,
		Name:      "Test Concept 2",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, mockRepo.SaveConcept(context.Background(), concept2))

	// Create a projection for concept 1
	projection := &CanonicalProjection{
		ID:          projectionID,
		ProjectID:   projectID,
		CanonicalID: conceptID1,
		ItemID:      itemID,
		Perspective: "code",
		Confidence:  0.9,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	require.NoError(t, mockRepo.SaveProjection(context.Background(), projection))

	// Register routes
	api := e.Group("/api/v1")
	handler.RegisterRoutes(api)

	// Try to delete projection from wrong concept
	req := httptest.NewRequest(
		http.MethodDelete,
		"/api/v1/equivalences/concepts/"+conceptID2.String()+"/projections/"+projectionID.String(),
		nil,
	)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("conceptId", "projectionId")
	c.SetParamValues(conceptID2.String(), projectionID.String())

	err := handler.DeleteCanonicalProjection(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

// TestCanonicalProjection_FullWorkflow tests the complete flow of creating and deleting projections
func TestCanonicalProjection_FullWorkflow(t *testing.T) {
	env := newEquivalenceHandlerTestEnv()
	conceptID := uuid.New()
	itemID1 := uuid.New()
	itemID2 := uuid.New()

	seedCanonicalConceptWithDetails(t, env, conceptID, "Database Layer", "architecture")

	projectionID1 := createCanonicalProjectionForConcept(
		t,
		env,
		conceptID,
		itemID1,
		"code",
		"primary",
		1.0,
		StrategyManualLink,
	)
	projectionID2 := createCanonicalProjectionForConcept(
		t,
		env,
		conceptID,
		itemID2,
		"requirements",
		"related",
		0.8,
		StrategyNamingPattern,
	)

	assertProjectionCount(t, env, conceptID, 2)

	deleteCanonicalProjectionForConcept(t, env, conceptID, projectionID1)
	assertProjectionRemaining(t, env, conceptID, projectionID2)

	deleteCanonicalProjectionForConcept(t, env, conceptID, projectionID2)
	assertProjectionCount(t, env, conceptID, 0)
}
