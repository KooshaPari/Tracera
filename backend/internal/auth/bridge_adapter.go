package auth

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
)

// BridgeAuthAdapter wraps TokenBridge to implement the AuthProvider interface
// This allows the middleware to use the token bridge for authentication
type BridgeAuthAdapter struct {
	bridge *TokenBridge
	db     DBQuerier
}

// NewBridgeAuthAdapter creates a new bridge auth adapter
func NewBridgeAuthAdapter(bridge *TokenBridge, db DBQuerier) *BridgeAuthAdapter {
	return &BridgeAuthAdapter{
		bridge: bridge,
		db:     db,
	}
}

// ValidateToken validates a token using the bridge (RS256 or HS256)
func (adapter *BridgeAuthAdapter) ValidateToken(ctx context.Context, token string) (*User, error) {
	// Historically token validation did not respect caller cancellation (only HTTP client timeouts).
	ctxNoCancel := context.WithoutCancel(ctx)
	claims, err := adapter.bridge.ValidateToken(ctxNoCancel, token)
	if err != nil {
		return nil, fmt.Errorf("token validation failed: %w", err)
	}

	// For service tokens, return user directly from claims
	if claims.TokenType == "service" {
		return &User{
			ID:        claims.Sub,
			Email:     claims.Email,
			ProjectID: claims.OrgID,
			Metadata: map[string]interface{}{
				"token_type": "service",
				"org_id":     claims.OrgID,
			},
		}, nil
	}

	// For user tokens, sync with database
	user, err := adapter.syncUserFromClaims(ctx, claims)
	if err != nil {
		slog.Error("Failed to sync user from token", "error", err)
		return nil, fmt.Errorf("failed to sync user: %w", err)
	}

	return user, nil
}

// syncUserFromClaims syncs user profile from token claims
func (adapter *BridgeAuthAdapter) syncUserFromClaims(ctx context.Context, claims *WorkOSClaims) (*User, error) {
	// Query profile from database
	var profile struct {
		ID           string
		WorkosUserID string
		WorkosOrgID  string
		Email        string
		FullName     string
	}

	query := `
		SELECT id, workos_user_id, workos_org_id, email, full_name
		FROM public.profiles
		WHERE workos_user_id = $1
	`

	err := adapter.db.QueryRow(ctx, query, claims.Sub).Scan(
		&profile.ID,
		&profile.WorkosUserID,
		&profile.WorkosOrgID,
		&profile.Email,
		&profile.FullName,
	)
	if err != nil {
		// If user not found in local DB (which happens on first login),
		// we fallback to using data directly from the verified claims.
		slog.Info("SyncUserFromClaims: user not found in local profiles, using claims", "user", claims.Sub, "path", err)
		return &User{
			ID:        claims.Sub,
			Email:     claims.Email,
			ProjectID: claims.OrgID,
			Metadata: map[string]interface{}{
				"workos_user_id": claims.Sub,
				"workos_org_id":  claims.OrgID,
				"permissions":    claims.Permissions,
			},
		}, nil
	}

	return &User{
		ID:        profile.WorkosUserID,
		Email:     profile.Email,
		Name:      profile.FullName,
		ProjectID: profile.WorkosOrgID,
		Metadata: map[string]interface{}{
			"workos_user_id": profile.WorkosUserID,
			"workos_org_id":  profile.WorkosOrgID,
			"permissions":    claims.Permissions,
			"profile_id":     profile.ID,
		},
	}, nil
}

// GetUser retrieves a user by ID
func (adapter *BridgeAuthAdapter) GetUser(ctx context.Context, userID string) (*User, error) {
	var profile struct {
		ID           string
		WorkosUserID string
		WorkosOrgID  string
		Email        string
		FullName     string
	}

	query := `
		SELECT id, workos_user_id, workos_org_id, email, full_name
		FROM public.profiles
		WHERE workos_user_id = $1
	`

	err := adapter.db.QueryRow(ctx, query, userID).Scan(
		&profile.ID,
		&profile.WorkosUserID,
		&profile.WorkosOrgID,
		&profile.Email,
		&profile.FullName,
	)
	if err != nil {
		return nil, fmt.Errorf("user not found: %w", err)
	}

	return &User{
		ID:        profile.WorkosUserID,
		Email:     profile.Email,
		Name:      profile.FullName,
		ProjectID: profile.WorkosOrgID,
	}, nil
}

// CreateUser is not implemented - users are created via WorkOS
func (a *BridgeAuthAdapter) CreateUser(_ context.Context, _, _, _ string) (*User, error) {
	return nil, errors.New("user creation must be done through WorkOS/AuthKit")
}

// UpdateUser updates user profile
func (a *BridgeAuthAdapter) UpdateUser(_ context.Context, _ string, _ map[string]interface{}) (*User, error) {
	return nil, errors.New("not implemented")
}

// DeleteUser soft-deletes a user
func (a *BridgeAuthAdapter) DeleteUser(_ context.Context, _ string) error {
	return errors.New("not implemented")
}

// ListUsers lists users with pagination
func (a *BridgeAuthAdapter) ListUsers(_ context.Context, _, _ int) ([]*User, error) {
	return nil, errors.New("not implemented")
}

// Close closes the adapter
func (a *BridgeAuthAdapter) Close() error {
	return a.bridge.Close()
}

// CreateBridgeToken creates a service token for inter-service auth
func (a *BridgeAuthAdapter) CreateBridgeToken(userID, orgID string) (string, error) {
	return a.bridge.CreateBridgeToken(userID, orgID)
}
