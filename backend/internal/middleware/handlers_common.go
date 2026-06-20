// Package middleware provides HTTP middleware utilities.
package middleware

import (
	"github.com/labstack/echo/v4"
)

const healthEndpoint = "/health"

// ErrorResponse represents a standardized error response format
type ErrorResponse struct {
	Error   string      `json:"error"`
	Message string      `json:"message"`
	Details interface{} `json:"details,omitempty"`
}

// SuccessResponse represents a standardized success response format
type SuccessResponse struct {
	Data  interface{} `json:"data"`
	Error *string     `json:"error,omitempty"`
}

// RespondError sends a standardized JSON error response
func RespondError(c echo.Context, statusCode int, errorCode, message string) error {
	return c.JSON(statusCode, ErrorResponse{
		Error:   errorCode,
		Message: message,
		Details: nil,
	})
}

// RespondErrorWithDetails sends an error response with additional details
func RespondErrorWithDetails(c echo.Context, statusCode int, errorCode, message string, details interface{}) error {
	return c.JSON(statusCode, ErrorResponse{
		Error:   errorCode,
		Message: message,
		Details: details,
	})
}

// RespondSuccess sends a standardized JSON success response
func RespondSuccess(c echo.Context, statusCode int, data interface{}) error {
	return c.JSON(statusCode, SuccessResponse{
		Data:  data,
		Error: nil,
	})
}

// SetContextValue safely sets a value in the context
func SetContextValue(c echo.Context, key string, value interface{}) {
	c.Set(key, value)
}

// GetContextValue safely gets a value from context
func GetContextValue(c echo.Context, key string) (interface{}, bool) {
	val := c.Get(key)
	return val, val != nil
}

// GetContextString safely gets a string value from context
func GetContextString(c echo.Context, key string) (string, bool) {
	val, ok := c.Get(key).(string)
	return val, ok
}

// SetSecurityHeader sets a single security header
func SetSecurityHeader(c echo.Context, name, value string) {
	c.Response().Header().Set(name, value)
}

// SetSecurityHeaders sets multiple security headers at once
func SetSecurityHeaders(c echo.Context, headers map[string]string) {
	for name, value := range headers {
		c.Response().Header().Set(name, value)
	}
}

// LogError logs an error message with context
func LogError(c echo.Context, message string, err error) {
	c.Logger().Errorf("%s: %v", message, err)
}

// LogWarn logs a warning message
func LogWarn(c echo.Context, message string) {
	c.Logger().Warn(message)
}

// GetRealIP extracts the client's real IP address
func GetRealIP(c echo.Context) string {
	return c.RealIP()
}

// ShouldSkipPath checks if a path should be skipped (helper for middleware)
func ShouldSkipPath(path string, skipPrefixes []string) bool {
	for _, prefix := range skipPrefixes {
		if path == prefix || (len(prefix) > 0 && len(path) > len(prefix) && path[:len(prefix)+1] == prefix+"/") {
			return true
		}
	}
	return false
}

// ExtractBearerToken extracts a bearer token from Authorization header
func ExtractBearerToken(c echo.Context) string {
	authHeader := c.Request().Header.Get("Authorization")
	if authHeader != "" {
		const bearerScheme = "Bearer "
		if len(authHeader) > len(bearerScheme) && authHeader[:len(bearerScheme)] == bearerScheme {
			return authHeader[len(bearerScheme):]
		}
	}
	return ""
}

// ExtractAPIKey extracts API key from various header sources
func ExtractAPIKey(c echo.Context) string {
	// Try X-API-Key header first
	if apiKey := c.Request().Header.Get("X-API-Key"); apiKey != "" {
		return apiKey
	}
	// Try Authorization header
	return ExtractBearerToken(c)
}

// ValidateHTTPError creates and returns an HTTP error response
func ValidateHTTPError(statusCode int, message string) error {
	return echo.NewHTTPError(statusCode, message)
}

// ChainMiddleware chains multiple middleware functions
func ChainMiddleware(middlewares ...echo.MiddlewareFunc) []echo.MiddlewareFunc {
	return middlewares
}
