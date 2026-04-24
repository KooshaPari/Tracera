package equivalence

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

// PgxRepository implements the Repository interface using pgx
type PgxRepository struct {
	db *pgxpool.Pool
}

const (
	defaultPageLimit = 50
	maxPageLimit     = 500
)

// NewPgxRepository creates a new equivalence repository
func NewPgxRepository(db *pgxpool.Pool) *PgxRepository {
	return &PgxRepository{db: db}
}

// ============================================================================
// SUGGESTION METHODS
// ============================================================================

// SaveSuggestion saves an equivalence suggestion to the database
func (repo *PgxRepository) SaveSuggestion(ctx context.Context, suggestion *Suggestion) error {
	if suggestion == nil {
		return errors.New("suggestion cannot be nil")
	}

	strategiesJSON, err := json.Marshal(suggestion.Strategies)
	if err != nil {
		return fmt.Errorf("failed to marshal strategies: %w", err)
	}

	evidenceJSON, err := json.Marshal(suggestion.Evidence)
	if err != nil {
		return fmt.Errorf("failed to marshal evidence: %w", err)
	}

	query := `
		INSERT INTO equivalence_suggestions
		(id, project_id, source_item_id, source_item_title, source_item_type,
		 target_item_id, target_item_title, target_item_type, suggested_type,
		 confidence, strategies, evidence, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
		ON CONFLICT (id) DO UPDATE SET
			confidence = EXCLUDED.confidence,
			strategies = EXCLUDED.strategies,
			evidence = EXCLUDED.evidence,
			created_at = EXCLUDED.created_at
	`

	_, err = repo.db.Exec(
		ctx,
		query,
		suggestion.ID,
		suggestion.ProjectID,
		suggestion.SourceItemID,
		suggestion.SourceItemTitle,
		suggestion.SourceItemType,
		suggestion.TargetItemID,
		suggestion.TargetItemTitle,
		suggestion.TargetItemType,
		suggestion.SuggestedType,
		suggestion.Confidence,
		strategiesJSON,
		evidenceJSON,
		suggestion.CreatedAt,
	)

	return err
}

// GetSuggestion retrieves a suggestion by ID
func (repo *PgxRepository) GetSuggestion(ctx context.Context, id uuid.UUID) (*Suggestion, error) {
	query := `
		SELECT id, project_id, source_item_id, source_item_title, source_item_type,
		       target_item_id, target_item_title, target_item_type, suggested_type,
		       confidence, strategies, evidence, created_at
		FROM equivalence_suggestions
		WHERE id = $1
	`

	var suggestion Suggestion
	var strategiesJSON, evidenceJSON []byte

	err := repo.db.QueryRow(ctx, query, id).Scan(
		&suggestion.ID,
		&suggestion.ProjectID,
		&suggestion.SourceItemID,
		&suggestion.SourceItemTitle,
		&suggestion.SourceItemType,
		&suggestion.TargetItemID,
		&suggestion.TargetItemTitle,
		&suggestion.TargetItemType,
		&suggestion.SuggestedType,
		&suggestion.Confidence,
		&strategiesJSON,
		&evidenceJSON,
		&suggestion.CreatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrSuggestionNotFound
		}
		return nil, err
	}

	if err := json.Unmarshal(strategiesJSON, &suggestion.Strategies); err != nil {
		return nil, fmt.Errorf("failed to unmarshal strategies: %w", err)
	}

	if err := json.Unmarshal(evidenceJSON, &suggestion.Evidence); err != nil {
		return nil, fmt.Errorf("failed to unmarshal evidence: %w", err)
	}

	return &suggestion, nil
}

// ListSuggestions retrieves suggestions for a project with pagination
func (repo *PgxRepository) ListSuggestions(
	ctx context.Context,
	projectID uuid.UUID,
	limit int,
	offset int,
) ([]Suggestion, error) {
	limit, offset = normalizePagination(limit, offset)

	query := `
		SELECT id, project_id, source_item_id, source_item_title, source_item_type,
		       target_item_id, target_item_title, target_item_type, suggested_type,
		       confidence, strategies, evidence, created_at
		FROM equivalence_suggestions
		WHERE project_id = $1
		ORDER BY created_at DESC
		LIMIT $2 OFFSET $3
	`

	rows, err := repo.db.Query(ctx, query, projectID, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var suggestions []Suggestion
	for rows.Next() {
		suggestion, err := scanSuggestionRow(rows.Scan)
		if err != nil {
			return nil, err
		}
		suggestions = append(suggestions, suggestion)
	}

	return suggestions, rows.Err()
}

func normalizePagination(limit, offset int) (int, int) {
	if limit <= 0 {
		limit = defaultPageLimit
	}
	if limit > maxPageLimit {
		limit = maxPageLimit
	}
	if offset < 0 {
		offset = 0
	}
	return limit, offset
}

func scanSuggestionRow(scan func(dest ...any) error) (Suggestion, error) {
	var suggestion Suggestion
	var strategiesJSON, evidenceJSON []byte

	if err := scan(
		&suggestion.ID,
		&suggestion.ProjectID,
		&suggestion.SourceItemID,
		&suggestion.SourceItemTitle,
		&suggestion.SourceItemType,
		&suggestion.TargetItemID,
		&suggestion.TargetItemTitle,
		&suggestion.TargetItemType,
		&suggestion.SuggestedType,
		&suggestion.Confidence,
		&strategiesJSON,
		&evidenceJSON,
		&suggestion.CreatedAt,
	); err != nil {
		return Suggestion{}, err
	}

	if err := json.Unmarshal(strategiesJSON, &suggestion.Strategies); err != nil {
		return Suggestion{}, err
	}

	if err := json.Unmarshal(evidenceJSON, &suggestion.Evidence); err != nil {
		return Suggestion{}, err
	}

	return suggestion, nil
}

// DeleteSuggestion deletes a suggestion by ID
func (repo *PgxRepository) DeleteSuggestion(ctx context.Context, id uuid.UUID) error {
	query := `DELETE FROM equivalence_suggestions WHERE id = $1`
	_, err := repo.db.Exec(ctx, query, id)
	return err
}

// ============================================================================
// LINK METHODS
// ============================================================================

// SaveLink saves an equivalence link to the database
func (repo *PgxRepository) SaveLink(ctx context.Context, link *Link) error {
	if link == nil {
		return errors.New("link cannot be nil")
	}

	evidenceJSON, err := json.Marshal(link.Evidence)
	if err != nil {
		return fmt.Errorf("failed to marshal evidence: %w", err)
	}

	query := `
		INSERT INTO equivalence_links
		(id, project_id, source_item_id, target_item_id, link_type, confidence,
		 provenance, evidence, status, confirmed_by, confirmed_at, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
		ON CONFLICT (id) DO UPDATE SET
			confidence = EXCLUDED.confidence,
			provenance = EXCLUDED.provenance,
			evidence = EXCLUDED.evidence,
			status = EXCLUDED.status,
			confirmed_by = EXCLUDED.confirmed_by,
			confirmed_at = EXCLUDED.confirmed_at,
			updated_at = EXCLUDED.updated_at
	`

	_, err = repo.db.Exec(ctx, query,
		link.ID, link.ProjectID, link.SourceItemID, link.TargetItemID,
		link.LinkType, link.Confidence, link.Provenance, evidenceJSON,
		link.Status, link.ConfirmedBy, link.ConfirmedAt,
		link.CreatedAt, link.UpdatedAt,
	)

	return err
}

// GetLink retrieves a link by ID
func (repo *PgxRepository) GetLink(ctx context.Context, id uuid.UUID) (*Link, error) {
	query := `
		SELECT id, project_id, source_item_id, target_item_id, link_type, confidence,
		       provenance, evidence, status, confirmed_by, confirmed_at,
		       created_at, updated_at
		FROM equivalence_links
		WHERE id = $1
	`

	var link Link
	var evidenceJSON []byte

	err := repo.db.QueryRow(ctx, query, id).Scan(
		&link.ID, &link.ProjectID, &link.SourceItemID, &link.TargetItemID,
		&link.LinkType, &link.Confidence, &link.Provenance, &evidenceJSON,
		&link.Status, &link.ConfirmedBy, &link.ConfirmedAt,
		&link.CreatedAt, &link.UpdatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrLinkNotFound
		}
		return nil, err
	}

	if err := json.Unmarshal(evidenceJSON, &link.Evidence); err != nil {
		return nil, err
	}

	return &link, nil
}

// GetLinksByItem retrieves all links for an item
func (repo *PgxRepository) GetLinksByItem(ctx context.Context, itemID uuid.UUID) ([]Link, error) {
	query := `
		SELECT id, project_id, source_item_id, target_item_id, link_type, confidence,
		       provenance, evidence, status, confirmed_by, confirmed_at,
		       created_at, updated_at
		FROM equivalence_links
		WHERE (source_item_id = $1 OR target_item_id = $1)
		AND status = 'confirmed'
		ORDER BY created_at DESC
	`

	rows, err := repo.db.Query(ctx, query, itemID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var links []Link
	for rows.Next() {
		var link Link
		var evidenceJSON []byte

		err := rows.Scan(
			&link.ID, &link.ProjectID, &link.SourceItemID, &link.TargetItemID,
			&link.LinkType, &link.Confidence, &link.Provenance, &evidenceJSON,
			&link.Status, &link.ConfirmedBy, &link.ConfirmedAt,
			&link.CreatedAt, &link.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}

		if err := json.Unmarshal(evidenceJSON, &link.Evidence); err != nil {
			return nil, err
		}

		links = append(links, link)
	}

	return links, rows.Err()
}

// ListLinksByProject retrieves links for a project with filtering
func (repo *PgxRepository) ListLinksByProject(
	ctx context.Context,
	filter Filter,
	limit int,
	offset int,
) ([]Link, int64, error) {
	limit, offset = normalizeLimitOffset(limit, offset)
	whereClause, args, argCount := buildLinksWhereClause(filter)

	total, err := repo.countLinks(ctx, whereClause, args)
	if err != nil {
		return nil, 0, err
	}

	links, err := repo.queryLinks(ctx, whereClause, args, argCount, limit, offset)
	if err != nil {
		return nil, 0, err
	}

	return links, total, nil
}

func normalizeLimitOffset(limit, offset int) (int, int) {
	if limit <= 0 {
		limit = defaultPageLimit
	}
	if limit > maxPageLimit {
		limit = maxPageLimit
	}
	if offset < 0 {
		offset = 0
	}

	return limit, offset
}

func buildLinksWhereClause(filter Filter) (string, []interface{}, int) {
	whereClause := "project_id = $1"
	args := []interface{}{filter.ProjectID}
	argCount := 2

	if filter.Status != "" {
		whereClause += fmt.Sprintf(" AND status = $%d", argCount)
		args = append(args, string(filter.Status))
		argCount++
	}

	if filter.MinConfidence > 0 {
		whereClause += fmt.Sprintf(" AND confidence >= $%d", argCount)
		args = append(args, filter.MinConfidence)
		argCount++
	}

	if filter.LinkType != "" {
		whereClause += fmt.Sprintf(" AND link_type = $%d", argCount)
		args = append(args, filter.LinkType)
		argCount++
	}

	if filter.Strategy != "" {
		whereClause += fmt.Sprintf(" AND provenance = $%d", argCount)
		args = append(args, string(filter.Strategy))
		argCount++
	}

	if filter.SourceItemID != nil {
		whereClause += fmt.Sprintf(" AND source_item_id = $%d", argCount)
		args = append(args, *filter.SourceItemID)
		argCount++
	}

	if filter.TargetItemID != nil {
		whereClause += fmt.Sprintf(" AND target_item_id = $%d", argCount)
		args = append(args, *filter.TargetItemID)
		argCount++
	}

	return whereClause, args, argCount
}

func (repo *PgxRepository) countLinks(ctx context.Context, whereClause string, args []interface{}) (int64, error) {
	countQuery := "SELECT COUNT(*) FROM equivalence_links WHERE " + whereClause
	var total int64
	if err := repo.db.QueryRow(ctx, countQuery, args...).Scan(&total); err != nil {
		return 0, err
	}

	return total, nil
}

func (repo *PgxRepository) queryLinks(
	ctx context.Context,
	whereClause string,
	args []interface{},
	argCount int,
	limit int,
	offset int,
) ([]Link, error) {
	query := fmt.Sprintf(`
		SELECT id, project_id, source_item_id, target_item_id, link_type, confidence,
		       provenance, evidence, status, confirmed_by, confirmed_at,
		       created_at, updated_at
		FROM equivalence_links
		WHERE %s
		ORDER BY created_at DESC
		LIMIT $%d OFFSET $%d
	`, whereClause, argCount, argCount+1)

	args = append(args, limit, offset)
	rows, err := repo.db.Query(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var links []Link
	for rows.Next() {
		link, err := scanLink(rows)
		if err != nil {
			return nil, err
		}
		links = append(links, link)
	}

	return links, rows.Err()
}

func scanLink(rows pgx.Rows) (Link, error) {
	var link Link
	var evidenceJSON []byte

	if err := rows.Scan(
		&link.ID, &link.ProjectID, &link.SourceItemID, &link.TargetItemID,
		&link.LinkType, &link.Confidence, &link.Provenance, &evidenceJSON,
		&link.Status, &link.ConfirmedBy, &link.ConfirmedAt,
		&link.CreatedAt, &link.UpdatedAt,
	); err != nil {
		return Link{}, err
	}

	if err := json.Unmarshal(evidenceJSON, &link.Evidence); err != nil {
		return Link{}, err
	}

	return link, nil
}

// UpdateLinkStatus updates the status of a link
func (repo *PgxRepository) UpdateLinkStatus(ctx context.Context, id uuid.UUID, status Status, userID uuid.UUID) error {
	query := `
		UPDATE equivalence_links
		SET status = $1, confirmed_by = $2, confirmed_at = $3, updated_at = $4
		WHERE id = $5
	`

	now := time.Now()
	_, err := repo.db.Exec(ctx, query, string(status), userID, now, now, id)
	return err
}

// ============================================================================
// CANONICAL CONCEPT METHODS
// ============================================================================

// SaveConcept saves a canonical concept to the database
func (repo *PgxRepository) SaveConcept(ctx context.Context, concept *CanonicalConcept) error {
	if concept == nil {
		return errors.New("concept cannot be nil")
	}

	tagsJSON, relatedJSON, childrenJSON, err := marshalConceptJSON(concept)
	if err != nil {
		return err
	}

	query := `
		INSERT INTO canonical_concepts
		(id, project_id, name, slug, description, domain, category, tags,
		 embedding, embedding_model, embedding_updated_at, projection_count,
		 related_concept_ids, parent_concept_id, child_concept_ids,
		 confidence, source, created_by, created_at, updated_at, version)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
		ON CONFLICT (id) DO UPDATE SET
			name = EXCLUDED.name,
			description = EXCLUDED.description,
			domain = EXCLUDED.domain,
			category = EXCLUDED.category,
			tags = EXCLUDED.tags,
			embedding = EXCLUDED.embedding,
			embedding_model = EXCLUDED.embedding_model,
			embedding_updated_at = EXCLUDED.embedding_updated_at,
			projection_count = EXCLUDED.projection_count,
			related_concept_ids = EXCLUDED.related_concept_ids,
			child_concept_ids = EXCLUDED.child_concept_ids,
			confidence = EXCLUDED.confidence,
			updated_at = EXCLUDED.updated_at,
			version = EXCLUDED.version
	`

	_, err = repo.db.Exec(
		ctx,
		query,
		concept.ID,
		concept.ProjectID,
		concept.Name,
		concept.Slug,
		concept.Description,
		concept.Domain,
		concept.Category,
		tagsJSON,
		concept.Embedding,
		concept.EmbeddingModel,
		concept.EmbeddingUpdatedAt,
		concept.ProjectionCount,
		relatedJSON,
		concept.ParentConceptID,
		childrenJSON,
		concept.Confidence,
		string(concept.Source),
		concept.CreatedBy,
		concept.CreatedAt,
		concept.UpdatedAt,
		concept.Version,
	)

	return err
}

func marshalConceptJSON(
	concept *CanonicalConcept,
) ([]byte, []byte, []byte, error) {
	tagsJSON, err := json.Marshal(concept.Tags)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("failed to marshal tags: %w", err)
	}

	relatedJSON, err := json.Marshal(concept.RelatedConceptIDs)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("failed to marshal related concept IDs: %w", err)
	}

	childrenJSON, err := json.Marshal(concept.ChildConceptIDs)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("failed to marshal child concept IDs: %w", err)
	}

	return tagsJSON, relatedJSON, childrenJSON, nil
}

// GetConcept retrieves a canonical concept by ID
func (repo *PgxRepository) GetConcept(ctx context.Context, id uuid.UUID) (*CanonicalConcept, error) {
	query := `
		SELECT id, project_id, name, slug, description, domain, category, tags,
		       embedding, embedding_model, embedding_updated_at, projection_count,
		       related_concept_ids, parent_concept_id, child_concept_ids,
		       confidence, source, created_by, created_at, updated_at, version
		FROM canonical_concepts
		WHERE id = $1
	`

	var concept CanonicalConcept
	var tagsJSON, relatedJSON, childrenJSON []byte

	err := repo.db.QueryRow(ctx, query, id).Scan(
		&concept.ID, &concept.ProjectID, &concept.Name, &concept.Slug, &concept.Description,
		&concept.Domain, &concept.Category, &tagsJSON, &concept.Embedding, &concept.EmbeddingModel,
		&concept.EmbeddingUpdatedAt, &concept.ProjectionCount, &relatedJSON, &concept.ParentConceptID,
		&childrenJSON, &concept.Confidence, (*string)(&concept.Source), &concept.CreatedBy,
		&concept.CreatedAt, &concept.UpdatedAt, &concept.Version,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrConceptNotFound
		}
		return nil, err
	}

	if err := json.Unmarshal(tagsJSON, &concept.Tags); err != nil {
		return nil, err
	}

	if err := json.Unmarshal(relatedJSON, &concept.RelatedConceptIDs); err != nil {
		return nil, err
	}

	if err := json.Unmarshal(childrenJSON, &concept.ChildConceptIDs); err != nil {
		return nil, err
	}

	return &concept, nil
}

// ListConcepts retrieves all canonical concepts for a project
func (repo *PgxRepository) ListConcepts(ctx context.Context, projectID uuid.UUID) ([]CanonicalConcept, error) {
	query := `
		SELECT id, project_id, name, slug, description, domain, category, tags,
		       embedding, embedding_model, embedding_updated_at, projection_count,
		       related_concept_ids, parent_concept_id, child_concept_ids,
		       confidence, source, created_by, created_at, updated_at, version
		FROM canonical_concepts
		WHERE project_id = $1
		ORDER BY created_at DESC
	`

	rows, err := repo.db.Query(ctx, query, projectID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanConcepts(rows)
}

// SearchConceptsByEmbedding searches for similar concepts using vector similarity
func (repo *PgxRepository) SearchConceptsByEmbedding(
	ctx context.Context,
	projectID uuid.UUID,
	embedding []float32,
	limit int,
) ([]CanonicalConcept, error) {
	if limit <= 0 {
		limit = 10
	}

	// Use pgvector for similarity search
	query := `
		SELECT id, project_id, name, slug, description, domain, category, tags,
		       embedding, embedding_model, embedding_updated_at, projection_count,
		       related_concept_ids, parent_concept_id, child_concept_ids,
		       confidence, source, created_by, created_at, updated_at, version
		FROM canonical_concepts
		WHERE project_id = $1 AND embedding IS NOT NULL
		ORDER BY embedding <=> $2
		LIMIT $3
	`

	embeddingJSON, err := json.Marshal(embedding)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal embedding: %w", err)
	}

	rows, err := repo.db.Query(ctx, query, projectID, embeddingJSON, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanConcepts(rows)
}

func scanConcepts(rows pgx.Rows) ([]CanonicalConcept, error) {
	var concepts []CanonicalConcept
	for rows.Next() {
		var concept CanonicalConcept
		var tagsJSON, relatedJSON, childrenJSON []byte

		err := rows.Scan(
			&concept.ID,
			&concept.ProjectID,
			&concept.Name,
			&concept.Slug,
			&concept.Description,
			&concept.Domain,
			&concept.Category,
			&tagsJSON,
			&concept.Embedding,
			&concept.EmbeddingModel,
			&concept.EmbeddingUpdatedAt,
			&concept.ProjectionCount,
			&relatedJSON,
			&concept.ParentConceptID,
			&childrenJSON,
			&concept.Confidence,
			(*string)(&concept.Source),
			&concept.CreatedBy,
			&concept.CreatedAt,
			&concept.UpdatedAt,
			&concept.Version,
		)
		if err != nil {
			return nil, err
		}

		if err := json.Unmarshal(tagsJSON, &concept.Tags); err != nil {
			return nil, err
		}

		if err := json.Unmarshal(relatedJSON, &concept.RelatedConceptIDs); err != nil {
			return nil, err
		}

		if err := json.Unmarshal(childrenJSON, &concept.ChildConceptIDs); err != nil {
			return nil, err
		}

		concepts = append(concepts, concept)
	}

	return concepts, rows.Err()
}

// ============================================================================
// PROJECTION METHODS
// ============================================================================

// SaveProjection saves a canonical projection to the database
func (repo *PgxRepository) SaveProjection(ctx context.Context, projection *CanonicalProjection) error {
	if projection == nil {
		return errors.New("projection cannot be nil")
	}

	metadataJSON, err := json.Marshal(projection.Metadata)
	if err != nil {
		return fmt.Errorf("failed to marshal metadata: %w", err)
	}

	query := `
		INSERT INTO canonical_projections
		(id, project_id, canonical_id, item_id, perspective, role, confidence,
		 provenance, status, confirmed_by, confirmed_at, metadata, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
		ON CONFLICT (id) DO UPDATE SET
			role = EXCLUDED.role,
			confidence = EXCLUDED.confidence,
			provenance = EXCLUDED.provenance,
			status = EXCLUDED.status,
			confirmed_by = EXCLUDED.confirmed_by,
			confirmed_at = EXCLUDED.confirmed_at,
			metadata = EXCLUDED.metadata,
			updated_at = EXCLUDED.updated_at
	`

	_, err = repo.db.Exec(ctx, query,
		projection.ID, projection.ProjectID, projection.CanonicalID, projection.ItemID,
		projection.Perspective, projection.Role, projection.Confidence,
		string(projection.Provenance), string(projection.Status),
		projection.ConfirmedBy, projection.ConfirmedAt, metadataJSON,
		projection.CreatedAt, projection.UpdatedAt,
	)

	return err
}

// GetProjectionsByItem retrieves all projections for an item
func (repo *PgxRepository) GetProjectionsByItem(ctx context.Context, itemID uuid.UUID) ([]CanonicalProjection, error) {
	return repo.getProjectionsBy(ctx, "item_id", itemID, "created_at DESC")
}

// GetProjectionsByConcept retrieves all projections for a concept
func (repo *PgxRepository) GetProjectionsByConcept(
	ctx context.Context,
	conceptID uuid.UUID,
) ([]CanonicalProjection, error) {
	return repo.getProjectionsBy(ctx, "canonical_id", conceptID, "perspective, created_at DESC")
}

func (repo *PgxRepository) getProjectionsBy(
	ctx context.Context,
	field string,
	id uuid.UUID,
	orderBy string,
) ([]CanonicalProjection, error) {
	query := fmt.Sprintf(`
		SELECT id, project_id, canonical_id, item_id, perspective, role, confidence,
		       provenance, status, confirmed_by, confirmed_at, metadata, created_at, updated_at
		FROM canonical_projections
		WHERE %s = $1
		ORDER BY %s
	`, field, orderBy)

	return repo.fetchProjections(ctx, query, id)
}

func (repo *PgxRepository) fetchProjections(
	ctx context.Context,
	query string,
	id uuid.UUID,
) ([]CanonicalProjection, error) {
	rows, err := repo.db.Query(ctx, query, id)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var projections []CanonicalProjection
	for rows.Next() {
		var projection CanonicalProjection
		var metadataJSON []byte

		err := rows.Scan(
			&projection.ID, &projection.ProjectID, &projection.CanonicalID, &projection.ItemID,
			&projection.Perspective, &projection.Role,
			&projection.Confidence, (*string)(&projection.Provenance), (*string)(&projection.Status),
			&projection.ConfirmedBy, &projection.ConfirmedAt, &metadataJSON,
			&projection.CreatedAt, &projection.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}

		if metadataJSON != nil {
			if err := json.Unmarshal(metadataJSON, &projection.Metadata); err != nil {
				return nil, err
			}
		}

		projections = append(projections, projection)
	}

	return projections, rows.Err()
}

// GetProjection retrieves a projection by ID
func (repo *PgxRepository) GetProjection(ctx context.Context, id uuid.UUID) (*CanonicalProjection, error) {
	query := `
		SELECT id, project_id, canonical_id, item_id, perspective, role, confidence,
		       provenance, status, confirmed_by, confirmed_at, metadata, created_at, updated_at
		FROM canonical_projections
		WHERE id = $1
	`

	var projection CanonicalProjection
	var metadataJSON []byte

	err := repo.db.QueryRow(ctx, query, id).Scan(
		&projection.ID, &projection.ProjectID, &projection.CanonicalID, &projection.ItemID,
		&projection.Perspective, &projection.Role,
		&projection.Confidence, (*string)(&projection.Provenance), (*string)(&projection.Status),
		&projection.ConfirmedBy, &projection.ConfirmedAt, &metadataJSON,
		&projection.CreatedAt, &projection.UpdatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("projection not found")
		}
		return nil, err
	}

	if metadataJSON != nil {
		if err := json.Unmarshal(metadataJSON, &projection.Metadata); err != nil {
			return nil, err
		}
	}

	return &projection, nil
}

// DeleteProjection deletes a projection by ID
func (repo *PgxRepository) DeleteProjection(ctx context.Context, id uuid.UUID) error {
	query := `DELETE FROM canonical_projections WHERE id = $1`
	_, err := repo.db.Exec(ctx, query, id)
	return err
}

// ============================================================================
// ERROR DEFINITIONS
// ============================================================================

var (
	// ErrSuggestionNotFound indicates a suggestion could not be found.
	ErrSuggestionNotFound = errors.New("suggestion not found")
	// ErrLinkNotFound indicates an equivalence link could not be found.
	ErrLinkNotFound = errors.New("equivalence link not found")
	// ErrConceptNotFound indicates a canonical concept could not be found.
	ErrConceptNotFound = errors.New("canonical concept not found")
)
