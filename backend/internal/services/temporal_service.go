package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

const (
	mergeRequestStatusMerged = "merged"
	mergeRequestStatusOpen   = "open"
	versionStatusApproved    = "approved"
	versionStatusRejected    = "rejected"
)

// TemporalService handles versioning, branching, and temporal operations
type TemporalService interface {
	// Branch operations
	CreateBranch(ctx context.Context, branch *VersionBranch) (*VersionBranch, error)
	GetBranch(ctx context.Context, branchID string) (*VersionBranch, error)
	ListBranches(ctx context.Context, projectID string) ([]*VersionBranch, error)
	UpdateBranch(ctx context.Context, branch *VersionBranch) (*VersionBranch, error)
	DeleteBranch(ctx context.Context, branchID string) error

	// Version operations
	CreateVersion(ctx context.Context, version *Version) (*Version, error)
	GetVersion(ctx context.Context, versionID string) (*Version, error)
	GetVersionsByBranch(ctx context.Context, branchID string) ([]*Version, error)
	ApproveVersion(ctx context.Context, versionID string, approvedBy string) error
	RejectVersion(ctx context.Context, versionID string, reason string) error

	// Item versioning
	GetItemVersion(ctx context.Context, itemID, versionID string) (*ItemVersionSnapshot, error)
	GetItemVersionHistory(ctx context.Context, itemID string, branchID string) ([]*ItemVersionSnapshot, error)
	GetItemAtTime(ctx context.Context, itemID string, timestamp time.Time) (*ItemVersionSnapshot, error)
	RestoreItemVersion(ctx context.Context, itemID, versionID string) error

	// Alternatives
	CreateAlternative(ctx context.Context, alt *ItemAlternative) (*ItemAlternative, error)
	GetAlternatives(ctx context.Context, baseItemID string) ([]*ItemAlternative, error)
	SelectAlternative(ctx context.Context, altID string, selectedBy string, reason string) error

	// Merge operations
	CreateMergeRequest(ctx context.Context, mr *MergeRequest) (*MergeRequest, error)
	GetMergeRequest(ctx context.Context, mrID string) (*MergeRequest, error)
	ListMergeRequests(ctx context.Context, projectID string, status string) ([]*MergeRequest, error)
	ComputeMergeDiff(ctx context.Context, mrID string) (*VersionDiff, error)
	MergeBranches(ctx context.Context, mrID string, mergedBy string) error

	// Version comparison
	ComparVersions(ctx context.Context, versionAID, versionBID string) (*VersionDiff, error)
}

// VersionBranch is a branch in the version tree (main, release, feature, experiment, hotfix, archive).
type VersionBranch struct {
	ID             string                 `json:"id"`
	ProjectID      string                 `json:"project_id"`
	Name           string                 `json:"name"`
	Slug           string                 `json:"slug"`
	Description    string                 `json:"description,omitempty"`
	BranchType     string                 `json:"branch_type"` // main, release, feature, experiment, hotfix, archive
	ParentBranchID string                 `json:"parent_branch_id,omitempty"`
	BaseVersionID  string                 `json:"base_version_id,omitempty"`
	Status         string                 `json:"status"` // active, review, merged, abandoned, archived
	IsDefault      bool                   `json:"is_default"`
	IsProtected    bool                   `json:"is_protected"`
	MergedAt       *time.Time             `json:"merged_at,omitempty"`
	MergedInto     string                 `json:"merged_into,omitempty"`
	MergedBy       string                 `json:"merged_by,omitempty"`
	VersionCount   int                    `json:"version_count"`
	ItemCount      int                    `json:"item_count"`
	Metadata       map[string]interface{} `json:"metadata,omitempty"`
	CreatedBy      string                 `json:"created_by"`
	CreatedAt      time.Time              `json:"created_at"`
	UpdatedAt      time.Time              `json:"updated_at"`
}

// Version represents a versioned snapshot on a branch (draft, pending_review, approved, etc.).
type Version struct {
	ID              string                 `json:"id"`
	BranchID        string                 `json:"branch_id"`
	ProjectID       string                 `json:"project_id"`
	VersionNumber   int                    `json:"version_number"`
	ParentVersionID string                 `json:"parent_version_id,omitempty"`
	SnapshotID      string                 `json:"snapshot_id"`
	ChangesetID     string                 `json:"changeset_id,omitempty"`
	Tag             string                 `json:"tag,omitempty"`
	Message         string                 `json:"message"`
	ItemCount       int                    `json:"item_count"`
	ChangeCount     int                    `json:"change_count"`
	Status          string                 `json:"status"` // draft, pending_review, approved, rejected, superseded
	ApprovedBy      string                 `json:"approved_by,omitempty"`
	ApprovedAt      *time.Time             `json:"approved_at,omitempty"`
	RejectionReason string                 `json:"rejection_reason,omitempty"`
	Metadata        map[string]interface{} `json:"metadata,omitempty"`
	CreatedBy       string                 `json:"created_by"`
	CreatedAt       time.Time              `json:"created_at"`
}

// ItemVersionSnapshot is the stored state of an item at a specific version.
type ItemVersionSnapshot struct {
	ID                      string                 `json:"id"`
	ItemID                  string                 `json:"item_id"`
	VersionID               string                 `json:"version_id"`
	BranchID                string                 `json:"branch_id"`
	ProjectID               string                 `json:"project_id"`
	State                   map[string]interface{} `json:"state"`
	Lifecycle               string                 `json:"lifecycle"`
	IntroducedInVersionID   string                 `json:"introduced_in_version_id"`
	LastModifiedInVersionID string                 `json:"last_modified_in_version_id"`
	CreatedAt               time.Time              `json:"created_at"`
}

// ItemAlternative represents an alternative variant of a base item (e.g. alternative_to, supersedes).
type ItemAlternative struct {
	ID                string                 `json:"id"`
	ProjectID         string                 `json:"project_id"`
	BaseItemID        string                 `json:"base_item_id"`
	AlternativeItemID string                 `json:"alternative_item_id"`
	Relationship      string                 `json:"relationship"` // alternative_to, supersedes, experiment_of
	Description       string                 `json:"description,omitempty"`
	IsChosen          bool                   `json:"is_chosen"`
	ChosenAt          *time.Time             `json:"chosen_at,omitempty"`
	ChosenBy          string                 `json:"chosen_by,omitempty"`
	ChosenReason      string                 `json:"chosen_reason,omitempty"`
	Metrics           map[string]interface{} `json:"metrics,omitempty"`
	CreatedAt         time.Time              `json:"created_at"`
	UpdatedAt         time.Time              `json:"updated_at"`
}

// MergeRequest represents a request to merge a source branch/version into a target branch.
type MergeRequest struct {
	ID              string                 `json:"id"`
	ProjectID       string                 `json:"project_id"`
	SourceBranchID  string                 `json:"source_branch_id"`
	TargetBranchID  string                 `json:"target_branch_id"`
	SourceVersionID string                 `json:"source_version_id"`
	BaseVersionID   string                 `json:"base_version_id"`
	Status          string                 `json:"status"` // open, approved, merged, closed, conflict
	Title           string                 `json:"title"`
	Description     string                 `json:"description,omitempty"`
	Diff            map[string]interface{} `json:"diff,omitempty"`
	Conflicts       []interface{}          `json:"conflicts,omitempty"`
	Reviewers       []string               `json:"reviewers"`
	ApprovedBy      []string               `json:"approved_by"`
	CreatedBy       string                 `json:"created_by"`
	CreatedAt       time.Time              `json:"created_at"`
	MergedAt        *time.Time             `json:"merged_at,omitempty"`
	MergedBy        string                 `json:"merged_by,omitempty"`
	ClosedAt        *time.Time             `json:"closed_at,omitempty"`
	UpdatedAt       time.Time              `json:"updated_at"`
}

// VersionDiff holds the computed diff between two versions (added, removed, modified items).
type VersionDiff struct {
	VersionAID     string     `json:"version_a_id"`
	VersionBID     string     `json:"version_b_id"`
	VersionANumber int        `json:"version_a_number"`
	VersionBNumber int        `json:"version_b_number"`
	Added          []DiffItem `json:"added"`
	Removed        []DiffItem `json:"removed"`
	Modified       []DiffItem `json:"modified"`
	UnchangedCount int        `json:"unchanged_count"`
	Stats          DiffStats  `json:"stats"`
	ComputedAt     time.Time  `json:"computed_at"`
}

// DiffItem represents a single item change in a version diff (added, removed, or modified).
type DiffItem struct {
	ItemID       string        `json:"item_id"`
	Type         string        `json:"type"`
	Title        string        `json:"title"`
	ChangeType   string        `json:"change_type"` // added, removed, modified
	FieldChanges []FieldChange `json:"field_changes,omitempty"`
	Significance string        `json:"significance"` // minor, moderate, major, breaking
}

// FieldChange describes one field-level change (old value, new value, change type).
type FieldChange struct {
	Field      string      `json:"field"`
	OldValue   interface{} `json:"old_value"`
	NewValue   interface{} `json:"new_value"`
	ChangeType string      `json:"change_type"`
}

// DiffStats holds aggregate counts for a version diff (added, removed, modified, unchanged).
type DiffStats struct {
	TotalChanges   int `json:"total_changes"`
	AddedCount     int `json:"added_count"`
	RemovedCount   int `json:"removed_count"`
	ModifiedCount  int `json:"modified_count"`
	UnchangedCount int `json:"unchanged_count"`
}

// Implementation
type temporalService struct {
	branchRepo      repository.BranchRepository
	versionRepo     repository.VersionRepository
	itemVersionRepo repository.ItemVersionRepository
	altRepo         repository.AlternativeRepository
	mergeRepo       repository.MergeRepository
	itemRepo        repository.ItemRepository
	redisClient     *redis.Client
}

// NewTemporalService constructs a TemporalService with the given repositories and Redis client.
func NewTemporalService(
	branchRepo repository.BranchRepository,
	versionRepo repository.VersionRepository,
	itemVersionRepo repository.ItemVersionRepository,
	altRepo repository.AlternativeRepository,
	mergeRepo repository.MergeRepository,
	itemRepo repository.ItemRepository,
	redisClient *redis.Client,
) TemporalService {
	return &temporalService{
		branchRepo:      branchRepo,
		versionRepo:     versionRepo,
		itemVersionRepo: itemVersionRepo,
		altRepo:         altRepo,
		mergeRepo:       mergeRepo,
		itemRepo:        itemRepo,
		redisClient:     redisClient,
	}
}

// Branch operations
func (ts *temporalService) CreateBranch(ctx context.Context, branch *VersionBranch) (*VersionBranch, error) {
	if branch == nil {
		return nil, errors.New("branch cannot be nil")
	}

	if branch.Name == "" || branch.ProjectID == "" {
		return nil, errors.New("branch name and project_id are required")
	}

	// Generate ID and timestamps if not set
	if branch.ID == "" {
		branch.ID = uuid.New().String()
	}
	now := time.Now()
	branch.CreatedAt = now
	branch.UpdatedAt = now

	if err := ts.branchRepo.Create(ctx, branch); err != nil {
		return nil, fmt.Errorf("failed to create branch: %w", err)
	}

	return branch, nil
}

func (ts *temporalService) GetBranch(ctx context.Context, branchID string) (*VersionBranch, error) {
	if branchID == "" {
		return nil, errors.New("branch_id is required")
	}

	branch, err := ts.branchRepo.GetByID(ctx, branchID)
	if err != nil {
		return nil, fmt.Errorf("failed to get branch: %w", err)
	}

	branchTyped, ok := branch.(*VersionBranch)
	if !ok {
		return nil, errors.New("invalid branch type")
	}
	return branchTyped, nil
}

func (ts *temporalService) ListBranches(ctx context.Context, projectID string) ([]*VersionBranch, error) {
	if projectID == "" {
		return nil, errors.New("project_id is required")
	}

	branches, err := ts.branchRepo.ListByProject(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to list branches: %w", err)
	}

	result := make([]*VersionBranch, 0, len(branches))
	for _, b := range branches {
		if branchTyped, ok := b.(*VersionBranch); ok {
			result = append(result, branchTyped)
		}
	}
	return result, nil
}

func (ts *temporalService) UpdateBranch(ctx context.Context, branch *VersionBranch) (*VersionBranch, error) {
	if branch == nil || branch.ID == "" {
		return nil, errors.New("branch and branch.id are required")
	}

	branch.UpdatedAt = time.Now()

	if err := ts.branchRepo.Update(ctx, branch); err != nil {
		return nil, fmt.Errorf("failed to update branch: %w", err)
	}

	return branch, nil
}

func (ts *temporalService) DeleteBranch(ctx context.Context, branchID string) error {
	if branchID == "" {
		return errors.New("branch_id is required")
	}

	return ts.branchRepo.Delete(ctx, branchID)
}

// Version operations
func (ts *temporalService) CreateVersion(ctx context.Context, version *Version) (*Version, error) {
	if version == nil {
		return nil, errors.New("version cannot be nil")
	}

	if version.BranchID == "" || version.ProjectID == "" {
		return nil, errors.New("branch_id and project_id are required")
	}

	// Generate ID and timestamps if not set
	if version.ID == "" {
		version.ID = uuid.New().String()
	}
	now := time.Now()
	version.CreatedAt = now

	// Generate snapshot ID if not provided
	if version.SnapshotID == "" {
		version.SnapshotID = uuid.New().String()
	}

	if err := ts.versionRepo.Create(ctx, version); err != nil {
		return nil, fmt.Errorf("failed to create version: %w", err)
	}

	// Invalidate branch cache (if redis is available)
	if ts.redisClient != nil {
		_ = ts.redisClient.Del(ctx, "branch:"+version.BranchID)
	}

	return version, nil
}

func (ts *temporalService) GetVersion(ctx context.Context, versionID string) (*Version, error) {
	if versionID == "" {
		return nil, errors.New("version_id is required")
	}

	version, err := ts.versionRepo.GetByID(ctx, versionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get version: %w", err)
	}

	versionTyped, ok := version.(*Version)
	if !ok {
		return nil, errors.New("invalid version type")
	}
	return versionTyped, nil
}

func (ts *temporalService) GetVersionsByBranch(ctx context.Context, branchID string) ([]*Version, error) {
	if branchID == "" {
		return nil, errors.New("branch_id is required")
	}

	versions, err := ts.versionRepo.ListByBranch(ctx, branchID)
	if err != nil {
		return nil, fmt.Errorf("failed to get versions: %w", err)
	}

	result := make([]*Version, 0, len(versions))
	for _, v := range versions {
		if versionTyped, ok := v.(*Version); ok {
			result = append(result, versionTyped)
		}
	}
	return result, nil
}

func (ts *temporalService) ApproveVersion(ctx context.Context, versionID string, approvedBy string) error {
	if versionID == "" || approvedBy == "" {
		return errors.New("version_id and approved_by are required")
	}

	version, err := ts.versionRepo.GetByID(ctx, versionID)
	if err != nil {
		return fmt.Errorf("failed to get version: %w", err)
	}

	versionTyped, ok := version.(*Version)
	if !ok {
		return errors.New("invalid version type")
	}

	now := time.Now()
	versionTyped.Status = versionStatusApproved
	versionTyped.ApprovedBy = approvedBy
	versionTyped.ApprovedAt = &now

	return ts.versionRepo.Update(ctx, versionTyped)
}

func (ts *temporalService) RejectVersion(ctx context.Context, versionID string, reason string) error {
	if versionID == "" {
		return errors.New("version_id is required")
	}

	version, err := ts.versionRepo.GetByID(ctx, versionID)
	if err != nil {
		return fmt.Errorf("failed to get version: %w", err)
	}

	versionTyped, ok := version.(*Version)
	if !ok {
		return errors.New("invalid version type")
	}

	versionTyped.Status = versionStatusRejected
	versionTyped.RejectionReason = reason

	return ts.versionRepo.Update(ctx, versionTyped)
}

// Item versioning
func (ts *temporalService) GetItemVersion(ctx context.Context, itemID, versionID string) (*ItemVersionSnapshot, error) {
	if itemID == "" || versionID == "" {
		return nil, errors.New("item_id and version_id are required")
	}

	snapshot, err := ts.itemVersionRepo.GetByItemAndVersion(ctx, itemID, versionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get item version: %w", err)
	}

	snapshotTyped, ok := snapshot.(*ItemVersionSnapshot)
	if !ok {
		return nil, errors.New("invalid snapshot type")
	}
	return snapshotTyped, nil
}

func (ts *temporalService) GetItemVersionHistory(ctx context.Context, itemID string, branchID string) ([]*ItemVersionSnapshot, error) {
	if itemID == "" || branchID == "" {
		return nil, errors.New("item_id and branch_id are required")
	}

	// GetHistory in repository interface doesn't exist, use GetByItemAndBranch or adapt
	// For now, use a workaround that calls the repository properly
	var history []interface{}
	var err error

	// Try type assertion to see if it's the concrete implementation
	if itemVerRepo, ok := ts.itemVersionRepo.(interface {
		GetByItemAndBranch(ctx context.Context, itemID, branchID string) ([]interface{}, error)
	}); ok {
		history, err = itemVerRepo.GetByItemAndBranch(ctx, itemID, branchID)
	} else {
		// Fallback: try the GetHistory method with interface{}
		history, err = ts.itemVersionRepo.GetHistory(ctx, itemID, branchID)
	}

	if err != nil {
		return nil, fmt.Errorf("failed to get item history: %w", err)
	}

	result := make([]*ItemVersionSnapshot, 0, len(history))
	for _, h := range history {
		if snapshotTyped, ok := h.(*ItemVersionSnapshot); ok {
			result = append(result, snapshotTyped)
		}
	}
	return result, nil
}

func (ts *temporalService) GetItemAtTime(ctx context.Context, itemID string, timestamp time.Time) (*ItemVersionSnapshot, error) {
	if itemID == "" {
		return nil, errors.New("item_id is required")
	}

	// Get item history from all branches
	// For now, we'll get from the main branch - in production, this would be more sophisticated
	history, err := ts.itemVersionRepo.GetHistory(ctx, itemID, "")
	if err != nil {
		return nil, fmt.Errorf("failed to get item history: %w", err)
	}

	// Find the latest version before or at the given timestamp
	var latestSnapshot *ItemVersionSnapshot
	for _, h := range history {
		snapshot, ok := h.(*ItemVersionSnapshot)
		if !ok {
			continue
		}
		if snapshot.CreatedAt.Before(timestamp) || snapshot.CreatedAt.Equal(timestamp) {
			if latestSnapshot == nil || snapshot.CreatedAt.After(latestSnapshot.CreatedAt) {
				latestSnapshot = snapshot
			}
		}
	}

	if latestSnapshot == nil {
		return nil, errors.New("no version found at or before the given timestamp")
	}

	return latestSnapshot, nil
}

func (ts *temporalService) RestoreItemVersion(ctx context.Context, itemID, versionID string) error {
	if itemID == "" || versionID == "" {
		return errors.New("item_id and version_id are required")
	}

	// Get the item version snapshot
	snapshot, err := ts.itemVersionRepo.GetByItemAndVersion(ctx, itemID, versionID)
	if err != nil {
		return fmt.Errorf("failed to get item version: %w", err)
	}

	snapshotTyped, ok := snapshot.(*ItemVersionSnapshot)
	if !ok {
		return errors.New("invalid snapshot type")
	}

	// Restore item to that state
	item := &models.Item{
		ID:        itemID,
		UpdatedAt: time.Now(),
	}

	// Merge snapshot state into item
	if data, err := json.Marshal(snapshotTyped.State); err == nil {
		if unmarshalErr := json.Unmarshal(data, item); unmarshalErr != nil {
			slog.Warn("failed to unmarshal snapshot state into item", "error", unmarshalErr)
		}
	}

	return ts.itemRepo.Update(ctx, item)
}

// Alternatives
func (ts *temporalService) CreateAlternative(ctx context.Context, alt *ItemAlternative) (*ItemAlternative, error) {
	if alt == nil {
		return nil, errors.New("alternative cannot be nil")
	}

	if alt.BaseItemID == "" || alt.AlternativeItemID == "" {
		return nil, errors.New("base_item_id and alternative_item_id are required")
	}

	if alt.ID == "" {
		alt.ID = uuid.New().String()
	}

	now := time.Now()
	alt.CreatedAt = now
	alt.UpdatedAt = now

	if err := ts.altRepo.Create(ctx, alt); err != nil {
		return nil, fmt.Errorf("failed to create alternative: %w", err)
	}

	return alt, nil
}

func (ts *temporalService) GetAlternatives(ctx context.Context, baseItemID string) ([]*ItemAlternative, error) {
	if baseItemID == "" {
		return nil, errors.New("base_item_id is required")
	}

	alts, err := ts.altRepo.ListByBase(ctx, baseItemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get alternatives: %w", err)
	}

	result := make([]*ItemAlternative, 0, len(alts))
	for _, a := range alts {
		if altTyped, ok := a.(*ItemAlternative); ok {
			result = append(result, altTyped)
		}
	}
	return result, nil
}

func (ts *temporalService) SelectAlternative(ctx context.Context, altID string, selectedBy string, reason string) error {
	if altID == "" || selectedBy == "" {
		return errors.New("alt_id and selected_by are required")
	}

	alt, err := ts.altRepo.GetByID(ctx, altID)
	if err != nil {
		return fmt.Errorf("failed to get alternative: %w", err)
	}

	altTyped, ok := alt.(*ItemAlternative)
	if !ok {
		return errors.New("invalid alternative type")
	}

	now := time.Now()
	altTyped.IsChosen = true
	altTyped.ChosenAt = &now
	altTyped.ChosenBy = selectedBy
	altTyped.ChosenReason = reason
	altTyped.UpdatedAt = now

	return ts.altRepo.Update(ctx, altTyped)
}

// Merge operations
func (ts *temporalService) CreateMergeRequest(ctx context.Context, mr *MergeRequest) (*MergeRequest, error) {
	if mr == nil {
		return nil, errors.New("merge request cannot be nil")
	}

	if mr.SourceBranchID == "" || mr.TargetBranchID == "" || mr.Title == "" {
		return nil, errors.New("source_branch_id, target_branch_id, and title are required")
	}

	if mr.ID == "" {
		mr.ID = uuid.New().String()
	}

	now := time.Now()
	mr.CreatedAt = now
	mr.UpdatedAt = now
	if mr.Status == "" {
		mr.Status = mergeRequestStatusOpen
	}

	if err := ts.mergeRepo.Create(ctx, mr); err != nil {
		return nil, fmt.Errorf("failed to create merge request: %w", err)
	}

	return mr, nil
}

func (ts *temporalService) GetMergeRequest(ctx context.Context, mrID string) (*MergeRequest, error) {
	if mrID == "" {
		return nil, errors.New("merge request id is required")
	}

	mr, err := ts.mergeRepo.GetByID(ctx, mrID)
	if err != nil {
		return nil, fmt.Errorf("failed to get merge request: %w", err)
	}

	mrTyped, ok := mr.(*MergeRequest)
	if !ok {
		return nil, errors.New("invalid merge request type")
	}
	return mrTyped, nil
}

func (ts *temporalService) ListMergeRequests(ctx context.Context, projectID string, status string) ([]*MergeRequest, error) {
	if projectID == "" {
		return nil, errors.New("project_id is required")
	}

	mrs, err := ts.mergeRepo.ListByProject(ctx, projectID, status)
	if err != nil {
		return nil, fmt.Errorf("failed to list merge requests: %w", err)
	}

	result := make([]*MergeRequest, 0, len(mrs))
	for _, m := range mrs {
		if mrTyped, ok := m.(*MergeRequest); ok {
			result = append(result, mrTyped)
		}
	}
	return result, nil
}

func (ts *temporalService) ComputeMergeDiff(ctx context.Context, mrID string) (*VersionDiff, error) {
	if mrID == "" {
		return nil, errors.New("merge request id is required")
	}

	mr, err := ts.mergeRepo.GetByID(ctx, mrID)
	if err != nil {
		return nil, fmt.Errorf("failed to get merge request: %w", err)
	}

	mrTyped, ok := mr.(*MergeRequest)
	if !ok {
		return nil, errors.New("invalid merge request type")
	}

	// Compute diff between source and target versions
	diff, err := ts.ComparVersions(ctx, mrTyped.SourceVersionID, mrTyped.BaseVersionID)
	if err != nil {
		return nil, fmt.Errorf("failed to compute diff: %w", err)
	}

	return diff, nil
}

func (ts *temporalService) MergeBranches(ctx context.Context, mrID string, mergedBy string) error {
	if mrID == "" || mergedBy == "" {
		return errors.New("merge request id and merged_by are required")
	}

	mr, err := ts.mergeRepo.GetByID(ctx, mrID)
	if err != nil {
		return fmt.Errorf("failed to get merge request: %w", err)
	}

	mrTyped, ok := mr.(*MergeRequest)
	if !ok {
		return errors.New("invalid merge request type")
	}

	now := time.Now()
	mrTyped.Status = mergeRequestStatusMerged
	mrTyped.MergedAt = &now
	mrTyped.MergedBy = mergedBy
	mrTyped.UpdatedAt = now

	if err := ts.mergeRepo.Update(ctx, mrTyped); err != nil {
		return fmt.Errorf("failed to update merge request: %w", err)
	}

	// Update source branch status
	sourceBranch, err := ts.branchRepo.GetByID(ctx, mrTyped.SourceBranchID)
	if err == nil {
		branchTyped, ok := sourceBranch.(*VersionBranch)
		if ok {
			branchTyped.Status = "merged"
			branchTyped.MergedInto = mrTyped.TargetBranchID
			branchTyped.MergedAt = &now
			branchTyped.MergedBy = mergedBy
			branchTyped.UpdatedAt = now
			if err := ts.branchRepo.Update(ctx, branchTyped); err != nil {
				slog.Warn("failed to update source branch status to merged", "branch_id", branchTyped.ID, "error", err)
			}
		}
	}

	// Invalidate caches (if redis is available)
	if ts.redisClient != nil {
		_ = ts.redisClient.Del(ctx, "branch:"+mrTyped.SourceBranchID)
		_ = ts.redisClient.Del(ctx, "branch:"+mrTyped.TargetBranchID)
	}

	return nil
}

// Version comparison
func (ts *temporalService) ComparVersions(ctx context.Context, versionAID, versionBID string) (*VersionDiff, error) {
	if versionAID == "" || versionBID == "" {
		return nil, errors.New("both version ids are required")
	}

	versionA, err := ts.versionRepo.GetByID(ctx, versionAID)
	if err != nil {
		return nil, fmt.Errorf("failed to get version A: %w", err)
	}

	versionATyped, ok := versionA.(*Version)
	if !ok {
		return nil, errors.New("invalid version A type")
	}

	versionB, err := ts.versionRepo.GetByID(ctx, versionBID)
	if err != nil {
		return nil, fmt.Errorf("failed to get version B: %w", err)
	}

	versionBTyped, ok := versionB.(*Version)
	if !ok {
		return nil, errors.New("invalid version B type")
	}

	// For now, return a basic diff structure
	// In production, this would compute actual item-level differences
	diff := &VersionDiff{
		VersionAID:     versionAID,
		VersionBID:     versionBID,
		VersionANumber: versionATyped.VersionNumber,
		VersionBNumber: versionBTyped.VersionNumber,
		Added:          []DiffItem{},
		Removed:        []DiffItem{},
		Modified:       []DiffItem{},
		ComputedAt:     time.Now(),
	}

	return diff, nil
}
