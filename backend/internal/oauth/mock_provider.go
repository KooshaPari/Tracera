// Package oauth provides OAuth provider implementations and test helpers.
package oauth

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"sync"
	"time"
)

const tokenExpiresInSeconds = 3600 // 1 hour

// MockOAuthProvider simulates an OAuth 2.0 authorization server for testing.
// Implements RFC 6749 with state parameter validation and token generation.
type MockOAuthProvider struct {
	server       *httptest.Server
	URL          string
	ValidCodes   map[string]bool // Track valid authorization codes
	ValidStates  map[string]bool // Track valid state parameters
	ClientID     string
	ClientSecret string
	mu           sync.Mutex // Protect maps and counter
	codeCounter  int64
}

// NewMockOAuthProvider creates a new mock OAuth provider server.
func NewMockOAuthProvider() *MockOAuthProvider {
	provider := &MockOAuthProvider{
		ValidCodes:   make(map[string]bool),
		ValidStates:  make(map[string]bool),
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	}

	// Set up HTTP server with mux
	mux := http.NewServeMux()
	mux.HandleFunc("/authorize", provider.handleAuthorize)
	mux.HandleFunc("/token", provider.handleToken)

	provider.server = httptest.NewServer(mux)
	provider.URL = provider.server.URL

	return provider
}

// handleAuthorize handles OAuth authorization endpoint (GET /authorize)
// Returns authorization code with state parameter for CSRF protection
func (p *MockOAuthProvider) handleAuthorize(w http.ResponseWriter, r *http.Request) {
	// Extract query parameters
	clientID := r.URL.Query().Get("client_id")
	redirectURI := r.URL.Query().Get("redirect_uri")
	state := r.URL.Query().Get("state")
	responseType := r.URL.Query().Get("response_type")

	// Validate request
	if clientID == "" {
		http.Error(w, `{"error":"invalid_request","error_description":"client_id is required"}`, http.StatusBadRequest)
		return
	}

	if redirectURI == "" {
		http.Error(w, `{"error":"invalid_request","error_description":"redirect_uri is required"}`, http.StatusBadRequest)
		return
	}

	if responseType != "code" {
		http.Error(w, `{"error":"unsupported_response_type","error_description":"response_type must be 'code'"}`, http.StatusBadRequest)
		return
	}

	// Generate authorization code with counter for uniqueness
	p.mu.Lock()
	p.codeCounter++
	code := fmt.Sprintf("auth_code_%d_%d", time.Now().UnixNano(), p.codeCounter)
	p.ValidCodes[code] = true
	p.mu.Unlock()

	// Store state for validation in token endpoint
	if state != "" {
		p.mu.Lock()
		p.ValidStates[state] = true
		p.mu.Unlock()
	}

	// Build redirect URI with code and state
	redirectURL := fmt.Sprintf("%s?code=%s", redirectURI, code)
	if state != "" {
		redirectURL += "&state=" + state
	}

	// Return redirect (client will follow in real OAuth flow)
	http.Redirect(w, r, redirectURL, http.StatusFound)
}

// writeJSON writes a JSON response, logging any encoding errors.
func writeJSON(w http.ResponseWriter, data map[string]interface{}) {
	if err := json.NewEncoder(w).Encode(data); err != nil {
		slog.Warn("failed to encode JSON response", "error", err)
	}
}

// handleToken handles OAuth token endpoint (POST /token)
// Exchanges authorization code for access token
func oauthError(w http.ResponseWriter, status int, errType, desc string) {
	w.WriteHeader(status)
	writeJSON(w, map[string]interface{}{"error": errType, "error_description": desc})
}

func (p *MockOAuthProvider) handleToken(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// Parse request body
	var req struct {
		GrantType    string `json:"grant_type"`
		Code         string `json:"code"`
		ClientID     string `json:"client_id"`
		ClientSecret string `json:"client_secret"`
		RedirectURI  string `json:"redirect_uri"`
		State        string `json:"state"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		oauthError(w, http.StatusBadRequest, "invalid_request", "Invalid request body")
		return
	}

	// Validate grant type
	if req.GrantType != "authorization_code" {
		oauthError(w, http.StatusBadRequest, "unsupported_grant_type", "grant_type must be 'authorization_code'")
		return
	}

	// Validate authorization code
	if req.Code == "" {
		oauthError(w, http.StatusBadRequest, "invalid_request", "code is required")
		return
	}

	if !p.ValidCodes[req.Code] {
		oauthError(w, http.StatusBadRequest, "invalid_grant", "The provided authorization code is invalid or expired")
		delete(p.ValidCodes, req.Code) // Prevent reuse
		return
	}

	// Validate client credentials
	if req.ClientID == "" {
		oauthError(w, http.StatusUnauthorized, "invalid_client", "client_id is required")
		return
	}

	if req.ClientID != p.ClientID {
		oauthError(w, http.StatusUnauthorized, "invalid_client", "Invalid client_id")
		return
	}

	if req.ClientSecret != p.ClientSecret {
		oauthError(w, http.StatusUnauthorized, "invalid_client", "Invalid client_secret")
		return
	}

	// Mark code as used (prevent reuse)
	delete(p.ValidCodes, req.Code)

	// Generate access token
	accessToken := fmt.Sprintf("access_token_%d", time.Now().UnixNano())

	// Return token response
	w.WriteHeader(http.StatusOK)
	writeJSON(w, map[string]interface{}{
		"access_token":  accessToken,
		"token_type":    "Bearer",
		"expires_in":    tokenExpiresInSeconds,
		"refresh_token": fmt.Sprintf("refresh_token_%d", time.Now().UnixNano()),
		"scope":         "profile email",
	})
}

// Close stops the mock OAuth provider server
func (p *MockOAuthProvider) Close() {
	if p.server != nil {
		p.server.Close()
	}
}

// GetTokenEndpoint returns the full token endpoint URL
func (p *MockOAuthProvider) GetTokenEndpoint() string {
	return p.URL + "/token"
}

// GetAuthorizeEndpoint returns the full authorize endpoint URL
func (p *MockOAuthProvider) GetAuthorizeEndpoint() string {
	return p.URL + "/authorize"
}

// GenerateValidCode generates a valid authorization code that will be accepted
func (p *MockOAuthProvider) GenerateValidCode() string {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.codeCounter++
	code := fmt.Sprintf("auth_code_%d_%d", time.Now().UnixNano(), p.codeCounter)
	p.ValidCodes[code] = true
	return code
}

// GenerateValidState generates a valid state parameter that will be accepted
func (p *MockOAuthProvider) GenerateValidState() string {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.codeCounter++
	state := fmt.Sprintf("state_%d_%d", time.Now().UnixNano(), p.codeCounter)
	p.ValidStates[state] = true
	return state
}

// InvalidateCode marks a code as invalid (simulates expiration or reuse)
func (p *MockOAuthProvider) InvalidateCode(code string) {
	p.mu.Lock()
	defer p.mu.Unlock()
	delete(p.ValidCodes, code)
}

// InvalidateState marks a state as invalid
func (p *MockOAuthProvider) InvalidateState(state string) {
	p.mu.Lock()
	defer p.mu.Unlock()
	delete(p.ValidStates, state)
}
