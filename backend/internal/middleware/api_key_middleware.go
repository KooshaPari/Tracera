// Package middleware provides HTTP middleware utilities.
package middleware

import (
	"log/slog"
	"net/http"
	"strings"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

// APIKeyMiddleware validates API keys and sets context for rate limiting
type APIKeyMiddleware struct {
	manager *auth.APIKeyManager
	skipper echo.MiddlewareFunc
}

const (
	httpErrorStatusMin = 400
	roleReadOnlyLevel  = 1
	roleReadWriteLevel = 2
	roleAdminLevel     = 3
	apiKeyBearerParts  = 2
)

// NewAPIKeyMiddleware creates a new API key validation middleware
func NewAPIKeyMiddleware(manager *auth.APIKeyManager) *APIKeyMiddleware {
	return &APIKeyMiddleware{
		manager: manager,
		skipper: nil,
	}
}

// Middleware returns the Echo middleware function
func (m *APIKeyMiddleware) Middleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Skip if skipper returns true
			if m.skipper != nil && m.shouldSkip(c) {
				return next(c)
			}

			// Extract API key from header
			apiKey := m.extractAPIKey(c)
			if apiKey == "" {
				// No API key provided, continue (user may have session auth)
				return next(c)
			}

			// Validate API key
			key, err := m.manager.ValidateAPIKey(c.Request().Context(), apiKey)
			if err != nil {
				return RespondError(c, http.StatusUnauthorized, "invalid_api_key",
					"The provided API key is invalid or has been revoked")
			}

			// Set API key information in context for downstream middleware
			SetContextValue(c, "api_key_id", key.ID.String())
			SetContextValue(c, "api_key_role", key.Role)
			SetContextValue(c, "api_key_scopes", key.Scopes)
			SetContextValue(c, "account_id", key.AccountID.String())
			if key.ProjectID != nil {
				SetContextValue(c, "project_id", key.ProjectID.String())
			}

			// Record usage (async)
			go m.recordUsage(c, key)

			return next(c)
		}
	}
}

// RequireAPIKey creates middleware that requires a valid API key
func (m *APIKeyMiddleware) RequireAPIKey() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			apiKey := m.extractAPIKey(c)
			if apiKey == "" {
				return RespondError(c, http.StatusUnauthorized, "api_key_required",
					"This endpoint requires an API key")
			}

			// Validate API key
			key, err := m.manager.ValidateAPIKey(c.Request().Context(), apiKey)
			if err != nil {
				return RespondError(c, http.StatusUnauthorized, "invalid_api_key",
					"The provided API key is invalid or has been revoked")
			}

			// Set context
			SetContextValue(c, "api_key_id", key.ID.String())
			SetContextValue(c, "api_key_role", key.Role)
			SetContextValue(c, "api_key_scopes", key.Scopes)
			SetContextValue(c, "account_id", key.AccountID.String())
			if key.ProjectID != nil {
				SetContextValue(c, "project_id", key.ProjectID.String())
			}

			return next(c)
		}
	}
}

// RequireScope creates middleware that requires a specific scope
func (m *APIKeyMiddleware) RequireScope(scope string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Get scopes from context
			scopes, ok := c.Get("api_key_scopes").([]string)
			if !ok {
				return RespondError(c, http.StatusForbidden, "insufficient_permissions",
					"This operation requires additional permissions")
			}

			// Check if scope is present
			if !containsScope(scopes, scope) {
				return RespondErrorWithDetails(c, http.StatusForbidden, "insufficient_scope",
					"API key does not have required scope", map[string]interface{}{
						"required":   scope,
						"has_scopes": scopes,
					})
			}

			return next(c)
		}
	}
}

// RequireRole creates middleware that requires a specific role or higher
func (m *APIKeyMiddleware) RequireRole(minRole auth.APIKeyRole) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Get role from context
			role, ok := c.Get("api_key_role").(auth.APIKeyRole)
			if !ok {
				return RespondError(c, http.StatusForbidden, "insufficient_permissions",
					"This operation requires additional permissions")
			}

			// Check role hierarchy
			if !hasRequiredRole(role, minRole) {
				return RespondErrorWithDetails(c, http.StatusForbidden, "insufficient_role",
					"API key role is insufficient for this operation", map[string]interface{}{
						"required": minRole,
						"has":      role,
					})
			}

			return next(c)
		}
	}
}

// extractAPIKey extracts the API key from request headers
func (m *APIKeyMiddleware) extractAPIKey(c echo.Context) string {
	// Try Authorization header first (Bearer token)
	authHeader := c.Request().Header.Get("Authorization")
	if authHeader != "" {
		parts := strings.SplitN(authHeader, " ", apiKeyBearerParts)
		if len(parts) == apiKeyBearerParts && strings.ToLower(parts[0]) == "bearer" {
			// Check if it's an API key (starts with trace_)
			if strings.HasPrefix(parts[1], "trace_") {
				return parts[1]
			}
		}
	}

	// Try X-API-Key header
	if apiKey := c.Request().Header.Get("X-API-Key"); apiKey != "" {
		return apiKey
	}

	return ""
}

// shouldSkip determines if middleware should be skipped
func (m *APIKeyMiddleware) shouldSkip(c echo.Context) bool {
	path := c.Request().URL.Path

	// Skip health checks
	if path == healthEndpoint || strings.HasPrefix(path, healthEndpoint+"/") {
		return true
	}

	// Skip static assets
	if strings.HasPrefix(path, "/static/") || strings.HasPrefix(path, "/assets/") {
		return true
	}

	return false
}

// recordUsage records API key usage metrics
func (m *APIKeyMiddleware) recordUsage(c echo.Context, key *auth.APIKey) {
	ctx := c.Request().Context()

	// Determine if request was successful
	success := c.Response().Status < httpErrorStatusMin

	// Calculate bytes transferred (approximate)
	bytesTransferred := c.Response().Size
	if bytesTransferred == 0 {
		// Estimate if not yet written
		bytesTransferred = c.Request().ContentLength
	}

	// Record usage
	if err := m.manager.RecordUsage(ctx, key.ID, success, bytesTransferred); err != nil {
		slog.Warn("failed to record API key usage", "key_id", key.ID, "error", err)
	}
}

// containsScope checks if a scope is present in the list
func containsScope(scopes []string, required string) bool {
	for _, scope := range scopes {
		// Check exact match
		if scope == required {
			return true
		}
		// Check wildcard match (e.g., "projects:*" matches "projects:read")
		if strings.HasSuffix(scope, ":*") {
			prefix := strings.TrimSuffix(scope, "*")
			if strings.HasPrefix(required, prefix) {
				return true
			}
		}
		// Check global wildcard
		if scope == "*" {
			return true
		}
	}
	return false
}

// hasRequiredRole checks if a role meets the minimum requirement
func hasRequiredRole(has, required auth.APIKeyRole) bool {
	roleHierarchy := map[auth.APIKeyRole]int{
		auth.APIKeyRoleReadOnly:  roleReadOnlyLevel,
		auth.APIKeyRoleReadWrite: roleReadWriteLevel,
		auth.APIKeyRoleAdmin:     roleAdminLevel,
	}

	return roleHierarchy[has] >= roleHierarchy[required]
}
