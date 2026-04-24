package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/alicebob/miniredis/v2"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/require"
)

type oauthLoginResp struct {
	Provider         string `json:"provider"`
	State            string `json:"state"`
	AuthorizationURL string `json:"authorization_url"`
	ExpiresAt        string `json:"expires_at"`
}

type oauthCallbackResp struct {
	Provider string `json:"provider"`
	Code     string `json:"code"`
	State    string `json:"state"`
}

func TestOAuthHandler_LoginAndCallback_StateOneTimeUse(t *testing.T) {
	mr, err := miniredis.Run()
	require.NoError(t, err)
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{Addr: mr.Addr()})
	defer func() { require.NoError(t, redisClient.Close()) }()

	t.Setenv("OAUTH_GITLAB_AUTHORIZE_URL", "https://gitlab.example.com/oauth/authorize")
	t.Setenv("OAUTH_GITLAB_CLIENT_ID", "client_123")
	t.Setenv("OAUTH_GITLAB_SCOPE", "api")
	t.Setenv("OAUTH_GITLAB_REDIRECT_URI", "http://localhost:8080/oauth/callback")

	handler := NewOAuthHandler(redisClient, nil)
	e := echo.New()

	// Login
	loginReqBody := `{"provider":"gitlab","redirect_uri":"http://localhost:8080/oauth/callback"}`
	req := httptest.NewRequest(http.MethodPost, "/oauth/login", strings.NewReader(loginReqBody))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	require.NoError(t, handler.Login(c))
	require.Equal(t, http.StatusOK, rec.Code)

	var loginResp oauthLoginResp
	require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &loginResp))
	require.Equal(t, "gitlab", loginResp.Provider)
	require.NotEmpty(t, loginResp.State)
	require.Contains(t, loginResp.AuthorizationURL, "response_type=code")
	require.Contains(t, loginResp.AuthorizationURL, "client_id=client_123")
	require.Contains(t, loginResp.AuthorizationURL, "redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Foauth%2Fcallback")
	require.Contains(t, loginResp.AuthorizationURL, "state=")

	// Callback succeeds once
	cbReq := httptest.NewRequest(http.MethodGet, "/oauth/callback?code=abc123&state="+loginResp.State+"&provider=gitlab", nil)
	cbRec := httptest.NewRecorder()
	cbCtx := e.NewContext(cbReq, cbRec)
	require.NoError(t, handler.Callback(cbCtx))
	require.Equal(t, http.StatusOK, cbRec.Code)

	var cbResp oauthCallbackResp
	require.NoError(t, json.Unmarshal(cbRec.Body.Bytes(), &cbResp))
	require.Equal(t, "gitlab", cbResp.Provider)
	require.Equal(t, "abc123", cbResp.Code)
	require.Equal(t, loginResp.State, cbResp.State)

	// Callback with same state fails (one-time use)
	cbReq2 := httptest.NewRequest(http.MethodGet, "/oauth/callback?code=abc123&state="+loginResp.State+"&provider=gitlab", nil)
	cbRec2 := httptest.NewRecorder()
	cbCtx2 := e.NewContext(cbReq2, cbRec2)
	require.NoError(t, handler.Callback(cbCtx2))
	require.Equal(t, http.StatusBadRequest, cbRec2.Code)
}

func TestOAuthHandler_Login_RejectsDisallowedRedirectURI(t *testing.T) {
	mr, err := miniredis.Run()
	require.NoError(t, err)
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{Addr: mr.Addr()})
	defer func() { require.NoError(t, redisClient.Close()) }()

	// Ensure env is clean for this test.
	require.NoError(t, os.Unsetenv("OAUTH_GITLAB_SCOPE"))

	t.Setenv("OAUTH_GITLAB_AUTHORIZE_URL", "https://gitlab.example.com/oauth/authorize")
	t.Setenv("OAUTH_GITLAB_CLIENT_ID", "client_123")
	t.Setenv("OAUTH_GITLAB_REDIRECT_URI", "http://localhost:8080/oauth/callback")

	handler := NewOAuthHandler(redisClient, nil)
	e := echo.New()

	loginReqBody := `{"provider":"gitlab","redirect_uri":"http://evil.example.com/oauth/callback"}`
	req := httptest.NewRequest(http.MethodPost, "/oauth/login", strings.NewReader(loginReqBody))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	require.NoError(t, handler.Login(c))
	require.Equal(t, http.StatusBadRequest, rec.Code)
}
