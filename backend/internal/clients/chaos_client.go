package clients

import (
	"context"
	"fmt"
	"net/http"
	"time"
)

const chaosCacheTTL = 10 * time.Minute

// ChaosClient manages chaos engineering and zombie detection services
type ChaosClient struct {
	pythonClient *PythonServiceClient
}

// DetectZombiesRequest represents a request to detect zombie items
type DetectZombiesRequest struct {
	ProjectID string `json:"project_id"`
}

// ZombieItem represents an item detected as a zombie
type ZombieItem struct {
	ItemID      string    `json:"item_id"`
	ItemType    string    `json:"item_type"`
	Reason      string    `json:"reason"`
	LastUpdated time.Time `json:"last_updated"`
}

// ZombieReport represents the result of zombie detection
type ZombieReport struct {
	ProjectID       string       `json:"project_id"`
	ZombieItems     []ZombieItem `json:"zombie_items"`
	DetectedAt      time.Time    `json:"detected_at"`
	Recommendations []string     `json:"recommendations"`
}

// ImpactAnalysis represents the impact analysis of an item
type ImpactAnalysis struct {
	ItemID           string                 `json:"item_id"`
	DirectDependents int                    `json:"direct_dependents"`
	TotalImpact      int                    `json:"total_impact"`
	CriticalPaths    [][]string             `json:"critical_paths"`
	RiskLevel        string                 `json:"risk_level"` // "low", "medium", "high", "critical"
	Details          map[string]interface{} `json:"details"`
}

// NewChaosClient creates a new chaos client
func NewChaosClient(pythonClient *PythonServiceClient) *ChaosClient {
	return &ChaosClient{
		pythonClient: pythonClient,
	}
}

// DetectZombies detects zombie items in a project
func (chaosClient *ChaosClient) DetectZombies(
	ctx context.Context,
	req DetectZombiesRequest,
) (*ZombieReport, error) {
	var result ZombieReport

	// Cache for 10 minutes (expensive graph analysis)
	cacheKey := GenerateCacheKey("chaos:zombies", http.MethodPost, "/api/v1/chaos/zombies", req)

	err := chaosClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodPost,
		"/api/v1/chaos/zombies",
		req,
		&result,
		true, // Cacheable
		cacheKey,
		chaosCacheTTL, // Long cache for expensive operations
	)
	if err != nil {
		return nil, fmt.Errorf("failed to detect zombies: %w", err)
	}

	return &result, nil
}

// AnalyzeImpact analyzes the impact of an item
func (chaosClient *ChaosClient) AnalyzeImpact(
	ctx context.Context,
	itemID string,
) (*ImpactAnalysis, error) {
	var result ImpactAnalysis

	// Cache for 10 minutes (expensive graph traversal)
	cacheKey := GenerateCacheKey("chaos:impact", http.MethodGet, "/api/v1/chaos/impact/"+itemID, nil)

	err := chaosClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodGet,
		"/api/v1/chaos/impact/"+itemID,
		nil,
		&result,
		true, // Cacheable
		cacheKey,
		chaosCacheTTL, // Long cache for expensive operations
	)
	if err != nil {
		return nil, fmt.Errorf("failed to analyze impact: %w", err)
	}

	return &result, nil
}
