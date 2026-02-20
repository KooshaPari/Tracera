package events

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
)

// PostgresEventStore implements EventStore using PostgreSQL
type PostgresEventStore struct {
	pool *pgxpool.Pool
}

// NewPostgresEventStore creates a new PostgreSQL event store
func NewPostgresEventStore(pool *pgxpool.Pool) *PostgresEventStore {
	return &PostgresEventStore{
		pool: pool,
	}
}

// Store saves an event to the database
func (store *PostgresEventStore) Store(event *Event) error {
	ctx := context.Background()

	dataJSON, metadataJSON, err := marshalEventPayloads(event)
	if err != nil {
		return err
	}

	query := `
		INSERT INTO events (
			id,
			project_id,
			entity_type,
			entity_id,
			event_type,
			data,
			metadata,
			version,
			causation_id,
			correlation_id,
			created_at
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
	`

	if err := execEventInsert(ctx, store.pool, query, event, dataJSON, metadataJSON); err != nil {
		return err
	}

	return nil
}

// StoreMany saves multiple events atomically in a transaction
func (store *PostgresEventStore) StoreMany(events []*Event) (returnErr error) {
	ctx := context.Background()

	tx, err := store.pool.Begin(ctx)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer func() {
		if returnErr == nil {
			return
		}
		if rollbackErr := tx.Rollback(ctx); rollbackErr != nil && !errors.Is(rollbackErr, pgx.ErrTxClosed) {
			returnErr = fmt.Errorf("%w; rollback failed: %w", returnErr, rollbackErr)
		}
	}()

	query := `
		INSERT INTO events (
			id,
			project_id,
			entity_type,
			entity_id,
			event_type,
			data,
			metadata,
			version,
			causation_id,
			correlation_id,
			created_at
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
		`

	for _, event := range events {
		if err := execEventInsertTx(ctx, tx, query, event); err != nil {
			return err
		}
	}

	if err := tx.Commit(ctx); err != nil {
		return fmt.Errorf("failed to commit transaction: %w", err)
	}

	return nil
}

func marshalEventPayloads(event *Event) ([]byte, []byte, error) {
	dataJSON, err := json.Marshal(event.Data)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to marshal event data: %w", err)
	}

	metadataJSON, err := json.Marshal(event.Metadata)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to marshal event metadata: %w", err)
	}

	return dataJSON, metadataJSON, nil
}

func execEventInsertTx(ctx context.Context, tx interface {
	Exec(context.Context, string, ...interface{}) (pgconn.CommandTag, error)
}, query string, event *Event,
) error {
	dataJSON, metadataJSON, err := marshalEventPayloads(event)
	if err != nil {
		return err
	}
	if err := execEventInsert(ctx, tx, query, event, dataJSON, metadataJSON); err != nil {
		return fmt.Errorf("failed to store event in transaction: %w", err)
	}
	return nil
}

func execEventInsert(ctx context.Context, execer interface {
	Exec(context.Context, string, ...interface{}) (pgconn.CommandTag, error)
}, query string, event *Event, dataJSON, metadataJSON []byte,
) error {
	_, err := execer.Exec(ctx, query,
		event.ID,
		event.ProjectID,
		event.EntityType,
		event.EntityID,
		event.EventType,
		dataJSON,
		metadataJSON,
		event.Version,
		event.CausationID,
		event.CorrelationID,
		event.CreatedAt,
	)
	if err != nil {
		return fmt.Errorf("failed to store event: %w", err)
	}
	return nil
}

// GetByEntityID retrieves all events for a specific entity
func (store *PostgresEventStore) GetByEntityID(entityID string) ([]*Event, error) {
	ctx := context.Background()

	query := `
		SELECT
			id,
			project_id,
			entity_type,
			entity_id,
			event_type,
			data,
			metadata,
			version,
			causation_id,
			correlation_id,
			created_at
		FROM events
		WHERE entity_id = $1
		ORDER BY version ASC, created_at ASC
	`

	rows, err := store.pool.Query(ctx, query, entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to query events: %w", err)
	}
	defer rows.Close()

	return store.scanEvents(rows)
}

// GetByEntityIDAfterVersion retrieves events after a specific version
func (store *PostgresEventStore) GetByEntityIDAfterVersion(entityID string, version int64) ([]*Event, error) {
	ctx := context.Background()

	query := `
		SELECT
			id,
			project_id,
			entity_type,
			entity_id,
			event_type,
			data,
			metadata,
			version,
			causation_id,
			correlation_id,
			created_at
		FROM events
		WHERE entity_id = $1 AND version > $2
		ORDER BY version ASC, created_at ASC
	`

	rows, err := store.pool.Query(ctx, query, entityID, version)
	if err != nil {
		return nil, fmt.Errorf("failed to query events: %w", err)
	}
	defer rows.Close()

	return store.scanEvents(rows)
}

// GetByProjectID retrieves all events for a project with pagination
func (store *PostgresEventStore) GetByProjectID(projectID string, limit, offset int) ([]*Event, error) {
	ctx := context.Background()

	query := `
		SELECT
			id,
			project_id,
			entity_type,
			entity_id,
			event_type,
			data,
			metadata,
			version,
			causation_id,
			correlation_id,
			created_at
		FROM events
		WHERE project_id = $1
		ORDER BY created_at DESC
		LIMIT $2 OFFSET $3
	`

	rows, err := store.pool.Query(ctx, query, projectID, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query events: %w", err)
	}
	defer rows.Close()

	return store.scanEvents(rows)
}

// GetByProjectIDAndType retrieves events by project and entity type
func (store *PostgresEventStore) GetByProjectIDAndType(
	projectID string,
	entityType EntityType,
	limit int,
	offset int,
) ([]*Event, error) {
	ctx := context.Background()

	query := `
		SELECT
			id,
			project_id,
			entity_type,
			entity_id,
			event_type,
			data,
			metadata,
			version,
			causation_id,
			correlation_id,
			created_at
		FROM events
		WHERE project_id = $1 AND entity_type = $2
		ORDER BY created_at DESC
		LIMIT $3 OFFSET $4
	`

	rows, err := store.pool.Query(ctx, query, projectID, entityType, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query events: %w", err)
	}
	defer rows.Close()

	return store.scanEvents(rows)
}

// GetByTimeRange retrieves events within a time range
func (store *PostgresEventStore) GetByTimeRange(projectID string, start, end time.Time) ([]*Event, error) {
	ctx := context.Background()

	query := `
		SELECT
			id,
			project_id,
			entity_type,
			entity_id,
			event_type,
			data,
			metadata,
			version,
			causation_id,
			correlation_id,
			created_at
		FROM events
		WHERE project_id = $1 AND created_at BETWEEN $2 AND $3
		ORDER BY created_at ASC
	`

	rows, err := store.pool.Query(ctx, query, projectID, start, end)
	if err != nil {
		return nil, fmt.Errorf("failed to query events: %w", err)
	}
	defer rows.Close()

	return store.scanEvents(rows)
}

// SaveSnapshot saves a snapshot to the database
func (store *PostgresEventStore) SaveSnapshot(snapshot *Snapshot) error {
	ctx := context.Background()

	// First, create snapshots table if it doesn't exist
	createTableQuery := `
		CREATE TABLE IF NOT EXISTS snapshots (
			id UUID PRIMARY KEY,
			project_id UUID NOT NULL,
			entity_type VARCHAR(50) NOT NULL,
			entity_id UUID NOT NULL,
			version BIGINT NOT NULL,
			state JSONB NOT NULL,
			created_at TIMESTAMP NOT NULL,
			UNIQUE(entity_id, version)
		);
		CREATE INDEX IF NOT EXISTS idx_snapshots_entity_id ON snapshots(entity_id);
		CREATE INDEX IF NOT EXISTS idx_snapshots_version ON snapshots(entity_id, version DESC);
	`

	_, err := store.pool.Exec(ctx, createTableQuery)
	if err != nil {
		return fmt.Errorf("failed to create snapshots table: %w", err)
	}

	stateJSON, err := json.Marshal(snapshot.State)
	if err != nil {
		return fmt.Errorf("failed to marshal snapshot state: %w", err)
	}

	query := `
		INSERT INTO snapshots (id, project_id, entity_type, entity_id, version, state, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		ON CONFLICT (entity_id, version) DO UPDATE SET
			state = EXCLUDED.state,
			created_at = EXCLUDED.created_at
	`

	_, err = store.pool.Exec(ctx, query,
		snapshot.ID,
		snapshot.ProjectID,
		snapshot.EntityType,
		snapshot.EntityID,
		snapshot.Version,
		stateJSON,
		snapshot.CreatedAt,
	)
	if err != nil {
		return fmt.Errorf("failed to save snapshot: %w", err)
	}

	return nil
}

// GetLatestSnapshot retrieves the most recent snapshot for an entity
func (store *PostgresEventStore) GetLatestSnapshot(entityID string) (*Snapshot, error) {
	ctx := context.Background()

	query := `
		SELECT id, project_id, entity_type, entity_id, version, state, created_at
		FROM snapshots
		WHERE entity_id = $1
		ORDER BY version DESC
		LIMIT 1
	`

	var snapshot Snapshot
	var stateJSON []byte

	err := store.pool.QueryRow(ctx, query, entityID).Scan(
		&snapshot.ID,
		&snapshot.ProjectID,
		&snapshot.EntityType,
		&snapshot.EntityID,
		&snapshot.Version,
		&stateJSON,
		&snapshot.CreatedAt,
	)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, nil // No snapshot found
		}
		return nil, fmt.Errorf("failed to get latest snapshot: %w", err)
	}

	if err := json.Unmarshal(stateJSON, &snapshot.State); err != nil {
		return nil, fmt.Errorf("failed to unmarshal snapshot state: %w", err)
	}

	return &snapshot, nil
}

// GetSnapshotAtVersion retrieves a snapshot at or before a specific version
func (store *PostgresEventStore) GetSnapshotAtVersion(entityID string, version int64) (*Snapshot, error) {
	ctx := context.Background()

	query := `
		SELECT id, project_id, entity_type, entity_id, version, state, created_at
		FROM snapshots
		WHERE entity_id = $1 AND version <= $2
		ORDER BY version DESC
		LIMIT 1
	`

	var snapshot Snapshot
	var stateJSON []byte

	err := store.pool.QueryRow(ctx, query, entityID, version).Scan(
		&snapshot.ID,
		&snapshot.ProjectID,
		&snapshot.EntityType,
		&snapshot.EntityID,
		&snapshot.Version,
		&stateJSON,
		&snapshot.CreatedAt,
	)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, nil // No snapshot found
		}
		return nil, fmt.Errorf("failed to get snapshot at version: %w", err)
	}

	if err := json.Unmarshal(stateJSON, &snapshot.State); err != nil {
		return nil, fmt.Errorf("failed to unmarshal snapshot state: %w", err)
	}

	return &snapshot, nil
}

// Replay replays all events to reconstruct entity state
func (store *PostgresEventStore) Replay(entityID string) (map[string]interface{}, error) {
	events, err := store.GetByEntityID(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get events for replay: %w", err)
	}

	state := make(map[string]interface{})
	for _, event := range events {
		// Apply each event's data to the state
		for k, v := range event.Data {
			state[k] = v
		}
	}

	return state, nil
}

// ReplayFromSnapshot replays events from a snapshot to reconstruct entity state
func (store *PostgresEventStore) ReplayFromSnapshot(
	entityID string,
	snapshotVersion int64,
) (map[string]interface{}, error) {
	// Get the snapshot at or before the specified version
	snapshot, err := store.GetSnapshotAtVersion(entityID, snapshotVersion)
	if err != nil {
		return nil, fmt.Errorf("failed to get snapshot: %w", err)
	}

	// Start with snapshot state or empty state
	state := make(map[string]interface{})
	if snapshot != nil {
		state = snapshot.State
		snapshotVersion = snapshot.Version
	}

	// Get events after the snapshot
	events, err := store.GetByEntityIDAfterVersion(entityID, snapshotVersion)
	if err != nil {
		return nil, fmt.Errorf("failed to get events after snapshot: %w", err)
	}

	// Apply events to the state
	for _, event := range events {
		for k, v := range event.Data {
			state[k] = v
		}
	}

	return state, nil
}

// scanEvents is a helper function to scan event rows
func (store *PostgresEventStore) scanEvents(rows pgx.Rows) ([]*Event, error) {
	events := make([]*Event, 0)

	for rows.Next() {
		var event Event
		var dataJSON []byte
		var metadataJSON []byte

		err := rows.Scan(
			&event.ID,
			&event.ProjectID,
			&event.EntityType,
			&event.EntityID,
			&event.EventType,
			&dataJSON,
			&metadataJSON,
			&event.Version,
			&event.CausationID,
			&event.CorrelationID,
			&event.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan event row: %w", err)
		}

		if err := json.Unmarshal(dataJSON, &event.Data); err != nil {
			return nil, fmt.Errorf("failed to unmarshal event data: %w", err)
		}

		if len(metadataJSON) > 0 {
			if err := json.Unmarshal(metadataJSON, &event.Metadata); err != nil {
				return nil, fmt.Errorf("failed to unmarshal event metadata: %w", err)
			}
		}

		events = append(events, &event)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating event rows: %w", err)
	}

	return events, nil
}

// GetEventCount returns the total number of events for an entity
func (store *PostgresEventStore) GetEventCount(entityID string) (int64, error) {
	ctx := context.Background()

	query := `SELECT COUNT(*) FROM events WHERE entity_id = $1`

	var count int64
	err := store.pool.QueryRow(ctx, query, entityID).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to get event count: %w", err)
	}

	return count, nil
}

// PurgeOldEvents removes events older than a specified time
func (store *PostgresEventStore) PurgeOldEvents(before time.Time) (int64, error) {
	ctx := context.Background()

	query := `DELETE FROM events WHERE created_at < $1`

	result, err := store.pool.Exec(ctx, query, before)
	if err != nil {
		return 0, fmt.Errorf("failed to purge old events: %w", err)
	}

	return result.RowsAffected(), nil
}
