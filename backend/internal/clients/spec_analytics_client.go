package clients

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/connectivity"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/metadata"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	pb "github.com/kooshapari/tracertm-backend/pkg/proto/tracertm/v1"
)

const (
	specAnalyticsCacheTTL      = 15 * time.Minute
	specAnalyticsMaxConcurrent = 10
	grpcDialTimeout            = 30 * time.Second
)

// SpecAnalyticsClient provides gRPC client for Python SpecAnalytics service communication
type SpecAnalyticsClient struct {
	grpcClient   pb.SpecAnalyticsServiceClient
	grpcConn     *grpc.ClientConn
	cache        cache.Cache
	serviceToken string
}

// AnalyzeSpecRequest represents a request for specification analysis
type AnalyzeSpecRequest struct {
	SpecID    string `json:"spec_id"`
	Content   string `json:"content"`
	ProjectID string `json:"project_id"`
}

// SpecAnalysisResult represents the result of a specification analysis
type SpecAnalysisResult struct {
	SpecID             string                    `json:"spec_id"`
	CompliantWithISO   bool                      `json:"compliant_with_iso"`
	EARSPatterns       []EARSPattern             `json:"ears_patterns"`
	ODCClassification  string                    `json:"odc_classification"`
	FormalVerification *FormalVerificationResult `json:"formal_verification,omitempty"`
	Recommendations    []string                  `json:"recommendations"`
	QualityScore       float64                   `json:"quality_score"`
	QualityGrade       string                    `json:"quality_grade"`
}

// EARSPattern represents an EARS (Easy Approach to Requirements Syntax) pattern match
type EARSPattern struct {
	Type       string  `json:"type"` // UBIQUITOUS, EVENT_DRIVEN, UNWANTED_BEHAVIOR, STATE_DRIVEN, OPTIONAL_FEATURE
	Matched    bool    `json:"matched"`
	Confidence float64 `json:"confidence"`
}

// FormalVerificationResult represents the result of formal verification
type FormalVerificationResult struct {
	IsVerifiable   bool     `json:"is_verifiable"`
	LogicalFormula string   `json:"logical_formula,omitempty"`
	Contradictions []string `json:"contradictions,omitempty"`
	Ambiguities    []string `json:"ambiguities,omitempty"`
}

// BatchAnalyzeResponse represents the response from batch analysis
type BatchAnalyzeResponse struct {
	Results []*SpecAnalysisResult `json:"results"`
}

// NewSpecAnalyticsClient creates a new SpecAnalytics gRPC client
func NewSpecAnalyticsClient(grpcAddr string, serviceToken string, cache cache.Cache) (*SpecAnalyticsClient, error) {
	if grpcAddr == "" {
		return nil, errors.New("python gRPC address is required")
	}

	conn, err := grpc.NewClient(
		grpcAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to python gRPC at %s: %w", grpcAddr, err)
	}
	if err := waitForReadyConn(grpcDialTimeout, conn); err != nil {
		if closeErr := conn.Close(); closeErr != nil {
			return nil, fmt.Errorf("gRPC connect failed: %w; close failed: %w", err, closeErr)
		}
		return nil, err
	}

	return &SpecAnalyticsClient{
		grpcClient:   pb.NewSpecAnalyticsServiceClient(conn),
		grpcConn:     conn,
		cache:        cache,
		serviceToken: serviceToken,
	}, nil
}

// Close shuts down the gRPC connection.
func (specClient *SpecAnalyticsClient) Close() error {
	if specClient.grpcConn == nil {
		return nil
	}
	return specClient.grpcConn.Close()
}

func waitForReadyConn(timeout time.Duration, conn *grpc.ClientConn) error {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	conn.Connect()
	for {
		state := conn.GetState()
		if state == connectivity.Ready {
			return nil
		}
		if state == connectivity.Shutdown {
			return errors.New("gRPC connection shutdown before ready")
		}
		if !conn.WaitForStateChange(ctx, state) {
			return fmt.Errorf("gRPC connection not ready within %s", timeout)
		}
	}
}

func (specClient *SpecAnalyticsClient) withAuth(ctx context.Context) context.Context {
	if specClient.serviceToken == "" {
		return ctx
	}
	return metadata.AppendToOutgoingContext(ctx, "authorization", "Bearer "+specClient.serviceToken)
}

// AnalyzeSpec performs single specification analysis with caching
func (specClient *SpecAnalyticsClient) AnalyzeSpec(
	ctx context.Context,
	req AnalyzeSpecRequest,
) (*SpecAnalysisResult, error) {
	cacheKey := specClient.generateCacheKey(req)
	var cachedResult SpecAnalysisResult
	if specClient.tryCacheGet(ctx, cacheKey, &cachedResult) {
		return &cachedResult, nil
	}

	resp, err := specClient.grpcClient.AnalyzeSpec(
		specClient.withAuth(ctx),
		&pb.AnalyzeSpecRequest{
			SpecId:    req.SpecID,
			Content:   req.Content,
			ProjectId: req.ProjectID,
		},
	)
	if err != nil {
		return nil, fmt.Errorf("spec analytics analysis failed: %w", err)
	}

	result := specClient.toSpecAnalysisResult(resp.GetResult())
	specClient.tryCacheSet(ctx, cacheKey, result)
	return result, nil
}

// BatchAnalyzeSpecs performs parallel batch analysis with concurrency limit
func (specClient *SpecAnalyticsClient) BatchAnalyzeSpecs(
	ctx context.Context,
	requests []AnalyzeSpecRequest,
) ([]*SpecAnalysisResult, error) {
	if len(requests) == 0 {
		return []*SpecAnalysisResult{}, nil
	}

	results := make([]*SpecAnalysisResult, len(requests))
	errorsList := make([]error, len(requests))

	var wg sync.WaitGroup
	semaphore := make(chan struct{}, specAnalyticsMaxConcurrent)

	for idx, req := range requests {
		wg.Add(1)
		go func(index int, request AnalyzeSpecRequest) {
			defer wg.Done()
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			result, err := specClient.AnalyzeSpec(ctx, request)
			if err != nil {
				errorsList[index] = err
				return
			}
			results[index] = result
		}(idx, req)
	}

	wg.Wait()
	for i, err := range errorsList {
		if err != nil {
			return nil, fmt.Errorf("batch analysis failed for spec %d: %w", i, err)
		}
	}
	return results, nil
}

// BatchAnalyzeSpecsOptimized uses the gRPC batch endpoint
func (specClient *SpecAnalyticsClient) BatchAnalyzeSpecsOptimized(
	ctx context.Context,
	requests []AnalyzeSpecRequest,
) ([]*SpecAnalysisResult, error) {
	if len(requests) == 0 {
		return []*SpecAnalysisResult{}, nil
	}

	pbReqs := make([]*pb.AnalyzeSpecRequest, 0, len(requests))
	for _, req := range requests {
		pbReqs = append(pbReqs, &pb.AnalyzeSpecRequest{
			SpecId:    req.SpecID,
			Content:   req.Content,
			ProjectId: req.ProjectID,
		})
	}

	resp, err := specClient.grpcClient.BatchAnalyzeSpecs(
		specClient.withAuth(ctx),
		&pb.BatchAnalyzeSpecsRequest{Requests: pbReqs},
	)
	if err != nil {
		return specClient.BatchAnalyzeSpecs(ctx, requests)
	}

	results := make([]*SpecAnalysisResult, 0, len(resp.GetResults()))
	for _, result := range resp.GetResults() {
		results = append(results, specClient.toSpecAnalysisResult(result))
	}
	return results, nil
}

// ValidateISO29148Compliance checks if a specification complies with ISO 29148
func (specClient *SpecAnalyticsClient) ValidateISO29148Compliance(
	ctx context.Context,
	specID string,
	content string,
	projectID string,
) (bool, []string, error) {
	resp, err := specClient.grpcClient.ValidateISO29148(
		specClient.withAuth(ctx),
		&pb.ValidateISO29148Request{
			SpecId:    specID,
			Content:   content,
			ProjectId: projectID,
		},
	)
	if err != nil {
		return false, nil, fmt.Errorf("validate ISO failed: %w", err)
	}
	return resp.GetCompliantWithIso(), resp.GetRecommendations(), nil
}

// GetEARSPatterns extracts EARS patterns from a specification
func (specClient *SpecAnalyticsClient) GetEARSPatterns(
	ctx context.Context,
	specID string,
	content string,
	projectID string,
) ([]EARSPattern, error) {
	resp, err := specClient.grpcClient.GetEARSPatterns(
		specClient.withAuth(ctx),
		&pb.GetEARSPatternsRequest{
			SpecId:    specID,
			Content:   content,
			ProjectId: projectID,
		},
	)
	if err != nil {
		return nil, fmt.Errorf("get EARS patterns failed: %w", err)
	}
	return specClient.toEARSPatterns(resp.GetEarsPatterns()), nil
}

func (specClient *SpecAnalyticsClient) toSpecAnalysisResult(pbResult *pb.SpecAnalysisResult) *SpecAnalysisResult {
	if pbResult == nil {
		return &SpecAnalysisResult{}
	}

	odc := pbResult.GetOdcClassification()
	odcSummary := ""
	if odc != nil {
		odcSummary = fmt.Sprintf("%s:%s:%s", odc.GetDefectType(), odc.GetTrigger(), odc.GetImpact())
	}

	formal := pbResult.GetFormalVerification()
	var formalResult *FormalVerificationResult
	if formal != nil {
		formalResult = &FormalVerificationResult{
			IsVerifiable:   formal.GetIsVerifiable(),
			LogicalFormula: formal.GetLogicalFormula(),
			Contradictions: formal.GetContradictions(),
			Ambiguities:    formal.GetAmbiguities(),
		}
	}

	return &SpecAnalysisResult{
		SpecID:             pbResult.GetSpecId(),
		CompliantWithISO:   pbResult.GetCompliantWithIso(),
		EARSPatterns:       specClient.toEARSPatterns(pbResult.GetEarsPatterns()),
		ODCClassification:  odcSummary,
		FormalVerification: formalResult,
		Recommendations:    pbResult.GetRecommendations(),
		QualityScore:       pbResult.GetQualityScore(),
		QualityGrade:       pbResult.GetQualityGrade(),
	}
}

func (specClient *SpecAnalyticsClient) toEARSPatterns(patterns []*pb.EARSPattern) []EARSPattern {
	converted := make([]EARSPattern, 0, len(patterns))
	for _, pattern := range patterns {
		converted = append(converted, EARSPattern{
			Type:       pattern.GetType(),
			Matched:    pattern.GetMatched(),
			Confidence: pattern.GetConfidence(),
		})
	}
	return converted
}

func (specClient *SpecAnalyticsClient) tryCacheGet(
	ctx context.Context,
	cacheKey string,
	response interface{},
) bool {
	if cacheKey == "" || specClient.cache == nil {
		return false
	}
	if err := specClient.cache.Get(ctx, cacheKey, response); err == nil {
		return true
	}
	return false
}

func (specClient *SpecAnalyticsClient) tryCacheSet(
	ctx context.Context,
	cacheKey string,
	response interface{},
) {
	if cacheKey == "" || specClient.cache == nil {
		return
	}
	if err := specClient.cache.Set(ctx, cacheKey, response); err != nil {
		slog.Error("Warning: failed to cache response", "error", err)
	}
}

// generateCacheKey creates a cache key based on spec content hash
func (specClient *SpecAnalyticsClient) generateCacheKey(req AnalyzeSpecRequest) string {
	h := sha256.New()
	h.Write([]byte(req.SpecID))
	h.Write([]byte(req.Content))
	h.Write([]byte(req.ProjectID))
	contentHash := hex.EncodeToString(h.Sum(nil)[:16])
	return "spec-analytics:" + req.SpecID + ":" + contentHash
}
