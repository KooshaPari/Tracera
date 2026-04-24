package services

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Temporal Repository Interfaces

// BranchRepository defines methods for version branch data access
type BranchRepository interface {
	Create(ctx context.Context, branch *VersionBranch) error
	GetByID(ctx context.Context, id string) (*VersionBranch, error)
	ListByProject(ctx context.Context, projectID string) ([]*VersionBranch, error)
	Update(ctx context.Context, branch *VersionBranch) error
	Delete(ctx context.Context, id string) error
	GetDefault(ctx context.Context, projectID string) (*VersionBranch, error)
}

// VersionRepository defines methods for version data access
type VersionRepository interface {
	Create(ctx context.Context, version *Version) error
	GetByID(ctx context.Context, id string) (*Version, error)
	ListByBranch(ctx context.Context, branchID string) ([]*Version, error)
	Update(ctx context.Context, version *Version) error
	Delete(ctx context.Context, id string) error
	GetByStatus(ctx context.Context, branchID string, status string) ([]*Version, error)
}

// ItemVersionRepository defines methods for item version snapshot data access
type ItemVersionRepository interface {
	Create(ctx context.Context, snapshot *ItemVersionSnapshot) error
	GetByID(ctx context.Context, id string) (*ItemVersionSnapshot, error)
	GetByItemAndVersion(ctx context.Context, itemID, versionID string) (*ItemVersionSnapshot, error)
	GetByItemID(ctx context.Context, itemID string) ([]*ItemVersionSnapshot, error)
	GetByItemAndBranch(ctx context.Context, itemID, branchID string) ([]*ItemVersionSnapshot, error)
	Update(ctx context.Context, snapshot *ItemVersionSnapshot) error
	Delete(ctx context.Context, id string) error
	List(ctx context.Context, versionID string) ([]*ItemVersionSnapshot, error)
}

// AlternativeRepository defines methods for item alternative data access
type AlternativeRepository interface {
	Create(ctx context.Context, alt *ItemAlternative) error
	GetByID(ctx context.Context, id string) (*ItemAlternative, error)
	ListByBase(ctx context.Context, baseItemID string) ([]*ItemAlternative, error)
	GetByAlternativeItemID(ctx context.Context, altItemID string) ([]*ItemAlternative, error)
	Update(ctx context.Context, alt *ItemAlternative) error
	Delete(ctx context.Context, id string) error
}

// MergeRepository defines methods for merge request data access
type MergeRepository interface {
	Create(ctx context.Context, mr *MergeRequest) error
	GetByID(ctx context.Context, id string) (*MergeRequest, error)
	ListByProject(ctx context.Context, projectID string, status string) ([]*MergeRequest, error)
	Update(ctx context.Context, mr *MergeRequest) error
	Delete(ctx context.Context, id string) error
}

// PGX Implementations

// BranchRepositoryPgx implements BranchRepository using pgx
type BranchRepositoryPgx struct {
	pool *pgxpool.Pool
}

// NewBranchRepository returns a BranchRepository backed by pgx.
func NewBranchRepository(pool *pgxpool.Pool) BranchRepository {
	return &BranchRepositoryPgx{pool: pool}
}

// Create persists a version branch.
func (r *BranchRepositoryPgx) Create(ctx context.Context, branch *VersionBranch) error {
	if branch.ID == "" {
		branch.ID = uuid.New().String()
	}

	query := `
		INSERT INTO version_branches
		(id, project_id, name, slug, description, branch_type, parent_branch_id, base_version_id,
		 status, is_default, is_protected, created_by, created_at, updated_at, metadata)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
	`

	metadataJSON, err := json.Marshal(branch.Metadata)
	if err != nil {
		return fmt.Errorf("marshal metadata: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		branch.ID, branch.ProjectID, branch.Name, branch.Slug, branch.Description,
		branch.BranchType, nullString(branch.ParentBranchID), nullString(branch.BaseVersionID),
		branch.Status, branch.IsDefault, branch.IsProtected, branch.CreatedBy,
		branch.CreatedAt, time.Now(), metadataJSON,
	)

	return err
}

// GetByID returns a version branch by ID.
func (r *BranchRepositoryPgx) GetByID(ctx context.Context, id string) (*VersionBranch, error) {
	query := `
		SELECT id, project_id, name, slug, description, branch_type, parent_branch_id, base_version_id,
		       status, is_default, is_protected, merged_at, merged_into, merged_by, version_count,
		       item_count, metadata, created_by, created_at, updated_at
		FROM version_branches
		WHERE id = $1
	`

	row := r.pool.QueryRow(ctx, query, id)
	return scanBranch(row)
}

// ListByProject returns all branches for a project.
func (r *BranchRepositoryPgx) ListByProject(ctx context.Context, projectID string) ([]*VersionBranch, error) {
	query := `
		SELECT id, project_id, name, slug, description, branch_type, parent_branch_id, base_version_id,
		       status, is_default, is_protected, merged_at, merged_into, merged_by, version_count,
		       item_count, metadata, created_by, created_at, updated_at
		FROM version_branches
		WHERE project_id = $1
		ORDER BY created_at DESC
	`

	rows, err := r.pool.Query(ctx, query, projectID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var branches []*VersionBranch
	for rows.Next() {
		branch, err := scanBranchRow(rows)
		if err != nil {
			return nil, err
		}
		branches = append(branches, branch)
	}

	return branches, rows.Err()
}

// Update updates a version branch.
func (r *BranchRepositoryPgx) Update(ctx context.Context, branch *VersionBranch) error {
	query := `
		UPDATE version_branches
		SET name = $2, description = $3, status = $4, is_protected = $5,
		    merged_at = $6, merged_into = $7, merged_by = $8,
		    version_count = $9, item_count = $10, metadata = $11, updated_at = $12
		WHERE id = $1
	`

	metadataJSON, err := json.Marshal(branch.Metadata)
	if err != nil {
		return fmt.Errorf("marshal metadata: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		branch.ID, branch.Name, branch.Description, branch.Status, branch.IsProtected,
		branch.MergedAt, nullString(branch.MergedInto), nullString(branch.MergedBy),
		branch.VersionCount, branch.ItemCount, metadataJSON, time.Now(),
	)

	return err
}

// Delete removes a version branch by ID.
func (r *BranchRepositoryPgx) Delete(ctx context.Context, id string) error {
	query := `DELETE FROM version_branches WHERE id = $1`
	_, err := r.pool.Exec(ctx, query, id)
	return err
}

// GetDefault returns the default branch for a project.
func (r *BranchRepositoryPgx) GetDefault(ctx context.Context, projectID string) (*VersionBranch, error) {
	query := `
		SELECT id, project_id, name, slug, description, branch_type, parent_branch_id, base_version_id,
		       status, is_default, is_protected, merged_at, merged_into, merged_by, version_count,
		       item_count, metadata, created_by, created_at, updated_at
		FROM version_branches
		WHERE project_id = $1 AND is_default = true
	`

	row := r.pool.QueryRow(ctx, query, projectID)
	return scanBranch(row)
}

// VersionRepositoryPgx implements VersionRepository using pgx
type VersionRepositoryPgx struct {
	pool *pgxpool.Pool
}

// NewVersionRepository returns a VersionRepository backed by pgx.
func NewVersionRepository(pool *pgxpool.Pool) VersionRepository {
	return &VersionRepositoryPgx{pool: pool}
}

// Create persists a version.
func (r *VersionRepositoryPgx) Create(ctx context.Context, version *Version) error {
	if version.ID == "" {
		version.ID = uuid.New().String()
	}

	query := `
		INSERT INTO versions
		(id, branch_id, project_id, version_number, parent_version_id, snapshot_id, changeset_id,
		 tag, message, item_count, change_count, status, approved_by, approved_at, rejection_reason,
		 metadata, created_by, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
	`

	metadataJSON, err := json.Marshal(version.Metadata)
	if err != nil {
		return fmt.Errorf("marshal metadata: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		version.ID, version.BranchID, version.ProjectID, version.VersionNumber,
		nullString(version.ParentVersionID), nullString(version.SnapshotID), nullString(version.ChangesetID),
		nullString(version.Tag), version.Message, version.ItemCount, version.ChangeCount,
		version.Status, nullString(version.ApprovedBy), version.ApprovedAt, nullString(version.RejectionReason),
		metadataJSON, version.CreatedBy, version.CreatedAt,
	)

	return err
}

// GetByID returns a version by ID.
func (r *VersionRepositoryPgx) GetByID(ctx context.Context, id string) (*Version, error) {
	query := `
		SELECT id, branch_id, project_id, version_number, parent_version_id, snapshot_id, changeset_id,
		       tag, message, item_count, change_count, status, approved_by, approved_at, rejection_reason,
		       metadata, created_by, created_at
		FROM versions
		WHERE id = $1
	`

	row := r.pool.QueryRow(ctx, query, id)
	return scanVersion(row)
}

// ListByBranch returns all versions for a branch.
func (r *VersionRepositoryPgx) ListByBranch(ctx context.Context, branchID string) ([]*Version, error) {
	query := `
		SELECT id, branch_id, project_id, version_number, parent_version_id, snapshot_id, changeset_id,
		       tag, message, item_count, change_count, status, approved_by, approved_at, rejection_reason,
		       metadata, created_by, created_at
		FROM versions
		WHERE branch_id = $1
		ORDER BY version_number DESC
	`

	rows, err := r.pool.Query(ctx, query, branchID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var versions []*Version
	for rows.Next() {
		version, err := scanVersionRow(rows)
		if err != nil {
			return nil, err
		}
		versions = append(versions, version)
	}

	return versions, rows.Err()
}

// Update updates a version.
func (r *VersionRepositoryPgx) Update(ctx context.Context, version *Version) error {
	query := `
		UPDATE versions
		SET message = $2, item_count = $3, change_count = $4, status = $5, approved_by = $6,
		    approved_at = $7, rejection_reason = $8, metadata = $9
		WHERE id = $1
	`

	metadataJSON, err := json.Marshal(version.Metadata)
	if err != nil {
		return fmt.Errorf("marshal metadata: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		version.ID, version.Message, version.ItemCount, version.ChangeCount, version.Status,
		nullString(version.ApprovedBy), version.ApprovedAt, nullString(version.RejectionReason),
		metadataJSON,
	)

	return err
}

// Delete removes a version by ID.
func (r *VersionRepositoryPgx) Delete(ctx context.Context, id string) error {
	query := `DELETE FROM versions WHERE id = $1`
	_, err := r.pool.Exec(ctx, query, id)
	return err
}

// GetByStatus returns versions for a branch filtered by status.
func (r *VersionRepositoryPgx) GetByStatus(ctx context.Context, branchID string, status string) ([]*Version, error) {
	query := `
		SELECT id, branch_id, project_id, version_number, parent_version_id, snapshot_id, changeset_id,
		       tag, message, item_count, change_count, status, approved_by, approved_at, rejection_reason,
		       metadata, created_by, created_at
		FROM versions
		WHERE branch_id = $1 AND status = $2
		ORDER BY version_number DESC
	`

	rows, err := r.pool.Query(ctx, query, branchID, status)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var versions []*Version
	for rows.Next() {
		version, err := scanVersionRow(rows)
		if err != nil {
			return nil, err
		}
		versions = append(versions, version)
	}

	return versions, rows.Err()
}

// ItemVersionRepositoryPgx implements ItemVersionRepository using pgx
type ItemVersionRepositoryPgx struct {
	pool *pgxpool.Pool
}

// NewItemVersionRepository returns an ItemVersionRepository backed by pgx.
func NewItemVersionRepository(pool *pgxpool.Pool) ItemVersionRepository {
	return &ItemVersionRepositoryPgx{pool: pool}
}

// Create persists an item version snapshot.
func (r *ItemVersionRepositoryPgx) Create(ctx context.Context, snapshot *ItemVersionSnapshot) error {
	if snapshot.ID == "" {
		snapshot.ID = uuid.New().String()
	}

	query := `
		INSERT INTO item_versions
		(id, item_id, version_id, branch_id, project_id, state, lifecycle,
		 introduced_in_version_id, last_modified_in_version_id, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
	`

	stateJSON, err := json.Marshal(snapshot.State)
	if err != nil {
		return fmt.Errorf("marshal state: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		snapshot.ID, snapshot.ItemID, snapshot.VersionID, snapshot.BranchID, snapshot.ProjectID,
		stateJSON, snapshot.Lifecycle, snapshot.IntroducedInVersionID, snapshot.LastModifiedInVersionID,
		snapshot.CreatedAt,
	)

	return err
}

// GetByID returns an item version snapshot by ID.
func (r *ItemVersionRepositoryPgx) GetByID(ctx context.Context, id string) (*ItemVersionSnapshot, error) {
	query := `
		SELECT id, item_id, version_id, branch_id, project_id, state, lifecycle,
		       introduced_in_version_id, last_modified_in_version_id, created_at
		FROM item_versions
		WHERE id = $1
	`

	row := r.pool.QueryRow(ctx, query, id)
	return scanItemVersion(row)
}

// GetByItemAndVersion returns the snapshot for an item in a given version.
func (r *ItemVersionRepositoryPgx) GetByItemAndVersion(ctx context.Context, itemID, versionID string) (*ItemVersionSnapshot, error) {
	query := `
		SELECT id, item_id, version_id, branch_id, project_id, state, lifecycle,
		       introduced_in_version_id, last_modified_in_version_id, created_at
		FROM item_versions
		WHERE item_id = $1 AND version_id = $2
	`

	row := r.pool.QueryRow(ctx, query, itemID, versionID)
	return scanItemVersion(row)
}

// GetByItemID returns all snapshots for an item.
func (r *ItemVersionRepositoryPgx) GetByItemID(ctx context.Context, itemID string) ([]*ItemVersionSnapshot, error) {
	query := `
		SELECT id, item_id, version_id, branch_id, project_id, state, lifecycle,
		       introduced_in_version_id, last_modified_in_version_id, created_at
		FROM item_versions
		WHERE item_id = $1
		ORDER BY created_at DESC
	`

	rows, err := r.pool.Query(ctx, query, itemID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var snapshots []*ItemVersionSnapshot
	for rows.Next() {
		snapshot, err := scanItemVersionRow(rows)
		if err != nil {
			return nil, err
		}
		snapshots = append(snapshots, snapshot)
	}

	return snapshots, rows.Err()
}

// GetByItemAndBranch returns snapshots for an item in a branch.
func (r *ItemVersionRepositoryPgx) GetByItemAndBranch(ctx context.Context, itemID, branchID string) ([]*ItemVersionSnapshot, error) {
	query := `
		SELECT id, item_id, version_id, branch_id, project_id, state, lifecycle,
		       introduced_in_version_id, last_modified_in_version_id, created_at
		FROM item_versions
		WHERE item_id = $1 AND branch_id = $2
		ORDER BY created_at DESC
	`

	rows, err := r.pool.Query(ctx, query, itemID, branchID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var snapshots []*ItemVersionSnapshot
	for rows.Next() {
		snapshot, err := scanItemVersionRow(rows)
		if err != nil {
			return nil, err
		}
		snapshots = append(snapshots, snapshot)
	}

	return snapshots, rows.Err()
}

// Update updates an item version snapshot.
func (r *ItemVersionRepositoryPgx) Update(ctx context.Context, snapshot *ItemVersionSnapshot) error {
	query := `
		UPDATE item_versions
		SET state = $2, lifecycle = $3, last_modified_in_version_id = $4
		WHERE id = $1
	`

	stateJSON, err := json.Marshal(snapshot.State)
	if err != nil {
		return fmt.Errorf("marshal state: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		snapshot.ID, stateJSON, snapshot.Lifecycle, snapshot.LastModifiedInVersionID,
	)

	return err
}

// Delete removes an item version snapshot by ID.
func (r *ItemVersionRepositoryPgx) Delete(ctx context.Context, id string) error {
	query := `DELETE FROM item_versions WHERE id = $1`
	_, err := r.pool.Exec(ctx, query, id)
	return err
}

// List returns all item version snapshots for a version.
func (r *ItemVersionRepositoryPgx) List(ctx context.Context, versionID string) ([]*ItemVersionSnapshot, error) {
	query := `
		SELECT id, item_id, version_id, branch_id, project_id, state, lifecycle,
		       introduced_in_version_id, last_modified_in_version_id, created_at
		FROM item_versions
		WHERE version_id = $1
		ORDER BY created_at DESC
	`

	rows, err := r.pool.Query(ctx, query, versionID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var snapshots []*ItemVersionSnapshot
	for rows.Next() {
		snapshot, err := scanItemVersionRow(rows)
		if err != nil {
			return nil, err
		}
		snapshots = append(snapshots, snapshot)
	}

	return snapshots, rows.Err()
}

// AlternativeRepositoryPgx implements AlternativeRepository using pgx
type AlternativeRepositoryPgx struct {
	pool *pgxpool.Pool
}

// NewAlternativeRepository returns an AlternativeRepository backed by the given pgx pool.
func NewAlternativeRepository(pool *pgxpool.Pool) AlternativeRepository {
	return &AlternativeRepositoryPgx{pool: pool}
}

// Create persists an ItemAlternative.
func (r *AlternativeRepositoryPgx) Create(ctx context.Context, alt *ItemAlternative) error {
	if alt.ID == "" {
		alt.ID = uuid.New().String()
	}

	query := `
		INSERT INTO item_alternatives
		(id, project_id, base_item_id, alternative_item_id, relationship, description,
		 is_chosen, chosen_at, chosen_by, chosen_reason, metrics, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
	`

	metricsJSON, err := json.Marshal(alt.Metrics)
	if err != nil {
		return fmt.Errorf("marshal metrics: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		alt.ID, alt.ProjectID, alt.BaseItemID, alt.AlternativeItemID, alt.Relationship,
		alt.Description, alt.IsChosen, alt.ChosenAt, nullString(alt.ChosenBy), nullString(alt.ChosenReason),
		metricsJSON, time.Now(), time.Now(),
	)

	return err
}

// GetByID returns the ItemAlternative with the given id.
func (r *AlternativeRepositoryPgx) GetByID(ctx context.Context, id string) (*ItemAlternative, error) {
	query := `
		SELECT id, project_id, base_item_id, alternative_item_id, relationship, description,
		       is_chosen, chosen_at, chosen_by, chosen_reason, metrics, created_at, updated_at
		FROM item_alternatives
		WHERE id = $1
	`

	row := r.pool.QueryRow(ctx, query, id)
	return scanAlternative(row)
}

// ListByBase returns all ItemAlternatives whose base item is baseItemID.
func (r *AlternativeRepositoryPgx) ListByBase(ctx context.Context, baseItemID string) ([]*ItemAlternative, error) {
	query := `
		SELECT id, project_id, base_item_id, alternative_item_id, relationship, description,
		       is_chosen, chosen_at, chosen_by, chosen_reason, metrics, created_at, updated_at
		FROM item_alternatives
		WHERE base_item_id = $1
		ORDER BY created_at DESC
	`

	rows, err := r.pool.Query(ctx, query, baseItemID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var alts []*ItemAlternative
	for rows.Next() {
		alt, err := scanAlternativeRow(rows)
		if err != nil {
			return nil, err
		}
		alts = append(alts, alt)
	}

	return alts, rows.Err()
}

// GetByAlternativeItemID returns all ItemAlternatives whose alternative item is altItemID.
func (r *AlternativeRepositoryPgx) GetByAlternativeItemID(ctx context.Context, altItemID string) ([]*ItemAlternative, error) {
	query := `
		SELECT id, project_id, base_item_id, alternative_item_id, relationship, description,
		       is_chosen, chosen_at, chosen_by, chosen_reason, metrics, created_at, updated_at
		FROM item_alternatives
		WHERE alternative_item_id = $1
		ORDER BY created_at DESC
	`

	rows, err := r.pool.Query(ctx, query, altItemID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var alts []*ItemAlternative
	for rows.Next() {
		alt, err := scanAlternativeRow(rows)
		if err != nil {
			return nil, err
		}
		alts = append(alts, alt)
	}

	return alts, rows.Err()
}

// Update updates an existing ItemAlternative.
func (r *AlternativeRepositoryPgx) Update(ctx context.Context, alt *ItemAlternative) error {
	query := `
		UPDATE item_alternatives
		SET is_chosen = $2, chosen_at = $3, chosen_by = $4, chosen_reason = $5, metrics = $6, updated_at = $7
		WHERE id = $1
	`

	metricsJSON, err := json.Marshal(alt.Metrics)
	if err != nil {
		return fmt.Errorf("marshal metrics: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		alt.ID, alt.IsChosen, alt.ChosenAt, nullString(alt.ChosenBy), nullString(alt.ChosenReason),
		metricsJSON, time.Now(),
	)

	return err
}

// Delete removes the ItemAlternative with the given id.
func (r *AlternativeRepositoryPgx) Delete(ctx context.Context, id string) error {
	query := `DELETE FROM item_alternatives WHERE id = $1`
	_, err := r.pool.Exec(ctx, query, id)
	return err
}

// MergeRepositoryPgx implements MergeRepository using pgx
type MergeRepositoryPgx struct {
	pool *pgxpool.Pool
}

// NewMergeRepository returns a MergeRepository backed by the given pgx pool.
func NewMergeRepository(pool *pgxpool.Pool) MergeRepository {
	return &MergeRepositoryPgx{pool: pool}
}

// Create persists a MergeRequest.
func (r *MergeRepositoryPgx) Create(ctx context.Context, mr *MergeRequest) error {
	if mr.ID == "" {
		mr.ID = uuid.New().String()
	}

	query := `
		INSERT INTO merge_requests
		(id, project_id, source_branch_id, target_branch_id, source_version_id, base_version_id,
		 status, title, description, diff, conflicts, reviewers, approved_by, created_by, created_at,
		 merged_at, merged_by, closed_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
	`

	diffJSON, err := json.Marshal(mr.Diff)
	if err != nil {
		return fmt.Errorf("marshal diff: %w", err)
	}
	conflictsJSON, err := json.Marshal(mr.Conflicts)
	if err != nil {
		return fmt.Errorf("marshal conflicts: %w", err)
	}
	reviewersJSON, err := json.Marshal(mr.Reviewers)
	if err != nil {
		return fmt.Errorf("marshal reviewers: %w", err)
	}
	approvedByJSON, err := json.Marshal(mr.ApprovedBy)
	if err != nil {
		return fmt.Errorf("marshal approved_by: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		mr.ID, mr.ProjectID, mr.SourceBranchID, mr.TargetBranchID, mr.SourceVersionID, mr.BaseVersionID,
		mr.Status, mr.Title, mr.Description, diffJSON, conflictsJSON, reviewersJSON, approvedByJSON,
		mr.CreatedBy, mr.CreatedAt, mr.MergedAt, nullString(mr.MergedBy), mr.ClosedAt, time.Now(),
	)

	return err
}

// GetByID returns the MergeRequest with the given id.
func (r *MergeRepositoryPgx) GetByID(ctx context.Context, id string) (*MergeRequest, error) {
	query := `
		SELECT id, project_id, source_branch_id, target_branch_id, source_version_id, base_version_id,
		       status, title, description, diff, conflicts, reviewers, approved_by, created_by, created_at,
		       merged_at, merged_by, closed_at, updated_at
		FROM merge_requests
		WHERE id = $1
	`

	row := r.pool.QueryRow(ctx, query, id)
	return scanMergeRequest(row)
}

// ListByProject returns MergeRequests for the project, optionally filtered by status.
func (r *MergeRepositoryPgx) ListByProject(ctx context.Context, projectID string, status string) ([]*MergeRequest, error) {
	query := `
		SELECT id, project_id, source_branch_id, target_branch_id, source_version_id, base_version_id,
		       status, title, description, diff, conflicts, reviewers, approved_by, created_by, created_at,
		       merged_at, merged_by, closed_at, updated_at
		FROM merge_requests
		WHERE project_id = $1
	`

	args := []interface{}{projectID}

	if status != "" {
		query += " AND status = $2"
		args = append(args, status)
	}

	query += " ORDER BY created_at DESC"

	rows, err := r.pool.Query(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var mrs []*MergeRequest
	for rows.Next() {
		mr, err := scanMergeRequestRow(rows)
		if err != nil {
			return nil, err
		}
		mrs = append(mrs, mr)
	}

	return mrs, rows.Err()
}

// Update updates an existing MergeRequest.
func (r *MergeRepositoryPgx) Update(ctx context.Context, mr *MergeRequest) error {
	query := `
		UPDATE merge_requests
		SET status = $2, diff = $3, conflicts = $4, reviewers = $5, approved_by = $6,
		    merged_at = $7, merged_by = $8, closed_at = $9, updated_at = $10
		WHERE id = $1
	`

	diffJSON, err := json.Marshal(mr.Diff)
	if err != nil {
		return fmt.Errorf("marshal diff: %w", err)
	}
	conflictsJSON, err := json.Marshal(mr.Conflicts)
	if err != nil {
		return fmt.Errorf("marshal conflicts: %w", err)
	}
	reviewersJSON, err := json.Marshal(mr.Reviewers)
	if err != nil {
		return fmt.Errorf("marshal reviewers: %w", err)
	}
	approvedByJSON, err := json.Marshal(mr.ApprovedBy)
	if err != nil {
		return fmt.Errorf("marshal approved_by: %w", err)
	}

	_, err = r.pool.Exec(ctx, query,
		mr.ID, mr.Status, diffJSON, conflictsJSON, reviewersJSON, approvedByJSON,
		mr.MergedAt, nullString(mr.MergedBy), mr.ClosedAt, time.Now(),
	)

	return err
}

// Delete removes the MergeRequest with the given id.
func (r *MergeRepositoryPgx) Delete(ctx context.Context, id string) error {
	query := `DELETE FROM merge_requests WHERE id = $1`
	_, err := r.pool.Exec(ctx, query, id)
	return err
}

// Helper functions

func nullString(s string) *string {
	if s == "" {
		return nil
	}
	return &s
}

func scanBranch(row pgx.Row) (*VersionBranch, error) {
	var branch VersionBranch
	var metadataJSON []byte

	err := row.Scan(
		&branch.ID, &branch.ProjectID, &branch.Name, &branch.Slug, &branch.Description,
		&branch.BranchType, &branch.ParentBranchID, &branch.BaseVersionID, &branch.Status,
		&branch.IsDefault, &branch.IsProtected, &branch.MergedAt, &branch.MergedInto,
		&branch.MergedBy, &branch.VersionCount, &branch.ItemCount, &metadataJSON,
		&branch.CreatedBy, &branch.CreatedAt, &branch.UpdatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("branch not found")
		}
		return nil, err
	}

	if metadataJSON != nil {
		if err := json.Unmarshal(metadataJSON, &branch.Metadata); err != nil {
			return nil, fmt.Errorf("unmarshal metadata: %w", err)
		}
	} else {
		branch.Metadata = make(map[string]interface{})
	}

	return &branch, nil
}

func scanBranchRow(rows pgx.Rows) (*VersionBranch, error) {
	var branch VersionBranch
	var metadataJSON []byte

	err := rows.Scan(
		&branch.ID, &branch.ProjectID, &branch.Name, &branch.Slug, &branch.Description,
		&branch.BranchType, &branch.ParentBranchID, &branch.BaseVersionID, &branch.Status,
		&branch.IsDefault, &branch.IsProtected, &branch.MergedAt, &branch.MergedInto,
		&branch.MergedBy, &branch.VersionCount, &branch.ItemCount, &metadataJSON,
		&branch.CreatedBy, &branch.CreatedAt, &branch.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}

	if metadataJSON != nil {
		if err := json.Unmarshal(metadataJSON, &branch.Metadata); err != nil {
			return nil, fmt.Errorf("unmarshal metadata: %w", err)
		}
	} else {
		branch.Metadata = make(map[string]interface{})
	}

	return &branch, nil
}

func scanVersion(row pgx.Row) (*Version, error) {
	var version Version
	var metadataJSON []byte

	err := row.Scan(
		&version.ID, &version.BranchID, &version.ProjectID, &version.VersionNumber,
		&version.ParentVersionID, &version.SnapshotID, &version.ChangesetID, &version.Tag,
		&version.Message, &version.ItemCount, &version.ChangeCount, &version.Status,
		&version.ApprovedBy, &version.ApprovedAt, &version.RejectionReason, &metadataJSON,
		&version.CreatedBy, &version.CreatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("version not found")
		}
		return nil, err
	}

	if metadataJSON != nil {
		if err := json.Unmarshal(metadataJSON, &version.Metadata); err != nil {
			return nil, fmt.Errorf("unmarshal metadata: %w", err)
		}
	} else {
		version.Metadata = make(map[string]interface{})
	}

	return &version, nil
}

func scanVersionRow(rows pgx.Rows) (*Version, error) {
	var version Version
	var metadataJSON []byte

	err := rows.Scan(
		&version.ID, &version.BranchID, &version.ProjectID, &version.VersionNumber,
		&version.ParentVersionID, &version.SnapshotID, &version.ChangesetID, &version.Tag,
		&version.Message, &version.ItemCount, &version.ChangeCount, &version.Status,
		&version.ApprovedBy, &version.ApprovedAt, &version.RejectionReason, &metadataJSON,
		&version.CreatedBy, &version.CreatedAt,
	)
	if err != nil {
		return nil, err
	}

	if metadataJSON != nil {
		if err := json.Unmarshal(metadataJSON, &version.Metadata); err != nil {
			return nil, fmt.Errorf("unmarshal metadata: %w", err)
		}
	} else {
		version.Metadata = make(map[string]interface{})
	}

	return &version, nil
}

func scanItemVersion(row pgx.Row) (*ItemVersionSnapshot, error) {
	var snapshot ItemVersionSnapshot
	var stateJSON []byte

	err := row.Scan(
		&snapshot.ID, &snapshot.ItemID, &snapshot.VersionID, &snapshot.BranchID,
		&snapshot.ProjectID, &stateJSON, &snapshot.Lifecycle, &snapshot.IntroducedInVersionID,
		&snapshot.LastModifiedInVersionID, &snapshot.CreatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("item version not found")
		}
		return nil, err
	}

	if stateJSON != nil {
		if err := json.Unmarshal(stateJSON, &snapshot.State); err != nil {
			return nil, fmt.Errorf("unmarshal state: %w", err)
		}
	} else {
		snapshot.State = make(map[string]interface{})
	}

	return &snapshot, nil
}

func scanItemVersionRow(rows pgx.Rows) (*ItemVersionSnapshot, error) {
	var snapshot ItemVersionSnapshot
	var stateJSON []byte

	err := rows.Scan(
		&snapshot.ID, &snapshot.ItemID, &snapshot.VersionID, &snapshot.BranchID,
		&snapshot.ProjectID, &stateJSON, &snapshot.Lifecycle, &snapshot.IntroducedInVersionID,
		&snapshot.LastModifiedInVersionID, &snapshot.CreatedAt,
	)
	if err != nil {
		return nil, err
	}

	if stateJSON != nil {
		if err := json.Unmarshal(stateJSON, &snapshot.State); err != nil {
			return nil, fmt.Errorf("unmarshal state: %w", err)
		}
	} else {
		snapshot.State = make(map[string]interface{})
	}

	return &snapshot, nil
}

func scanAlternative(row pgx.Row) (*ItemAlternative, error) {
	var alt ItemAlternative
	var metricsJSON []byte

	err := row.Scan(
		&alt.ID, &alt.ProjectID, &alt.BaseItemID, &alt.AlternativeItemID, &alt.Relationship,
		&alt.Description, &alt.IsChosen, &alt.ChosenAt, &alt.ChosenBy, &alt.ChosenReason,
		&metricsJSON, &alt.CreatedAt, &alt.UpdatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("alternative not found")
		}
		return nil, err
	}

	if metricsJSON != nil {
		if err := json.Unmarshal(metricsJSON, &alt.Metrics); err != nil {
			return nil, fmt.Errorf("unmarshal metrics: %w", err)
		}
	} else {
		alt.Metrics = make(map[string]interface{})
	}

	return &alt, nil
}

func scanAlternativeRow(rows pgx.Rows) (*ItemAlternative, error) {
	var alt ItemAlternative
	var metricsJSON []byte

	err := rows.Scan(
		&alt.ID, &alt.ProjectID, &alt.BaseItemID, &alt.AlternativeItemID, &alt.Relationship,
		&alt.Description, &alt.IsChosen, &alt.ChosenAt, &alt.ChosenBy, &alt.ChosenReason,
		&metricsJSON, &alt.CreatedAt, &alt.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}

	if metricsJSON != nil {
		if err := json.Unmarshal(metricsJSON, &alt.Metrics); err != nil {
			return nil, fmt.Errorf("unmarshal metrics: %w", err)
		}
	} else {
		alt.Metrics = make(map[string]interface{})
	}

	return &alt, nil
}

// unmarshalMergeRequestJSON unmarshals JSON fields for a merge request
func unmarshalMergeRequestJSON(mr *MergeRequest, diffJSON, conflictsJSON, reviewersJSON, approvedByJSON []byte) error {
	if diffJSON != nil {
		if err := json.Unmarshal(diffJSON, &mr.Diff); err != nil {
			return fmt.Errorf("unmarshal diff: %w", err)
		}
	}
	if conflictsJSON != nil {
		if err := json.Unmarshal(conflictsJSON, &mr.Conflicts); err != nil {
			return fmt.Errorf("unmarshal conflicts: %w", err)
		}
	}
	if reviewersJSON != nil {
		if err := json.Unmarshal(reviewersJSON, &mr.Reviewers); err != nil {
			return fmt.Errorf("unmarshal reviewers: %w", err)
		}
	}
	if approvedByJSON != nil {
		if err := json.Unmarshal(approvedByJSON, &mr.ApprovedBy); err != nil {
			return fmt.Errorf("unmarshal approved_by: %w", err)
		}
	}
	return nil
}

func scanMergeRequest(row pgx.Row) (*MergeRequest, error) {
	var mr MergeRequest
	var diffJSON, conflictsJSON, reviewersJSON, approvedByJSON []byte

	err := row.Scan(
		&mr.ID, &mr.ProjectID, &mr.SourceBranchID, &mr.TargetBranchID, &mr.SourceVersionID,
		&mr.BaseVersionID, &mr.Status, &mr.Title, &mr.Description, &diffJSON, &conflictsJSON,
		&reviewersJSON, &approvedByJSON, &mr.CreatedBy, &mr.CreatedAt, &mr.MergedAt,
		&mr.MergedBy, &mr.ClosedAt, &mr.UpdatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("merge request not found")
		}
		return nil, err
	}

	if err := unmarshalMergeRequestJSON(&mr, diffJSON, conflictsJSON, reviewersJSON, approvedByJSON); err != nil {
		return nil, err
	}

	return &mr, nil
}

func scanMergeRequestRow(rows pgx.Rows) (*MergeRequest, error) {
	var mr MergeRequest
	var diffJSON, conflictsJSON, reviewersJSON, approvedByJSON []byte

	err := rows.Scan(
		&mr.ID, &mr.ProjectID, &mr.SourceBranchID, &mr.TargetBranchID, &mr.SourceVersionID,
		&mr.BaseVersionID, &mr.Status, &mr.Title, &mr.Description, &diffJSON, &conflictsJSON,
		&reviewersJSON, &approvedByJSON, &mr.CreatedBy, &mr.CreatedAt, &mr.MergedAt,
		&mr.MergedBy, &mr.ClosedAt, &mr.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}

	if diffJSON != nil {
		if err := json.Unmarshal(diffJSON, &mr.Diff); err != nil {
			return nil, fmt.Errorf("unmarshal diff: %w", err)
		}
	}
	if conflictsJSON != nil {
		if err := json.Unmarshal(conflictsJSON, &mr.Conflicts); err != nil {
			return nil, fmt.Errorf("unmarshal conflicts: %w", err)
		}
	}
	if reviewersJSON != nil {
		if err := json.Unmarshal(reviewersJSON, &mr.Reviewers); err != nil {
			return nil, fmt.Errorf("unmarshal reviewers: %w", err)
		}
	}
	if approvedByJSON != nil {
		if err := json.Unmarshal(approvedByJSON, &mr.ApprovedBy); err != nil {
			return nil, fmt.Errorf("unmarshal approved_by: %w", err)
		}
	}

	return &mr, nil
}
