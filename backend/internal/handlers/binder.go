//go:build !integration && !e2e
// +build !integration,!e2e

package handlers

import (
	"encoding/json"

	"github.com/labstack/echo/v4"
)

// RequestBinder defines the interface for binding request data
type RequestBinder interface {
	Bind(c echo.Context, v interface{}) error
}

// EchoBinder is the production binder that delegates to Echo's default binding
type EchoBinder struct{}

// Bind delegates to Echo's standard binding mechanism
func (eb *EchoBinder) Bind(c echo.Context, v interface{}) error {
	return c.Bind(v)
}

// TestBinder is a test-friendly binder that bypasses Echo's internal binding complexities
// It's specifically designed for httptest contexts where normal binding doesn't work
type TestBinder struct{}

// Bind unmarshals JSON from the request body using json.Decoder
// This approach works in httptest contexts where Echo's binding mechanism has limitations
func (tb *TestBinder) Bind(c echo.Context, val interface{}) error {
	// Create a new reader from the request body to handle the binding
	// This is safe because httptest requests provide a fresh body Reader
	req := c.Request()
	if req.ContentLength == 0 {
		return nil
	}

	// Use json.NewDecoder to parse the body
	decoder := json.NewDecoder(req.Body)
	return decoder.Decode(val)
}

// NoOpBinder is a binder that does nothing (for testing scenarios where binding should be skipped)
type NoOpBinder struct{}

// Bind is a no-op that always succeeds
func (nb *NoOpBinder) Bind(_ echo.Context, _ interface{}) error {
	return nil
}
