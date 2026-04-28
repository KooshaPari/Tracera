package equivalence

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

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
		assert.Empty(t, resp)
	})
}

// TestProjectScopedConceptEndpointsBackwardCompatibility tests that both
// the old /equivalences/concepts and new /projects/:projectId/concepts endpoints work together
func TestProjectScopedConceptEndpointsBackwardCompatibility(t *testing.T) {
	env := newEquivalenceHandlerTestEnv()
	createdConceptID := createBackwardCompatibleConcept(t, env)
	oldList := listConceptsOldEndpoint(t, env)
	newList := listConceptsProjectEndpoint(t, env)

	assert.NotEmpty(t, oldList)
	assert.Equal(t, createdConceptID, oldList[0].ID)
	assert.Len(t, newList, len(oldList))
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
