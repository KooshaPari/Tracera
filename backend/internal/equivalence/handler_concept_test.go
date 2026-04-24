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
		assert.InEpsilon(t, 0.9, resp.Projection.Confidence, 1e-9)
		assert.NotEmpty(t, resp.Message)
		assert.False(t, resp.CreatedAt.IsZero())
	})
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
		require.Error(t, err)
		assert.Nil(t, deletedProjection)
	})
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
	assert.Len(t, projections, expected)
}

func assertProjectionRemaining(t *testing.T, env *equivalenceHandlerTestEnv, conceptID, projectionID uuid.UUID) {
	projections, err := env.repo.GetProjectionsByConcept(context.Background(), conceptID)
	require.NoError(t, err)
	assert.Len(t, projections, 1)
	assert.Equal(t, projectionID, projections[0].ID)
}
