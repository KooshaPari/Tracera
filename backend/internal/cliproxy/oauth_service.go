package cliproxy

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/kooshapari/tracertm-backend/internal/sessions"
)

const authorizeStateExpiresInSeconds = 600 // 10 minutes

// OAuthService orchestrates OAuth authorization code flow
// Coordinates: StateTokenManager, OAuthHandler, and SessionService
type OAuthService struct {
	stateManager   *auth.StateTokenManager
	sessionService *sessions.SessionService
	eventPublisher *auth.EventPublisher
}

// NewOAuthService creates a new OAuth service
func NewOAuthService(
	stateManager *auth.StateTokenManager,
	sessionService *sessions.SessionService,
	eventPublisher *auth.EventPublisher,
) *OAuthService {
	return &OAuthService{
		stateManager:   stateManager,
		sessionService: sessionService,
		eventPublisher: eventPublisher,
	}
}

// HandleAuthorizeRequest generates an OAuth authorization URL with state token
// GET /oauth/authorize?provider=claude
func (svc *OAuthService) HandleAuthorizeRequest(
	ctx context.Context,
	provider *ProviderConfig,
) (*AuthorizeResponse, error) {
	if provider == nil {
		return nil, errors.New("provider config is required")
	}

	// Generate state token for CSRF protection
	stateToken, err := svc.stateManager.GenerateStateToken(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to generate state token: %w", err)
	}

	// Publish login started event
	if svc.eventPublisher != nil {
		if err := svc.eventPublisher.PublishOAuthLoginStarted(ctx, provider.Name, stateToken); err != nil {
			slog.Error("Failed to publish OAuth login started event", "error", err)
		}
	}

	// Build authorization URL
	authURL := buildAuthorizationURL(provider, stateToken)

	return &AuthorizeResponse{
		AuthorizationURL: authURL,
		State:            stateToken,
		ExpiresIn:        authorizeStateExpiresInSeconds,
	}, nil
}

// HandleCallbackRequest processes OAuth callback with authorization code
// GET /oauth/callback?code=AUTH_CODE&state=STATE&provider=claude
func (svc *OAuthService) HandleCallbackRequest(
	ctx context.Context,
	provider *ProviderConfig,
	authCode string,
	state string,
) (*CallbackResponse, error) {
	if provider == nil {
		return nil, errors.New("provider config is required")
	}

	if authCode == "" {
		return nil, errors.New("authorization code is required")
	}

	// Step 1: Validate state parameter (CSRF protection)
	if err := svc.validateState(ctx, state, provider.Name); err != nil {
		return nil, err
	}

	// Step 2: Exchange authorization code for access token
	tokenResp, err := svc.exchangeCode(ctx, provider, authCode)
	if err != nil {
		return nil, err
	}

	// Step 3: Extract user ID from token
	userID := generateUserIDFromToken(provider.Name, authCode)

	// Step 4: Create session
	sessionResp, err := svc.createSession(ctx, userID, provider.Name, tokenResp)
	if err != nil {
		return nil, err
	}

	// Step 5: Generate session token
	sessionToken, err := svc.sessionService.GenerateSessionToken(sessionResp.SessionID)
	if err != nil {
		svc.handleFinalError(ctx, userID, provider.Name, authCode, "session token generation failed", err)
		return nil, fmt.Errorf("failed to generate session token: %w", err)
	}

	svc.logCallbackSuccess(authCode, provider.Name, userID, sessionResp.SessionID)

	return &CallbackResponse{
		AccessToken:  tokenResp.AccessToken,
		TokenType:    tokenResp.TokenType,
		ExpiresIn:    tokenResp.ExpiresIn,
		RefreshToken: tokenResp.RefreshToken,
		SessionID:    sessionResp.SessionID.String(),
		SessionToken: sessionToken,
		Provider:     provider.Name,
	}, nil
}

func (svc *OAuthService) validateState(
	ctx context.Context,
	state string,
	providerName string,
) error {
	if state != "" {
		if err := svc.stateManager.ValidateStateToken(ctx, state); err != nil {
			logSecurityEvent("oauth_invalid_state", state, providerName, "state validation failed", nil)
			return fmt.Errorf("invalid state parameter: %w", err)
		}
	}
	return nil
}

func (svc *OAuthService) exchangeCode(
	ctx context.Context,
	provider *ProviderConfig,
	authCode string,
) (*TokenExchangeResponse, error) {
	tokenResp, err := exchangeCodeForToken(ctx, provider, authCode)
	if err != nil {
		logSecurityEvent("oauth_token_exchange_failed", authCode, provider.Name, err.Error(), nil)
		if svc.eventPublisher != nil {
			if pubErr := svc.eventPublisher.PublishOAuthError(
				ctx,
				"unknown",
				provider.Name,
				"token exchange failed",
			); pubErr != nil {
				slog.Error("Failed to publish OAuth error event", "error", pubErr)
			}
		}
		return nil, fmt.Errorf("failed to exchange authorization code: %w", err)
	}

	if svc.eventPublisher != nil {
		if pubErr := svc.eventPublisher.PublishOAuthCallbackReceived(
			ctx,
			provider.Name,
			authCode,
		); pubErr != nil {
			slog.Error("Failed to publish OAuth callback received event", "error", pubErr)
		}
	}
	return tokenResp, nil
}

func (svc *OAuthService) createSession(
	ctx context.Context,
	userID uuid.UUID,
	providerName string,
	tokenResp *TokenExchangeResponse,
) (*sessions.CreateSessionResponse, error) {
	sessionReq := &sessions.CreateSessionRequest{
		UserID:       userID,
		Provider:     providerName,
		AccessToken:  tokenResp.AccessToken,
		RefreshToken: tokenResp.RefreshToken,
		TokenType:    tokenResp.TokenType,
		ExpiresIn:    time.Duration(tokenResp.ExpiresIn) * time.Second,
	}

	sessionResp, err := svc.sessionService.CreateSession(ctx, sessionReq)
	if err != nil {
		logSecurityEvent("oauth_session_creation_failed", userID.String(), providerName, err.Error(), nil)
		if svc.eventPublisher != nil {
			if pubErr := svc.eventPublisher.PublishOAuthError(
				ctx,
				userID.String(),
				providerName,
				"session creation failed",
			); pubErr != nil {
				slog.Error("Failed to publish OAuth error event", "error", pubErr)
			}
		}
		return nil, fmt.Errorf("failed to create session: %w", err)
	}

	if svc.eventPublisher != nil {
		if pubErr := svc.eventPublisher.PublishOAuthTokenExchanged(
			ctx,
			providerName,
			userID.String(),
		); pubErr != nil {
			slog.Error("Failed to publish OAuth token exchanged event", "error", pubErr)
		}
		if pubErr := svc.eventPublisher.PublishOAuthSessionCreated(
			ctx,
			userID.String(),
			sessionResp.SessionID.String(),
		); pubErr != nil {
			slog.Error("Failed to publish OAuth session created event", "error", pubErr)
		}
	}
	return sessionResp, nil
}

func (svc *OAuthService) handleFinalError(
	ctx context.Context,
	userID uuid.UUID,
	providerName string,
	authCode string,
	msg string,
	err error,
) {
	logSecurityEvent("oauth_final_error", authCode, providerName, err.Error(), nil)
	if svc.eventPublisher != nil {
		if pubErr := svc.eventPublisher.PublishOAuthError(
			ctx,
			userID.String(),
			providerName,
			msg,
		); pubErr != nil {
			slog.Error("Failed to publish OAuth error event", "error", pubErr)
		}
	}
}

func (svc *OAuthService) logCallbackSuccess(
	authCode string,
	providerName string,
	userID uuid.UUID,
	sessionID uuid.UUID,
) {
	logSecurityEvent("oauth_callback_success", authCode, providerName, "session created", map[string]interface{}{
		"session_id": sessionID.String(),
		"user_id":    userID.String(),
	})
}

// AuthorizeResponse is returned from authorization request
type AuthorizeResponse struct {
	AuthorizationURL string `json:"authorization_url"`
	State            string `json:"state"`
	ExpiresIn        int    `json:"expires_in"` // seconds
}

// CallbackResponse is returned from callback request
type CallbackResponse struct {
	AccessToken  string `json:"access_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
	RefreshToken string `json:"refresh_token,omitempty"`
	SessionID    string `json:"session_id"`
	SessionToken string `json:"session_token"`
	Provider     string `json:"provider"`
}

// buildAuthorizationURL constructs the OAuth authorization URL with state
func buildAuthorizationURL(provider *ProviderConfig, state string) string {
	// Get authorization endpoint for provider
	authEndpoint := getAuthorizationEndpoint(provider)

	return fmt.Sprintf(
		"%s?client_id=%s&redirect_uri=%s&response_type=code&state=%s&scope=profile+email",
		authEndpoint,
		provider.ClientID,
		provider.RedirectURI,
		state,
	)
}

// getAuthorizationEndpoint returns the authorization endpoint for a provider
func getAuthorizationEndpoint(provider *ProviderConfig) string {
	switch provider.Type {
	case anthropicProviderType:
		return "https://api.anthropic.com/oauth/authorize"
	case openAIProviderType, codexProviderType:
		return "https://oauth.openai.com/authorize"
	default:
		if provider.BaseURL != "" {
			return provider.BaseURL + "/authorize"
		}
		return "https://example.com/oauth/authorize"
	}
}

// exchangeCodeForToken calls the OAuth provider to exchange code for token
func exchangeCodeForToken(
	ctx context.Context,
	provider *ProviderConfig,
	authCode string,
) (*TokenExchangeResponse, error) {
	tokenEndpoint := getTokenEndpoint(provider)

	// Build token exchange request
	tokenReq := TokenExchangeRequest{
		GrantType:    "authorization_code",
		Code:         authCode,
		ClientID:     provider.ClientID,
		ClientSecret: provider.ClientSecret,
		RedirectURI:  provider.RedirectURI,
	}

	// Use exchange function from oauth_handler.go
	// (This assumes a global or Service-level function exists)
	// For now, we'll implement a simple version here
	return executeTokenExchange(ctx, tokenEndpoint, &tokenReq)
}

// getTokenEndpoint returns the token endpoint for a provider
func getTokenEndpoint(provider *ProviderConfig) string {
	switch provider.Type {
	case anthropicProviderType:
		return "https://api.anthropic.com/oauth/token"
	case openAIProviderType, codexProviderType:
		return "https://oauth.openai.com/token"
	default:
		if provider.BaseURL != "" {
			return provider.BaseURL + "/token"
		}
		return "https://example.com/oauth/token"
	}
}

// executeTokenExchange performs the actual HTTP request to the provider
func executeTokenExchange(
	ctx context.Context,
	endpoint string,
	req *TokenExchangeRequest,
) (
	*TokenExchangeResponse,
	error,
) {
	// This is implemented in oauth_handler.go and called via Service
	// For the OAuthService, we delegate to the global handler
	// In production, this would be injected as a dependency

	// Placeholder for now - actual implementation in oauth_handler.go
	if endpoint == "" {
		return nil, errors.New("token endpoint is empty")
	}

	// Note: Real implementation would:
	// 1. Marshal TokenExchangeRequest to JSON
	// 2. POST to endpoint with timeout
	// 3. Parse TokenExchangeResponse
	// 4. Return token or error

	return nil, errors.New("token exchange not fully implemented in oauth_service")
}

// generateUserIDFromToken creates a deterministic user ID from provider and code
// In production, this would decode a JWT or call the provider's userinfo endpoint
func generateUserIDFromToken(provider string, authCode string) uuid.UUID {
	// Create deterministic UUID from provider and code
	// This ensures same user gets same UUID for same provider
	namespace := uuid.MustParse("6ba7b810-9dad-11d1-80b4-00c04fd430c8") // DNS namespace
	name := fmt.Sprintf("%s:%s", provider, authCode)
	return uuid.NewSHA1(namespace, []byte(name))
}

// logSecurityEvent logs OAuth security events
func logSecurityEvent(event string, code string, provider string, message string, metadata map[string]interface{}) {
	// Do NOT log sensitive data like tokens or codes
	var b strings.Builder
	fmt.Fprintf(&b, "[OAUTH_SECURITY] %s | provider:%s | msg:%s", event, provider, message)
	for key, val := range metadata {
		fmt.Fprintf(&b, " | %s:%v", key, val)
	}
	slog.Info("message", "detail", b.String())
}

// HandleAuthorizeEcho wraps HandleAuthorizeRequest for Echo framework
func (svc *OAuthService) HandleAuthorizeEcho(echoCtx echo.Context) error {
	provider := echoCtx.QueryParam("provider")
	if provider == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{
			"error":             "invalid_request",
			"error_description": "provider parameter is required",
		})
	}

	// Get provider config (would come from Service.getProvider)
	// For now, return error
	return echoCtx.JSON(http.StatusBadRequest, map[string]string{
		"error": "provider config not available in service",
	})
}

// HandleCallbackEcho wraps HandleCallbackRequest for Echo framework
func (svc *OAuthService) HandleCallbackEcho(echoCtx echo.Context) error {
	code := echoCtx.QueryParam("code")
	// state := echoCtx.QueryParam("state")
	provider := echoCtx.QueryParam("provider")

	if code == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{
			"error":             "invalid_request",
			"error_description": "code parameter is required",
		})
	}

	if provider == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{
			"error":             "invalid_request",
			"error_description": "provider parameter is required",
		})
	}

	// Get provider config (would come from Service.getProvider)
	// For now, return error
	return echoCtx.JSON(http.StatusBadRequest, map[string]string{
		"error": "provider config not available in service",
	})
}
