package oauth

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// testPost is a helper that uses http.NewRequestWithContext instead of http.Post.
func testPost(ctx context.Context, url, contentType string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, body)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", contentType)
	return http.DefaultClient.Do(req)
}

// testGet is a helper that uses http.NewRequestWithContext instead of client.Get.
func testGet(ctx context.Context, client *http.Client, url string) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	return client.Do(req)
}

func TestNewMockOAuthProvider(t *testing.T) {
	t.Run("creates provider with valid server", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		assert.NotEmpty(t, provider.URL)
		assert.NotEmpty(t, provider.ClientID)
		assert.NotEmpty(t, provider.ClientSecret)
		assert.NotNil(t, provider.ValidCodes)
		assert.NotNil(t, provider.ValidStates)
	})
}

func TestAuthorizeEndpoint(t *testing.T) {
	t.Run("generates authorization code", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		client := &http.Client{
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				return http.ErrUseLastResponse
			},
		}

		resp, err := testGet(t.Context(), client, fmt.Sprintf(
			"%s/authorize?client_id=%s&redirect_uri=http://localhost/callback&response_type=code&state=test_state",
			provider.URL, provider.ClientID,
		))
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		// Should redirect to redirect_uri with code
		assert.Equal(t, http.StatusFound, resp.StatusCode)
		location := resp.Header.Get("Location")
		assert.Contains(t, location, "code=auth_code_")
		assert.Contains(t, location, "state=test_state")
	})

	t.Run("rejects missing client_id", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		client := &http.Client{
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				return http.ErrUseLastResponse
			},
		}

		resp, err := testGet(t.Context(), client, provider.URL+"/authorize?redirect_uri=http://localhost/callback&response_type=code")
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
	})

	t.Run("rejects missing redirect_uri", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		client := &http.Client{
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				return http.ErrUseLastResponse
			},
		}

		resp, err := testGet(t.Context(), client, fmt.Sprintf(
			"%s/authorize?client_id=%s&response_type=code",
			provider.URL, provider.ClientID,
		))
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
	})

	t.Run("rejects invalid response_type", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		client := &http.Client{
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				return http.ErrUseLastResponse
			},
		}

		resp, err := testGet(t.Context(), client, fmt.Sprintf(
			"%s/authorize?client_id=%s&redirect_uri=http://localhost/callback&response_type=token",
			provider.URL, provider.ClientID,
		))
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
	})
}

func TestTokenEndpoint(t *testing.T) {
	t.Run("exchanges valid code for token", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		// Generate valid code
		code := provider.GenerateValidCode()

		// Exchange code for token
		reqBody := map[string]string{
			"grant_type":    "authorization_code",
			"code":          code,
			"client_id":     provider.ClientID,
			"client_secret": provider.ClientSecret,
			"redirect_uri":  "http://localhost/callback",
		}

		body, err := json.Marshal(reqBody)
		require.NoError(t, err)

		resp, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var tokenResp map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&tokenResp)
		require.NoError(t, err)

		assert.NotEmpty(t, tokenResp["access_token"])
		assert.Equal(t, "Bearer", tokenResp["token_type"])
		assert.InEpsilon(t, float64(3600), tokenResp["expires_in"], 1e-9)
	})

	t.Run("rejects invalid authorization code", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		reqBody := map[string]string{
			"grant_type":    "authorization_code",
			"code":          "invalid_code",
			"client_id":     provider.ClientID,
			"client_secret": provider.ClientSecret,
		}

		body, err := json.Marshal(reqBody)
		require.NoError(t, err)

		resp, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

		var errResp map[string]interface{}
		require.NoError(t, json.NewDecoder(resp.Body).Decode(&errResp))
		assert.Equal(t, "invalid_grant", errResp["error"])
	})

	t.Run("rejects invalid client_secret", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		code := provider.GenerateValidCode()

		reqBody := map[string]string{
			"grant_type":    "authorization_code",
			"code":          code,
			"client_id":     provider.ClientID,
			"client_secret": "wrong_secret",
		}

		body, err := json.Marshal(reqBody)
		require.NoError(t, err)

		resp, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	})

	t.Run("prevents code reuse", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		code := provider.GenerateValidCode()

		reqBody := map[string]string{
			"grant_type":    "authorization_code",
			"code":          code,
			"client_id":     provider.ClientID,
			"client_secret": provider.ClientSecret,
		}

		body, err := json.Marshal(reqBody)
		require.NoError(t, err)

		// First exchange succeeds
		resp1, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		if err := resp1.Body.Close(); err != nil {
			t.Logf("close error: %v", err)
		}
		assert.Equal(t, http.StatusOK, resp1.StatusCode)

		// Second exchange with same code fails
		body, err = json.Marshal(reqBody)
		require.NoError(t, err)

		resp2, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		defer func() {
			if err := resp2.Body.Close(); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		assert.Equal(t, http.StatusBadRequest, resp2.StatusCode)
	})

	t.Run("rejects invalid grant_type", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		code := provider.GenerateValidCode()

		reqBody := map[string]string{
			"grant_type":    "password",
			"code":          code,
			"client_id":     provider.ClientID,
			"client_secret": provider.ClientSecret,
		}

		body, err := json.Marshal(reqBody)
		require.NoError(t, err)

		resp, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

		var errResp map[string]interface{}
		require.NoError(t, json.NewDecoder(resp.Body).Decode(&errResp))
		assert.Equal(t, "unsupported_grant_type", errResp["error"])
	})
}

func TestGenerateValidCode(t *testing.T) {
	t.Run("generates unique codes", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		codes := make(map[string]bool)
		for i := 0; i < 5; i++ {
			code := provider.GenerateValidCode()
			assert.NotEmpty(t, code)
			codes[code] = true
		}

		// Should have generated 5 unique codes
		assert.Len(t, codes, 5)
	})

	t.Run("generated codes are valid", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		code := provider.GenerateValidCode()

		reqBody := map[string]string{
			"grant_type":    "authorization_code",
			"code":          code,
			"client_id":     provider.ClientID,
			"client_secret": provider.ClientSecret,
		}

		body, err := json.Marshal(reqBody)
		require.NoError(t, err)

		resp, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusOK, resp.StatusCode)
	})
}

func TestInvalidateCode(t *testing.T) {
	t.Run("invalidates code for reuse", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		code := provider.GenerateValidCode()

		// Invalidate the code
		provider.InvalidateCode(code)

		// Try to exchange should fail
		reqBody := map[string]string{
			"grant_type":    "authorization_code",
			"code":          code,
			"client_id":     provider.ClientID,
			"client_secret": provider.ClientSecret,
		}

		body, err := json.Marshal(reqBody)
		require.NoError(t, err)

		resp, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
	})
}

func TestGetEndpoints(t *testing.T) {
	t.Run("returns correct endpoints", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		tokenEndpoint := provider.GetTokenEndpoint()
		authorizeEndpoint := provider.GetAuthorizeEndpoint()

		assert.Contains(t, tokenEndpoint, "/token")
		assert.Contains(t, authorizeEndpoint, "/authorize")
		assert.Contains(t, tokenEndpoint, provider.URL)
		assert.Contains(t, authorizeEndpoint, provider.URL)
	})
}

func TestTokenResponseFormat(t *testing.T) {
	t.Run("response includes required fields", func(t *testing.T) {
		provider := NewMockOAuthProvider()
		defer provider.Close()

		code := provider.GenerateValidCode()

		reqBody := map[string]string{
			"grant_type":    "authorization_code",
			"code":          code,
			"client_id":     provider.ClientID,
			"client_secret": provider.ClientSecret,
		}

		body, err := json.Marshal(reqBody)
		require.NoError(t, err)

		resp, err := testPost(t.Context(),
			provider.GetTokenEndpoint(),
			"application/json",
			bytes.NewReader(body),
		)
		require.NoError(t, err)
		defer func() { require.NoError(t, resp.Body.Close()) }()

		var tokenResp map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&tokenResp)
		require.NoError(t, err)

		// Required fields
		assert.Contains(t, tokenResp, "access_token")
		assert.Contains(t, tokenResp, "token_type")
		assert.Contains(t, tokenResp, "expires_in")

		// Optional fields (should be present in mock)
		assert.Contains(t, tokenResp, "refresh_token")
		assert.Contains(t, tokenResp, "scope")

		// Type assertions
		_, ok := tokenResp["access_token"].(string)
		assert.True(t, ok, "access_token should be string")

		_, ok = tokenResp["expires_in"].(float64)
		assert.True(t, ok, "expires_in should be number")
	})
}
