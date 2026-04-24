//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestE2E_Login_AccessResource_Logout tests complete authentication flow
func TestE2E_Login_AccessResource_Logout(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Step 1: Register user
	registerReq := map[string]interface{}{
		"email":    "auth.test@example.com",
		"password": "SecurePass123!",
		"name":     "Auth Test User",
	}
	registerBody, _ := json.Marshal(registerReq)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(registerBody))
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)

	var registerResp struct {
		Token  string `json:"token"`
		UserID string `json:"user_id"`
	}
	err = json.NewDecoder(resp.Body).Decode(&registerResp)
	require.NoError(t, err)
	resp.Body.Close()

	initialToken := registerResp.Token
	userID := registerResp.UserID
	assert.NotEmpty(t, initialToken)
	assert.NotEmpty(t, userID)

	// Step 2: Logout
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/auth/logout", nil)
	req.Header.Set("Authorization", "Bearer "+initialToken)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// Step 3: Try to access resource with old token (should fail)
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+initialToken)

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	resp.Body.Close()

	// Step 4: Login again
	loginReq := map[string]interface{}{
		"email":    "auth.test@example.com",
		"password": "SecurePass123!",
	}
	loginBody, _ := json.Marshal(loginReq)
	resp, err = client.Post(baseURL+"/api/v1/auth/login", "application/json", bytes.NewBuffer(loginBody))
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)

	var loginResp struct {
		Token        string `json:"token"`
		RefreshToken string `json:"refresh_token"`
	}
	err = json.NewDecoder(resp.Body).Decode(&loginResp)
	require.NoError(t, err)
	resp.Body.Close()

	newToken := loginResp.Token
	assert.NotEmpty(t, newToken)
	assert.NotEqual(t, initialToken, newToken)

	// Step 5: Access resource with new token (should succeed)
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+newToken)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)

	var userResp struct {
		ID    string `json:"id"`
		Email string `json:"email"`
		Name  string `json:"name"`
	}
	err = json.NewDecoder(resp.Body).Decode(&userResp)
	require.NoError(t, err)
	resp.Body.Close()

	assert.Equal(t, userID, userResp.ID)
	assert.Equal(t, "auth.test@example.com", userResp.Email)
	assert.Equal(t, "Auth Test User", userResp.Name)
}

// TestE2E_Login_TokenExpiry_Refresh tests token expiry and refresh flow
func TestE2E_Login_TokenExpiry_Refresh(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Register user
	registerReq := map[string]interface{}{
		"email":    "refresh.test@example.com",
		"password": "SecurePass123!",
		"name":     "Refresh Test User",
	}
	registerBody, _ := json.Marshal(registerReq)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(registerBody))
	require.NoError(t, err)

	var registerResp struct {
		Token        string `json:"token"`
		RefreshToken string `json:"refresh_token"`
		UserID       string `json:"user_id"`
	}
	json.NewDecoder(resp.Body).Decode(&registerResp)
	resp.Body.Close()

	refreshToken := registerResp.RefreshToken
	userID := registerResp.UserID
	assert.NotEmpty(t, refreshToken)

	// Access resource with valid token
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+registerResp.Token)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// Simulate token expiry by using an invalid/expired token
	expiredToken := "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"

	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+expiredToken)

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	resp.Body.Close()

	// Refresh token
	refreshReq := map[string]interface{}{
		"refresh_token": refreshToken,
	}
	refreshBody, _ := json.Marshal(refreshReq)
	resp, err = client.Post(baseURL+"/api/v1/auth/refresh", "application/json", bytes.NewBuffer(refreshBody))
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)

	var refreshResp struct {
		Token        string `json:"token"`
		RefreshToken string `json:"refresh_token"`
	}
	err = json.NewDecoder(resp.Body).Decode(&refreshResp)
	require.NoError(t, err)
	resp.Body.Close()

	newToken := refreshResp.Token
	assert.NotEmpty(t, newToken)

	// Access resource with new token
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+newToken)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()
}

// TestE2E_Unauthorized_AccessDenied tests unauthorized access attempts
func TestE2E_Unauthorized_AccessDenied(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Create two users
	user1Token := ""
	user2ID := ""

	// User 1
	user1Req := map[string]interface{}{
		"email":    "user1@example.com",
		"password": "SecurePass123!",
		"name":     "User One",
	}
	user1Body, _ := json.Marshal(user1Req)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(user1Body))
	require.NoError(t, err)

	var user1Resp struct {
		Token string `json:"token"`
	}
	json.NewDecoder(resp.Body).Decode(&user1Resp)
	resp.Body.Close()
	user1Token = user1Resp.Token

	// User 2
	user2Req := map[string]interface{}{
		"email":    "user2@example.com",
		"password": "SecurePass123!",
		"name":     "User Two",
	}
	user2Body, _ := json.Marshal(user2Req)
	resp, err = client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(user2Body))
	require.NoError(t, err)

	var user2Resp struct {
		Token  string `json:"token"`
		UserID string `json:"user_id"`
	}
	json.NewDecoder(resp.Body).Decode(&user2Resp)
	resp.Body.Close()
	user2ID = user2Resp.UserID

	// User 2 creates a private project
	projectReq := map[string]interface{}{
		"name": "User 2 Private Project",
		"settings": map[string]interface{}{
			"visibility": "private",
		},
	}
	projectBody, _ := json.Marshal(projectReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/projects", bytes.NewBuffer(projectBody))
	req.Header.Set("Authorization", "Bearer "+user2Resp.Token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	var projectResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&projectResp)
	resp.Body.Close()
	projectID := projectResp.ID

	// User 1 tries to access User 2's private project (should fail)
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID, nil)
	req.Header.Set("Authorization", "Bearer "+user1Token)

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusForbidden, resp.StatusCode)
	resp.Body.Close()

	// User 1 tries to access User 2's profile (should fail on sensitive endpoints)
	req, _ = http.NewRequestWithContext(context.Background(), "PATCH", baseURL+"/api/v1/users/"+user2ID, bytes.NewBuffer([]byte(`{"name":"Hacked"}`)))
	req.Header.Set("Authorization", "Bearer "+user1Token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusForbidden, resp.StatusCode)
	resp.Body.Close()

	// No token access (should fail)
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects", nil)

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	resp.Body.Close()

	// Invalid token (should fail)
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects", nil)
	req.Header.Set("Authorization", "Bearer invalid.token.here")

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	resp.Body.Close()
}

// TestE2E_MultiSession_SameUser tests multiple concurrent sessions
func TestE2E_MultiSession_SameUser(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Register user
	registerReq := map[string]interface{}{
		"email":    "multisession@example.com",
		"password": "SecurePass123!",
		"name":     "Multi Session User",
	}
	registerBody, _ := json.Marshal(registerReq)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(registerBody))
	require.NoError(t, err)

	var registerResp struct {
		UserID string `json:"user_id"`
	}
	json.NewDecoder(resp.Body).Decode(&registerResp)
	resp.Body.Close()
	userID := registerResp.UserID

	// Login from "device 1"
	loginReq := map[string]interface{}{
		"email":    "multisession@example.com",
		"password": "SecurePass123!",
	}
	loginBody, _ := json.Marshal(loginReq)
	resp, err = client.Post(baseURL+"/api/v1/auth/login", "application/json", bytes.NewBuffer(loginBody))
	require.NoError(t, err)

	var login1Resp struct {
		Token string `json:"token"`
	}
	json.NewDecoder(resp.Body).Decode(&login1Resp)
	resp.Body.Close()
	token1 := login1Resp.Token

	// Login from "device 2"
	resp, err = client.Post(baseURL+"/api/v1/auth/login", "application/json", bytes.NewBuffer(loginBody))
	require.NoError(t, err)

	var login2Resp struct {
		Token string `json:"token"`
	}
	json.NewDecoder(resp.Body).Decode(&login2Resp)
	resp.Body.Close()
	token2 := login2Resp.Token

	assert.NotEqual(t, token1, token2, "Different login sessions should have different tokens")

	// Both tokens should work
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+token1)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+token2)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// Logout from device 1
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/auth/logout", nil)
	req.Header.Set("Authorization", "Bearer "+token1)

	resp, err = client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	// Token 1 should no longer work
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+token1)

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	resp.Body.Close()

	// Token 2 should still work
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/users/"+userID, nil)
	req.Header.Set("Authorization", "Bearer "+token2)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()
}
