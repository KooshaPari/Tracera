package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
)

const (
	oauthLoginStateTTL = 10 * time.Minute
)

var oauthProviderNameRe = regexp.MustCompile(`^[a-zA-Z0-9_-]{1,32}$`)

type OAuthHandler struct {
	redisClient  *redis.Client
	stateManager *auth.StateTokenManager
	authProvider auth.Provider
}

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

type OAuthLoginRequest struct {
	Provider    string   `json:"provider"`
	RedirectURI string   `json:"redirect_uri"`
	Scopes      []string `json:"scopes,omitempty"`
}

type OAuthLoginResponse struct {
	Provider         string `json:"provider"`
	State            string `json:"state"`
	AuthorizationURL string `json:"authorization_url"`
	ExpiresAt        string `json:"expires_at"`
}

// Login handles POST /oauth/login.
// It generates a state token, stores minimal login context, and returns an OAuth authorization URL.
func (h *OAuthHandler) Login(c echo.Context) error {
	if h.redisClient == nil || h.stateManager == nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "oauth state storage not configured (redis unavailable)"})
	}

	var req OAuthLoginRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
	}
	req.Provider = strings.TrimSpace(req.Provider)
	req.RedirectURI = strings.TrimSpace(req.RedirectURI)

	if req.Provider == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "provider is required"})
	}
	if !oauthProviderNameRe.MatchString(req.Provider) {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "provider contains invalid characters"})
	}
	if req.RedirectURI == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "redirect_uri is required"})
	}

	redirectURI, err := url.Parse(req.RedirectURI)
	if err != nil || !redirectURI.IsAbs() || (redirectURI.Scheme != "http" && redirectURI.Scheme != "https") {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "redirect_uri must be an absolute http(s) URL"})
	}

	authorizeURL, clientID, scope, allowedRedirect, err := loadOAuthProviderConfig(req.Provider)
	if err != nil {
		log.Printf("oauth login config error provider=%s: %v", req.Provider, err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "oauth provider is not configured"})
	}
	if allowedRedirect != "" && allowedRedirect != req.RedirectURI {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "redirect_uri is not allowed"})
	}

	// State token (stored in Redis, one-time use).
	stateToken, err := h.stateManager.GenerateStateToken(c.Request().Context())
	if err != nil {
		log.Printf("oauth login failed to generate state provider=%s: %v", req.Provider, err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to start oauth flow"})
	}

	if len(req.Scopes) > 0 {
		scope = strings.Join(req.Scopes, " ")
	}

	authURL, err := buildAuthorizationURL(authorizeURL, clientID, req.RedirectURI, scope, stateToken)
	if err != nil {
		log.Printf("oauth login failed to build auth url provider=%s: %v", req.Provider, err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to start oauth flow"})
	}

	// Store minimal login context so callback can validate provider binding.
	if err := h.storeLoginContext(c.Request().Context(), stateToken, req.Provider, req.RedirectURI); err != nil {
		log.Printf("oauth login failed to store login context provider=%s: %v", req.Provider, err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to start oauth flow"})
	}

	return c.JSON(http.StatusOK, OAuthLoginResponse{
		Provider:         req.Provider,
		State:            stateToken,
		AuthorizationURL: authURL,
		ExpiresAt:        time.Now().Add(oauthLoginStateTTL).UTC().Format(time.RFC3339),
	})
}

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

	code := strings.TrimSpace(c.QueryParam("code"))
	state := strings.TrimSpace(c.QueryParam("state"))
	provider := strings.TrimSpace(c.QueryParam("provider"))

	if code == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "code is required"})
	}
	if state == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "state is required"})
	}

	// One-time CSRF protection via state token.
	if err := h.stateManager.ValidateStateToken(c.Request().Context(), state); err != nil {
		log.Printf("oauth callback invalid state: %v", err)
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid or expired state"})
	}

	// Ensure provider binding matches the state issued in Login().
	loginCtx, err := h.loadAndDeleteLoginContext(c.Request().Context(), state)
	if err != nil && !errors.Is(err, redis.Nil) {
		log.Printf("oauth callback failed to load login context: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to complete oauth flow"})
	}
	if loginCtx != nil {
		if provider == "" {
			provider = loginCtx.Provider
		} else if provider != loginCtx.Provider {
			return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "provider does not match oauth login state"})
		}
	}

	if provider == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "provider is required"})
	}

	// Optional redirect for browser-based flows.
	// This keeps the default JSON response (used by tests and API callers), but supports
	// redirecting to a safe return target for web clients.
	if redirectTo := strings.TrimSpace(c.QueryParam("redirect_to")); redirectTo != "" {
		safe, err := validateOAuthRedirectTarget(redirectTo)
		if err != nil {
			return c.JSON(http.StatusBadRequest, ErrorResponse{Error: err.Error()})
		}
		u, err := url.Parse(safe)
		if err != nil {
			return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "redirect_to is invalid"})
		}
		q := u.Query()
		q.Set("provider", provider)
		q.Set("code", code)
		q.Set("state", state)
		u.RawQuery = q.Encode()
		return c.Redirect(http.StatusSeeOther, u.String())
	}

	return c.JSON(http.StatusOK, OAuthCallbackResponse{
		Provider: provider,
		Code:     code,
		State:    state,
	})
}

type OAuthLogoutRequest struct {
	// State is optional. If provided, we revoke any outstanding OAuth state/login context.
	State string `json:"state,omitempty"`
}

// Logout handles POST /oauth/logout.
// Requires auth provider configuration (and should be protected by auth middleware at routing layer).
func (h *OAuthHandler) Logout(c echo.Context) error {
	if h.authProvider == nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "auth provider not configured"})
	}

	// We rely on AuthAdapterMiddleware to validate and set user context; still sanity-check.
	if user, _ := c.Get("user").(*auth.User); user == nil {
		return c.JSON(http.StatusUnauthorized, ErrorResponse{Error: "unauthenticated"})
	}

	var req OAuthLogoutRequest
	// Body is optional; ignore bind error if empty body.
	if c.Request().Body != nil && c.Request().ContentLength > 0 {
		if err := c.Bind(&req); err != nil {
			return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
		}
	}

	if strings.TrimSpace(req.State) != "" && h.redisClient != nil && h.stateManager != nil {
		// Best-effort cleanup: revoke state token + delete login context. Don't fail logout on cleanup errors.
		_ = h.stateManager.RevokeStateToken(context.Background(), strings.TrimSpace(req.State))
		_ = h.redisClient.Del(context.Background(), oauthLoginContextKey(strings.TrimSpace(req.State))).Err()
	}

	return c.JSON(http.StatusOK, map[string]bool{"success": true})
}

// Status handles GET /oauth/status.
// If routed behind auth middleware, it returns the authenticated user context.
// If not authenticated, it returns a 401.
func (h *OAuthHandler) Status(c echo.Context) error {
	if h.authProvider == nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "auth provider not configured"})
	}

	user, _ := c.Get("user").(*auth.User)
	if user == nil {
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
	tt := strings.TrimSpace(target)
	if tt == "" {
		return "", errors.New("redirect_to is required")
	}

	// Relative paths are always allowed.
	if strings.HasPrefix(tt, "/") && !strings.HasPrefix(tt, "//") {
		return tt, nil
	}

	u, err := url.Parse(tt)
	if err != nil || u.Scheme == "" || u.Host == "" {
		return "", errors.New("redirect_to must be a relative path or absolute URL")
	}
	if u.Scheme != "http" && u.Scheme != "https" {
		return "", errors.New("redirect_to must be http(s)")
	}

	allowed := loadAllowedOriginsFromEnv("CORS_ALLOWED_ORIGINS")
	allowed = append(allowed, loadAllowedOriginsFromEnv("OAUTH_ALLOWED_REDIRECT_ORIGINS")...)
	if len(allowed) == 0 {
		return "", errors.New("redirect_to origin not allowed (no allowlist configured)")
	}

	origin := u.Scheme + "://" + u.Host
	for _, a := range allowed {
		if origin == a {
			return tt, nil
		}
	}
	return "", errors.New("redirect_to origin not allowed")
}

func loadAllowedOriginsFromEnv(envKey string) []string {
	raw := strings.TrimSpace(os.Getenv(envKey))
	if raw == "" {
		return nil
	}
	parts := strings.Split(raw, ",")
	out := make([]string, 0, len(parts))
	for _, p := range parts {
		v := strings.TrimSpace(p)
		if v == "" {
			continue
		}
		if v == "*" || strings.Contains(v, "*") {
			continue
		}
		u, err := url.Parse(v)
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
	_ = h.redisClient.Del(ctx, oauthLoginContextKey(state)).Err()

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
	if parseErr != nil || !parsed.IsAbs() || (parsed.Scheme != "http" && parsed.Scheme != "https") {
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
	u, err := url.Parse(authorizeURL)
	if err != nil {
		return "", err
	}

	q := u.Query()
	q.Set("response_type", "code")
	q.Set("client_id", clientID)
	q.Set("redirect_uri", redirectURI)
	if strings.TrimSpace(scope) != "" {
		q.Set("scope", strings.TrimSpace(scope))
	}
	if strings.TrimSpace(state) != "" {
		q.Set("state", strings.TrimSpace(state))
	}
	u.RawQuery = q.Encode()
	return u.String(), nil
}
