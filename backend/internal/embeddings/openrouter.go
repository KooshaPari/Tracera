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
	// OpenRouterAPIBaseURL is the base URL for OpenRouter API requests.
	OpenRouterAPIBaseURL = "https://openrouter.ai/api/v1"
	// OpenRouterMaxBatch is the maximum number of texts per request.
	OpenRouterMaxBatch           = 100 // Conservative batch size
	openRouterRateDivisor        = 60
	openRouterDefaultTimeout     = 60 * time.Second
	openRouterDefaultMaxRetries  = 3
	openRouterDefaultRateLimit   = 100
	openRouterTokensPerMillion   = 1_000_000
	openRouterDimsLarge          = 3072
	openRouterDimsDefault        = 1536
	openRouterCostEmbeddingSmall = 0.02
	openRouterCostEmbeddingLarge = 0.13
	openRouterCostEmbeddingAda   = 0.10
)

// OpenRouter popular embedding models
const (
	ModelTextEmbedding3Small = "openai/text-embedding-3-small" // 1536 dims, $0.02/1M
	ModelTextEmbedding3Large = "openai/text-embedding-3-large" // 3072 dims, $0.13/1M
	ModelTextEmbeddingAda002 = "openai/text-embedding-ada-002" // 1536 dims, $0.10/1M
)

// OpenRouterProvider implements the Provider interface for OpenRouter
type OpenRouterProvider struct {
	apiKey       string
	httpClient   *http.Client
	rateLimiter  *rate.Limiter
	defaultModel string
	dimensions   int
	maxRetries   int
}

// openRouterRequest represents the API request structure (OpenAI-compatible)
type openRouterRequest struct {
	Input          interface{} `json:"input"`                     // String or array of strings
	Model          string      `json:"model"`                     // Model name
	EncodingFormat string      `json:"encoding_format,omitempty"` // "float" or "base64"
}

// openRouterResponse represents the API response structure (OpenAI-compatible)
type openRouterResponse struct {
	Object string `json:"object"`
	Data   []struct {
		Object    string    `json:"object"`
		Embedding []float32 `json:"embedding"`
		Index     int       `json:"index"`
	} `json:"data"`
	Model string `json:"model"`
	Usage struct {
		PromptTokens int `json:"prompt_tokens"`
		TotalTokens  int `json:"total_tokens"`
	} `json:"usage"`
}

// openRouterErrorResponse represents error responses from the API
type openRouterErrorResponse struct {
	Error struct {
		Message string `json:"message"`
		Type    string `json:"type"`
		Code    string `json:"code"`
	} `json:"error"`
}

// NewOpenRouterProvider creates a new OpenRouter provider
func NewOpenRouterProvider(config *ProviderConfig) (*OpenRouterProvider, error) {
	if config.APIKey == "" {
		return nil, errors.New("OpenRouter API key is required")
	}

	defaultModel := config.DefaultModel
	if defaultModel == "" {
		defaultModel = ModelTextEmbedding3Small
	}

	dimensions := config.Dimensions
	if dimensions == 0 {
		// Default dimensions based on model
		switch defaultModel {
		case ModelTextEmbedding3Large:
			dimensions = openRouterDimsLarge
		case ModelTextEmbedding3Small, ModelTextEmbeddingAda002:
			dimensions = openRouterDimsDefault
		default:
			dimensions = openRouterDimsDefault
		}
	}

	timeout := time.Duration(config.TimeoutSeconds) * time.Second
	if timeout == 0 {
		timeout = openRouterDefaultTimeout
	}

	maxRetries := config.MaxRetries
	if maxRetries == 0 {
		maxRetries = openRouterDefaultMaxRetries
	}

	// Rate limiter (conservative default)
	rateLimit := config.RateLimitPerMinute
	if rateLimit == 0 {
		rateLimit = openRouterDefaultRateLimit // Conservative for OpenRouter
	}

	return &OpenRouterProvider{
		apiKey: config.APIKey,
		httpClient: &http.Client{
			Timeout: timeout,
		},
		rateLimiter:  rate.NewLimiter(rate.Limit(rateLimit)/openRouterRateDivisor, 1), // Per second
		defaultModel: defaultModel,
		dimensions:   dimensions,
		maxRetries:   maxRetries,
	}, nil
}

// Embed generates embeddings using OpenRouter
func (o *OpenRouterProvider) Embed(ctx context.Context, req *EmbeddingRequest) (*EmbeddingResponse, error) {
	if len(req.Texts) == 0 {
		return nil, errors.New("no texts provided for embedding")
	}

	model := o.resolveModel(req)

	// Handle batching if needed
	if len(req.Texts) > OpenRouterMaxBatch {
		return o.embedBatched(ctx, req)
	}

	if err := o.waitRateLimit(ctx); err != nil {
		return nil, err
	}

	orReq := buildOpenRouterRequest(req.Texts, model)
	resp, err := o.callWithRetries(ctx, &orReq)
	if err != nil {
		return nil, err
	}

	return o.buildEmbeddingResponse(resp, model), nil
}

func (o *OpenRouterProvider) resolveModel(req *EmbeddingRequest) string {
	if req.Model == "" {
		return o.defaultModel
	}

	return req.Model
}

func (o *OpenRouterProvider) waitRateLimit(ctx context.Context) error {
	if err := o.rateLimiter.Wait(ctx); err != nil {
		return fmt.Errorf("rate limiter error: %w", err)
	}

	return nil
}

func buildOpenRouterRequest(texts []string, model string) openRouterRequest {
	return openRouterRequest{
		Input:          texts,
		Model:          model,
		EncodingFormat: "float",
	}
}

func (o *OpenRouterProvider) callWithRetries(ctx context.Context, orReq *openRouterRequest) (*openRouterResponse, error) {
	var resp *openRouterResponse
	var err error

	for attempt := 0; attempt <= o.maxRetries; attempt++ {
		resp, err = o.callAPI(ctx, orReq)
		if err == nil {
			return resp, nil
		}

		if !isRetryableError(err) {
			return nil, err
		}

		if attempt < o.maxRetries {
			shift := min(attempt, 30) // cap shift to prevent overflow
			backoff := time.Duration(1<<shift) * time.Second
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(backoff):
				continue
			}
		}
	}

	return nil, fmt.Errorf("failed after %d retries: %w", o.maxRetries, err)
}

func (o *OpenRouterProvider) buildEmbeddingResponse(resp *openRouterResponse, model string) *EmbeddingResponse {
	embeddings := make([]EmbeddingVector, len(resp.Data))
	for _, data := range resp.Data {
		embeddings[data.Index] = data.Embedding
	}

	cost := o.estimateCost(model, resp.Usage.TotalTokens)

	return &EmbeddingResponse{
		Embeddings: embeddings,
		Model:      resp.Model,
		Usage: TokenUsage{
			PromptTokens: resp.Usage.PromptTokens,
			TotalTokens:  resp.Usage.TotalTokens,
			CostUSD:      cost,
		},
	}
}

// embedBatched handles large embedding requests by batching
func (o *OpenRouterProvider) embedBatched(ctx context.Context, req *EmbeddingRequest) (*EmbeddingResponse, error) {
	batches := BatchRequest(req.Texts, OpenRouterMaxBatch)
	responses := make([]*EmbeddingResponse, 0, len(batches))

	for _, batch := range batches {
		batchReq := &EmbeddingRequest{
			Texts:     batch,
			Model:     req.Model,
			InputType: req.InputType,
		}

		resp, err := o.Embed(ctx, batchReq)
		if err != nil {
			return nil, fmt.Errorf("batch embedding failed: %w", err)
		}

		responses = append(responses, resp)
	}

	return MergeResponses(responses), nil
}

// callAPI makes the actual HTTP request to OpenRouter
func (o *OpenRouterProvider) callAPI(ctx context.Context, req *openRouterRequest) (*openRouterResponse, error) {
	// Marshal request
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Create HTTP request
	httpReq, err := http.NewRequestWithContext(
		ctx,
		http.MethodPost,
		OpenRouterAPIBaseURL+"/embeddings",
		bytes.NewBuffer(body),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+o.apiKey)
	httpReq.Header.Set("HTTP-Referer", "https://tracertm.dev") // Optional: for rankings
	httpReq.Header.Set("X-Title", "TraceRTM")                  // Optional: for rankings

	// Execute request
	httpResp, err := o.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("HTTP request failed: %w", err)
	}
	defer func() {
		if cerr := httpResp.Body.Close(); cerr != nil {
			slog.Warn("failed to close HTTP response body", "error", cerr)
		}
	}()

	// Read response
	respBody, err := io.ReadAll(httpResp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Check for errors
	if httpResp.StatusCode != http.StatusOK {
		var errResp openRouterErrorResponse
		if err := json.Unmarshal(respBody, &errResp); err != nil {
			return nil, fmt.Errorf("API error (status %d): %s", httpResp.StatusCode, string(respBody))
		}
		return nil, fmt.Errorf("API error: %s (type: %s)", errResp.Error.Message, errResp.Error.Type)
	}

	// Parse success response
	var resp openRouterResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &resp, nil
}

// estimateCost estimates the cost based on model and tokens
func (o *OpenRouterProvider) estimateCost(model string, tokens int) float64 {
	// Pricing per 1M tokens
	var costPer1M float64
	switch model {
	case ModelTextEmbedding3Small:
		costPer1M = openRouterCostEmbeddingSmall
	case ModelTextEmbedding3Large:
		costPer1M = openRouterCostEmbeddingLarge
	case ModelTextEmbeddingAda002:
		costPer1M = openRouterCostEmbeddingAda
	default:
		costPer1M = openRouterCostEmbeddingAda // Default estimate
	}

	return float64(tokens) * costPer1M / openRouterTokensPerMillion
}

// GetDimensions returns the embedding dimensionality
func (o *OpenRouterProvider) GetDimensions() int {
	return o.dimensions
}

// GetName returns the provider name
func (o *OpenRouterProvider) GetName() string {
	return "OpenRouter"
}

// GetDefaultModel returns the default model
func (o *OpenRouterProvider) GetDefaultModel() string {
	return o.defaultModel
}

// HealthCheck verifies the API is accessible
func (o *OpenRouterProvider) HealthCheck(ctx context.Context) error {
	// Try embedding a simple text
	req := &EmbeddingRequest{
		Texts:     []string{"health check"},
		Model:     o.defaultModel,
		InputType: "",
	}

	_, err := o.Embed(ctx, req)
	if err != nil {
		return fmt.Errorf("OpenRouter health check failed: %w", err)
	}

	return nil
}
