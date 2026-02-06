package auth

import (
	"context"
)

// User represents an authenticated user
type User struct {
	ID        string
	Email     string
	Name      string
	Role      string
	ProjectID string
	Metadata  map[string]interface{}
}

// Provider defines the interface for authentication providers.
// This allows swapping between AuthKit, Supabase Auth, or other providers.
type Provider interface {
	// ValidateToken validates a token and returns the user
	ValidateToken(ctx context.Context, token string) (*User, error)

	// GetUser retrieves a user by ID
	GetUser(ctx context.Context, userID string) (*User, error)

	// CreateUser creates a new user
	CreateUser(ctx context.Context, email, password, name string) (*User, error)

	// UpdateUser updates user information
	UpdateUser(ctx context.Context, userID string, updates map[string]interface{}) (*User, error)

	// DeleteUser deletes a user
	DeleteUser(ctx context.Context, userID string) error

	// ListUsers lists users with pagination
	ListUsers(ctx context.Context, limit, offset int) ([]*User, error)

	// Close closes the provider connection
	Close() error
}

// SessionManager defines the interface for session management
type SessionManager interface {
	// CreateSession creates a new session for a user
	CreateSession(ctx context.Context, userID string) (string, error)

	// ValidateSession validates a session token
	ValidateSession(ctx context.Context, token string) (*User, error)

	// RevokeSession revokes a session
	RevokeSession(ctx context.Context, token string) error

	// RefreshSession refreshes a session token
	RefreshSession(ctx context.Context, token string) (string, error)
}

// PermissionChecker defines the interface for permission checking
type PermissionChecker interface {
	// HasPermission checks if a user has a specific permission
	HasPermission(ctx context.Context, userID, projectID, permission string) (bool, error)

	// HasRole checks if a user has a specific role
	HasRole(ctx context.Context, userID, projectID, role string) (bool, error)

	// GetPermissions gets all permissions for a user in a project
	GetPermissions(ctx context.Context, userID, projectID string) ([]string, error)

	// GetRoles gets all roles for a user in a project
	GetRoles(ctx context.Context, userID, projectID string) ([]string, error)
}
