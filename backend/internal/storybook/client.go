package storybook

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"golang.org/x/time/rate"
)

// Client configuration constants
const (
	defaultHTTPTimeoutSeconds = 30
	defaultRateLimitRequests  = 10
)

// Client provides methods to interact with Storybook's API.
type Client struct {
	baseURL     string
	httpClient  *http.Client
	rateLimiter *rate.Limiter
	maxRetries  int
}

// NewClient creates a new Storybook client.
func NewClient(config *Config) (*Client, error) {
	if config.BaseURL == "" {
		return nil, errors.New("storybook base URL is required")
	}

	timeout := time.Duration(config.TimeoutSeconds) * time.Second
	if timeout == 0 {
		timeout = defaultHTTPTimeoutSeconds * time.Second
	}

	maxRetries := config.MaxRetries
	if maxRetries == 0 {
		maxRetries = 3
	}

	return &Client{
		baseURL: config.BaseURL,
		httpClient: &http.Client{
			Timeout: timeout,
		},
		rateLimiter: rate.NewLimiter(rate.Limit(defaultRateLimitRequests), 1),
		maxRetries:  maxRetries,
	}, nil
}

// FetchStoriesJSON fetches the stories.json index from Storybook.
func (c *Client) FetchStoriesJSON(ctx context.Context) (*StoriesResponse, error) {
	if err := c.rateLimiter.Wait(ctx); err != nil {
		return nil, fmt.Errorf("rate limiter error: %w", err)
	}

	url := c.baseURL + "/stories.json"
	var resp *StoriesResponse
	var err error

	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		resp, err = c.getStoriesJSON(ctx, url)
		if err == nil {
			return resp, nil
		}

		if !isRetryableError(err) {
			return nil, err
		}

		if attempt < c.maxRetries {
			shift := min(attempt, 30)
			backoff := time.Duration(1<<shift) * time.Second
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(backoff):
				continue
			}
		}
	}

	return nil, fmt.Errorf("failed to fetch stories after %d retries: %w", c.maxRetries, err)
}

// getStoriesJSON performs the actual HTTP request to fetch stories.json.
func (c *Client) getStoriesJSON(ctx context.Context, url string) (*StoriesResponse, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")
	req.Header.Set("User-Agent", "TracerTM-Storybook-Indexer/1.0")

	httpResp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("HTTP request failed: %w", err)
	}
	defer func() {
		if cerr := httpResp.Body.Close(); cerr != nil {
			slog.Warn("failed to close storybook response body", "error", cerr)
		}
	}()

	if httpResp.StatusCode != http.StatusOK {
		body, readErr := io.ReadAll(httpResp.Body)
		if readErr != nil {
			return nil, fmt.Errorf("unexpected status code %d (failed to read body: %w)", httpResp.StatusCode, readErr)
		}
		return nil, fmt.Errorf("unexpected status code %d: %s", httpResp.StatusCode, string(body))
	}

	respBody, err := io.ReadAll(httpResp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	var resp StoriesResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("failed to parse stories.json: %w", err)
	}

	return &resp, nil
}

// FetchComponentMetadata fetches metadata for a specific component story.
func (c *Client) FetchComponentMetadata(ctx context.Context, storyID string) (*StoryEntry, error) {
	stories, err := c.FetchStoriesJSON(ctx)
	if err != nil {
		return nil, err
	}

	if story, ok := stories.Stories[storyID]; ok {
		return &story, nil
	}

	return nil, fmt.Errorf("story not found: %s", storyID)
}

// ExtractComponentName extracts the component name from story title.
func (c *Client) ExtractComponentName(title string) string {
	// Parse title like "Components/Button" -> "Button"
	// This is a simple implementation; can be enhanced based on naming conventions
	if title == "" {
		return ""
	}

	// Handle titles with path separators
	parts := splitPath(title)
	if len(parts) > 0 {
		return parts[len(parts)-1]
	}

	return title
}

// ExtractCategory extracts the category from story title.
func (c *Client) ExtractCategory(title string) string {
	// Parse title like "Components/Button/Default" -> "Components/Button"
	// or "Components/Button" -> "Components"
	if title == "" {
		return ""
	}

	parts := splitPath(title)
	if len(parts) > 1 {
		// Return all but the last part
		return joinPath(parts[:len(parts)-1])
	}

	if len(parts) == 1 {
		return parts[0]
	}

	return ""
}

// ExtractPropsFromArgTypes converts ArgTypes to a structured PropSchema slice.
func (c *Client) ExtractPropsFromArgTypes(argTypes map[string]ArgType) []PropSchema {
	props := make([]PropSchema, 0, len(argTypes))

	for name, argType := range argTypes {
		prop := PropSchema{
			Name:         name,
			Description:  argType.Description,
			Required:     argType.Required,
			DefaultValue: argType.DefaultValue,
			Category:     "prop",
		}

		// Extract type information
		if argType.Type != nil {
			prop.Type = argType.Type.Name
		}

		// Extract options if available
		if len(argType.Options) > 0 {
			prop.Options = argType.Options
		}

		// Extract category from table info
		if argType.Table != nil && argType.Table.Category != "" {
			prop.Category = argType.Table.Category
		}

		props = append(props, prop)
	}

	return props
}

// ExtractComponentDocumentation extracts documentation from story parameters.
func (c *Client) ExtractComponentDocumentation(story *StoryEntry) string {
	// Try to extract documentation from various sources
	if story.Parameters != nil {
		// Check for docs.description
		if docs, ok := story.Parameters["docs"]; ok {
			if docsMap, ok := docs.(map[string]interface{}); ok {
				if desc, ok := docsMap["description"]; ok {
					if descStr, ok := desc.(string); ok {
						return descStr
					}
				}
			}
		}
	}

	return ""
}

// GetScreenshotURL constructs a screenshot URL from Storybook parameters.
func (c *Client) GetScreenshotURL(story *StoryEntry, storyID string) string {
	// Common screenshot patterns in Storybook
	if story.Parameters != nil {
		// Check for screenshot in parameters
		if screenshot, ok := story.Parameters["screenshot"]; ok {
			if screenshotStr, ok := screenshot.(string); ok {
				return screenshotStr
			}
		}
	}

	// Default screenshot URL pattern for Storybook
	// This assumes Storybook is hosted at baseURL
	return c.baseURL + "/?path=/story/" + storyID + "--docs"
}

// GetStorybookVersion retrieves the version of the Storybook instance.
func (c *Client) GetStorybookVersion(ctx context.Context) (string, error) {
	stories, err := c.FetchStoriesJSON(ctx)
	if err != nil {
		return "", err
	}

	if stories.Metadata.Version != "" {
		return stories.Metadata.Version, nil
	}

	return "unknown", nil
}

// HealthCheck verifies the Storybook instance is accessible.
func (c *Client) HealthCheck(ctx context.Context) error {
	_, err := c.FetchStoriesJSON(ctx)
	if err != nil {
		return fmt.Errorf("storybook health check failed: %w", err)
	}

	return nil
}

// Helper functions

// isRetryableError determines if an error is retryable.
func isRetryableError(err error) bool {
	// Network timeouts and temporary errors are retryable
	if errors.Is(err, context.DeadlineExceeded) || errors.Is(err, context.Canceled) {
		return false
	}

	// HTTP errors that are retryable
	if httpErr, ok := err.(interface{ Timeout() bool }); ok && httpErr.Timeout() {
		return true
	}

	// Connection errors are typically retryable
	errStr := err.Error()
	return errStr == "connection refused" || errStr == "no such host"
}

// splitPath splits a path string by "/" or "/"
func splitPath(path string) []string {
	if path == "" {
		return []string{}
	}

	// Handle both "/" and custom separators
	parts := make([]string, 0)
	current := ""

	for _, ch := range path {
		if ch == '/' || ch == '\\' {
			if current != "" {
				parts = append(parts, current)
				current = ""
			}
		} else {
			current += string(ch)
		}
	}

	if current != "" {
		parts = append(parts, current)
	}

	return parts
}

// joinPath joins path parts with "/"
func joinPath(parts []string) string {
	return strings.Join(parts, "/")
}
