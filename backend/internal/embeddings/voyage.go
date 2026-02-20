package embeddings

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"time"

	"golang.org/x/time/rate"
)

const (
	// VoyageAPIBaseURL is the base URL for Voyage API requests.
	VoyageAPIBaseURL = "https://api.voyageai.com/v1"
	// VoyageMaxTokens is the maximum tokens per input.
	VoyageMaxTokens = 32000 // Maximum tokens per input
	// VoyageMaxBatch is the maximum texts per batch.
	VoyageMaxBatch = 128 // Maximum texts per batch
	// VoyageRateLimit is the requests per minute.
	VoyageRateLimit         = 300 // Requests per minute
	voyageDefaultDimensions = 1024
	voyageDefaultTimeout    = 60 * time.Second
	voyageDefaultMaxRetries = 3
	voyageRateDivisor       = 60
	voyageDefaultCostPer1M  = 0.06
	voyageCostLargePer1M    = 0.18
	voyageTokensPerMillion  = 1_000_000
)

// VoyageAI models and their specifications
const (
	ModelVoyage35         = "voyage-3.5"          // Latest general-purpose model
	ModelVoyage3Large     = "voyage-3-large"      // Highest quality model
	ModelVoyageMultimodal = "voyage-multimodal-3" // Multimodal support
	ModelVoyageCode3      = "voyage-code-3"       // Optimized for code
	ModelVoyageFinance2   = "voyage-finance-2"    // Finance domain
	ModelVoyageLaw2       = "voyage-law-2"        // Legal domain
)

// voyagePricingPerMillion returns the cost per 1M tokens for the given model.
func voyagePricingPerMillion(model string) float64 {
	switch model {
	case ModelVoyage3Large:
		return voyageCostLargePer1M
	case ModelVoyage35, ModelVoyageMultimodal, ModelVoyageCode3, ModelVoyageFinance2, ModelVoyageLaw2:
		return voyageDefaultCostPer1M
	default:
		return 0
	}
}

// VoyageProvider implements the Provider interface for VoyageAI
type VoyageProvider struct {
	apiKey       string
	httpClient   *http.Client
	rateLimiter  *rate.Limiter
	defaultModel string
	dimensions   int
	maxRetries   int
}

// voyageRequest represents the API request structure
type voyageRequest struct {
	Input     interface{} `json:"input"`                // String or array of strings
	Model     string      `json:"model"`                // Model name
	InputType string      `json:"input_type,omitempty"` // Optional: "document" or "query"
	Truncate  bool        `json:"truncate,omitempty"`   // Auto-truncate to max tokens
}

// voyageResponse represents the API response structure
type voyageResponse struct {
	Object string `json:"object"`
	Data   []struct {
		Object    string    `json:"object"`
		Embedding []float32 `json:"embedding"`
		Index     int       `json:"index"`
	} `json:"data"`
	Model string `json:"model"`
	Usage struct {
		TotalTokens int `json:"total_tokens"`
	} `json:"usage"`
}

// voyageErrorResponse represents error responses from the API
type voyageErrorResponse struct {
	Error struct {
		Message string `json:"message"`
		Type    string `json:"type"`
		Code    string `json:"code"`
	} `json:"error"`
}

// NewVoyageProvider creates a new VoyageAI provider
func NewVoyageProvider(config *ProviderConfig) (*VoyageProvider, error) {
	if config.APIKey == "" {
		return nil, errors.New("VoyageAI API key is required")
	}

	defaultModel := config.DefaultModel
	if defaultModel == "" {
		defaultModel = ModelVoyage35
	}

	dimensions := config.Dimensions
	if dimensions == 0 {
		dimensions = voyageDefaultDimensions // voyage-3.5 default
	}

	timeout := time.Duration(config.TimeoutSeconds) * time.Second
	if timeout == 0 {
		timeout = voyageDefaultTimeout
	}

	maxRetries := config.MaxRetries
	if maxRetries == 0 {
		maxRetries = voyageDefaultMaxRetries
	}

	// Rate limiter: 300 requests per minute
	rateLimit := config.RateLimitPerMinute
	if rateLimit == 0 {
		rateLimit = VoyageRateLimit
	}

	return &VoyageProvider{
		apiKey: config.APIKey,
		httpClient: &http.Client{
			Timeout: timeout,
		},
		rateLimiter:  rate.NewLimiter(rate.Limit(rateLimit)/voyageRateDivisor, 1), // Per second
		defaultModel: defaultModel,
		dimensions:   dimensions,
		maxRetries:   maxRetries,
	}, nil
}

// Embed generates embeddings using VoyageAI
func (v *VoyageProvider) Embed(ctx context.Context, req *EmbeddingRequest) (*EmbeddingResponse, error) {
	if len(req.Texts) == 0 {
		return nil, errors.New("no texts provided for embedding")
	}

	model := v.resolveModel(req)

	// Handle batching if needed
	if len(req.Texts) > VoyageMaxBatch {
		return v.embedBatched(ctx, req)
	}

	if err := v.waitRateLimit(ctx); err != nil {
		return nil, err
	}

	voyageReq := buildVoyageRequest(req, model)
	resp, err := v.callWithRetries(ctx, &voyageReq)
	if err != nil {
		return nil, err
	}

	return v.buildEmbeddingResponse(resp, model), nil
}

func (v *VoyageProvider) resolveModel(req *EmbeddingRequest) string {
	if req.Model == "" {
		return v.defaultModel
	}

	return req.Model
}

func (v *VoyageProvider) waitRateLimit(ctx context.Context) error {
	if err := v.rateLimiter.Wait(ctx); err != nil {
		return fmt.Errorf("rate limiter error: %w", err)
	}

	return nil
}

func buildVoyageRequest(req *EmbeddingRequest, model string) voyageRequest {
	return voyageRequest{
		Input:     req.Texts,
		Model:     model,
		InputType: req.InputType,
		Truncate:  true, // Auto-truncate to 32K tokens
	}
}

func (v *VoyageProvider) callWithRetries(ctx context.Context, voyageReq *voyageRequest) (*voyageResponse, error) {
	var resp *voyageResponse
	var err error

	for attempt := 0; attempt <= v.maxRetries; attempt++ {
		resp, err = v.callAPI(ctx, voyageReq)
		if err == nil {
			return resp, nil
		}

		if !isRetryableError(err) {
			return nil, err
		}

		if attempt < v.maxRetries {
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

	return nil, fmt.Errorf("failed after %d retries: %w", v.maxRetries, err)
}

func (v *VoyageProvider) buildEmbeddingResponse(resp *voyageResponse, model string) *EmbeddingResponse {
	embeddings := make([]EmbeddingVector, len(resp.Data))
	for _, data := range resp.Data {
		embeddings[data.Index] = data.Embedding
	}

	costPer1M := voyagePricingPerMillion(model)
	if costPer1M == 0 {
		costPer1M = voyageDefaultCostPer1M // Default
	}
	cost := float64(resp.Usage.TotalTokens) * costPer1M / voyageTokensPerMillion

	return &EmbeddingResponse{
		Embeddings: embeddings,
		Model:      resp.Model,
		Usage: TokenUsage{
			PromptTokens: resp.Usage.TotalTokens,
			TotalTokens:  resp.Usage.TotalTokens,
			CostUSD:      cost,
		},
	}
}

// embedBatched handles large embedding requests by batching
func (v *VoyageProvider) embedBatched(ctx context.Context, req *EmbeddingRequest) (*EmbeddingResponse, error) {
	batches := BatchRequest(req.Texts, VoyageMaxBatch)
	responses := make([]*EmbeddingResponse, 0, len(batches))

	for _, batch := range batches {
		batchReq := &EmbeddingRequest{
			Texts:     batch,
			Model:     req.Model,
			InputType: req.InputType,
		}

		resp, err := v.Embed(ctx, batchReq)
		if err != nil {
			return nil, fmt.Errorf("batch embedding failed: %w", err)
		}

		responses = append(responses, resp)
	}

	return MergeResponses(responses), nil
}

// callAPI makes the actual HTTP request to VoyageAI
func (v *VoyageProvider) callAPI(ctx context.Context, req *voyageRequest) (*voyageResponse, error) {
	// Marshal request
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Create HTTP request
	httpReq, err := http.NewRequestWithContext(
		ctx,
		http.MethodPost,
		VoyageAPIBaseURL+"/embeddings",
		bytes.NewBuffer(body),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+v.apiKey)

	// Execute request
	httpResp, err := v.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("HTTP request failed: %w", err)
	}
	defer func() {
		if err := httpResp.Body.Close(); err != nil {
			slog.Error("failed to close voyage response body", "error", err)
		}
	}()

	// Read response
	respBody, err := io.ReadAll(httpResp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Check for errors
	if httpResp.StatusCode != http.StatusOK {
		var errResp voyageErrorResponse
		if err := json.Unmarshal(respBody, &errResp); err != nil {
			return nil, fmt.Errorf("API error (status %d): %s", httpResp.StatusCode, string(respBody))
		}
		return nil, fmt.Errorf("API error: %s (type: %s)", errResp.Error.Message, errResp.Error.Type)
	}

	// Parse success response
	var resp voyageResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &resp, nil
}

// GetDimensions returns the embedding dimensionality
func (v *VoyageProvider) GetDimensions() int {
	return v.dimensions
}

// GetName returns the provider name
func (v *VoyageProvider) GetName() string {
	return "VoyageAI"
}

// GetDefaultModel returns the default model
func (v *VoyageProvider) GetDefaultModel() string {
	return v.defaultModel
}

// HealthCheck verifies the API is accessible
func (v *VoyageProvider) HealthCheck(ctx context.Context) error {
	// Try embedding a simple text
	req := &EmbeddingRequest{
		Texts:     []string{"health check"},
		Model:     v.defaultModel,
		InputType: "",
	}

	_, err := v.Embed(ctx, req)
	if err != nil {
		return fmt.Errorf("VoyageAI health check failed: %w", err)
	}

	return nil
}

// isRetryableError determines if an error should be retried
func isRetryableError(err error) bool {
	if err == nil {
		return false
	}

	errStr := err.Error()
	// Retry on rate limits and transient errors
	retryableErrors := []string{
		"rate limit",
		"timeout",
		"connection",
		"temporary",
		"502",
		"503",
		"504",
	}

	for _, retryable := range retryableErrors {
		if contains(errStr, retryable) {
			return true
		}
	}

	return false
}

// contains checks if a string contains a substring (case-insensitive)
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > len(substr) &&
		(s[:len(substr)] == substr || s[len(s)-len(substr):] == substr ||
			bytes.Contains([]byte(s), []byte(substr))))
}
