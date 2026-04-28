package auth

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

const (
	authKitHSSecretMinLen = 32
	authKitClientTimeout  = 10 * time.Second
)

// WorkOSClaims represents WorkOS JWT claims from AuthKit or bridge tokens
type WorkOSClaims struct {
	Sub           string   `json:"sub"` // WorkOS user ID
	Email         string   `json:"email"`
	EmailVerified bool     `json:"email_verified"`
	Name          string   `json:"name"`
	GivenName     string   `json:"given_name"`
	FamilyName    string   `json:"family_name"`
	Picture       string   `json:"picture"`
	OrgID         string   `json:"org_id"` // WorkOS organization ID
	OrgSlug       string   `json:"org_slug"`
	Role          string   `json:"role"`
	Permissions   []string `json:"permissions"`
	TokenType     string   `json:"token_type,omitempty"` // "service" for bridge tokens
	jwt.RegisteredClaims
}

// KitAdapter implements AuthProvider using AuthKit/WorkOS
// Uses GORM for public.profiles (schema owned by GORM AutoMigrate)
// Uses JWKS (RS256) for validating WorkOS access tokens per WorkOS documentation
type KitAdapter struct {
	tokenBridge *TokenBridge
	httpClient  *http.Client
	db          *gorm.DB
}

// NewKitAdapter creates a new AuthKit adapter
// clientID: WorkOS Client ID for JWKS URL construction (required for RS256 validation)
// jwtSecret: WorkOS JWT secret for HS256 service tokens (optional, fallback)
// db: GORM DB for profile management (profiles table created via AutoMigrate)
func NewKitAdapter(clientID, jwtSecret string, db *gorm.DB) *KitAdapter {
	jwksURL := "https://api.workos.com/sso/jwks/" + clientID

	hsSecret := []byte(jwtSecret)
	if len(hsSecret) < authKitHSSecretMinLen {
		if len(hsSecret) == 0 {
			hsSecret = []byte("default-fallback-secret-not-for-production-use-32")
		} else {
			padded := make([]byte, authKitHSSecretMinLen)
			copy(padded, hsSecret)
			hsSecret = padded
		}
	}

	tokenBridge, err := NewTokenBridge(hsSecret, jwksURL, clientID, "")
	if err != nil {
		slog.Error("Warning: Failed to initialize TokenBridge", "error", err)
	}

	return &KitAdapter{
		tokenBridge: tokenBridge,
		db:          db,
		httpClient: &http.Client{
			Timeout: authKitClientTimeout,
		},
	}
}

// ValidateToken validates a WorkOS JWT token and syncs profile to public.profiles
func (adapter *KitAdapter) ValidateToken(ctx context.Context, token string) (*User, error) {
	if adapter.tokenBridge == nil {
		return nil, errors.New("token bridge not initialized")
	}

	// Token validation historically did not respect caller cancellation (only HTTP client timeouts).
	// Keep that behavior while still threading context through.
	ctxNoCancel := context.WithoutCancel(ctx)
	claims, err := adapter.tokenBridge.ValidateToken(ctxNoCancel, token)
	if err != nil {
		return nil, fmt.Errorf("failed to validate token: %w", err)
	}

	user, err := adapter.SyncProfileFromWorkOS(ctx, claims)
	if err != nil {
		slog.Error("Failed to sync WorkOS profile", "error", err)
		return nil, fmt.Errorf("failed to sync profile: %w", err)
	}

	display := user.Email
	if display == "" {
		display = user.Name
	}
	if display == "" {
		display = user.ID
	}
	slog.Info("Validated WorkOS token for user ( )", "id", display, "id", user.ID)
	return user, nil
}

// SyncProfileFromWorkOS creates or updates profile using GORM upsert.
func (adapter *KitAdapter) SyncProfileFromWorkOS(ctx context.Context, claims *WorkOSClaims) (*User, error) {
	workosIDs := map[string]interface{}{"org_slug": claims.OrgSlug}
	workosIDsJSON, err := json.Marshal(workosIDs)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal WorkOS IDs: %w", err)
	}

	profile := &models.Profile{
		WorkosUserID: claims.Sub,
		WorkosOrgID:  claims.OrgID,
		Email:        claims.Email,
		FullName:     claims.Name,
		WorkosIDs:    workosIDsJSON,
	}

	updateColumns := []string{
		"workos_org_id",
		"email",
		"full_name",
		"workos_ids",
		"updated_at",
	}
	err = adapter.db.WithContext(ctx).Clauses(clause.OnConflict{
		Columns:   []clause.Column{{Name: "workos_user_id"}},
		DoUpdates: clause.AssignmentColumns(updateColumns),
	}).Create(profile).Error
	if err != nil {
		return nil, fmt.Errorf("failed to sync profile: %w", err)
	}

	return &User{
		ID:        profile.WorkosUserID,
		Email:     profile.Email,
		Name:      profile.FullName,
		Role:      claims.Role,
		ProjectID: profile.WorkosOrgID,
		Metadata: map[string]interface{}{
			"workos_user_id": profile.WorkosUserID,
			"workos_org_id":  profile.WorkosOrgID,
			"permissions":    claims.Permissions,
			"profile_id":     profile.ID,
		},
	}, nil
}

// GetUser retrieves a user from public.profiles by WorkOS user ID
func (a *KitAdapter) GetUser(ctx context.Context, userID string) (*User, error) {
	var profile models.Profile
	err := a.db.WithContext(ctx).Where("workos_user_id = ? AND deleted_at IS NULL", userID).First(&profile).Error
	if err != nil {
		return nil, fmt.Errorf("user not found: %w", err)
	}

	var metadata map[string]interface{}
	if len(profile.Metadata) > 0 {
		if err := json.Unmarshal(profile.Metadata, &metadata); err != nil {
			return nil, fmt.Errorf("failed to decode user metadata: %w", err)
		}
	}

	return &User{
		ID:        profile.WorkosUserID,
		Email:     profile.Email,
		Name:      profile.FullName,
		ProjectID: profile.WorkosOrgID,
		Metadata:  metadata,
	}, nil
}

// CreateUser is not implemented - users are created via WorkOS/AuthKit
func (a *KitAdapter) CreateUser(_ context.Context, _, _, _ string) (*User, error) {
	return nil, errors.New("user creation must be done through WorkOS/AuthKit, not directly")
}

// UpdateUser updates user profile in public.profiles
func (adapter *KitAdapter) UpdateUser(
	ctx context.Context,
	userID string,
	updates map[string]interface{},
) (*User, error) {
	updatesJSON, err := json.Marshal(updates)
	if err != nil {
		return nil, fmt.Errorf("failed to encode user updates: %w", err)
	}

	res := adapter.db.WithContext(ctx).Model(&models.Profile{}).
		Where("workos_user_id = ? AND deleted_at IS NULL", userID).
		Update("metadata", gorm.Expr("COALESCE(metadata, '{}'::jsonb) || ?::jsonb", string(updatesJSON)))
	if res.Error != nil {
		return nil, fmt.Errorf("failed to update user: %w", res.Error)
	}
	if res.RowsAffected == 0 {
		return nil, errors.New("user not found")
	}

	return adapter.GetUser(ctx, userID)
}

// DeleteUser soft-deletes a user from public.profiles
func (a *KitAdapter) DeleteUser(ctx context.Context, userID string) error {
	now := time.Now()
	res := a.db.WithContext(ctx).Model(&models.Profile{}).
		Where("workos_user_id = ?", userID).
		Update("deleted_at", now)
	if res.Error != nil {
		return fmt.Errorf("failed to delete user: %w", res.Error)
	}
	return nil
}

// ListUsers lists users from public.profiles
func (a *KitAdapter) ListUsers(ctx context.Context, limit, offset int) ([]*User, error) {
	var profiles []models.Profile
	err := a.db.WithContext(ctx).Where("deleted_at IS NULL").
		Order("created_at DESC").
		Limit(limit).Offset(offset).
		Find(&profiles).Error
	if err != nil {
		return nil, fmt.Errorf("failed to list users: %w", err)
	}

	users := make([]*User, 0, len(profiles))
	for _, profile := range profiles {
		var metadata map[string]interface{}
		if len(profile.Metadata) > 0 {
			if err := json.Unmarshal(profile.Metadata, &metadata); err != nil {
				return nil, fmt.Errorf("failed to decode user metadata: %w", err)
			}
		}
		users = append(users, &User{
			ID:        profile.WorkosUserID,
			Email:     profile.Email,
			Name:      profile.FullName,
			ProjectID: profile.WorkosOrgID,
			Metadata:  metadata,
		})
	}
	return users, nil
}

// Close closes the AuthKit adapter
func (a *KitAdapter) Close() error {
	if a.tokenBridge != nil {
		if err := a.tokenBridge.Close(); err != nil {
			slog.Error("Error closing token bridge", "error", err)
		}
	}
	slog.Info("Closing AuthKit adapter")
	return nil
}
