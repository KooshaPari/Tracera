package handlers

import (
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"strings"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	um "github.com/workos/workos-go/v4/pkg/usermanagement"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

// AuthKitHandler handles AuthKit hosted UI authorization flow endpoints.
type AuthKitHandler struct {
	workos       *um.Client
	kitAdapter   *auth.KitAdapter
	stateManager *auth.StateTokenManager
	authHandler  *AuthHandler
	clientID     string
	redirectURI  string
}

// NewAuthKitHandler creates a new AuthKitHandler.
func NewAuthKitHandler(
	workosAPIKey string,
	kitAdapter *auth.KitAdapter,
	redisClient *redis.Client,
	authHandler *AuthHandler,
	clientID string,
	redirectURI string,
) *AuthKitHandler {
	return &AuthKitHandler{
		workos:       um.NewClient(workosAPIKey),
		kitAdapter:   kitAdapter,
		stateManager: auth.NewStateTokenManager(redisClient),
		authHandler:  authHandler,
		clientID:     clientID,
		redirectURI:  redirectURI,
	}
}

// authKitCallbackRequest is the JSON body for the callback endpoint.
type authKitCallbackRequest struct {
	Code  string `json:"code"`
	State string `json:"state"`
}

// authKitRefreshRequest is the JSON body for the refresh endpoint.
type authKitRefreshRequest struct {
	RefreshToken string `json:"refresh_token"`
}

// Authorize returns the AuthKit authorization URL and a CSRF state token.
// GET /api/v1/auth/authkit/authorize
func (h *AuthKitHandler) Authorize(c echo.Context) error {
	ctx := c.Request().Context()

	stateToken, err := h.stateManager.GenerateStateToken(ctx)
	if err != nil {
		slog.Error("authkit: failed to generate state token", "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to start authorization flow"})
	}

	authURL, err := h.workos.GetAuthorizationURL(um.GetAuthorizationURLOpts{
		ClientID:    h.clientID,
		RedirectURI: h.redirectURI,
		Provider:    "authkit",
		State:       stateToken,
	})
	if err != nil {
		slog.Error("authkit: failed to build authorization URL", "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to build authorization URL"})
	}

	return c.JSON(http.StatusOK, map[string]string{
		"authorization_url": authURL.String(),
		"state":             stateToken,
	})
}

// Callback exchanges an authorization code for tokens, syncs the user profile,
// creates a session, and sets the auth cookie.
// POST /api/v1/auth/authkit/callback
func (h *AuthKitHandler) Callback(c echo.Context) error {
	ctx := c.Request().Context()

	var req authKitCallbackRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
	}
	if req.Code == "" || req.State == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "code and state are required"})
	}

	if err := h.stateManager.ValidateStateToken(ctx, req.State); err != nil {
		slog.Info("authkit: invalid state token", "error", err)
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid or expired state"})
	}

	ipAddress := c.RealIP()
	userAgent := c.Request().UserAgent()

	authResp, err := h.workos.AuthenticateWithCode(ctx, um.AuthenticateWithCodeOpts{
		ClientID:  h.clientID,
		Code:      req.Code,
		IPAddress: ipAddress,
		UserAgent: userAgent,
	})
	if err != nil {
		slog.Error("authkit: code exchange failed", "error", err)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{Error: "authentication failed"})
	}

	workosUser := authResp.User
	displayName := strings.TrimSpace(workosUser.FirstName + " " + workosUser.LastName)

	claims := &auth.WorkOSClaims{
		Sub:   workosUser.ID,
		Email: workosUser.Email,
		Name:  displayName,
		OrgID: authResp.OrganizationID,
	}

	user, err := h.kitAdapter.SyncProfileFromWorkOS(ctx, claims)
	if err != nil {
		slog.Error("authkit: profile sync failed", "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to sync user profile"})
	}

	token, err := h.authHandler.createSessionToken(ctx, user)
	if err != nil {
		slog.Error("authkit: session creation failed", "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to create session"})
	}

	h.authHandler.setAuthCookie(c, token)
	slog.Info("authkit: user authenticated", "user", user.Email, "id", user.ID)

	return c.JSON(http.StatusOK, AuthKitAuthResponse{
		User:         user,
		Token:        token,
		AccessToken:  authResp.AccessToken,
		RefreshToken: authResp.RefreshToken,
		ExpiresIn:    int64(h.authHandler.sessionTTL.Seconds()),
	})
}

// Refresh exchanges a WorkOS refresh token for new tokens.
// POST /api/v1/auth/authkit/refresh
func (h *AuthKitHandler) Refresh(c echo.Context) error {
	ctx := c.Request().Context()

	var req authKitRefreshRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
	}
	if req.RefreshToken == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "refresh_token is required"})
	}

	ipAddress := c.RealIP()
	userAgent := c.Request().UserAgent()

	refreshResp, err := h.workos.AuthenticateWithRefreshToken(ctx, um.AuthenticateWithRefreshTokenOpts{
		ClientID:     h.clientID,
		RefreshToken: req.RefreshToken,
		IPAddress:    ipAddress,
		UserAgent:    userAgent,
	})
	if err != nil {
		slog.Error("authkit: token refresh failed", "error", err)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{Error: "failed to refresh token"})
	}

	return c.JSON(http.StatusOK, map[string]string{
		"access_token":  refreshResp.AccessToken,
		"refresh_token": refreshResp.RefreshToken,
	})
}

// AuthKitAuthResponse is the JSON response for a successful AuthKit callback.
type AuthKitAuthResponse struct {
	User         *auth.User `json:"user"`
	Token        string     `json:"token"`
	AccessToken  string     `json:"access_token"`
	RefreshToken string     `json:"refresh_token"`
	ExpiresIn    int64      `json:"expires_in"`
}

// LoadAuthKitEnv reads AuthKit-related environment variables and returns
// (clientID, redirectURI, apiKey, error).
func LoadAuthKitEnv() (string, string, string, error) {
	clientID := os.Getenv("WORKOS_CLIENT_ID")
	if clientID == "" {
		return "", "", "", fmt.Errorf("WORKOS_CLIENT_ID is required")
	}
	redirectURI := os.Getenv("WORKOS_REDIRECT_URI")
	if redirectURI == "" {
		return "", "", "", fmt.Errorf("WORKOS_REDIRECT_URI is required")
	}
	apiKey := os.Getenv("WORKOS_API_KEY")
	if apiKey == "" {
		return "", "", "", fmt.Errorf("WORKOS_API_KEY is required")
	}
	return clientID, redirectURI, apiKey, nil
}
