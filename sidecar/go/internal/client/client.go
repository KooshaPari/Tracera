// Package client provides the optional sidecar's HTTP boundary to Tracera.
package client

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

const (
	readinessPath    = "/readyz"
	maxResponseBytes = 1 << 20
)

// Client is a bounded HTTP client for the Tracera API. It is not enabled or
// constructed by the sidecar command unless the operator opts in.
type Client struct {
	baseURL    string
	httpClient *http.Client
}

// Response is the decoded response from a dispatch request.
type Response struct {
	StatusCode int
	Headers    http.Header
	Body       []byte
}

// HTTPError describes a non-2xx response, retaining only a bounded body.
type HTTPError struct {
	StatusCode int
	Body       string
}

func (e *HTTPError) Error() string {
	return fmt.Sprintf("tracera API returned HTTP %d: %s", e.StatusCode, e.Body)
}

// New constructs a client with a required positive timeout.
func New(baseURL string, timeout time.Duration) (*Client, error) {
	baseURL = strings.TrimRight(strings.TrimSpace(baseURL), "/")
	if baseURL == "" {
		return nil, errors.New("client base URL is required")
	}
	if timeout <= 0 {
		return nil, errors.New("client timeout must be positive")
	}
	return &Client{baseURL: baseURL, httpClient: &http.Client{Timeout: timeout}}, nil
}

// Dispatch sends an HTTP request to path. path must be absolute and the
// request body is JSON encoded when non-nil.
func (c *Client) Dispatch(ctx context.Context, method, path string, body any, requestID, idempotencyKey string) (Response, error) {
	if c == nil || c.httpClient == nil {
		return Response{}, errors.New("client is nil")
	}
	if !strings.HasPrefix(path, "/") {
		return Response{}, errors.New("client path must start with /")
	}
	if strings.TrimSpace(method) == "" {
		return Response{}, errors.New("client method is required")
	}
	var reader io.Reader
	if body != nil {
		payload, err := json.Marshal(body)
		if err != nil {
			return Response{}, fmt.Errorf("encode request body: %w", err)
		}
		reader = strings.NewReader(string(payload))
	}
	req, err := http.NewRequestWithContext(ctx, strings.ToUpper(method), c.baseURL+path, reader)
	if err != nil {
		return Response{}, fmt.Errorf("build request: %w", err)
	}
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	if requestID == "" {
		requestID = newRequestID()
	}
	req.Header.Set("X-Request-ID", requestID)
	if idempotencyKey != "" {
		req.Header.Set("Idempotency-Key", idempotencyKey)
	}
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return Response{}, fmt.Errorf("dispatch %s %s: %w", method, path, err)
	}
	defer resp.Body.Close()
	data, err := io.ReadAll(io.LimitReader(resp.Body, maxResponseBytes+1))
	if err != nil {
		return Response{}, fmt.Errorf("read response: %w", err)
	}
	if len(data) > maxResponseBytes {
		return Response{}, errors.New("response exceeds 1 MiB limit")
	}
	result := Response{StatusCode: resp.StatusCode, Headers: resp.Header.Clone(), Body: data}
	if resp.StatusCode < http.StatusOK || resp.StatusCode >= http.StatusMultipleChoices {
		return result, &HTTPError{StatusCode: resp.StatusCode, Body: string(data)}
	}
	return result, nil
}

// Readiness queries the canonical Tracera readiness endpoint.
func (c *Client) Readiness(ctx context.Context, requestID string) (Response, error) {
	return c.Dispatch(ctx, http.MethodGet, readinessPath, nil, requestID, "")
}

func newRequestID() string {
	b := make([]byte, 16)
	if _, err := rand.Read(b); err != nil {
		return "sidecar-request"
	}
	return hex.EncodeToString(b)
}
