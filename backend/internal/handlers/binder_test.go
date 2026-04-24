//go:build !integration && !e2e

package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEchoBinder_Bind(t *testing.T) {
	e := echo.New()

	t.Run("success", func(t *testing.T) {
		binder := &EchoBinder{}

		body := map[string]string{"name": "test"}
		bodyBytes, err := json.Marshal(body)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/", bytes.NewReader(bodyBytes))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		var result map[string]string
		err = binder.Bind(c, &result)
		require.NoError(t, err)
		assert.Equal(t, "test", result["name"])
	})
}

func TestTestBinder_Bind(t *testing.T) {
	e := echo.New()

	t.Run("success", func(t *testing.T) {
		binder := &TestBinder{}

		body := map[string]string{"name": "test"}
		bodyBytes, err := json.Marshal(body)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/", bytes.NewReader(bodyBytes))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		var result map[string]string
		err = binder.Bind(c, &result)
		require.NoError(t, err)
		assert.Equal(t, "test", result["name"])
	})

	t.Run("empty body", func(t *testing.T) {
		binder := &TestBinder{}

		req := httptest.NewRequest(http.MethodPost, "/", bytes.NewReader([]byte{}))
		req.ContentLength = 0
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		var result map[string]string
		err := binder.Bind(c, &result)
		require.NoError(t, err) // Should succeed with empty body
	})

	t.Run("invalid JSON", func(t *testing.T) {
		binder := &TestBinder{}

		req := httptest.NewRequest(http.MethodPost, "/", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		var result map[string]string
		err := binder.Bind(c, &result)
		assert.Error(t, err)
	})
}

func TestNoOpBinder_Bind(t *testing.T) {
	e := echo.New()
	binder := &NoOpBinder{}

	req := httptest.NewRequest(http.MethodPost, "/", bytes.NewReader([]byte("anything")))
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	var result map[string]string
	err := binder.Bind(c, &result)
	require.NoError(t, err) // Always succeeds
}
