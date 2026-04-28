package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

const (
	oauthLoginStateTTL = 10 * time.Minute
	schemeHTTP         = "http"
	schemeHTTPS        = "https"
)

var oauthProviderNameRe = regexp.MustCompile(`^[a-zA-Z0-9_-]{1,32}$`)

// OAuthHandler handles OAuth login, callback, and logout flows.
type OAuthHandler struct {
	redisClient  *redis.Client
	stateManager *auth.StateTokenManager
	authProvider auth.Provider
}

// NewOAuthHandler creates an OAuthHandler with the given Redis client and auth provider.
func NewOAuthHandler(redisClient *redis.Client, authProvider auth.Provider) *OAuthHandler {
	var stateManager *auth.StateTokenManager
	if redisClient != nil {
		stateManager = auth.NewStateTokenManager(redisClient)
	}

	return &OAuthHandler{
		redisClient:  redisClient,
		stateManager: stateManager,
		authProvider: authProvider,
	}
}

// OAuthLoginRequest holds the parameters for initiating an OAuth login.
type OAuthLoginRequest struct {
	Provider    string   `json:"provider"`
	RedirectURI string   `json:"redirect_uri"`
	Scopes      []string `json:"scopes,omitempty"`
}

// OAuthLoginResponse is returned after a successful OAuth login initiation.
type OAuthLoginResponse struct {
	Provider         string `json:"provider"`
	State            string `json:"state"`
	AuthorizationURL string `json:"authorization_url"`
	ExpiresAt        string `json:"expires_at"`
}

// validateOAuthLoginRequest validates and normalizes an OAuth login request.
func validateOAuthLoginRequest(c echo.Context) (*OAuthLoginRequest, error) {
	var req OAuthLoginRequest
	if err := c.Bind(&req); err != nil {
		return nil, echo.NewHTTPError(http.StatusBadRequest, "invalid request body")
	}
	req.Provider = strings.TrimSpace(req.Provider)
	req.RedirectURI = strings.TrimSpace(req.RedirectURI)

	if req.Provider == "" {
		return nil, echo.NewHTTPError(http.StatusBadRequest, "provider is required")
	}
	if !oauthProviderNameRe.MatchString(req.Provider) {
		return nil, echo.NewHTTPError(http.StatusBadRequest, "provider contains invalid characters")
	}
	if req.RedirectURI == "" {
		return nil, echo.NewHTTPError(http.StatusBadRequest, "redirect_uri is required")
	}

	redirectURI, err := url.Parse(req.RedirectURI)
	if err != nil || !redirectURI.IsAbs() || (redirectURI.Scheme != schemeHTTP && redirectURI.Scheme != schemeHTTPS) {
		return nil, echo.NewHTTPError(http.StatusBadRequest, "redirect_uri must be an absolute http(s) URL")
	}

	return &req, nil
}

// validateRedirectURI checks if the redirect URI is allowed for the provider
func validateRedirectURI(allowedRedirect, requestedRedirect string) error {
	if allowedRedirect != "" && allowedRedirect != requestedRedirect {
		return errors.New("redirect_uri is not allowed")
	}
	return nil
}

// resolveOAuthScope resolves the OAuth scope from request or config
func resolveOAuthScope(configScope string, requestScopes []string) string {
	if len(requestScopes) > 0 {
		return strings.Join(requestScopes, " ")
	}
	return configScope
}

// Login handles POST /oauth/login.
// It generates a state token, stores minimal login context, and returns an OAuth authorization URL.
func (h *OAuthHandler) Login(c echo.Context) error {
	if h.redisClient == nil || h.stateManager == nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "oauth state storage not configured (redis unavailable)"})
	}

	req, err := validateOAuthLoginRequest(c)
	if err != nil {
		return err
	}

	authorizeURL, clientID, scope, allowedRedirect, err := loadOAuthProviderConfig(req.Provider)
	if err != nil {
		slog.Error("oauth login config error provider=", "error", req.Provider, "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "oauth provider is not configured"})
	}

	if err := validateRedirectURI(allowedRedirect, req.RedirectURI); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: err.Error()})
	}

	// State token (stored in Redis, one-time use).
	stateToken, err := h.stateManager.GenerateStateToken(c.Request().Context())
	if err != nil {
		slog.Error("oauth login failed to generate state provider=", "error", req.Provider, "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to start oauth flow"})
	}

	scope = resolveOAuthScope(scope, req.Scopes)

	authURL, err := buildAuthorizationURL(authorizeURL, clientID, req.RedirectURI, scope, stateToken)
	if err != nil {
		slog.Error("oauth login failed to build auth url provider=", "error", req.Provider, "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to start oauth flow"})
	}

	// Store minimal login context so callback can validate provider binding.
	if err := h.storeLoginContext(c.Request().Context(), stateToken, req.Provider, req.RedirectURI); err != nil {
		slog.Error("oauth login failed to store login context provider=", "error", req.Provider, "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to start oauth flow"})
	}

	return c.JSON(http.StatusOK, OAuthLoginResponse{
		Provider:         req.Provider,
		State:            stateToken,
		AuthorizationURL: authURL,
		ExpiresAt:        time.Now().Add(oauthLoginStateTTL).UTC().Format(time.RFC3339),
	})
}

// OAuthCallbackResponse is returned after a successful OAuth callback.
type OAuthCallbackResponse struct {
	Provider string `json:"provider"`
	Code     string `json:"code"`
	State    string `json:"state"`
}

// Callback handles GET /oauth/callback.
// Validates state token, binds it to provider, and returns the received authorization code.
func (h *OAuthHandler) Callback(c echo.Context) error {
	if h.redisClient == nil || h.stateManager == nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "oauth state storage not configured (redis unavailable)"})
	}

	params, err := readOAuthCallbackParams(c)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: err.Error()})
	}

	ctx := c.Request().Context()
	provider, status, err := h.validateStateAndResolveProvider(ctx, params.State, params.Provider)
	if err != nil {
		return c.JSON(status, ErrorResponse{Error: err.Error()})
	}
	if provider == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "provider is required"})
	}

	if params.RedirectTo != "" {
		return redirectOAuthCallback(c, params.RedirectTo, provider, params.Code, params.State)
	}

	return c.JSON(http.StatusOK, OAuthCallbackResponse{
		Provider: provider,
		Code:     params.Code,
		State:    params.State,
	})
}

type oauthCallbackParams struct {
	Code       string
	State      string
	Provider   string
	RedirectTo string
}

func readOAuthCallbackParams(c echo.Context) (oauthCallbackParams, error) {
	params := oauthCallbackParams{
		Code:       strings.TrimSpace(c.QueryParam("code")),
		State:      strings.TrimSpace(c.QueryParam("state")),
		Provider:   strings.TrimSpace(c.QueryParam("provider")),
		RedirectTo: strings.TrimSpace(c.QueryParam("redirect_to")),
	}

	if params.Code == "" {
		return oauthCallbackParams{}, errors.New("code is required")
	}
	if params.State == "" {
		return oauthCallbackParams{}, errors.New("state is required")
	}

	return params, nil
}

func (h *OAuthHandler) validateStateAndResolveProvider(ctx context.Context, state, provider string) (string, int, error) {
	// One-time CSRF protection via state token.
	if err := h.stateManager.ValidateStateToken(ctx, state); err != nil {
		slog.Info("oauth callback invalid state", "id", err)
		return "", http.StatusBadRequest, errors.New("invalid or expired state")
	}

	// Ensure provider binding matches the state issued in Login().
	loginCtx, err := h.loadAndDeleteLoginContext(ctx, state)
	if err != nil && !errors.Is(err, redis.Nil) {
		slog.Error("oauth callback failed to load login context", "error", err)
		return "", http.StatusInternalServerError, errors.New("failed to complete oauth flow")
	}

	if loginCtx == nil {
		return provider, 0, nil
	}
	if provider == "" {
		return loginCtx.Provider, 0, nil
	}
	if provider != loginCtx.Provider {
		return "", http.StatusBadRequest, errors.New("provider does not match oauth login state")
	}
	return provider, 0, nil
}

func redirectOAuthCallback(c echo.Context, redirectTo, provider, code, state string) error {
	// Optional redirect for browser-based flows.
	// This keeps the default JSON response (used by tests and API callers), but supports
	// redirecting to a safe return target for web clients.
	safe, err := validateOAuthRedirectTarget(redirectTo)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: err.Error()})
	}
	parsedURL, err := url.Parse(safe)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "redirect_to is invalid"})
	}

	queryValues := parsedURL.Query()
	queryValues.Set("provider", provider)
	queryValues.Set("code", code)
	queryValues.Set("state", state)
	parsedURL.RawQuery = queryValues.Encode()

	return c.Redirect(http.StatusSeeOther, parsedURL.String())
}

// OAuthLogoutRequest holds the parameters for an OAuth logout.
type OAuthLogoutRequest struct {
	// State is optional. If provided, we revoke any outstanding OAuth state/login context.
	State string `json:"state,omitempty"`
}

// cleanupLogoutState performs best-effort cleanup of OAuth state during logout.
func (h *OAuthHandler) cleanupLogoutState(state string) {
	if strings.TrimSpace(state) == "" || h.redisClient == nil || h.stateManager == nil {
		return
	}

	trimmedState := strings.TrimSpace(state)
	// Best-effort cleanup: revoke state token + delete login context. Don't fail logout on cleanup errors.
	if err := h.stateManager.RevokeStateToken(context.Background(), trimmedState); err != nil {
		slog.Warn("failed to revoke state token during logout", "error", err)
	}
	if err := h.redisClient.Del(context.Background(), oauthLoginContextKey(trimmedState)).Err(); err != nil {
		slog.Warn("failed to delete login context during logout", "error", err)
	}
}

// Logout handles POST /oauth/logout.
// Requires auth provider configuration (and should be protected by auth middleware at routing layer).
func (h *OAuthHandler) Logout(c echo.Context) error {
	if h.authProvider == nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "auth provider not configured"})
	}

	// We rely on AuthAdapterMiddleware to validate and set user context; still sanity-check.
	if user, ok := c.Get("user").(*auth.User); !ok || user == nil {
		return c.JSON(http.StatusUnauthorized, ErrorResponse{Error: "unauthenticated"})
	}

	var req OAuthLogoutRequest
	// Body is optional; ignore bind error if empty body.
	if c.Request().Body != nil && c.Request().ContentLength > 0 {
		if err := c.Bind(&req); err != nil {
			return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
		}
	}

	h.cleanupLogoutState(req.State)

	return c.JSON(http.StatusOK, map[string]bool{"success": true})
}

// Status handles GET /oauth/status.
// If routed behind auth middleware, it returns the authenticated user context.
// If not authenticated, it returns a 401.
func (h *OAuthHandler) Status(c echo.Context) error {
	if h.authProvider == nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "auth provider not configured"})
	}

	user, ok := c.Get("user").(*auth.User)
	if !ok || user == nil {
		return c.JSON(http.StatusUnauthorized, ErrorResponse{Error: "unauthenticated"})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"authenticated": true,
		"user":          user,
	})
}

type oauthLoginContext struct {
	Provider    string `json:"provider"`
	RedirectURI string `json:"redirect_uri"`
	CreatedAt   string `json:"created_at"`
}

func validateOAuthRedirectTarget(target string) (string, error) {
	trimmedTarget := strings.TrimSpace(target)
	if trimmedTarget == "" {
		return "", errors.New("redirect_to is required")
	}

	// Relative paths are always allowed.
	if isAllowedRelativeRedirectTarget(trimmedTarget) {
		return trimmedTarget, nil
	}

	parsedURL, err := parseAbsoluteRedirectTarget(trimmedTarget)
	if err != nil {
		return "", err
	}

	allowedOrigins, err := loadAllowedRedirectOrigins()
	if err != nil {
		return "", err
	}
	if !isAllowedRedirectOrigin(parsedURL, allowedOrigins) {
		return "", errors.New("redirect_to origin not allowed")
	}
	return trimmedTarget, nil
}

func isAllowedRelativeRedirectTarget(target string) bool {
	return strings.HasPrefix(target, "/") && !strings.HasPrefix(target, "//")
}

func parseAbsoluteRedirectTarget(target string) (*url.URL, error) {
	parsedURL, err := url.Parse(target)
	if err != nil || parsedURL.Scheme == "" || parsedURL.Host == "" {
		return nil, errors.New("redirect_to must be a relative path or absolute URL")
	}
	if parsedURL.Scheme != schemeHTTP && parsedURL.Scheme != schemeHTTPS {
		return nil, errors.New("redirect_to must be http(s)")
	}
	return parsedURL, nil
}

func loadAllowedRedirectOrigins() ([]string, error) {
	allowed := loadAllowedOriginsFromEnv("CORS_ALLOWED_ORIGINS")
	allowed = append(allowed, loadAllowedOriginsFromEnv("OAUTH_ALLOWED_REDIRECT_ORIGINS")...)
	if len(allowed) == 0 {
		return nil, errors.New("redirect_to origin not allowed (no allowlist configured)")
	}
	return allowed, nil
}

func isAllowedRedirectOrigin(targetURL *url.URL, allowedOrigins []string) bool {
	origin := targetURL.Scheme + "://" + targetURL.Host
	for _, a := range allowedOrigins {
		if origin == a {
			return true
		}
	}
	return false
}

func loadAllowedOriginsFromEnv(envKey string) []string {
	raw := strings.TrimSpace(os.Getenv(envKey))
	if raw == "" {
		return nil
	}
	parts := strings.Split(raw, ",")
	out := make([]string, 0, len(parts))
	for _, p := range parts {
		val := strings.TrimSpace(p)
		if val == "" {
			continue
		}
		if val == "*" || strings.Contains(val, "*") {
			continue
		}
		u, err := url.Parse(val)
		if err != nil || u.Scheme == "" || u.Host == "" {
			continue
		}
		out = append(out, u.Scheme+"://"+u.Host)
	}
	return out
}

func oauthLoginContextKey(state string) string {
	return "oauth:login:" + state
}

func (h *OAuthHandler) storeLoginContext(ctx context.Context, state, provider, redirectURI string) error {
	payload, err := json.Marshal(oauthLoginContext{
		Provider:    provider,
		RedirectURI: redirectURI,
		CreatedAt:   time.Now().UTC().Format(time.RFC3339),
	})
	if err != nil {
		return err
	}
	return h.redisClient.Set(ctx, oauthLoginContextKey(state), payload, oauthLoginStateTTL).Err()
}

func (h *OAuthHandler) loadAndDeleteLoginContext(ctx context.Context, state string) (*oauthLoginContext, error) {
	val, err := h.redisClient.Get(ctx, oauthLoginContextKey(state)).Result()
	if err != nil {
		return nil, err
	}
	if err := h.redisClient.Del(ctx, oauthLoginContextKey(state)).Err(); err != nil {
		slog.Warn("failed to delete login context", "error", err)
	}

	var out oauthLoginContext
	if err := json.Unmarshal([]byte(val), &out); err != nil {
		return nil, err
	}
	return &out, nil
}

func loadOAuthProviderConfig(provider string) (authorizeURL string, clientID string, scope string, allowedRedirect string, err error) {
	prefix := "OAUTH_" + sanitizeEnvSegment(provider) + "_"
	authorizeURL = strings.TrimSpace(os.Getenv(prefix + "AUTHORIZE_URL"))
	clientID = strings.TrimSpace(os.Getenv(prefix + "CLIENT_ID"))
	scope = strings.TrimSpace(os.Getenv(prefix + "SCOPE"))
	allowedRedirect = strings.TrimSpace(os.Getenv(prefix + "REDIRECT_URI"))

	if authorizeURL == "" || clientID == "" {
		return "", "", "", "", errors.New("missing AUTHORIZE_URL or CLIENT_ID")
	}

	parsed, parseErr := url.Parse(authorizeURL)
	if parseErr != nil || !parsed.IsAbs() || (parsed.Scheme != schemeHTTP && parsed.Scheme != schemeHTTPS) {
		return "", "", "", "", errors.New("AUTHORIZE_URL must be absolute http(s)")
	}

	return authorizeURL, clientID, scope, allowedRedirect, nil
}

func sanitizeEnvSegment(provider string) string {
	seg := strings.ToUpper(provider)
	seg = strings.ReplaceAll(seg, "-", "_")
	return seg
}

func buildAuthorizationURL(authorizeURL, clientID, redirectURI, scope, state string) (string, error) {
	parsedURL, err := url.Parse(authorizeURL)
	if err != nil {
		return "", err
	}

	queryValues := parsedURL.Query()
	queryValues.Set("response_type", "code")
	queryValues.Set("client_id", clientID)
	queryValues.Set("redirect_uri", redirectURI)
	if strings.TrimSpace(scope) != "" {
		queryValues.Set("scope", strings.TrimSpace(scope))
	}
	if strings.TrimSpace(state) != "" {
		queryValues.Set("state", strings.TrimSpace(state))
	}
	parsedURL.RawQuery = queryValues.Encode()
	return parsedURL.String(), nil
}
