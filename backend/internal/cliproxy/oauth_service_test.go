package cliproxy

import (
	"context"
	"net/http"
	"testing"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

func setupMockRedisForService(t *testing.T) *redis.Client {
	t.Helper()
	mockRedis, err := miniredis.Run()
	require.NoError(t, err)
	t.Cleanup(mockRedis.Close)

	return redis.NewClient(&redis.Options{
		Addr: mockRedis.Addr(),
	})
}

func TestNewOAuthService(t *testing.T) {
	t.Run("creates oauth service with dependencies", func(t *testing.T) {
		redisClient := setupMockRedisForService(t)
		stateManager := auth.NewStateTokenManager(redisClient)

		service := NewOAuthService(stateManager, nil, nil)

		assert.NotNil(t, service)
		assert.NotNil(t, service.stateManager)
	})
}

func TestHandleAuthorizeRequest(t *testing.T) {
	t.Run("generates authorization url with state token", func(t *testing.T) {
		redisClient := setupMockRedisForService(t)
		stateManager := auth.NewStateTokenManager(redisClient)
		service := NewOAuthService(stateManager, nil, nil)

		provider := &ProviderConfig{
			Name:         "claude",
			Type:         "anthropic",
			ClientID:     "test-client",
			ClientSecret: "test-secret",
			RedirectURI:  "http://localhost:8080/callback",
		}

		ctx := context.Background()
		resp, err := service.HandleAuthorizeRequest(ctx, provider)

		require.NoError(t, err)
		assert.NotNil(t, resp)
		assert.NotEmpty(t, resp.AuthorizationURL)
		assert.NotEmpty(t, resp.State)
		assert.Positive(t, resp.ExpiresIn)
	})

	t.Run("includes correct query parameters", func(t *testing.T) {
		redisClient := setupMockRedisForService(t)
		stateManager := auth.NewStateTokenManager(redisClient)
		service := NewOAuthService(stateManager, nil, nil)

		provider := &ProviderConfig{
			Name:         "claude",
			Type:         "anthropic",
			ClientID:     "test-client",
			ClientSecret: "test-secret",
			RedirectURI:  "http://localhost:8080/callback",
		}

		ctx := context.Background()
		resp, err := service.HandleAuthorizeRequest(ctx, provider)

		require.NoError(t, err)
		assert.Contains(t, resp.AuthorizationURL, "client_id=test-client")
		assert.Contains(t, resp.AuthorizationURL, "redirect_uri=http://localhost:8080/callback")
		assert.Contains(t, resp.AuthorizationURL, "response_type=code")
		assert.Contains(t, resp.AuthorizationURL, "state=")
	})

	t.Run("rejects nil provider", func(t *testing.T) {
		redisClient := setupMockRedisForService(t)
		stateManager := auth.NewStateTokenManager(redisClient)
		service := NewOAuthService(stateManager, nil, nil)

		ctx := context.Background()
		_, err := service.HandleAuthorizeRequest(ctx, nil)

		assert.Error(t, err)
	})
}

func TestBuildAuthorizationURL(t *testing.T) {
	t.Run("builds correct anthropic url", func(t *testing.T) {
		provider := &ProviderConfig{
			Type:        "anthropic",
			ClientID:    "test-id",
			RedirectURI: "http://localhost/callback",
		}

		url := buildAuthorizationURL(provider, "state123")

		assert.Contains(t, url, "https://api.anthropic.com/oauth/authorize")
		assert.Contains(t, url, "client_id=test-id")
		assert.Contains(t, url, "state=state123")
	})

	t.Run("builds correct openai url", func(t *testing.T) {
		provider := &ProviderConfig{
			Type:        "openai",
			ClientID:    "test-id",
			RedirectURI: "http://localhost/callback",
		}

		url := buildAuthorizationURL(provider, "state123")

		assert.Contains(t, url, "https://oauth.openai.com/authorize")
	})

	t.Run("uses custom base url if provided", func(t *testing.T) {
		provider := &ProviderConfig{
			Type:        "custom",
			BaseURL:     "https://custom.oauth.com",
			ClientID:    "test-id",
			RedirectURI: "http://localhost/callback",
		}

		url := buildAuthorizationURL(provider, "state123")

		assert.Contains(t, url, "https://custom.oauth.com/authorize")
	})
}

func TestGetAuthorizationEndpoint(t *testing.T) {
	t.Run("returns anthropic endpoint", func(t *testing.T) {
		provider := &ProviderConfig{Type: "anthropic"}
		endpoint := getAuthorizationEndpoint(provider)
		assert.Contains(t, endpoint, "api.anthropic.com")
	})

	t.Run("returns openai endpoint", func(t *testing.T) {
		provider := &ProviderConfig{Type: "openai"}
		endpoint := getAuthorizationEndpoint(provider)
		assert.Contains(t, endpoint, "oauth.openai.com")
	})

	t.Run("returns custom endpoint if set", func(t *testing.T) {
		provider := &ProviderConfig{
			Type:    "custom",
			BaseURL: "https://custom.com",
		}
		endpoint := getAuthorizationEndpoint(provider)
		assert.Equal(t, "https://custom.com/authorize", endpoint)
	})
}

func TestGetTokenEndpoint(t *testing.T) {
	t.Run("returns anthropic endpoint", func(t *testing.T) {
		provider := &ProviderConfig{Type: "anthropic"}
		endpoint := getTokenEndpoint(provider)
		assert.Contains(t, endpoint, "api.anthropic.com")
	})

	t.Run("returns openai endpoint", func(t *testing.T) {
		provider := &ProviderConfig{Type: "openai"}
		endpoint := getTokenEndpoint(provider)
		assert.Contains(t, endpoint, "oauth.openai.com")
	})

	t.Run("returns custom endpoint if set", func(t *testing.T) {
		provider := &ProviderConfig{
			Type:    "custom",
			BaseURL: "https://custom.com",
		}
		endpoint := getTokenEndpoint(provider)
		assert.Equal(t, "https://custom.com/token", endpoint)
	})
}

func TestGenerateUserIDFromToken(t *testing.T) {
	t.Run("generates deterministic user id", func(t *testing.T) {
		id1 := generateUserIDFromToken("claude", "code123")
		id2 := generateUserIDFromToken("claude", "code123")

		assert.Equal(t, id1, id2)
	})

	t.Run("generates different ids for different codes", func(t *testing.T) {
		id1 := generateUserIDFromToken("claude", "code123")
		id2 := generateUserIDFromToken("claude", "code456")

		assert.NotEqual(t, id1, id2)
	})

	t.Run("generates different ids for different providers", func(t *testing.T) {
		id1 := generateUserIDFromToken("claude", "code123")
		id2 := generateUserIDFromToken("openai", "code123")

		assert.NotEqual(t, id1, id2)
	})

	t.Run("generates valid uuid", func(t *testing.T) {
		id := generateUserIDFromToken("claude", "code123")

		assert.NotNil(t, id)
		assert.NotEqual(t, [16]byte{}, id)
	})
}

func TestNewOAuthError(t *testing.T) {
	t.Run("creates error with correct status code for invalid_request", func(t *testing.T) {
		err := NewOAuthError("invalid_request", "something is missing", "state123")

		assert.Equal(t, "invalid_request", err.ErrorCode)
		assert.Equal(t, http.StatusBadRequest, err.StatusCode)
		assert.Equal(t, "state123", err.State)
	})

	t.Run("creates error with correct status code for invalid_code", func(t *testing.T) {
		err := NewOAuthError("invalid_code", "code is invalid", "state123")

		assert.Equal(t, "invalid_code", err.ErrorCode)
		assert.Equal(t, http.StatusBadRequest, err.StatusCode)
	})

	t.Run("creates error with correct status code for server_error", func(t *testing.T) {
		err := NewOAuthError("server_error", "something went wrong", "state123")

		assert.Equal(t, "server_error", err.ErrorCode)
		assert.Equal(t, http.StatusInternalServerError, err.StatusCode)
	})

	t.Run("creates error with correct status code for unauthorized_client", func(t *testing.T) {
		err := NewOAuthError("unauthorized_client", "not authorized", "state123")

		assert.Equal(t, "unauthorized_client", err.ErrorCode)
		assert.Equal(t, http.StatusUnauthorized, err.StatusCode)
	})
}
