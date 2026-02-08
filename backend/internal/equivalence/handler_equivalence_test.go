package equivalence

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

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
