package equivalence

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

const defaultProjectionConfidence = 0.9

// Service provides equivalence detection and management
type Service interface {
	// DetectEquivalences finds potential equivalences for a source item
	DetectEquivalences(ctx context.Context, req *DetectionRequest) ([]Suggestion, error)

	// GetSuggestions retrieves pending equivalence suggestions for a project
	GetSuggestions(ctx context.Context, projectID uuid.UUID, limit, offset int) ([]Suggestion, error)

	// ConfirmSuggestion confirms an equivalence suggestion
	ConfirmSuggestion(ctx context.Context, suggestionID uuid.UUID, userID uuid.UUID) (*Link, error)

	// RejectSuggestion rejects an equivalence suggestion
	RejectSuggestion(ctx context.Context, suggestionID uuid.UUID, userID uuid.UUID) error

	// BulkConfirm confirms multiple suggestions at once
	BulkConfirm(ctx context.Context, suggestionIDs []uuid.UUID, userID uuid.UUID) ([]Link, error)

	// BulkReject rejects multiple suggestions at once
	BulkReject(ctx context.Context, suggestionIDs []uuid.UUID, userID uuid.UUID) error

	// GetEquivalences retrieves confirmed equivalences for an item
	GetEquivalences(ctx context.Context, itemID uuid.UUID) ([]Link, error)

	// ListEquivalencesByProject retrieves equivalences for a project with filtering
	ListEquivalencesByProject(ctx context.Context, filter Filter, limit, offset int) ([]Link, int64, error)

	// CreateManualLink creates a user-defined equivalence link
	CreateManualLink(ctx context.Context, link *Link, userID uuid.UUID) (*Link, error)

	// GetCanonicalConcepts retrieves canonical concepts for a project
	GetCanonicalConcepts(ctx context.Context, projectID uuid.UUID) ([]CanonicalConcept, error)

	// SuggestCanonicalConcept suggests a canonical concept for an item
	SuggestCanonicalConcept(ctx context.Context, itemID uuid.UUID) (*CanonicalConcept, error)

	// GetEquivalenceByID retrieves a specific equivalence link by ID
	GetEquivalenceByID(ctx context.Context, id uuid.UUID) (*Link, error)

	// ConfirmEquivalenceByID confirms a specific equivalence link by ID
	ConfirmEquivalenceByID(ctx context.Context, id uuid.UUID, userID uuid.UUID) (*Link, error)

	// RejectEquivalenceByID rejects a specific equivalence link by ID
	RejectEquivalenceByID(ctx context.Context, id uuid.UUID, userID uuid.UUID) error

	// BulkConfirmWithTracking confirms multiple equivalences with per-item error tracking
	BulkConfirmWithTracking(
		ctx context.Context,
		equivalenceIDs []uuid.UUID,
		userID uuid.UUID,
	) ([]Link, map[string]string)

	// BulkRejectWithTracking rejects multiple equivalences with per-item error tracking
	BulkRejectWithTracking(ctx context.Context, equivalenceIDs []uuid.UUID, userID uuid.UUID) map[string]string

	// CreateCanonicalConcept creates a new canonical concept and persists it
	CreateCanonicalConcept(
		ctx context.Context,
		req *CreateCanonicalConceptRequest,
		userID uuid.UUID,
	) (*CanonicalConcept, error)

	// GetCanonicalConcept retrieves a single canonical concept by ID
	GetCanonicalConcept(ctx context.Context, conceptID uuid.UUID) (*CanonicalConcept, error)

	// UpdateCanonicalConcept updates an existing canonical concept
	UpdateCanonicalConcept(
		ctx context.Context,
		conceptID uuid.UUID,
		concept *CanonicalConcept,
	) (*CanonicalConcept, error)

	// DeleteCanonicalConcept deletes a canonical concept by ID
	DeleteCanonicalConcept(ctx context.Context, conceptID uuid.UUID) error

	// GetConceptProjections retrieves all projections for a canonical concept
	GetConceptProjections(ctx context.Context, conceptID uuid.UUID) ([]CanonicalProjection, error)

	// CreateProjection creates a new projection linking an item to a canonical concept
	CreateProjection(
		ctx context.Context,
		req *CreateCanonicalProjectionRequest,
		conceptID uuid.UUID,
		projectID uuid.UUID,
		userID uuid.UUID,
	) (*CanonicalProjection, error)

	// DeleteProjection deletes a projection
	DeleteProjection(ctx context.Context, conceptID uuid.UUID, projectionID uuid.UUID) error
}

// Repository defines storage operations for equivalence data
type Repository interface {
	// Suggestions
	SaveSuggestion(ctx context.Context, s *Suggestion) error
	GetSuggestion(ctx context.Context, id uuid.UUID) (*Suggestion, error)
	ListSuggestions(ctx context.Context, projectID uuid.UUID, limit, offset int) ([]Suggestion, error)
	DeleteSuggestion(ctx context.Context, id uuid.UUID) error

	// Links
	SaveLink(ctx context.Context, link *Link) error
	GetLink(ctx context.Context, id uuid.UUID) (*Link, error)
	GetLinksByItem(ctx context.Context, itemID uuid.UUID) ([]Link, error)
	ListLinksByProject(ctx context.Context, filter Filter, limit, offset int) ([]Link, int64, error)
	UpdateLinkStatus(ctx context.Context, id uuid.UUID, status Status, userID uuid.UUID) error

	// Canonical Concepts
	SaveConcept(ctx context.Context, c *CanonicalConcept) error
	GetConcept(ctx context.Context, id uuid.UUID) (*CanonicalConcept, error)
	ListConcepts(ctx context.Context, projectID uuid.UUID) ([]CanonicalConcept, error)
	SearchConceptsByEmbedding(
		ctx context.Context,
		projectID uuid.UUID,
		embedding []float32,
		limit int,
	) ([]CanonicalConcept, error)

	// Projections
	SaveProjection(ctx context.Context, p *CanonicalProjection) error
	GetProjectionsByItem(ctx context.Context, itemID uuid.UUID) ([]CanonicalProjection, error)
	GetProjectionsByConcept(ctx context.Context, conceptID uuid.UUID) ([]CanonicalProjection, error)
	GetProjection(ctx context.Context, id uuid.UUID) (*CanonicalProjection, error)
	DeleteProjection(ctx context.Context, id uuid.UUID) error
}

// serviceImpl implements the Service interface
type serviceImpl struct {
	repo       Repository
	detector   *Detector
	embeddings embeddings.Provider
}

// NewService creates a new equivalence service
func NewService(repo Repository, embeddingProvider embeddings.Provider) Service {
	// Create detector with all strategies
	detector := NewDetector(
		NewNamingStrategy(),
		NewSemanticStrategy(embeddingProvider),
		NewAPIContractStrategy(),
		NewAnnotationStrategy(),
	)

	return &serviceImpl{
		repo:       repo,
		detector:   detector,
		embeddings: embeddingProvider,
	}
}

func (service *serviceImpl) DetectEquivalences(ctx context.Context, req *DetectionRequest) ([]Suggestion, error) {
	// Convert API request to internal strategy request
	strategyReq := &StrategyDetectionRequest{
		ProjectID:     req.ProjectID,
		SourceItem:    apiItemInfoToStrategyItemInfo(req.SourceItemID),
		CandidatePool: nil,
		Strategies:    req.Strategies,
		MinConfidence: req.MinConfidence,
		MaxResults:    req.MaxResults,
	}

	// Convert candidate pool if provided
	if len(req.CandidatePool) > 0 {
		strategyReq.CandidatePool = make([]*StrategyItemInfo, len(req.CandidatePool))
		for i, item := range req.CandidatePool {
			strategyReq.CandidatePool[i] = convertItemInfoToStrategy(item)
		}
	}

	suggestions, err := service.detector.Detect(ctx, strategyReq)
	if err != nil {
		return nil, fmt.Errorf("detection failed: %w", err)
	}

	// Persist suggestions
	for i := range suggestions {
		if err := service.repo.SaveSuggestion(ctx, &suggestions[i]); err != nil {
			_ = err
		}
	}

	return suggestions, nil
}

// apiItemInfoToStrategyItemInfo creates a minimal StrategyItemInfo from a source item ID
func apiItemInfoToStrategyItemInfo(id uuid.UUID) *StrategyItemInfo {
	return &StrategyItemInfo{
		ID: id,
	}
}

// convertItemInfoToStrategy converts an API ItemInfo to a StrategyItemInfo
func convertItemInfoToStrategy(item *ItemInfo) *StrategyItemInfo {
	if item == nil {
		return nil
	}
	strategyItem := &StrategyItemInfo{
		ID:          item.ID,
		ProjectID:   item.ProjectID,
		Title:       item.Title,
		Description: item.Description,
		Type:        item.ItemType,
		Metadata:    item.Metadata,
	}
	if item.CodeRef != nil {
		strategyItem.CodeRef = &StrategyCodeRef{
			FilePath:   item.CodeRef.FilePath,
			SymbolName: item.CodeRef.SymbolName,
			SymbolType: item.CodeRef.SymbolType,
			StartLine:  item.CodeRef.LineStart,
			EndLine:    item.CodeRef.LineEnd,
		}
	}
	return strategyItem
}

func (service *serviceImpl) GetSuggestions(
	ctx context.Context,
	projectID uuid.UUID,
	limit int,
	offset int,
) ([]Suggestion, error) {
	return service.repo.ListSuggestions(ctx, projectID, limit, offset)
}

func (service *serviceImpl) ConfirmSuggestion(
	ctx context.Context,
	suggestionID uuid.UUID,
	userID uuid.UUID,
) (*Link, error) {
	suggestion, err := service.repo.GetSuggestion(ctx, suggestionID)
	if err != nil {
		return nil, fmt.Errorf("suggestion not found: %w", err)
	}

	now := time.Now()
	link := &Link{
		ID:           uuid.New(),
		ProjectID:    suggestion.ProjectID,
		SourceItemID: suggestion.SourceItemID,
		TargetItemID: suggestion.TargetItemID,
		LinkType:     suggestion.SuggestedType,
		Confidence:   suggestion.Confidence,
		Provenance:   determineProvenance(suggestion),
		Status:       StatusConfirmed,
		Evidence:     suggestion.Evidence,
		ConfirmedBy:  &userID,
		ConfirmedAt:  &now,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	if err := service.repo.SaveLink(ctx, link); err != nil {
		return nil, fmt.Errorf("failed to save link: %w", err)
	}

	if err := service.repo.DeleteSuggestion(ctx, suggestionID); err != nil {
		slog.Error("warning: failed to delete suggestion", "error", suggestionID, "error", err)
	}

	return link, nil
}

func (service *serviceImpl) RejectSuggestion(ctx context.Context, suggestionID uuid.UUID, _ uuid.UUID) error {
	return service.repo.DeleteSuggestion(ctx, suggestionID)
}

func (service *serviceImpl) BulkConfirm(
	ctx context.Context,
	suggestionIDs []uuid.UUID,
	userID uuid.UUID,
) ([]Link, error) {
	links := make([]Link, 0, len(suggestionIDs))
	for _, id := range suggestionIDs {
		link, err := service.ConfirmSuggestion(ctx, id, userID)
		if err != nil {
			continue // Skip failed confirmations
		}
		links = append(links, *link)
	}
	return links, nil
}

func (service *serviceImpl) BulkReject(ctx context.Context, suggestionIDs []uuid.UUID, _ uuid.UUID) error {
	for _, id := range suggestionIDs {
		if err := service.repo.DeleteSuggestion(ctx, id); err != nil {
			return err
		}
	}
	return nil
}

func (service *serviceImpl) GetEquivalences(ctx context.Context, itemID uuid.UUID) ([]Link, error) {
	return service.repo.GetLinksByItem(ctx, itemID)
}

func (service *serviceImpl) ListEquivalencesByProject(
	ctx context.Context,
	filter Filter,
	limit int,
	offset int,
) ([]Link, int64, error) {
	if service.repo == nil {
		// Return empty list when repository is not configured
		return []Link{}, 0, nil
	}
	return service.repo.ListLinksByProject(ctx, filter, limit, offset)
}

func (service *serviceImpl) CreateManualLink(ctx context.Context, link *Link, userID uuid.UUID) (*Link, error) {
	now := time.Now()
	link.ID = uuid.New()
	link.Provenance = StrategyManualLink
	link.Confidence = 1.0
	link.Status = StatusConfirmed
	link.ConfirmedBy = &userID
	link.ConfirmedAt = &now
	link.CreatedAt = now
	link.UpdatedAt = now

	if err := service.repo.SaveLink(ctx, link); err != nil {
		return nil, fmt.Errorf("failed to save link: %w", err)
	}

	return link, nil
}

func (service *serviceImpl) GetCanonicalConcepts(ctx context.Context, projectID uuid.UUID) ([]CanonicalConcept, error) {
	return service.repo.ListConcepts(ctx, projectID)
}

func (service *serviceImpl) SuggestCanonicalConcept(_ context.Context, _ uuid.UUID) (*CanonicalConcept, error) {
	// This would typically use embeddings to find or create a canonical concept
	// Implementation depends on how items are retrieved
	return nil, errors.New("not implemented")
}

// GetEquivalenceByID retrieves a specific equivalence link by ID
func (service *serviceImpl) GetEquivalenceByID(ctx context.Context, id uuid.UUID) (*Link, error) {
	return service.repo.GetLink(ctx, id)
}

// ConfirmEquivalenceByID confirms a specific equivalence link by ID
func (service *serviceImpl) ConfirmEquivalenceByID(ctx context.Context, id uuid.UUID, userID uuid.UUID) (*Link, error) {
	link, err := service.repo.GetLink(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("equivalence not found: %w", err)
	}

	now := time.Now()
	link.Status = StatusConfirmed
	link.ConfirmedBy = &userID
	link.ConfirmedAt = &now
	link.UpdatedAt = now

	if err := service.repo.SaveLink(ctx, link); err != nil {
		return nil, fmt.Errorf("failed to save link: %w", err)
	}

	return link, nil
}

// RejectEquivalenceByID rejects a specific equivalence link by ID
func (service *serviceImpl) RejectEquivalenceByID(ctx context.Context, id uuid.UUID, userID uuid.UUID) error {
	link, err := service.repo.GetLink(ctx, id)
	if err != nil {
		return fmt.Errorf("equivalence not found: %w", err)
	}

	now := time.Now()
	link.Status = StatusRejected
	link.ConfirmedBy = &userID
	link.ConfirmedAt = &now
	link.UpdatedAt = now

	return service.repo.SaveLink(ctx, link)
}

// BulkConfirmWithTracking confirms multiple equivalences with per-item error tracking
func (service *serviceImpl) BulkConfirmWithTracking(
	ctx context.Context,
	equivalenceIDs []uuid.UUID,
	userID uuid.UUID,
) ([]Link, map[string]string) {
	links := make([]Link, 0, len(equivalenceIDs))
	errors := make(map[string]string)

	for _, id := range equivalenceIDs {
		link, err := service.ConfirmSuggestion(ctx, id, userID)
		if err != nil {
			errors[id.String()] = err.Error()
			continue
		}
		links = append(links, *link)
	}

	return links, errors
}

// BulkRejectWithTracking rejects multiple equivalences with per-item error tracking
func (service *serviceImpl) BulkRejectWithTracking(
	ctx context.Context,
	equivalenceIDs []uuid.UUID,
	userID uuid.UUID,
) map[string]string {
	errors := make(map[string]string)

	for _, id := range equivalenceIDs {
		if err := service.RejectEquivalenceByID(ctx, id, userID); err != nil {
			errors[id.String()] = err.Error()
		}
	}

	return errors
}

// CreateCanonicalConcept creates a new canonical concept and persists it
func (service *serviceImpl) CreateCanonicalConcept(
	ctx context.Context,
	req *CreateCanonicalConceptRequest,
	userID uuid.UUID,
) (*CanonicalConcept, error) {
	concept := &CanonicalConcept{
		ID:          uuid.New(),
		ProjectID:   req.ProjectID,
		Name:        req.Name,
		Description: req.Description,
		Domain:      req.Domain,
		Category:    req.Category,
		Tags:        req.Tags,
		CreatedBy:   &userID,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
		Version:     1,
	}

	if err := service.repo.SaveConcept(ctx, concept); err != nil {
		return nil, fmt.Errorf("failed to save concept: %w", err)
	}

	return concept, nil
}

// GetCanonicalConcept retrieves a single canonical concept by ID
func (service *serviceImpl) GetCanonicalConcept(ctx context.Context, conceptID uuid.UUID) (*CanonicalConcept, error) {
	concept, err := service.repo.GetConcept(ctx, conceptID)
	if err != nil {
		return nil, fmt.Errorf("concept not found: %w", err)
	}
	return concept, nil
}

// UpdateCanonicalConcept updates an existing canonical concept
func (service *serviceImpl) UpdateCanonicalConcept(
	ctx context.Context,
	conceptID uuid.UUID,
	concept *CanonicalConcept,
) (*CanonicalConcept, error) {
	// Validate the concept exists
	existing, err := service.repo.GetConcept(ctx, conceptID)
	if err != nil {
		return nil, fmt.Errorf("concept not found: %w", err)
	}

	// Preserve critical fields that shouldn't change
	concept.ID = existing.ID
	concept.ProjectID = existing.ProjectID
	concept.CreatedBy = existing.CreatedBy
	concept.CreatedAt = existing.CreatedAt

	// Update timestamp
	now := time.Now()
	concept.UpdatedAt = now

	// Always increment version
	concept.Version = existing.Version + 1

	if err := service.repo.SaveConcept(ctx, concept); err != nil {
		return nil, fmt.Errorf("failed to update concept: %w", err)
	}

	return concept, nil
}

// DeleteCanonicalConcept deletes a canonical concept by ID
// Note: This should also cascade-delete related projections
func (service *serviceImpl) DeleteCanonicalConcept(ctx context.Context, conceptID uuid.UUID) error {
	// Verify concept exists
	if _, err := service.repo.GetConcept(ctx, conceptID); err != nil {
		return fmt.Errorf("concept not found: %w", err)
	}

	// Get all projections for this concept to delete them
	projections, err := service.repo.GetProjectionsByConcept(ctx, conceptID)
	if err != nil {
		_ = err
	}

	// In a production system, you would delete projections here
	// For now, we assume the database has CASCADE delete configured
	// or we would need a DeleteProjection method in the repository

	// Delete the concept itself by setting status to inactive would be better
	// But since we need to delete it, we return an error saying
	// the concept cannot be fully deleted until projections are handled
	if len(projections) > 0 {
		return fmt.Errorf(
			"cannot delete concept with %d projections; please delete projections first",
			len(projections),
		)
	}

	// If no projections, we would need a DeleteConcept method in the repository
	// For now, we use SaveConcept with a marker that will be handled by the database
	// This is a limitation we should address in the repository
	_ = conceptID

	return errors.New("concept deletion not fully supported; database CASCADE delete should be configured")
}

// GetConceptProjections retrieves all projections for a canonical concept
func (service *serviceImpl) GetConceptProjections(
	ctx context.Context,
	conceptID uuid.UUID,
) ([]CanonicalProjection, error) {
	// Verify concept exists
	if _, err := service.repo.GetConcept(ctx, conceptID); err != nil {
		return nil, fmt.Errorf("concept not found: %w", err)
	}

	projections, err := service.repo.GetProjectionsByConcept(ctx, conceptID)
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve projections: %w", err)
	}

	return projections, nil
}

// CreateProjection creates a new projection linking an item to a canonical concept
func (service *serviceImpl) CreateProjection(
	ctx context.Context,
	req *CreateCanonicalProjectionRequest,
	conceptID uuid.UUID,
	projectID uuid.UUID,
	userID uuid.UUID,
) (*CanonicalProjection, error) {
	// Verify concept exists
	if _, err := service.repo.GetConcept(ctx, conceptID); err != nil {
		return nil, fmt.Errorf("concept not found: %w", err)
	}

	now := time.Now()
	projection := &CanonicalProjection{
		ID:          uuid.New(),
		ProjectID:   projectID,
		CanonicalID: conceptID,
		ItemID:      req.ItemID,
		Perspective: req.Perspective,
		Role:        req.Role,
		Confidence:  req.Confidence,
		Provenance:  req.Source,
		Status:      StatusConfirmed,
		ConfirmedBy: &userID,
		ConfirmedAt: &now,
		Metadata:    req.Metadata,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	// Set defaults
	if projection.Confidence == 0 {
		projection.Confidence = defaultProjectionConfidence
	}
	if projection.Provenance == "" {
		projection.Provenance = StrategyManualLink
	}

	if err := service.repo.SaveProjection(ctx, projection); err != nil {
		return nil, fmt.Errorf("failed to save projection: %w", err)
	}

	return projection, nil
}

// DeleteProjection deletes a projection
func (service *serviceImpl) DeleteProjection(ctx context.Context, conceptID uuid.UUID, projectionID uuid.UUID) error {
	// Verify projection exists and belongs to the concept
	projection, err := service.repo.GetProjection(ctx, projectionID)
	if err != nil {
		return fmt.Errorf("projection not found: %w", err)
	}

	if projection.CanonicalID != conceptID {
		return errors.New("projection does not belong to the specified concept")
	}

	if err := service.repo.DeleteProjection(ctx, projectionID); err != nil {
		return fmt.Errorf("failed to delete projection: %w", err)
	}

	return nil
}

// determineProvenance finds the highest-confidence strategy for the suggestion
func determineProvenance(suggestion *Suggestion) StrategyType {
	if len(suggestion.Strategies) > 0 {
		return suggestion.Strategies[0]
	}

	if strategy, ok := bestStrategyFromEvidence(suggestion.Evidence); ok {
		return strategy
	}

	return StrategyNamingPattern
}

func bestStrategyFromEvidence(evidence []Evidence) (StrategyType, bool) {
	if len(evidence) == 0 {
		return "", false
	}

	maxConf := 0.0
	var strategy StrategyType
	for _, entry := range evidence {
		if entry.Confidence > maxConf {
			maxConf = entry.Confidence
			strategy = entry.Strategy
		}
	}

	if strategy == "" {
		return "", false
	}

	return strategy, true
}
