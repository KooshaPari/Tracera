// Package grpc provides gRPC server implementations for internal services.
package grpc

import (
	"context"
	"fmt"
	"log/slog"
	"math"
	"net"
	"strconv"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/health"
	"google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"
	"google.golang.org/grpc/status"

	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	pb "github.com/kooshapari/tracertm-backend/pkg/proto/tracertm/v1"
)

// safeInt32 converts int to int32 with bounds clamping.
func safeInt32(n int) int32 {
	if n > math.MaxInt32 {
		return math.MaxInt32
	}
	if n < math.MinInt32 {
		return math.MinInt32
	}
	return int32(n)
}

// gRPC direction constants for impact analysis
const (
	grpcDirectionUpstream   = "upstream"
	grpcDirectionDownstream = "downstream"
	grpcDirectionBoth       = "both"
)

const (
	criticalPathImpactThreshold = 0.5
	bytesPerKiB                 = 1024
	grpcMaxMessageSizeMiB       = 10
	grpcMaxMessageSizeBytes     = grpcMaxMessageSizeMiB * bytesPerKiB * bytesPerKiB
)

// GraphServiceServer implements the GraphService gRPC service
type GraphServiceServer struct {
	pb.UnimplementedGraphServiceServer
	itemRepo repository.ItemRepository
	linkRepo repository.LinkRepository
	graphSvc *graph.AnalysisService
}

// NewGraphServiceServer creates a new GraphService server instance
func NewGraphServiceServer(
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	graphSvc *graph.AnalysisService,
) *GraphServiceServer {
	return &GraphServiceServer{
		itemRepo: itemRepo,
		linkRepo: linkRepo,
		graphSvc: graphSvc,
	}
}

// AnalyzeImpact performs impact analysis for a given item
func (server *GraphServiceServer) AnalyzeImpact(
	ctx context.Context,
	req *pb.AnalyzeImpactRequest,
) (*pb.AnalyzeImpactResponse, error) {
	// Validate request
	if err := validateAnalyzeImpactRequest(req); err != nil {
		return nil, err
	}

	slog.Info("Analyzing impact",
		"item_id", req.ItemId, "project_id", req.ProjectId,
		"direction", req.Direction, "max_depth", req.MaxDepth)

	// Verify item exists
	_, err := server.itemRepo.GetByID(ctx, req.ItemId)
	if err != nil {
		return nil, status.Error(codes.NotFound, "item not found: "+req.ItemId)
	}

	// Get and filter links based on direction
	links, err := server.fetchLinksForDirection(ctx, req)
	if err != nil {
		return nil, err
	}

	// Filter by link types if specified
	links = filterLinksByType(links, req.LinkTypes)

	// Build impacted items using BFS traversal
	result := performBFSImpactAnalysis(ctx, server.itemRepo, server.linkRepo, req, links)

	// Identify critical paths (items with high impact scores)
	criticalPaths := identifyCriticalPaths(result.impactedItems)

	response := &pb.AnalyzeImpactResponse{
		ItemId:        req.ItemId,
		ImpactedItems: result.impactedItems,
		TotalCount:    safeInt32(len(result.impactedItems)),
		ItemsByType:   result.itemsByType,
		ItemsByDepth:  result.itemsByDepth,
		CriticalPaths: criticalPaths,
	}

	slog.Info("[gRPC] Impact analysis complete impacted items", "value", len(result.impactedItems))
	return response, nil
}

// validateAnalyzeImpactRequest validates the AnalyzeImpact request
func validateAnalyzeImpactRequest(req *pb.AnalyzeImpactRequest) error {
	if req.ItemId == "" {
		return status.Error(codes.InvalidArgument, "item_id is required")
	}
	if req.ProjectId == "" {
		return status.Error(codes.InvalidArgument, "project_id is required")
	}
	if !isValidImpactDirection(req.Direction) {
		return status.Error(codes.InvalidArgument, "direction must be 'upstream', 'downstream', or 'both'")
	}
	return nil
}

func isValidImpactDirection(direction string) bool {
	return direction == grpcDirectionUpstream ||
		direction == grpcDirectionDownstream ||
		direction == grpcDirectionBoth
}

// impactAnalysisResult holds the result of BFS impact analysis
type impactAnalysisResult struct {
	impactedItems []*pb.ImpactedItem
	itemsByType   map[string]int32
	itemsByDepth  map[string]int32
}

// fetchLinksForDirection fetches links based on direction
func fetchLinksForDirection(
	ctx context.Context,
	linkRepo repository.LinkRepository,
	itemID string,
	direction string,
) ([]*models.Link, error) {
	var links []*models.Link
	var err error

	switch direction {
	case grpcDirectionUpstream:
		links, err = linkRepo.GetByTargetID(ctx, itemID)
	case grpcDirectionDownstream:
		links, err = linkRepo.GetBySourceID(ctx, itemID)
	case grpcDirectionBoth:
		sourceLinks, err1 := linkRepo.GetBySourceID(ctx, itemID)
		targetLinks, err2 := linkRepo.GetByTargetID(ctx, itemID)
		if err1 != nil {
			return nil, err1
		}
		if err2 != nil {
			return nil, err2
		}
		sourceLinks = append(sourceLinks, targetLinks...)
		links = sourceLinks
	}

	return links, err
}

// fetchLinksForDirection wraps the call with error handling
func (server *GraphServiceServer) fetchLinksForDirection(
	ctx context.Context,
	req *pb.AnalyzeImpactRequest,
) ([]*models.Link, error) {
	links, err := fetchLinksForDirection(ctx, server.linkRepo, req.ItemId, req.Direction)
	if err != nil {
		return nil, status.Error(codes.Internal, fmt.Sprintf("failed to fetch links: %v", err))
	}
	return links, nil
}

// filterLinksByType filters links by the specified link types
func filterLinksByType(links []*models.Link, linkTypes []string) []*models.Link {
	if len(linkTypes) == 0 {
		return links
	}

	linkTypeMap := make(map[string]bool)
	for _, lt := range linkTypes {
		linkTypeMap[lt] = true
	}

	filteredLinks := make([]*models.Link, 0)
	for _, link := range links {
		if linkTypeMap[link.Type] {
			filteredLinks = append(filteredLinks, link)
		}
	}
	return filteredLinks
}

// getRelatedID returns the related item ID from a link based on the source item
func getRelatedID(link *models.Link, sourceItemID string) string {
	if link.SourceID == sourceItemID {
		return link.TargetID
	}
	return link.SourceID
}

type impactQueueItem struct {
	itemID   string
	depth    int32
	linkType string
}

// performBFSImpactAnalysis performs BFS traversal for impact analysis
func performBFSImpactAnalysis(
	ctx context.Context,
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	req *pb.AnalyzeImpactRequest,
	links []*models.Link,
) impactAnalysisResult {
	result := impactAnalysisResult{
		impactedItems: make([]*pb.ImpactedItem, 0),
		itemsByType:   make(map[string]int32),
		itemsByDepth:  make(map[string]int32),
	}

	visited := map[string]bool{req.ItemId: true}
	queue := initImpactQueue(links, req.ItemId, visited)

	for len(queue) > 0 {
		var current impactQueueItem
		current, queue = popImpactQueue(queue)
		if exceedsMaxDepth(req.MaxDepth, current.depth) {
			continue
		}

		if !appendImpactResult(ctx, itemRepo, &result, current) {
			continue
		}

		if shouldExpandImpactTraversal(req.MaxDepth, current.depth) {
			queue = expandImpactTraversal(ctx, linkRepo, req.Direction, queue, current, visited)
		}
	}

	return result
}

func popImpactQueue(queue []impactQueueItem) (impactQueueItem, []impactQueueItem) {
	return queue[0], queue[1:]
}

func exceedsMaxDepth(maxDepth, depth int32) bool {
	return maxDepth > 0 && depth > maxDepth
}

func appendImpactResult(
	ctx context.Context,
	itemRepo repository.ItemRepository,
	result *impactAnalysisResult,
	current impactQueueItem,
) bool {
	relatedItem, err := itemRepo.GetByID(ctx, current.itemID)
	if err != nil {
		slog.Error("[gRPC] Warning: failed to fetch item", "error", current.itemID, "error", err)
		return false
	}

	result.impactedItems = append(
		result.impactedItems,
		buildImpactedItem(relatedItem, current.depth, current.linkType),
	)
	updateImpactCounts(result, relatedItem.Type, current.depth)
	return true
}

func shouldExpandImpactTraversal(maxDepth, currentDepth int32) bool {
	return maxDepth == 0 || currentDepth < maxDepth
}

func expandImpactTraversal(
	ctx context.Context,
	linkRepo repository.LinkRepository,
	direction string,
	queue []impactQueueItem,
	current impactQueueItem,
	visited map[string]bool,
) []impactQueueItem {
	nextLinks, err := fetchNextLinks(ctx, linkRepo, current.itemID, direction)
	if err != nil {
		slog.Error("[gRPC] Warning: failed to fetch links for", "error", current.itemID, "error", err)
		return queue
	}

	return enqueueNextLinks(queue, nextLinks, current, visited)
}

func initImpactQueue(links []*models.Link, rootID string, visited map[string]bool) []impactQueueItem {
	queue := make([]impactQueueItem, 0)
	for _, link := range links {
		relatedID := getRelatedID(link, rootID)
		queue = enqueueImpactItem(queue, visited, relatedID, 1, link.Type)
	}
	return queue
}

func enqueueNextLinks(
	queue []impactQueueItem,
	links []*models.Link,
	current impactQueueItem,
	visited map[string]bool,
) []impactQueueItem {
	for _, link := range links {
		nextID := getRelatedID(link, current.itemID)
		queue = enqueueImpactItem(queue, visited, nextID, current.depth+1, link.Type)
	}
	return queue
}

func enqueueImpactItem(
	queue []impactQueueItem,
	visited map[string]bool,
	itemID string,
	depth int32,
	linkType string,
) []impactQueueItem {
	if visited[itemID] {
		return queue
	}
	visited[itemID] = true
	return append(queue, impactQueueItem{itemID: itemID, depth: depth, linkType: linkType})
}

func buildImpactedItem(item *models.Item, depth int32, linkType string) *pb.ImpactedItem {
	impactScore := 1.0 / float64(depth)
	return &pb.ImpactedItem{
		Id:          item.ID,
		Type:        item.Type,
		Title:       item.Title,
		Depth:       depth,
		LinkType:    linkType,
		ImpactScore: impactScore,
	}
}

func updateImpactCounts(result *impactAnalysisResult, itemType string, depth int32) {
	result.itemsByType[itemType]++
	result.itemsByDepth[strconv.Itoa(int(depth))]++
}

// fetchNextLinks fetches the next set of links for traversal
func fetchNextLinks(
	ctx context.Context,
	linkRepo repository.LinkRepository,
	itemID string,
	direction string,
) ([]*models.Link, error) {
	switch direction {
	case grpcDirectionUpstream:
		links, err := linkRepo.GetByTargetID(ctx, itemID)
		if err != nil {
			return nil, err
		}
		return links, nil
	case grpcDirectionDownstream:
		links, err := linkRepo.GetBySourceID(ctx, itemID)
		if err != nil {
			return nil, err
		}
		return links, nil
	case grpcDirectionBoth:
		sourceLinks, err := linkRepo.GetBySourceID(ctx, itemID)
		if err != nil {
			return nil, err
		}
		targetLinks, err := linkRepo.GetByTargetID(ctx, itemID)
		if err != nil {
			return nil, err
		}
		return append(sourceLinks, targetLinks...), nil
	default:
		return nil, nil
	}
}

// identifyCriticalPaths identifies items with high impact scores as critical paths
func identifyCriticalPaths(impactedItems []*pb.ImpactedItem) []string {
	criticalPaths := make([]string, 0)
	for _, item := range impactedItems {
		if item.ImpactScore > criticalPathImpactThreshold {
			criticalPaths = append(criticalPaths, item.Id)
		}
	}
	return criticalPaths
}

// FindCycles detects circular dependencies in the graph
func (server *GraphServiceServer) FindCycles(
	ctx context.Context,
	req *pb.FindCyclesRequest,
) (*pb.FindCyclesResponse, error) {
	if req.ProjectId == "" {
		return nil, status.Error(codes.InvalidArgument, "project_id is required")
	}

	slog.Info("[gRPC] Finding cycles in project", "project", req.ProjectId)

	// Use graph service to detect cycles
	cycles, err := server.graphSvc.DetectCycles(ctx, req.ProjectId)
	if err != nil {
		return nil, status.Error(codes.Internal, fmt.Sprintf("failed to detect cycles: %v", err))
	}

	// Convert to protobuf format
	pbCycles := make([]*pb.Cycle, 0)
	for _, cycle := range cycles {
		if req.MaxCycleLength > 0 && safeInt32(len(cycle.Nodes)) > req.MaxCycleLength {
			continue
		}

		// Map severity string to float (warning=0.5, error=1.0)
		severityScore := 0.5
		if cycle.Severity == "error" {
			severityScore = 1.0
		}

		pbCycle := &pb.Cycle{
			ItemIds:   cycle.Nodes,
			LinkTypes: []string{}, // Link types not extracted from cycle data
			Length:    safeInt32(len(cycle.Nodes)),
			Severity:  float64(severityScore),
		}
		pbCycles = append(pbCycles, pbCycle)
	}

	response := &pb.FindCyclesResponse{
		Cycles:     pbCycles,
		TotalCount: safeInt32(len(pbCycles)),
		HasCycles:  len(pbCycles) > 0,
	}

	slog.Info("[gRPC] Found cycles", "value", len(pbCycles))
	return response, nil
}

// CalculatePath finds the shortest path between two items
func (server *GraphServiceServer) CalculatePath(
	ctx context.Context,
	req *pb.CalculatePathRequest,
) (*pb.CalculatePathResponse, error) {
	if req.ProjectId == "" {
		return nil, status.Error(codes.InvalidArgument, "project_id is required")
	}
	if req.SourceItemId == "" {
		return nil, status.Error(codes.InvalidArgument, "source_item_id is required")
	}
	if req.TargetItemId == "" {
		return nil, status.Error(codes.InvalidArgument, "target_item_id is required")
	}

	slog.Info("[gRPC] Calculating path from to", "path", req.SourceItemId, "id", req.TargetItemId)

	// Use graph service to find shortest path
	path, err := server.graphSvc.ShortestPath(ctx, req.SourceItemId, req.TargetItemId)
	if err != nil {
		return nil, status.Error(codes.Internal, fmt.Sprintf("failed to calculate path: %v", err))
	}

	pathExists := len(path.Nodes) > 0

	response := &pb.CalculatePathResponse{
		ItemIds:    path.Nodes,
		LinkTypes:  path.LinkTypes,
		PathLength: safeInt32(len(path.Nodes)),
		PathExists: pathExists,
		PathWeight: 1.0, // Default weight
	}

	slog.Info("[gRPC] Path calculation complete: exists= , length=", "path", pathExists, "size", len(path.Nodes))
	return response, nil
}

// StreamGraphUpdates streams real-time graph changes
func (s *GraphServiceServer) StreamGraphUpdates(
	req *pb.StreamGraphUpdatesRequest,
	_ pb.GraphService_StreamGraphUpdatesServer,
) error {
	if req.ProjectId == "" {
		return status.Error(codes.InvalidArgument, "project_id is required")
	}

	slog.Info("[gRPC] Starting graph update stream for project", "project", req.ProjectId)

	// Subscribe to graph updates (this would integrate with NATS or event system)
	// For now, return unimplemented
	return status.Error(codes.Unimplemented, "streaming not yet implemented")
}

// Server wraps the gRPC server with lifecycle management
type Server struct {
	grpcServer *grpc.Server
	listener   net.Listener
	port       int
}

// NewServer creates a new gRPC server
func NewServer(
	port int,
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	graphSvc *graph.AnalysisService,
) (*Server, error) {
	// Create listener
	listenConfig := net.ListenConfig{}
	listener, err := listenConfig.Listen(context.Background(), "tcp", ":"+strconv.Itoa(port))
	if err != nil {
		return nil, fmt.Errorf("failed to listen on port %d: %w", port, err)
	}

	// Create gRPC server
	grpcServer := grpc.NewServer(
		grpc.MaxRecvMsgSize(grpcMaxMessageSizeBytes), // 10MB max message size
		grpc.MaxSendMsgSize(grpcMaxMessageSizeBytes),
	)

	// Register GraphService
	graphServiceServer := NewGraphServiceServer(itemRepo, linkRepo, graphSvc)
	pb.RegisterGraphServiceServer(grpcServer, graphServiceServer)

	// Register health service
	healthServer := health.NewServer()
	healthServer.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)
	grpc_health_v1.RegisterHealthServer(grpcServer, healthServer)

	// Enable reflection for development/debugging
	reflection.Register(grpcServer)

	return &Server{
		grpcServer: grpcServer,
		listener:   listener,
		port:       port,
	}, nil
}

// Start starts the gRPC server
func (s *Server) Start() error {
	slog.Info("🚀 gRPC server listening on port", "address", s.port)
	return s.grpcServer.Serve(s.listener)
}

// Stop gracefully stops the gRPC server
func (s *Server) Stop() {
	slog.Info("Stopping gRPC server...")
	s.grpcServer.GracefulStop()
	slog.Info("gRPC server stopped")
}
