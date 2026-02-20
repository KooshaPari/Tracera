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
	"sort"
	"strings"
	"time"

	"golang.org/x/time/rate"
)

const (
	// VoyageRerankAPIURL is the base URL for Voyage rerank requests.
	VoyageRerankAPIURL = "https://api.voyageai.com/v1/rerank"
	// VoyageRerankMax is the maximum documents per request.
	VoyageRerankMax = 1000 // Maximum documents per request
	// VoyageRerankContext is the maximum context length per document.
	VoyageRerankContext = 16000 // Maximum context length per document
	// ModelRerank25 is the rerank-2.5 model.
	ModelRerank25 = "rerank-2.5"
	// ModelRerank2Lite is the rerank-2-lite model.
	ModelRerank2Lite = "rerank-2-lite"

	rerankDefaultRateLimit  = 300
	rerankDefaultMaxRetries = 3
	rerankDefaultTimeout    = 60 * time.Second
	rerankRateDivisor       = 60
	rerankDefaultCostPer1M  = 0.05
	rerankTokensPerMillion  = 1_000_000
	rerankCostRerank25      = 0.05
	rerankCostRerank2Lite   = 0.02
	asciiLowerDelta         = 32
)

// Model pricing per 1M tokens.
func rerankCostPer1M(model string) float64 {
	switch model {
	case ModelRerank25:
		return rerankCostRerank25
	case ModelRerank2Lite:
		return rerankCostRerank2Lite
	default:
		return 0
	}
}

// Document represents a document to be reranked
type Document struct {
	ID       string                 `json:"id,omitempty"`       // Optional document ID
	Text     string                 `json:"text"`               // Document text
	Metadata map[string]interface{} `json:"metadata,omitempty"` // Optional metadata
}

// RerankRequest represents a reranking request
type RerankRequest struct {
	Query           string     `json:"query"`                      // Search query
	Documents       []Document `json:"documents"`                  // Documents to rerank
	Model           string     `json:"model,omitempty"`            // Model to use
	TopK            int        `json:"top_k,omitempty"`            // Number of top results to return
	ReturnDocuments bool       `json:"return_documents,omitempty"` // Return document text in results
}

// RerankResult represents a single reranked document
type RerankResult struct {
	Index          int                    `json:"index"`              // Original document index
	Document       *Document              `json:"document,omitempty"` // Document (if requested)
	RelevanceScore float64                `json:"relevance_score"`    // Relevance score (0-1)
	Metadata       map[string]interface{} `json:"metadata,omitempty"` // Original metadata
}

// RerankResponse represents the response from reranking
type RerankResponse struct {
	Results []RerankResult `json:"results"` // Reranked results
	Model   string         `json:"model"`   // Model used
	Usage   TokenUsage     `json:"usage"`   // Token usage
}

// voyageRerankRequest represents the API request structure
type voyageRerankRequest struct {
	Query           string   `json:"query"`                      // Search query
	Documents       []string `json:"documents"`                  // Document texts
	Model           string   `json:"model,omitempty"`            // Model name
	TopK            int      `json:"top_k,omitempty"`            // Number of results
	ReturnDocuments bool     `json:"return_documents,omitempty"` // Return documents
	Truncate        bool     `json:"truncate,omitempty"`         // Auto-truncate
}

// voyageRerankResponse represents the API response structure
type voyageRerankResponse struct {
	Object string `json:"object"`
	Data   []struct {
		Index          int     `json:"index"`
		RelevanceScore float64 `json:"relevance_score"`
		Document       string  `json:"document,omitempty"`
	} `json:"data"`
	Model string `json:"model"`
	Usage struct {
		TotalTokens int `json:"total_tokens"`
	} `json:"usage"`
}

// Reranker handles document reranking using VoyageAI
type Reranker struct {
	apiKey       string
	httpClient   *http.Client
	rateLimiter  *rate.Limiter
	defaultModel string
	maxRetries   int
}

// NewReranker creates a new reranker instance
func NewReranker(apiKey string, model string, rateLimitPerMinute int, maxRetries int) (*Reranker, error) {
	if apiKey == "" {
		return nil, errors.New("VoyageAI API key is required for reranking")
	}

	if model == "" {
		model = ModelRerank25
	}

	if rateLimitPerMinute == 0 {
		rateLimitPerMinute = rerankDefaultRateLimit // Default for VoyageAI
	}

	if maxRetries == 0 {
		maxRetries = rerankDefaultMaxRetries
	}

	return &Reranker{
		apiKey: apiKey,
		httpClient: &http.Client{
			Timeout: rerankDefaultTimeout,
		},
		rateLimiter:  rate.NewLimiter(rate.Limit(rateLimitPerMinute)/rerankRateDivisor, 1),
		defaultModel: model,
		maxRetries:   maxRetries,
	}, nil
}

// Rerank reranks documents based on query relevance
func (r *Reranker) Rerank(ctx context.Context, req *RerankRequest) (*RerankResponse, error) {
	if err := r.validateRerankRequest(req); err != nil {
		return nil, err
	}

	if len(req.Documents) == 0 {
		return r.emptyResponse(), nil
	}

	model := r.resolveModel(req)
	if err := r.waitRateLimit(ctx); err != nil {
		return nil, err
	}

	voyageReq := buildVoyageRerankRequest(req, model)
	resp, err := r.callWithRetries(ctx, &voyageReq)
	if err != nil {
		return nil, err
	}

	results := buildRerankResults(req, resp)
	usage := buildRerankUsage(model, resp)

	return &RerankResponse{
		Results: results,
		Model:   resp.Model,
		Usage:   usage,
	}, nil
}

func (r *Reranker) validateRerankRequest(req *RerankRequest) error {
	if req.Query == "" {
		return errors.New("query is required for reranking")
	}

	if len(req.Documents) > VoyageRerankMax {
		return fmt.Errorf("too many documents: %d (max: %d)", len(req.Documents), VoyageRerankMax)
	}

	return nil
}

func (r *Reranker) emptyResponse() *RerankResponse {
	return &RerankResponse{
		Results: []RerankResult{},
		Model:   r.defaultModel,
		Usage:   TokenUsage{},
	}
}

func (r *Reranker) resolveModel(req *RerankRequest) string {
	if req.Model == "" {
		return r.defaultModel
	}

	return req.Model
}

func (r *Reranker) waitRateLimit(ctx context.Context) error {
	if err := r.rateLimiter.Wait(ctx); err != nil {
		return fmt.Errorf("rate limiter error: %w", err)
	}

	return nil
}

func buildVoyageRerankRequest(req *RerankRequest, model string) voyageRerankRequest {
	docTexts := make([]string, len(req.Documents))
	for i, doc := range req.Documents {
		docTexts[i] = doc.Text
	}

	return voyageRerankRequest{
		Query:           req.Query,
		Documents:       docTexts,
		Model:           model,
		TopK:            req.TopK,
		ReturnDocuments: req.ReturnDocuments,
		Truncate:        true, // Auto-truncate to 16K context
	}
}

func (r *Reranker) callWithRetries(ctx context.Context, voyageReq *voyageRerankRequest) (*voyageRerankResponse, error) {
	var resp *voyageRerankResponse
	var err error

	for attempt := 0; attempt <= r.maxRetries; attempt++ {
		resp, err = r.callAPI(ctx, voyageReq)
		if err == nil {
			return resp, nil
		}

		if !isRetryableError(err) {
			return nil, err
		}

		if attempt < r.maxRetries {
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

	return nil, fmt.Errorf("reranking failed after %d retries: %w", r.maxRetries, err)
}

func buildRerankResults(req *RerankRequest, resp *voyageRerankResponse) []RerankResult {
	results := make([]RerankResult, len(resp.Data))
	for i, data := range resp.Data {
		result := RerankResult{
			Index:          data.Index,
			RelevanceScore: data.RelevanceScore,
		}

		if data.Index < len(req.Documents) {
			if req.ReturnDocuments {
				result.Document = &req.Documents[data.Index]
			}
			result.Metadata = req.Documents[data.Index].Metadata
		}

		results[i] = result
	}

	return results
}

func buildRerankUsage(model string, resp *voyageRerankResponse) TokenUsage {
	costPer1M := rerankCostPer1M(model)
	if costPer1M == 0 {
		costPer1M = rerankDefaultCostPer1M // Default
	}
	cost := float64(resp.Usage.TotalTokens) * costPer1M / rerankTokensPerMillion

	return TokenUsage{
		PromptTokens: resp.Usage.TotalTokens,
		TotalTokens:  resp.Usage.TotalTokens,
		CostUSD:      cost,
	}
}

// callAPI makes the actual HTTP request to VoyageAI rerank API
func (r *Reranker) callAPI(ctx context.Context, req *voyageRerankRequest) (*voyageRerankResponse, error) {
	// Marshal request
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Create HTTP request
	httpReq, err := http.NewRequestWithContext(
		ctx,
		http.MethodPost,
		VoyageRerankAPIURL,
		bytes.NewBuffer(body),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+r.apiKey)

	// Execute request
	httpResp, err := r.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("HTTP request failed: %w", err)
	}
	defer func() {
		if err := httpResp.Body.Close(); err != nil {
			slog.Error("failed to close reranker response body", "error", err)
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
	var resp voyageRerankResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &resp, nil
}

// RerankSearchResults is a helper to rerank search results
func (r *Reranker) RerankSearchResults(_ context.Context, _ string, results interface{}, _ int) (interface{}, error) {
	// This is a generic helper that can be customized based on your search result structure
	// For now, it's a placeholder for the integration with search.go
	return results, nil
}

// LocalReranker provides simple local reranking without API calls
type LocalReranker struct{}

// NewLocalReranker creates a new local reranker
func NewLocalReranker() *LocalReranker {
	return &LocalReranker{}
}

// Rerank performs simple local reranking based on text similarity
func (l *LocalReranker) Rerank(_ context.Context, req *RerankRequest) (*RerankResponse, error) {
	// Simple local reranking based on keyword overlap
	// This is a basic implementation for fallback when API is unavailable

	results := make([]RerankResult, len(req.Documents))

	for i, doc := range req.Documents {
		score := calculateSimpleScore(req.Query, doc.Text)
		results[i] = RerankResult{
			Index:          i,
			RelevanceScore: score,
			Metadata:       doc.Metadata,
		}

		if req.ReturnDocuments {
			results[i].Document = &doc
		}
	}

	// Sort by score descending
	sort.Slice(results, func(i, j int) bool {
		return results[i].RelevanceScore > results[j].RelevanceScore
	})

	// Apply TopK if specified
	if req.TopK > 0 && req.TopK < len(results) {
		results = results[:req.TopK]
	}

	return &RerankResponse{
		Results: results,
		Model:   "local",
		Usage:   TokenUsage{},
	}, nil
}

// calculateSimpleScore calculates a simple similarity score
func calculateSimpleScore(query, text string) float64 {
	// Very basic keyword matching for local fallback
	// In production, you might use BM25 or TF-IDF

	queryWords := tokenize(query)
	textWords := tokenize(text)

	if len(queryWords) == 0 || len(textWords) == 0 {
		return 0.0
	}

	matches := 0
	for _, qw := range queryWords {
		for _, tw := range textWords {
			if qw == tw {
				matches++
				break
			}
		}
	}

	return float64(matches) / float64(len(queryWords))
}

// tokenize splits text into lowercase words
func tokenize(text string) []string {
	// Simple tokenization - split on whitespace and convert to lowercase
	words := make([]string, 0)
	current := ""

	for _, char := range text {
		if char == ' ' || char == '\t' || char == '\n' || char == '\r' {
			if current != "" {
				words = append(words, toLower(current))
				current = ""
			}
		} else {
			current += string(char)
		}
	}

	if current != "" {
		words = append(words, toLower(current))
	}

	return words
}

// toLower converts a string to lowercase
func toLower(s string) string {
	var builder strings.Builder
	builder.Grow(len(s))
	for _, char := range s {
		if char >= 'A' && char <= 'Z' {
			builder.WriteByte(byte(char + asciiLowerDelta))
		} else {
			builder.WriteRune(char)
		}
	}
	return builder.String()
}
