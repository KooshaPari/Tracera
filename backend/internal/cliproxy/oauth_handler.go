package cliproxy

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

const (
	// OAuth token endpoint request timeout
	tokenExchangeTimeout = 10 * time.Second
	tokenCacheTTL        = 10 * time.Minute

	// Default expiration to 1 hour if not specified by the provider.
	defaultTokenExpirySeconds = 3600

	// Token exchange error codes (RFC 6749)
	errorInvalidCode          = "invalid_code"
	errorInvalidState         = "invalid_state"
	errorUnauthorizedClient   = "unauthorized_client"
	errorServerError          = "server_error"
	errorUnsupportedGrantType = "unsupported_grant_type"
)

// TokenExchangeRequest is sent to the OAuth provider's token endpoint
type TokenExchangeRequest struct {
	GrantType    string `json:"grant_type"`
	Code         string `json:"code"`
	ClientID     string `json:"client_id"`
	ClientSecret string `json:"client_secret"`
	RedirectURI  string `json:"redirect_uri"`
}

// TokenExchangeResponse is returned from the OAuth provider
type TokenExchangeResponse struct {
	AccessToken  string `json:"access_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
	RefreshToken string `json:"refresh_token,omitempty"`
	Scope        string `json:"scope,omitempty"`
	IDToken      string `json:"id_token,omitempty"`
}

// OAuthCallbackResponse is returned to the client after successful token exchange
type OAuthCallbackResponse struct {
	AccessToken  string `json:"access_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
	RefreshToken string `json:"refresh_token,omitempty"`
	Provider     string `json:"provider"`
	State        string `json:"state"`
	SessionID    string `json:"session_id,omitempty"`
}

// OAuthErrorResponse follows RFC 6749 error format
type OAuthErrorResponse struct {
	ErrorCode        string `json:"error_code"`
	ErrorDescription string `json:"error_description,omitempty"`
	ErrorURI         string `json:"error_uri,omitempty"`
	State            string `json:"state,omitempty"`
	StatusCode       int    `json:"-"`
}

// UnmarshalJSON accepts both `error` (RFC 6749) and `error_code` (internal convention).
// The struct tag stays `error_code` to satisfy tagliatelle.
func (errResp *OAuthErrorResponse) UnmarshalJSON(data []byte) error {
	type oauthErrWire struct {
		Error            string `json:"error"`
		ErrorCode        string `json:"error_code"`
		ErrorDescription string `json:"error_description,omitempty"`
		ErrorURI         string `json:"error_uri,omitempty"`
		State            string `json:"state,omitempty"`
	}

	var wire oauthErrWire
	if err := json.Unmarshal(data, &wire); err != nil {
		return err
	}

	errResp.ErrorCode = wire.ErrorCode
	if errResp.ErrorCode == "" {
		errResp.ErrorCode = wire.Error
	}
	errResp.ErrorDescription = wire.ErrorDescription
	errResp.ErrorURI = wire.ErrorURI
	errResp.State = wire.State
	return nil
}

// Error implements the error interface
func (errResp *OAuthErrorResponse) Error() string {
	if errResp.ErrorDescription != "" {
		return fmt.Sprintf("%s: %s", errResp.ErrorCode, errResp.ErrorDescription)
	}
	return errResp.ErrorCode
}

// tokenEndpointURL returns the token endpoint URL for a provider
func (provider *ProviderConfig) tokenEndpointURL() string {
	if provider.BaseURL != "" {
		return provider.BaseURL + "/token"
	}

	// Default token endpoints by provider type
	switch provider.Type {
	case anthropicProviderType:
		return "https://api.anthropic.com/oauth/token"
	case openAIProviderType, codexProviderType:
		return "https://oauth.openai.com/token"
	default:
		return "https://example.com/oauth/token"
	}
}

// ExchangeCodeForToken implements RFC 6749 authorization code grant flow
// This exchanges an authorization code for an access token by calling the provider's token endpoint
func (service *Service) ExchangeCodeForToken(
	ctx context.Context,
	provider *ProviderConfig,
	authCode string,
) (*TokenExchangeResponse, error) {
	if authCode == "" {
		return nil, errors.New("authorization code is required")
	}

	// Build token exchange request
	tokenReq := TokenExchangeRequest{
		GrantType:    "authorization_code",
		Code:         authCode,
		ClientID:     provider.ClientID,
		ClientSecret: provider.ClientSecret,
		RedirectURI:  provider.RedirectURI,
	}

	// Marshal request body
	reqBody, err := json.Marshal(tokenReq)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal token request: %w", err)
	}

	return service.executeTokenExchange(ctx, provider, reqBody)
}

func (service *Service) executeTokenExchange(
	ctx context.Context,
	provider *ProviderConfig,
	reqBody []byte,
) (token *TokenExchangeResponse, retErr error) {
	// Create HTTP request with timeout
	tokenCtx, cancel := context.WithTimeout(ctx, tokenExchangeTimeout)
	defer cancel()

	httpReq, err := http.NewRequestWithContext(
		tokenCtx,
		http.MethodPost,
		provider.tokenEndpointURL(),
		bytes.NewReader(reqBody),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create token request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Accept", "application/json")

	// Send request
	client := &http.Client{
		Timeout: tokenExchangeTimeout,
	}

	resp, err := client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("failed to exchange code for token: %w", err)
	}
	defer func() {
		if closeErr := resp.Body.Close(); closeErr != nil {
			if retErr != nil {
				retErr = errors.Join(retErr, fmt.Errorf("failed to close token response body: %w", closeErr))
				return
			}
			retErr = fmt.Errorf("failed to close token response body: %w", closeErr)
		}
	}()

	// Read response body
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read token response: %w", err)
	}

	token, retErr = service.parseTokenResponse(resp, respBody)
	return token, retErr
}

func (service *Service) parseTokenResponse(resp *http.Response, respBody []byte) (*TokenExchangeResponse, error) {
	// Check HTTP status
	if resp.StatusCode != http.StatusOK {
		var oauthErr OAuthErrorResponse
		if err := json.Unmarshal(respBody, &oauthErr); err == nil && oauthErr.ErrorCode != "" {
			oauthErr.StatusCode = resp.StatusCode
			return nil, fmt.Errorf("token endpoint error (%d): %w", resp.StatusCode, &oauthErr)
		}
		return nil, fmt.Errorf("token endpoint returned %d: %s", resp.StatusCode, string(respBody))
	}

	// Parse successful response
	var tokenResp TokenExchangeResponse
	if err := json.Unmarshal(respBody, &tokenResp); err != nil {
		return nil, fmt.Errorf("failed to parse token response: %w", err)
	}

	// Validate required fields
	if tokenResp.AccessToken == "" {
		return nil, errors.New("token response missing access_token")
	}

	if tokenResp.TokenType == "" {
		tokenResp.TokenType = "Bearer"
	}

	// Default expiration to 1 hour if not specified
	if tokenResp.ExpiresIn == 0 {
		tokenResp.ExpiresIn = defaultTokenExpirySeconds
	}

	return &tokenResp, nil
}

// ValidateStateAndExchangeToken is the full callback flow:
// 1. Validate state parameter (CSRF protection)
// 2. Exchange authorization code for token
// 3. Return token to client
func (service *Service) ValidateStateAndExchangeToken(
	ctx context.Context,
	stateManager *auth.StateTokenManager,
	provider *ProviderConfig,
	state string,
	authCode string,
) (*OAuthCallbackResponse, error) {
	// Step 1: Validate state parameter
	if state != "" {
		if err := stateManager.ValidateStateToken(ctx, state); err != nil {
			return nil, fmt.Errorf("%s: %w", errorInvalidState, err)
		}
	}

	// Step 2: Exchange code for token
	tokenResp, err := service.ExchangeCodeForToken(ctx, provider, authCode)
	if err != nil {
		return nil, fmt.Errorf("%s: %w", errorInvalidCode, err)
	}

	// Step 3: Return response
	return &OAuthCallbackResponse{
		AccessToken:  tokenResp.AccessToken,
		TokenType:    tokenResp.TokenType,
		ExpiresIn:    tokenResp.ExpiresIn,
		RefreshToken: tokenResp.RefreshToken,
		Provider:     provider.Name,
		State:        state,
		SessionID:    "",
	}, nil
}

// StoreTokenInRedis temporarily caches the token exchange result in Redis
// This is useful for the client to retrieve the token if they miss the initial response
func (service *Service) StoreTokenInRedis(
	ctx context.Context,
	redisClient *redis.Client,
	authCode string,
	tokenResp *TokenExchangeResponse,
) error {
	if authCode == "" {
		return errors.New("auth code is required")
	}

	tokenData, err := json.Marshal(tokenResp)
	if err != nil {
		return fmt.Errorf("failed to marshal token response: %w", err)
	}

	// Store for 10 minutes (token exchange must complete within this time)
	redisKey := "oauth:token_exchange:" + authCode
	if err := redisClient.Set(ctx, redisKey, tokenData, tokenCacheTTL).Err(); err != nil {
		return fmt.Errorf("failed to store token in redis: %w", err)
	}

	return nil
}

// RetrieveTokenFromRedis retrieves a cached token response from Redis
func (service *Service) RetrieveTokenFromRedis(
	ctx context.Context,
	redisClient *redis.Client,
	authCode string,
) (*TokenExchangeResponse, error) {
	if authCode == "" {
		return nil, errors.New("auth code is required")
	}

	redisKey := "oauth:token_exchange:" + authCode
	tokenData, err := redisClient.Get(ctx, redisKey).Result()
	if err != nil {
		return nil, fmt.Errorf("token not found in cache: %w", err)
	}

	var tokenResp TokenExchangeResponse
	if err := json.Unmarshal([]byte(tokenData), &tokenResp); err != nil {
		return nil, fmt.Errorf("failed to parse cached token: %w", err)
	}

	return &tokenResp, nil
}
