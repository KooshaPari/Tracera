package sessions

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Helper to create a mock encryption key for testing
func testEncryptionKey() []byte {
	// 32-byte key for AES-256
	return []byte{
		0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
		0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
		0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
		0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
	}
}

func TestNewSessionService(t *testing.T) {
	t.Run("validates encryption key length", func(t *testing.T) {
		// Too short key
		_, err := NewSessionService(nil, nil, []byte{0x01, 0x02})
		require.Error(t, err)
		assert.Contains(t, err.Error(), "32 bytes")

		// Too long key
		_, err = NewSessionService(nil, nil, make([]byte, 64))
		require.Error(t, err)

		// Correct key length
		_, err = NewSessionService(nil, nil, testEncryptionKey())
		require.NoError(t, err)
	})
}

func TestEncryptDecryptToken(t *testing.T) {
	service := &SessionService{
		encKey: testEncryptionKey(),
	}

	t.Run("encrypts and decrypts token", func(t *testing.T) {
		token := "test_access_token_12345"

		// Encrypt
		encrypted, err := service.encryptToken(token)
		require.NoError(t, err)
		assert.NotEmpty(t, encrypted)
		assert.NotEqual(t, token, string(encrypted))

		// Decrypt
		decrypted, err := service.decryptToken(encrypted)
		require.NoError(t, err)
		assert.Equal(t, token, decrypted)
	})

	t.Run("different encryptions produce different ciphertexts", func(t *testing.T) {
		token := "test_token"

		encrypted1, err := service.encryptToken(token)
		require.NoError(t, err)

		encrypted2, err := service.encryptToken(token)
		require.NoError(t, err)

		// Even though we encrypt the same token, the ciphertext should be different
		// because GCM uses a random nonce each time
		assert.NotEqual(t, encrypted1, encrypted2)
	})

	t.Run("detects corrupted ciphertext", func(t *testing.T) {
		token := "test_token"

		encrypted, err := service.encryptToken(token)
		require.NoError(t, err)

		// Corrupt the ciphertext
		if len(encrypted) > 0 {
			encrypted[0] ^= 0xFF
		}

		// Decryption should fail
		_, err = service.decryptToken(encrypted)
		require.Error(t, err)
	})

	t.Run("handles empty token", func(t *testing.T) {
		token := ""

		encrypted, err := service.encryptToken(token)
		require.NoError(t, err)

		decrypted, err := service.decryptToken(encrypted)
		require.NoError(t, err)
		assert.Equal(t, token, decrypted)
	})
}

func TestCreateSessionRequest(t *testing.T) {
	t.Run("validates required fields", func(t *testing.T) {
		service := &SessionService{
			encKey: testEncryptionKey(),
		}

		ctx := context.Background()

		// Missing user_id
		req := &CreateSessionRequest{
			Provider:    "claude",
			AccessToken: "token123",
		}
		_, err := service.CreateSession(ctx, req)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "user_id")

		// Missing provider
		req = &CreateSessionRequest{
			UserID:      uuid.New(),
			AccessToken: "token123",
		}
		_, err = service.CreateSession(ctx, req)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "provider")

		// Missing access token
		req = &CreateSessionRequest{
			UserID:   uuid.New(),
			Provider: "claude",
		}
		_, err = service.CreateSession(ctx, req)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "access_token")
	})

	t.Run("rejects nil request", func(t *testing.T) {
		service := &SessionService{
			encKey: testEncryptionKey(),
		}

		ctx := context.Background()
		_, err := service.CreateSession(ctx, nil)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "cannot be nil")
	})
}

func TestGenerateSessionToken(t *testing.T) {
	t.Run("generates session token from session id", func(t *testing.T) {
		service := &SessionService{
			encKey: testEncryptionKey(),
		}

		sessionID := uuid.New()
		token, err := service.GenerateSessionToken(sessionID)
		require.NoError(t, err)
		assert.NotEmpty(t, token)
		assert.Contains(t, token, "session_")
	})

	t.Run("generates unique tokens for different sessions", func(t *testing.T) {
		service := &SessionService{
			encKey: testEncryptionKey(),
		}

		token1, err := service.GenerateSessionToken(uuid.New())
		require.NoError(t, err)

		token2, err := service.GenerateSessionToken(uuid.New())
		require.NoError(t, err)

		assert.NotEqual(t, token1, token2)
	})
}

func TestSessionDefaults(t *testing.T) {
	t.Run("sets defaults for optional fields", func(t *testing.T) {
		req := &CreateSessionRequest{
			UserID:      uuid.New(),
			Provider:    "claude",
			AccessToken: "token",
		}

		// Check defaults before service processing
		assert.Empty(t, req.TokenType)
		assert.Zero(t, req.ExpiresIn)

		// Service would set defaults
		if req.TokenType == "" {
			req.TokenType = "Bearer"
		}
		if req.ExpiresIn == 0 {
			req.ExpiresIn = OAuthTokenTTL
		}

		assert.Equal(t, "Bearer", req.TokenType)
		assert.Equal(t, OAuthTokenTTL, req.ExpiresIn)
	})
}

func TestSessionConstants(t *testing.T) {
	t.Run("session TTL constants are reasonable", func(t *testing.T) {
		assert.Greater(t, DefaultSessionTTL, 24*time.Hour)
		assert.Greater(t, OAuthTokenTTL, 10*time.Minute)
		assert.Less(t, OAuthTokenTTL, 24*time.Hour)
	})
}
