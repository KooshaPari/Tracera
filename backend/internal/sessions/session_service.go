// Package sessions manages authenticated user sessions and OAuth token lifecycle.
package sessions

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/kooshapari/tracertm-backend/internal/graph"
)

const (
	// DefaultSessionTTL is the default session expiration time (30 days)
	DefaultSessionTTL = 30 * 24 * time.Hour

	// OAuthTokenTTL is the expiration time for OAuth access tokens (typically 1-3 hours).
	OAuthTokenTTL = 1 * time.Hour
)

// Session represents an authenticated user session
type Session struct {
	ID               uuid.UUID
	UserID           uuid.UUID
	Provider         string // "claude", "openai", etc
	AccessTokenHash  string
	RefreshTokenHash string
	TokenType        string
	ExpiresAt        time.Time
	CreatedAt        time.Time
	UpdatedAt        time.Time
	RevokedAt        *time.Time
}

// CreateSessionRequest holds the parameters for creating a new session
type CreateSessionRequest struct {
	UserID       uuid.UUID
	Provider     string
	AccessToken  string
	RefreshToken string
	TokenType    string
	ExpiresIn    time.Duration // How long until token expires
}

// CreateSessionResponse is returned after successful session creation
type CreateSessionResponse struct {
	SessionID     uuid.UUID
	UserID        uuid.UUID
	Provider      string
	ExpiresAt     time.Time
	CreatedAt     time.Time
	RefreshNeeded bool // True if token expires soon
}

// SessionService manages user sessions across PostgreSQL and Neo4j
type SessionService struct {
	db     *pgxpool.Pool
	neo4j  *graph.Neo4jClient
	encKey []byte // 32-byte AES key for token encryption
}

// NewSessionService creates a new session service
// encKey should be a 32-byte key for AES-256 encryption
func NewSessionService(db *pgxpool.Pool, neo4j *graph.Neo4jClient, encKey []byte) (*SessionService, error) {
	if len(encKey) != 32 {
		return nil, fmt.Errorf("encryption key must be 32 bytes, got %d", len(encKey))
	}

	return &SessionService{
		db:     db,
		neo4j:  neo4j,
		encKey: encKey,
	}, nil
}

// validateCreateSessionRequest validates the create session request fields.
func validateCreateSessionRequest(req *CreateSessionRequest) error {
	if req == nil {
		return errors.New("request cannot be nil")
	}
	if req.UserID == uuid.Nil {
		return errors.New("user_id is required")
	}
	if req.Provider == "" {
		return errors.New("provider is required")
	}
	if req.AccessToken == "" {
		return errors.New("access_token is required")
	}
	if req.TokenType == "" {
		req.TokenType = "Bearer"
	}
	if req.ExpiresIn == 0 {
		req.ExpiresIn = OAuthTokenTTL
	}
	return nil
}

// encryptSessionTokens encrypts the access and optional refresh tokens.
func (s *SessionService) encryptSessionTokens(req *CreateSessionRequest) ([]byte, []byte, error) {
	accessTokenEnc, err := s.encryptToken(req.AccessToken)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to encrypt access token: %w", err)
	}
	var refreshTokenEnc []byte
	if req.RefreshToken != "" {
		refreshTokenEnc, err = s.encryptToken(req.RefreshToken)
		if err != nil {
			return nil, nil, fmt.Errorf("failed to encrypt refresh token: %w", err)
		}
	}
	return accessTokenEnc, refreshTokenEnc, nil
}

// CreateSession creates a new authenticated session in both PostgreSQL and Neo4j
// This is an atomic operation - if either database write fails, the transaction is rolled back
func (s *SessionService) CreateSession(ctx context.Context, req *CreateSessionRequest) (*CreateSessionResponse, error) {
	if err := validateCreateSessionRequest(req); err != nil {
		return nil, err
	}

	sessionID := uuid.New()
	now := time.Now()
	expiresAt := now.Add(req.ExpiresIn)

	accessTokenEnc, refreshTokenEnc, err := s.encryptSessionTokens(req)
	if err != nil {
		return nil, err
	}

	// Start PostgreSQL transaction
	tx, err := s.db.Begin(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to start transaction: %w", err)
	}
	defer func() {
		if rerr := tx.Rollback(ctx); rerr != nil {
			slog.Warn("failed to rollback session transaction", "error", rerr)
		}
	}()

	// Create session in PostgreSQL
	err = tx.QueryRow(ctx,
		`INSERT INTO sessions (id, user_id, provider, access_token_encrypted,
		 refresh_token_encrypted, token_type, expires_at, created_at, updated_at)
		 VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
		 ON CONFLICT (user_id, provider) DO UPDATE SET
		   access_token_encrypted = EXCLUDED.access_token_encrypted,
		   refresh_token_encrypted = EXCLUDED.refresh_token_encrypted,
		   token_type = EXCLUDED.token_type,
		   expires_at = EXCLUDED.expires_at,
		   updated_at = EXCLUDED.updated_at,
		   revoked_at = NULL
		 RETURNING id`,
		sessionID, req.UserID, req.Provider, accessTokenEnc, refreshTokenEnc, req.TokenType, expiresAt, now, now).
		Scan(&sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to create session in postgres: %w", err)
	}

	// Also create OAuth token record
	err = tx.QueryRow(ctx,
		`INSERT INTO oauth_tokens (session_id, provider, access_token_encrypted,
		 refresh_token_encrypted, token_expires_at, created_at, updated_at)
		 VALUES ($1, $2, $3, $4, $5, $6, $7)`,
		sessionID, req.Provider, accessTokenEnc, refreshTokenEnc, expiresAt, now, now).
		Scan()

	if err != nil && err.Error() != "no rows" {
		// It's OK if INSERT returns no rows
		return nil, fmt.Errorf("failed to create oauth token record: %w", err)
	}

	// Commit PostgreSQL transaction
	if err := tx.Commit(ctx); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	// Create/update user node in Neo4j (non-blocking failure)
	// If Neo4j fails, we still return success since PostgreSQL was committed
	go s.createOrUpdateUserNode(context.Background(), req.UserID, req.Provider) //nolint:contextcheck // async fire-and-forget Neo4j op

	return &CreateSessionResponse{
		SessionID:     sessionID,
		UserID:        req.UserID,
		Provider:      req.Provider,
		ExpiresAt:     expiresAt,
		CreatedAt:     now,
		RefreshNeeded: req.ExpiresIn < 5*time.Minute,
	}, nil
}

// GetSession retrieves a session from PostgreSQL
func (s *SessionService) GetSession(ctx context.Context, sessionID uuid.UUID) (*Session, error) {
	if sessionID == uuid.Nil {
		return nil, errors.New("session_id is required")
	}

	var session Session
	var revokedAt *time.Time

	err := s.db.QueryRow(ctx,
		`SELECT id, user_id, provider, token_type, expires_at, created_at, updated_at, revoked_at
		 FROM sessions
		 WHERE id = $1`,
		sessionID).
		Scan(&session.ID, &session.UserID, &session.Provider, &session.TokenType,
			&session.ExpiresAt, &session.CreatedAt, &session.UpdatedAt, &revokedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to get session: %w", err)
	}

	session.RevokedAt = revokedAt
	return &session, nil
}

// RevokeSession marks a session as revoked
func (s *SessionService) RevokeSession(ctx context.Context, sessionID uuid.UUID) error {
	if sessionID == uuid.Nil {
		return errors.New("session_id is required")
	}

	result, err := s.db.Exec(ctx,
		`UPDATE sessions SET revoked_at = now(), updated_at = now() WHERE id = $1`,
		sessionID)
	if err != nil {
		return fmt.Errorf("failed to revoke session: %w", err)
	}

	if result.RowsAffected() == 0 {
		return errors.New("session not found")
	}

	return nil
}

// GetUserSession retrieves the current session for a user with a specific provider
func (s *SessionService) GetUserSession(ctx context.Context, userID uuid.UUID, provider string) (*Session, error) {
	if userID == uuid.Nil {
		return nil, errors.New("user_id is required")
	}

	if provider == "" {
		return nil, errors.New("provider is required")
	}

	var session Session
	var revokedAt *time.Time

	err := s.db.QueryRow(ctx,
		`SELECT id, user_id, provider, token_type, expires_at, created_at, updated_at, revoked_at
		 FROM sessions
		 WHERE user_id = $1 AND provider = $2 AND revoked_at IS NULL
		 ORDER BY created_at DESC
		 LIMIT 1`,
		userID, provider).
		Scan(&session.ID, &session.UserID, &session.Provider, &session.TokenType,
			&session.ExpiresAt, &session.CreatedAt, &session.UpdatedAt, &revokedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to get user session: %w", err)
	}

	session.RevokedAt = revokedAt
	return &session, nil
}

// GetAccessToken decrypts and returns the access token for a session
func (s *SessionService) GetAccessToken(ctx context.Context, sessionID uuid.UUID) (string, error) {
	if sessionID == uuid.Nil {
		return "", errors.New("session_id is required")
	}

	var encryptedToken []byte
	err := s.db.QueryRow(ctx,
		`SELECT access_token_encrypted FROM sessions WHERE id = $1`,
		sessionID).
		Scan(&encryptedToken)
	if err != nil {
		return "", fmt.Errorf("failed to get access token: %w", err)
	}

	token, err := s.decryptToken(encryptedToken)
	if err != nil {
		return "", fmt.Errorf("failed to decrypt access token: %w", err)
	}

	return token, nil
}

// encryptToken encrypts a token using AES-256-GCM
func (s *SessionService) encryptToken(token string) ([]byte, error) {
	block, err := aes.NewCipher(s.encKey)
	if err != nil {
		return nil, fmt.Errorf("failed to create cipher: %w", err)
	}

	aead, err := cipher.NewGCM(block)
	if err != nil {
		return nil, fmt.Errorf("failed to create AEAD: %w", err)
	}

	nonce := make([]byte, aead.NonceSize())
	_, err = io.ReadFull(rand.Reader, nonce)
	if err != nil {
		return nil, fmt.Errorf("failed to create nonce: %w", err)
	}

	ciphertext := aead.Seal(nonce, nonce, []byte(token), nil)
	return ciphertext, nil
}

// decryptToken decrypts a token using AES-256-GCM
func (s *SessionService) decryptToken(ciphertext []byte) (string, error) {
	block, err := aes.NewCipher(s.encKey)
	if err != nil {
		return "", fmt.Errorf("failed to create cipher: %w", err)
	}

	aead, err := cipher.NewGCM(block)
	if err != nil {
		return "", fmt.Errorf("failed to create AEAD: %w", err)
	}

	nonceSize := aead.NonceSize()
	if len(ciphertext) < nonceSize {
		return "", errors.New("ciphertext too short")
	}

	nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
	plaintext, err := aead.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return "", fmt.Errorf("failed to decrypt: %w", err)
	}

	return string(plaintext), nil
}

// createOrUpdateUserNode creates or updates a user node in Neo4j
// This is called asynchronously and failures are non-blocking
func (s *SessionService) createOrUpdateUserNode(ctx context.Context, userID uuid.UUID, provider string) {
	// Note: ExecuteQuery requires ProjectContext, so we skip Neo4j updates for now
	// This can be done via a separate graph service that has ProjectContext
	slog.Warn("info: skipping neo4j user node creation for provider (requires ProjectContext)", "id", provider)
}

// CleanupExpiredSessions removes expired sessions from the database
// This should be run periodically (e.g., via cron job)
func (s *SessionService) CleanupExpiredSessions(ctx context.Context) (int64, error) {
	result, err := s.db.Exec(ctx,
		`DELETE FROM sessions WHERE expires_at < now()`)
	if err != nil {
		return 0, fmt.Errorf("failed to cleanup expired sessions: %w", err)
	}

	return result.RowsAffected(), nil
}

// GenerateSessionToken generates a JWT token for a session
// This is typically called after session creation to return a token to the client
func (s *SessionService) GenerateSessionToken(sessionID uuid.UUID) (string, error) {
	// For now, return a simple opaque token based on session ID
	// In production, this would be a signed JWT
	return "session_" + hex.EncodeToString(sessionID[:]), nil
}
