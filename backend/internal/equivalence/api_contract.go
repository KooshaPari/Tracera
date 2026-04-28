package equivalence

import (
	"context"
	"regexp"
	"strings"
	"time"

	"github.com/google/uuid"
)

const apiContractDefaultConfidence = 0.9

// APIContractStrategy detects equivalences between frontend API calls and backend routes
type APIContractStrategy struct {
	routePatterns map[string]*regexp.Regexp
}

// NewAPIContractStrategy creates a new API contract matcher
func NewAPIContractStrategy() *APIContractStrategy {
	return &APIContractStrategy{
		routePatterns: make(map[string]*regexp.Regexp),
	}
}

// Name returns the strategy identifier.
func (strategy *APIContractStrategy) Name() StrategyType {
	return StrategyAPIContract
}

// DefaultConfidence returns the base confidence for API contracts.
func (strategy *APIContractStrategy) DefaultConfidence() float64 {
	return apiContractDefaultConfidence
}

// RequiresEmbeddings reports whether this strategy needs embeddings.
func (strategy *APIContractStrategy) RequiresEmbeddings() bool {
	return false
}

// Detect finds equivalences based on API contract matching.
func (strategy *APIContractStrategy) Detect(
	ctx context.Context,
	req *StrategyDetectionRequest,
) (*DetectionResult, error) {
	start := time.Now()
	result := &DetectionResult{
		Strategy: strategy.Name(),
		Links:    make([]Link, 0),
	}

	// Check if source has API-related metadata
	sourceEndpoint := strategy.extractEndpoint(req.SourceItem)
	if sourceEndpoint == "" {
		result.DurationMs = time.Since(start).Milliseconds()
		return result, nil
	}

	for _, candidate := range req.CandidatePool {
		select {
		case <-ctx.Done():
			result.Error = ctx.Err().Error()
			return result, ctx.Err()
		default:
		}

		if candidate.ID == req.SourceItem.ID {
			continue
		}
		result.ItemsScanned++

		candidateEndpoint := strategy.extractEndpoint(candidate)
		if candidateEndpoint == "" {
			continue
		}

		// Check for matching endpoints
		match, matchType := strategy.matchEndpoints(sourceEndpoint, candidateEndpoint)
		if match {
			link := strategy.buildLink(req, candidate.ID, sourceEndpoint, candidateEndpoint, matchType)
			result.Links = append(result.Links, link)
		}
	}

	result.DurationMs = time.Since(start).Milliseconds()
	return result, nil
}

func (strategy *APIContractStrategy) buildLink(
	req *StrategyDetectionRequest,
	targetID uuid.UUID,
	sourceEndpoint string,
	candidateEndpoint string,
	matchType string,
) Link {
	now := time.Now()
	confidence := strategy.DefaultConfidence()

	return Link{
		ID:           uuid.New(),
		ProjectID:    req.ProjectID,
		SourceItemID: req.SourceItem.ID,
		TargetItemID: targetID,
		LinkType:     "implements",
		Confidence:   confidence,
		Provenance:   strategy.Name(),
		Status:       StatusSuggested,
		Evidence: []Evidence{{
			Strategy:    strategy.Name(),
			Confidence:  confidence,
			Description: "API contract match: frontend call implements backend route",
			Details: map[string]any{
				"source_endpoint": sourceEndpoint,
				"target_endpoint": candidateEndpoint,
				"match_type":      matchType,
			},
			DetectedAt: now,
		}},
		CreatedAt: now,
		UpdatedAt: now,
	}
}

// extractEndpoint extracts API endpoint information from item metadata
func (strategy *APIContractStrategy) extractEndpoint(item *StrategyItemInfo) string {
	if item.Metadata == nil {
		return ""
	}

	// Check for explicit endpoint metadata
	if endpoint, ok := item.Metadata["endpoint"].(string); ok {
		return endpoint
	}
	if route, ok := item.Metadata["route"].(string); ok {
		return route
	}
	if url, ok := item.Metadata["url"].(string); ok {
		return url
	}

	// Check code reference for route patterns
	if item.CodeRef != nil {
		if strings.Contains(item.CodeRef.SymbolType, "route") ||
			strings.Contains(item.CodeRef.SymbolType, "handler") ||
			strings.Contains(item.CodeRef.SymbolType, "endpoint") {
			return item.CodeRef.SymbolName
		}
	}

	return ""
}

// matchEndpoints checks if two endpoints refer to the same API
func (strategy *APIContractStrategy) matchEndpoints(sourceEndpoint, targetEndpoint string) (bool, string) {
	// Normalize endpoints
	sourceEndpoint = strategy.normalizeEndpoint(sourceEndpoint)
	targetEndpoint = strategy.normalizeEndpoint(targetEndpoint)

	// Exact match
	if sourceEndpoint == targetEndpoint {
		return true, "exact"
	}

	// Pattern match (e.g., /api/users/:id matches /api/users/123)
	if strategy.patternMatch(sourceEndpoint, targetEndpoint) {
		return true, "pattern"
	}

	// Resource match (e.g., getUsers matches GET /users)
	if strategy.resourceMatch(sourceEndpoint, targetEndpoint) {
		return true, "resource"
	}

	return false, ""
}

// normalizeEndpoint normalizes an endpoint for comparison
func (strategy *APIContractStrategy) normalizeEndpoint(endpoint string) string {
	endpoint = strings.ToLower(strings.TrimSpace(endpoint))
	endpoint = strings.TrimPrefix(endpoint, "/api")
	endpoint = strings.TrimPrefix(endpoint, "/v1")
	endpoint = strings.TrimPrefix(endpoint, "/v2")
	endpoint = strings.Trim(endpoint, "/")
	return endpoint
}

// patternMatch checks if endpoints match with parameter placeholders
func (strategy *APIContractStrategy) patternMatch(a, b string) bool {
	// Replace common parameter patterns with regex
	paramPattern := regexp.MustCompile(`(:[a-zA-Z_]+|\{[a-zA-Z_]+\}|[0-9a-f-]{36}|\d+)`)

	aPattern := paramPattern.ReplaceAllString(a, `[^/]+`)
	bPattern := paramPattern.ReplaceAllString(b, `[^/]+`)

	return aPattern == bPattern
}

// resourceMatch checks if a function name matches an endpoint resource
func (strategy *APIContractStrategy) resourceMatch(sourceName, targetName string) bool {
	// Extract resource from function-style names
	methods := []string{"get", "post", "put", "patch", "delete", "fetch", "create", "update", "list"}

	for _, method := range methods {
		if strings.HasPrefix(sourceName, method) {
			resource := strings.TrimPrefix(sourceName, method)
			resource = strings.ToLower(resource)
			if strings.Contains(targetName, resource) {
				return true
			}
		}
		if strings.HasPrefix(targetName, method) {
			resource := strings.TrimPrefix(targetName, method)
			resource = strings.ToLower(resource)
			if strings.Contains(sourceName, resource) {
				return true
			}
		}
	}

	return false
}
