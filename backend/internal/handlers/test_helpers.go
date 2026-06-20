//go:build !integration && !e2e

package handlers

import (
	"bytes"
	"encoding/json"
	"net/http/httptest"
	"testing"

	"github.com/alicebob/miniredis/v2"
	"github.com/labstack/echo/v4"
)

// CreateEchoContext creates a properly configured Echo context for testing
// This helper ensures JSON binding works correctly in test environments
func CreateEchoContext(
	t *testing.T,
	method string,
	path string,
	body interface{},
) (echo.Context, *httptest.ResponseRecorder) {
	// Create request body
	var bodyReader *bytes.Reader
	if body != nil {
		bodyBytes, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("Failed to marshal body: %v", err)
		}
		bodyReader = bytes.NewReader(bodyBytes)
	} else {
		bodyReader = bytes.NewReader([]byte{})
	}

	// Create HTTP request with proper headers
	req := httptest.NewRequest(method, path, bodyReader)
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)

	// Create response recorder
	rec := httptest.NewRecorder()

	// Create Echo instance and context
	e := echo.New()
	c := e.NewContext(req, rec)

	return c, rec
}

// BindAndAssert is a test helper that binds data and asserts success
func BindAndAssert(t *testing.T, c echo.Context, target interface{}) {
	// Read body
	body := c.Request().Body
	bodyBytes := make([]byte, c.Request().ContentLength)
	_, err := body.Read(bodyBytes)
	if err != nil && err.Error() != "EOF" {
		t.Fatalf("Failed to read body: %v", err)
	}

	// Unmarshal directly (bypassing Echo's binder)
	err = json.Unmarshal(bodyBytes, target)
	if err != nil {
		t.Fatalf("Failed to unmarshal body: %v", err)
	}
}

// AssertStatusCode asserts the response status code
func AssertStatusCode(t *testing.T, rec *httptest.ResponseRecorder, expected int) {
	if rec.Code != expected {
		t.Errorf("Expected status code %d, got %d. Response: %s", expected, rec.Code, rec.Body.String())
	}
}

// AssertResponseBody unmarshals and asserts the response body
func AssertResponseBody(t *testing.T, rec *httptest.ResponseRecorder, target interface{}) {
	err := json.Unmarshal(rec.Body.Bytes(), target)
	if err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}
}

// MockRealtimeBroadcaster is a test mock for realtime.Broadcaster.
type MockRealtimeBroadcaster struct{}

// Publish satisfies the realtime.Broadcaster interface for tests.
func (m *MockRealtimeBroadcaster) Publish(_ interface{}, _ interface{}) error {
	return nil
}

// Miniredis wraps the real miniredis for testing
type Miniredis struct {
	server *miniredis.Miniredis
}

// NewMiniredis creates a new in-memory Redis for testing using the real miniredis library
func NewMiniredis() (*Miniredis, error) {
	mr, err := miniredis.Run()
	if err != nil {
		return nil, err
	}

	return &Miniredis{
		server: mr,
	}, nil
}

// Addr returns the address of the miniredis server
func (m *Miniredis) Addr() string {
	return m.server.Addr()
}

// Close closes the miniredis server
func (m *Miniredis) Close() error {
	m.server.Close()
	return nil
}
