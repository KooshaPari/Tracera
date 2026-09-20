package nodeapi

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// DesiredState is the converged service set a node should be running.
// Empty Services means no services assigned.
type DesiredState struct {
	// Generation increments on every control-plane change. The node echoes
	// it back when reporting status so the control plane can tell whether a
	// report is about the state it most recently published.
	Generation int `json:"generation"`
	// Services maps a service name to the image reference that should be
	// running. An entry with an empty image means "stop this service".
	Services map[string]string `json:"services"`
}

// Status is the report a node sends back after attempting convergence.
type Status struct {
	NodeID     string               `json:"node_id"`
	Generation int                  `json:"generation"`
	// Per-service result: "ok", "failed:<reason>", or "pending".
	Services   map[string]string    `json:"services"`
	UpdatedAt  time.Time            `json:"updated_at"`
}

// EnrollRequest is sent on first contact to claim a node identity.
type EnrollRequest struct {
	NodeID     string            `json:"node_id"`
	Caps       map[string]string `json:"caps,omitempty"`
	SidecarVer string            `json:"sidecar_version"`
}

// EnrollResponse is the control plane's ack with the assigned generation.
type EnrollResponse struct {
	Accepted   bool   `json:"accepted"`
	Generation int    `json:"generation"`
	Reason     string `json:"reason,omitempty"`
}

// APIError distinguishes a control-plane rejection from a transport failure.
type APIError struct {
	StatusCode int
	Body       string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("control plane returned HTTP %d: %s", e.StatusCode, e.Body)
}

// Client talks to the control plane (Cloudflare Worker). Bearer auth uses
// the enroll token issued per node.
type Client struct {
	BaseURL string
	Token   string
	HTTP    *http.Client
}

func NewClient(baseURL, token string, timeout time.Duration) *Client {
	return &Client{
		BaseURL: strings.TrimRight(baseURL, "/"),
		Token:   token,
		HTTP:    &http.Client{Timeout: timeout},
	}
}

func (c *Client) do(ctx context.Context, method, path string, body any, out any) error {
	var reader *bytes.Reader
	if body != nil {
		payload, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("encode request: %w", err)
		}
		reader = bytes.NewReader(payload)
	} else {
		reader = bytes.NewReader(nil)
	}
	req, err := http.NewRequestWithContext(ctx, method, c.BaseURL+path, reader)
	if err != nil {
		return fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.Token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return fmt.Errorf("control plane request: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()
	buf := new(bytes.Buffer)
	if _, err := buf.ReadFrom(resp.Body); err != nil {
		return fmt.Errorf("read response: %w", err)
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return &APIError{StatusCode: resp.StatusCode, Body: buf.String()}
	}
	if out == nil {
		return nil
	}
	if err := json.Unmarshal(buf.Bytes(), out); err != nil {
		return fmt.Errorf("decode response: %w", err)
	}
	return nil
}

// Enroll registers or re-acknowledges this node with the control plane.
func (c *Client) Enroll(ctx context.Context, req EnrollRequest) (*EnrollResponse, error) {
	var out EnrollResponse
	if err := c.do(ctx, http.MethodPost, "/fleet/enroll", req, &out); err != nil {
		return nil, err
	}
	if !out.Accepted {
		return nil, errors.New("enroll rejected: " + out.Reason)
	}
	return &out, nil
}

// FetchDesired pulls the service set this node should be running.
func (c *Client) FetchDesired(ctx context.Context, nodeID string) (*DesiredState, error) {
	var out DesiredState
	if err := c.do(ctx, http.MethodGet, "/fleet/desired?node_id="+url.QueryEscape(nodeID), nil, &out); err != nil {
		return nil, err
	}
	return &out, nil
}

// Report posts convergence results back to the control plane.
func (c *Client) Report(ctx context.Context, status Status) error {
	return c.do(ctx, http.MethodPost, "/fleet/report", status, nil)
}
