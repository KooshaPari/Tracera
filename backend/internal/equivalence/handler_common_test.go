package equivalence

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
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
