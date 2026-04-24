// Package auth provides authentication helpers and API key management.
package auth

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"golang.org/x/crypto/argon2"
)

const (
	apiKeyByteLength   = 32
	apiKeySaltLength   = 16
	apiKeyArgonTime    = 2
	apiKeyArgonMemory  = 19 * 1024
	apiKeyArgonThreads = 1
	apiKeyArgonKeyLen  = 32
)

// APIKeyRole defines the permission level for an API key
type APIKeyRole string

const (
	// APIKeyRoleReadOnly grants read-only access.
	APIKeyRoleReadOnly APIKeyRole = "read-only"
	// APIKeyRoleReadWrite grants read and write access.
	APIKeyRoleReadWrite APIKeyRole = "read-write"
	// APIKeyRoleAdmin grants administrative access.
	APIKeyRoleAdmin APIKeyRole = "admin"
)

// APIKey represents an API key with its metadata
type APIKey struct {
	ID            uuid.UUID  `json:"id"`
	AccountID     uuid.UUID  `json:"account_id"`
	ProjectID     *uuid.UUID `json:"project_id,omitempty"`
	Name          string     `json:"name"`
	KeyHash       string     `json:"-"` // Never expose the hash
	Role          APIKeyRole `json:"role"`
	Scopes        []string   `json:"scopes"`
	LastUsedAt    *time.Time `json:"last_used_at,omitempty"`
	ExpiresAt     *time.Time `json:"expires_at,omitempty"`
	IsActive      bool       `json:"is_active"`
	CreatedAt     time.Time  `json:"created_at"`
	CreatedByID   uuid.UUID  `json:"created_by_id"`
	RevokedAt     *time.Time `json:"revoked_at,omitempty"`
	RevokedByID   *uuid.UUID `json:"revoked_by_id,omitempty"`
	RevokedReason string     `json:"revoked_reason,omitempty"`
}

// APIKeyUsage tracks usage metrics for an API key
type APIKeyUsage struct {
	APIKeyID         uuid.UUID `json:"api_key_id"`
	Date             time.Time `json:"date"`
	RequestCount     int64     `json:"request_count"`
	ErrorCount       int64     `json:"error_count"`
	BytesTransferred int64     `json:"bytes_transferred"`
}

// APIKeyManager handles API key lifecycle and operations
type APIKeyManager struct {
	db *pgxpool.Pool
}

// NewAPIKeyManager creates a new API key manager
func NewAPIKeyManager(db *pgxpool.Pool) *APIKeyManager {
	return &APIKeyManager{db: db}
}

// CreateAPIKey generates a new API key and stores it securely
// Returns the plaintext key (only shown once) and the key metadata
func (manager *APIKeyManager) CreateAPIKey(ctx context.Context, params CreateAPIKeyParams) (*APIKey, string, error) {
	// Generate a cryptographically secure random key
	keyBytes := make([]byte, apiKeyByteLength)
	if _, err := rand.Read(keyBytes); err != nil {
		return nil, "", fmt.Errorf("failed to generate random key: %w", err)
	}

	// Format: trace_<base64_key>
	plaintextKey := "trace_" + base64.RawURLEncoding.EncodeToString(keyBytes)

	// Hash the key using Argon2id
	keyHash, err := hashAPIKey(plaintextKey)
	if err != nil {
		return nil, "", fmt.Errorf("failed to hash API key: %w", err)
	}

	// Create key record
	apiKey := &APIKey{
		ID:          uuid.New(),
		AccountID:   params.AccountID,
		ProjectID:   params.ProjectID,
		Name:        params.Name,
		KeyHash:     keyHash,
		Role:        params.Role,
		Scopes:      params.Scopes,
		ExpiresAt:   params.ExpiresAt,
		IsActive:    true,
		CreatedAt:   time.Now(),
		CreatedByID: params.CreatedByID,
	}

	// Insert into database
	query := `
		INSERT INTO api_keys (
			id, account_id, project_id, name, key_hash, role, scopes,
			expires_at, is_active, created_at, created_by_id
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
	`

	_, err = manager.db.Exec(ctx, query,
		apiKey.ID, apiKey.AccountID, apiKey.ProjectID, apiKey.Name,
		apiKey.KeyHash, apiKey.Role, apiKey.Scopes, apiKey.ExpiresAt,
		apiKey.IsActive, apiKey.CreatedAt, apiKey.CreatedByID,
	)
	if err != nil {
		return nil, "", fmt.Errorf("failed to create API key: %w", err)
	}

	return apiKey, plaintextKey, nil
}

// CreateAPIKeyParams contains parameters for creating an API key
type CreateAPIKeyParams struct {
	AccountID   uuid.UUID
	ProjectID   *uuid.UUID
	Name        string
	Role        APIKeyRole
	Scopes      []string
	ExpiresAt   *time.Time
	CreatedByID uuid.UUID
}

// ValidateAPIKey validates a plaintext API key and returns its metadata
func (manager *APIKeyManager) ValidateAPIKey(ctx context.Context, plaintextKey string) (*APIKey, error) {
	// Hash the provided key
	keyHash, err := hashAPIKey(plaintextKey)
	if err != nil {
		return nil, fmt.Errorf("failed to hash API key: %w", err)
	}

	// Look up the key in the database
	query := `
		SELECT
			id, account_id, project_id, name, key_hash, role, scopes,
			last_used_at, expires_at, is_active, created_at, created_by_id,
			revoked_at, revoked_by_id, revoked_reason
		FROM api_keys
		WHERE key_hash = $1
	`

	var apiKey APIKey
	err = manager.db.QueryRow(ctx, query, keyHash).Scan(
		&apiKey.ID, &apiKey.AccountID, &apiKey.ProjectID, &apiKey.Name,
		&apiKey.KeyHash, &apiKey.Role, &apiKey.Scopes, &apiKey.LastUsedAt,
		&apiKey.ExpiresAt, &apiKey.IsActive, &apiKey.CreatedAt,
		&apiKey.CreatedByID, &apiKey.RevokedAt, &apiKey.RevokedByID,
		&apiKey.RevokedReason,
	)
	if err != nil {
		return nil, errors.New("invalid API key")
	}

	// Check if key is active
	if !apiKey.IsActive {
		return nil, errors.New("API key is inactive")
	}

	// Check if key is revoked
	if apiKey.RevokedAt != nil {
		return nil, errors.New("API key has been revoked")
	}

	// Check expiration
	if apiKey.ExpiresAt != nil && time.Now().After(*apiKey.ExpiresAt) {
		return nil, errors.New("API key has expired")
	}

	// Update last used timestamp (async)
	ctxNoCancel := context.WithoutCancel(ctx)
	go func(ctx context.Context, keyID uuid.UUID) {
		manager.updateLastUsed(ctx, keyID)
	}(ctxNoCancel, apiKey.ID)

	return &apiKey, nil
}

// RevokeAPIKey revokes an API key
func (manager *APIKeyManager) RevokeAPIKey(
	ctx context.Context,
	keyID uuid.UUID,
	revokedByID uuid.UUID,
	reason string,
) error {
	query := `
		UPDATE api_keys
		SET is_active = false,
		    revoked_at = $1,
		    revoked_by_id = $2,
		    revoked_reason = $3
		WHERE id = $4 AND is_active = true
	`

	result, err := manager.db.Exec(ctx, query, time.Now(), revokedByID, reason, keyID)
	if err != nil {
		return fmt.Errorf("failed to revoke API key: %w", err)
	}

	if result.RowsAffected() == 0 {
		return errors.New("API key not found or already revoked")
	}

	return nil
}

// RotateAPIKey creates a new key and revokes the old one
func (manager *APIKeyManager) RotateAPIKey(
	ctx context.Context,
	oldKeyID uuid.UUID,
	rotatedByID uuid.UUID,
) (*APIKey, string, error) {
	// Get old key details
	oldKey, err := manager.GetAPIKey(ctx, oldKeyID)
	if err != nil {
		return nil, "", fmt.Errorf("failed to get old key: %w", err)
	}

	// Create new key with same properties
	newKey, plaintextKey, err := manager.CreateAPIKey(ctx, CreateAPIKeyParams{
		AccountID:   oldKey.AccountID,
		ProjectID:   oldKey.ProjectID,
		Name:        oldKey.Name + " (rotated)",
		Role:        oldKey.Role,
		Scopes:      oldKey.Scopes,
		ExpiresAt:   oldKey.ExpiresAt,
		CreatedByID: rotatedByID,
	})
	if err != nil {
		return nil, "", fmt.Errorf("failed to create new key: %w", err)
	}

	// Revoke old key
	err = manager.RevokeAPIKey(ctx, oldKeyID, rotatedByID, "Key rotated")
	if err != nil {
		// Attempt to revoke the new key to maintain consistency
		revokeNewErr := manager.RevokeAPIKey(ctx, newKey.ID, rotatedByID, "Rotation failed")
		if revokeNewErr != nil {
			return nil, "", fmt.Errorf(
				"failed to revoke old key: %w; also failed to revoke new key: %w",
				err,
				revokeNewErr,
			)
		}
		return nil, "", fmt.Errorf("failed to revoke old key: %w", err)
	}

	return newKey, plaintextKey, nil
}

// GetAPIKey retrieves an API key by ID
func (manager *APIKeyManager) GetAPIKey(ctx context.Context, keyID uuid.UUID) (*APIKey, error) {
	query := `
		SELECT
			id, account_id, project_id, name, key_hash, role, scopes,
			last_used_at, expires_at, is_active, created_at, created_by_id,
			revoked_at, revoked_by_id, revoked_reason
		FROM api_keys
		WHERE id = $1
	`

	var apiKey APIKey
	err := manager.db.QueryRow(ctx, query, keyID).Scan(
		&apiKey.ID, &apiKey.AccountID, &apiKey.ProjectID, &apiKey.Name,
		&apiKey.KeyHash, &apiKey.Role, &apiKey.Scopes, &apiKey.LastUsedAt,
		&apiKey.ExpiresAt, &apiKey.IsActive, &apiKey.CreatedAt,
		&apiKey.CreatedByID, &apiKey.RevokedAt, &apiKey.RevokedByID,
		&apiKey.RevokedReason,
	)
	if err != nil {
		return nil, fmt.Errorf("API key not found: %w", err)
	}

	return &apiKey, nil
}

// ListAPIKeys lists all API keys for an account
func (manager *APIKeyManager) ListAPIKeys(
	ctx context.Context,
	accountID uuid.UUID,
	includeRevoked bool,
) ([]*APIKey, error) {
	query := `
		SELECT
			id, account_id, project_id, name, key_hash, role, scopes,
			last_used_at, expires_at, is_active, created_at, created_by_id,
			revoked_at, revoked_by_id, revoked_reason
		FROM api_keys
		WHERE account_id = $1
	`

	if !includeRevoked {
		query += " AND is_active = true AND revoked_at IS NULL"
	}

	query += " ORDER BY created_at DESC"

	rows, err := manager.db.Query(ctx, query, accountID)
	if err != nil {
		return nil, fmt.Errorf("failed to list API keys: %w", err)
	}
	defer rows.Close()

	var keys []*APIKey
	for rows.Next() {
		var apiKey APIKey
		err := rows.Scan(
			&apiKey.ID, &apiKey.AccountID, &apiKey.ProjectID, &apiKey.Name,
			&apiKey.KeyHash, &apiKey.Role, &apiKey.Scopes, &apiKey.LastUsedAt,
			&apiKey.ExpiresAt, &apiKey.IsActive, &apiKey.CreatedAt,
			&apiKey.CreatedByID, &apiKey.RevokedAt, &apiKey.RevokedByID,
			&apiKey.RevokedReason,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan API key: %w", err)
		}
		keys = append(keys, &apiKey)
	}

	return keys, nil
}

// RecordUsage records API key usage metrics
func (manager *APIKeyManager) RecordUsage(
	ctx context.Context,
	keyID uuid.UUID,
	success bool,
	bytesTransferred int64,
) error {
	query := `
		INSERT INTO api_key_usage (api_key_id, date, request_count, error_count, bytes_transferred)
		VALUES ($1, CURRENT_DATE, 1, $2, $3)
		ON CONFLICT (api_key_id, date)
		DO UPDATE SET
			request_count = api_key_usage.request_count + 1,
			error_count = api_key_usage.error_count + $2,
			bytes_transferred = api_key_usage.bytes_transferred + $3
	`

	errorCount := 0
	if !success {
		errorCount = 1
	}

	_, err := manager.db.Exec(ctx, query, keyID, errorCount, bytesTransferred)
	if err != nil {
		return fmt.Errorf("failed to record usage: %w", err)
	}

	return nil
}

// GetUsageStats retrieves usage statistics for an API key
func (manager *APIKeyManager) GetUsageStats(
	ctx context.Context,
	keyID uuid.UUID,
	from, to time.Time,
) ([]*APIKeyUsage, error) {
	query := `
		SELECT api_key_id, date, request_count, error_count, bytes_transferred
		FROM api_key_usage
		WHERE api_key_id = $1 AND date >= $2 AND date <= $3
		ORDER BY date DESC
	`

	rows, err := manager.db.Query(ctx, query, keyID, from, to)
	if err != nil {
		return nil, fmt.Errorf("failed to get usage stats: %w", err)
	}
	defer rows.Close()

	var stats []*APIKeyUsage
	for rows.Next() {
		var usage APIKeyUsage
		err := rows.Scan(&usage.APIKeyID, &usage.Date, &usage.RequestCount, &usage.ErrorCount, &usage.BytesTransferred)
		if err != nil {
			return nil, fmt.Errorf("failed to scan usage: %w", err)
		}
		stats = append(stats, &usage)
	}

	return stats, nil
}

// CheckPermission checks if an API key has permission for a specific scope
func (apiKey *APIKey) CheckPermission(scope string) bool {
	// Admin role has all permissions
	if apiKey.Role == APIKeyRoleAdmin {
		return true
	}

	// Check if scope is in the key's scopes
	for _, s := range apiKey.Scopes {
		if s == scope || s == "*" {
			return true
		}
	}

	return false
}

// updateLastUsed updates the last_used_at timestamp for an API key
func (m *APIKeyManager) updateLastUsed(ctx context.Context, keyID uuid.UUID) {
	query := `UPDATE api_keys SET last_used_at = $1 WHERE id = $2`
	if _, err := m.db.Exec(ctx, query, time.Now(), keyID); err != nil {
		slog.Error("failed to update last_used_at for API key", "error", keyID, "error", err)
	}
}

// hashAPIKey creates a secure hash of an API key using Argon2id
func hashAPIKey(plaintextKey string) (string, error) {
	salt := make([]byte, apiKeySaltLength)
	if _, err := rand.Read(salt); err != nil {
		return "", fmt.Errorf("failed to generate API key salt: %w", err)
	}

	// Argon2id parameters (OWASP recommendations)
	hash := argon2.IDKey(
		[]byte(plaintextKey),
		salt,
		apiKeyArgonTime,
		apiKeyArgonMemory,
		apiKeyArgonThreads,
		apiKeyArgonKeyLen,
	)

	// Combine salt and hash for storage
	return base64.RawStdEncoding.EncodeToString(salt) + ":" + base64.RawStdEncoding.EncodeToString(hash), nil
}
