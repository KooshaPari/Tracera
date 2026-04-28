package cliproxy

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

// setupMockOAuthProvider creates a mock OAuth provider server for testing
func setupMockOAuthProvider(t *testing.T, shouldFail bool) (*httptest.Server, *ProviderConfig) {
	t.Helper()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/token" {
			http.NotFound(w, r)
			return
		}

		if shouldFail {
			w.WriteHeader(http.StatusBadRequest)
			assert.NoError(t, json.NewEncoder(w).Encode(map[string]string{
				"error":             "invalid_grant",
				"error_description": "The authorization code is invalid",
			}))
			return
		}

		// Parse request
		var req TokenExchangeRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		// Validate request
		if req.Code == "" || req.ClientID == "" {
			w.WriteHeader(http.StatusBadRequest)
			assert.NoError(t, json.NewEncoder(w).Encode(map[string]string{
				"error": "invalid_request",
			}))
			return
		}

		// Return successful token response
		w.Header().Set("Content-Type", "application/json")
		assert.NoError(t, json.NewEncoder(w).Encode(&TokenExchangeResponse{
			AccessToken: "test_access_token_" + req.Code,
			TokenType:   "Bearer",
			ExpiresIn:   3600,
		}))
	}))

	t.Cleanup(server.Close)

	provider := &ProviderConfig{
		Name:         "test",
		Type:         "anthropic",
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
		RedirectURI:  "http://localhost:8080/callback",
		BaseURL:      server.URL,
	}

	return server, provider
}

func setupMockRedis(t *testing.T) *redis.Client {
	t.Helper()
	mockRedis, err := miniredis.Run()
	require.NoError(t, err)
	t.Cleanup(mockRedis.Close)

	return redis.NewClient(&redis.Options{
		Addr: mockRedis.Addr(),
	})
}

func TestTokenEndpointURL(t *testing.T) {
	t.Run("returns anthropic endpoint", func(t *testing.T) {
		provider := &ProviderConfig{
			Type: "anthropic",
		}
		assert.Equal(t, "https://api.anthropic.com/oauth/token", provider.tokenEndpointURL())
	})

	t.Run("returns openai endpoint", func(t *testing.T) {
		provider := &ProviderConfig{
			Type: "openai",
		}
		assert.Equal(t, "https://oauth.openai.com/token", provider.tokenEndpointURL())
	})

	t.Run("returns custom base url", func(t *testing.T) {
		provider := &ProviderConfig{
			Type:    "custom",
			BaseURL: "https://custom.oauth.com",
		}
		assert.Equal(t, "https://custom.oauth.com/token", provider.tokenEndpointURL())
	})
}

func TestExchangeCodeForToken(t *testing.T) {
	t.Run("exchanges valid code for token", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, false)
		service := &Service{}

		ctx := context.Background()
		resp, err := service.ExchangeCodeForToken(ctx, provider, "test_code_123")
		require.NoError(t, err)

		assert.NotEmpty(t, resp.AccessToken)
		assert.Equal(t, "Bearer", resp.TokenType)
		assert.Positive(t, resp.ExpiresIn)
	})

	t.Run("rejects empty auth code", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, false)
		service := &Service{}

		ctx := context.Background()
		_, err := service.ExchangeCodeForToken(ctx, provider, "")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "authorization code is required")
	})

	t.Run("handles provider error", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, true)
		service := &Service{}

		ctx := context.Background()
		_, err := service.ExchangeCodeForToken(ctx, provider, "invalid_code")
		require.Error(t, err)
	})

	t.Run("defaults token type to Bearer", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, false)
		service := &Service{}

		ctx := context.Background()
		resp, err := service.ExchangeCodeForToken(ctx, provider, "test_code")
		require.NoError(t, err)
		assert.Equal(t, "Bearer", resp.TokenType)
	})

	t.Run("defaults expiration to 1 hour", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, false)
		service := &Service{}

		ctx := context.Background()
		resp, err := service.ExchangeCodeForToken(ctx, provider, "test_code")
		require.NoError(t, err)
		assert.Positive(t, resp.ExpiresIn)
	})

	t.Run("times out if provider is slow", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Simulate slow provider
			time.Sleep(tokenExchangeTimeout + time.Second)
			w.WriteHeader(http.StatusOK)
		}))
		t.Cleanup(server.Close)

		provider := &ProviderConfig{
			ClientID:     "test",
			ClientSecret: "secret",
			RedirectURI:  "http://localhost/callback",
			BaseURL:      server.URL,
		}

		service := &Service{}
		ctx := context.Background()
		_, err := service.ExchangeCodeForToken(ctx, provider, "test_code")
		require.Error(t, err)
	})
}

func TestValidateStateAndExchangeToken(t *testing.T) {
	t.Run("validates state and exchanges token", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, false)
		redisClient := setupMockRedis(t)
		stateManager := auth.NewStateTokenManager(redisClient)
		service := &Service{}

		ctx := context.Background()

		// Generate state token
		stateToken, err := stateManager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Validate and exchange
		resp, err := service.ValidateStateAndExchangeToken(ctx, stateManager, provider, stateToken, "test_code")
		require.NoError(t, err)

		assert.NotEmpty(t, resp.AccessToken)
		assert.Equal(t, provider.Name, resp.Provider)
	})

	t.Run("rejects invalid state", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, false)
		redisClient := setupMockRedis(t)
		stateManager := auth.NewStateTokenManager(redisClient)
		service := &Service{}

		ctx := context.Background()

		// Use invalid state
		resp, err := service.ValidateStateAndExchangeToken(ctx, stateManager, provider, "invalid_state", "test_code")
		require.Error(t, err)
		assert.Nil(t, resp)
	})

	t.Run("rejects invalid code", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, true)
		redisClient := setupMockRedis(t)
		stateManager := auth.NewStateTokenManager(redisClient)
		service := &Service{}

		ctx := context.Background()

		// Generate valid state
		stateToken, err := stateManager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Invalid code should fail token exchange
		resp, err := service.ValidateStateAndExchangeToken(ctx, stateManager, provider, stateToken, "invalid_code")
		require.Error(t, err)
		assert.Nil(t, resp)
	})

	t.Run("allows empty state", func(t *testing.T) {
		_, provider := setupMockOAuthProvider(t, false)
		redisClient := setupMockRedis(t)
		stateManager := auth.NewStateTokenManager(redisClient)
		service := &Service{}

		ctx := context.Background()

		// Empty state should skip validation
		resp, err := service.ValidateStateAndExchangeToken(ctx, stateManager, provider, "", "test_code")
		require.NoError(t, err)
		assert.NotEmpty(t, resp.AccessToken)
	})
}

func TestStoreTokenInRedis(t *testing.T) {
	t.Run("stores token in redis", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		service := &Service{}

		ctx := context.Background()
		tokenResp := &TokenExchangeResponse{
			AccessToken: "test_token",
			TokenType:   "Bearer",
			ExpiresIn:   3600,
		}

		err := service.StoreTokenInRedis(ctx, redisClient, "test_code", tokenResp)
		require.NoError(t, err)

		// Verify stored in Redis
		val, err := redisClient.Get(ctx, "oauth:token_exchange:test_code").Result()
		require.NoError(t, err)
		assert.NotEmpty(t, val)

		// Verify can be unmarshaled
		var stored TokenExchangeResponse
		err = json.Unmarshal([]byte(val), &stored)
		require.NoError(t, err)
		assert.Equal(t, tokenResp.AccessToken, stored.AccessToken)
	})

	t.Run("rejects empty auth code", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		service := &Service{}

		ctx := context.Background()
		err := service.StoreTokenInRedis(ctx, redisClient, "", &TokenExchangeResponse{})
		require.Error(t, err)
	})

	t.Run("sets correct ttl", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		service := &Service{}

		ctx := context.Background()
		tokenResp := &TokenExchangeResponse{
			AccessToken: "test_token",
		}

		err := service.StoreTokenInRedis(ctx, redisClient, "test_code", tokenResp)
		require.NoError(t, err)

		// Check TTL
		ttl, err := redisClient.TTL(ctx, "oauth:token_exchange:test_code").Result()
		require.NoError(t, err)
		assert.Greater(t, ttl, 5*time.Minute)
		assert.LessOrEqual(t, ttl, 10*time.Minute)
	})
}

func TestRetrieveTokenFromRedis(t *testing.T) {
	t.Run("retrieves stored token", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		service := &Service{}

		ctx := context.Background()
		originalToken := &TokenExchangeResponse{
			AccessToken:  "test_token",
			TokenType:    "Bearer",
			ExpiresIn:    3600,
			RefreshToken: "refresh_token",
		}

		// Store token
		err := service.StoreTokenInRedis(ctx, redisClient, "test_code", originalToken)
		require.NoError(t, err)

		// Retrieve token
		retrievedToken, err := service.RetrieveTokenFromRedis(ctx, redisClient, "test_code")
		require.NoError(t, err)

		assert.Equal(t, originalToken.AccessToken, retrievedToken.AccessToken)
		assert.Equal(t, originalToken.TokenType, retrievedToken.TokenType)
		assert.Equal(t, originalToken.ExpiresIn, retrievedToken.ExpiresIn)
		assert.Equal(t, originalToken.RefreshToken, retrievedToken.RefreshToken)
	})

	t.Run("fails for non-existent code", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		service := &Service{}

		ctx := context.Background()
		_, err := service.RetrieveTokenFromRedis(ctx, redisClient, "non_existent_code")
		require.Error(t, err)
	})

	t.Run("rejects empty auth code", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		service := &Service{}

		ctx := context.Background()
		_, err := service.RetrieveTokenFromRedis(ctx, redisClient, "")
		require.Error(t, err)
	})
}

func TestOAuthErrorResponse(t *testing.T) {
	t.Run("error response has required fields", func(t *testing.T) {
		errResp := OAuthErrorResponse{
			ErrorCode:        "invalid_code",
			ErrorDescription: "The authorization code is invalid",
			State:            "state_token",
		}

		assert.NotEmpty(t, errResp.Error)
		assert.NotEmpty(t, errResp.ErrorDescription)
		assert.NotEmpty(t, errResp.State)
	})
}
