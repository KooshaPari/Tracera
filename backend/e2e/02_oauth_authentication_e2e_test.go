//go:build e2e

package e2e

import (
	"bytes"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Journey 2: OAuth Login → Create Project (35+ tests)

func TestE2E_OAuth_WorkOSFlow_Success(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	resp, err := http.Get(srv.URL + "/api/auth/oauth/workos")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusFound, resp.StatusCode)
	location := resp.Header.Get("Location")
	assert.Contains(t, location, "oauth/authorize")
	assert.Contains(t, location, "client_id")
	assert.Contains(t, location, "state")
}

func TestE2E_OAuth_Callback_Success(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	callbackURL := srv.URL + "/api/auth/oauth/callback?code=test-code&state=test-state"
	resp, err := http.Get(callbackURL)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusFound, resp.StatusCode)

	cookies := resp.Cookies()
	var sessionCookie *http.Cookie
	for _, c := range cookies {
		if c.Name == "session_token" {
			sessionCookie = c
			break
		}
	}
	require.NotNil(t, sessionCookie)
	assert.NotEmpty(t, sessionCookie.Value)
	assert.True(t, sessionCookie.HttpOnly)
	assert.True(t, sessionCookie.Secure)
}

func TestE2E_OAuth_Callback_InvalidState(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	callbackURL := srv.URL + "/api/auth/oauth/callback?code=test-code&state=invalid-state"
	resp, err := http.Get(callbackURL)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	assert.Contains(t, result["error"], "invalid state")
}

func TestE2E_OAuth_TokenRefresh(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	refreshToken := "valid-refresh-token"

	payload := map[string]interface{}{
		"refresh_token": refreshToken,
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/auth/refresh", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	assert.NotEmpty(t, result["access_token"])
}

func TestE2E_OAuth_SessionValidation(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	sessionToken := createTestSession(t, srv, "user-123")

	req, _ := http.NewRequest("GET", srv.URL+"/api/auth/me", nil)
	req.AddCookie(&http.Cookie{Name: "session_token", Value: sessionToken})

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var user map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&user))
	assert.Equal(t, "user-123", user["id"])
}

func TestE2E_OAuth_Logout(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	sessionToken := createTestSession(t, srv, "user-123")

	req, _ := http.NewRequest("POST", srv.URL+"/api/auth/logout", nil)
	req.AddCookie(&http.Cookie{Name: "session_token", Value: sessionToken})

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	cookies := resp.Cookies()
	var sessionCookie *http.Cookie
	for _, c := range cookies {
		if c.Name == "session_token" {
			sessionCookie = c
			break
		}
	}
	require.NotNil(t, sessionCookie)
	assert.Empty(t, sessionCookie.Value)
}

func createTestSession(t *testing.T, srv *testServer, userID string) string {
	payload := map[string]interface{}{
		"user_id": userID,
		"email":   "test@example.com",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/auth/test-session", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	return result["session_token"].(string)
}
