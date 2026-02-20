package server

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
)

func TestEchoInstanceCreation(t *testing.T) {
	t.Run("echo instance can be created", func(t *testing.T) {
		e := echo.New()
		assert.NotNil(t, e)
	})

	t.Run("routes can be registered on echo", func(t *testing.T) {
		e := echo.New()
		e.GET("/test", func(c echo.Context) error {
			return c.String(200, "ok")
		})

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		assert.Equal(t, 200, rec.Code)
	})

	t.Run("middleware can be added to echo", func(t *testing.T) {
		e := echo.New()
		middlewareCalled := false

		e.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
			return func(c echo.Context) error {
				middlewareCalled = true
				return next(c)
			}
		})

		e.GET("/test", func(c echo.Context) error {
			return c.String(200, "ok")
		})

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		assert.True(t, middlewareCalled)
	})

	t.Run("error handler on echo", func(t *testing.T) {
		e := echo.New()
		e.GET("/error", func(c echo.Context) error {
			return echo.NewHTTPError(http.StatusBadRequest, "test error")
		})

		req := httptest.NewRequest(http.MethodGet, "/error", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("404 on echo", func(t *testing.T) {
		e := echo.New()
		req := httptest.NewRequest(http.MethodGet, "/nonexistent", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusNotFound, rec.Code)
	})
}
