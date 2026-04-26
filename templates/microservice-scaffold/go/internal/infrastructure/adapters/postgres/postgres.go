package postgres

import (
	"context"
	"database/sql"
	"fmt"
	"github.com/google/uuid"
	_ "github.com/jackc/pgx/v5/stdlib"
	"github.com/org/microservice/internal/domain/entities"
	"github.com/org/microservice/internal/domain/errors"
)

// PostgresAdapter wraps pgx driver (Wrap-Over pattern)
type PostgresAdapter struct {
	db *sql.DB
}

// Compile-time interface check
var _ Repository = (*PostgresAdapter)(nil)

type Repository interface {
	Save(ctx context.Context, entity *entities.Entity) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.Entity, error)
	Delete(ctx context.Context, id uuid.UUID) error
}

func NewPostgresAdapter(connectionString string) (*PostgresAdapter, error) {
	db, err := sql.Open("pgx", connectionString)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &PostgresAdapter{db: db}, nil
}

func (a *PostgresAdapter) Close() error {
	return a.db.Close()
}

func (a *PostgresAdapter) Save(ctx context.Context, entity *entities.Entity) error {
	query := `INSERT INTO entities (id, created_at, updated_at) VALUES ($1, $2, $3)`
	_, err := a.db.ExecContext(ctx, query, entity.ID, entity.CreatedAt, entity.UpdatedAt)
	return err
}

func (a *PostgresAdapter) FindByID(ctx context.Context, id uuid.UUID) (*entities.Entity, error) {
	query := `SELECT id, created_at, updated_at FROM entities WHERE id = $1`
	row := a.db.QueryRowContext(ctx, query, id)

	var entity entities.Entity
	err := row.Scan(&entity.ID, &entity.CreatedAt, &entity.UpdatedAt)
	if err == sql.ErrNoRows {
		return nil, errors.ErrNotFound
	}
	if err != nil {
		return nil, err
	}
	return &entity, nil
}

func (a *PostgresAdapter) Delete(ctx context.Context, id uuid.UUID) error {
	query := `DELETE FROM entities WHERE id = $1`
	result, err := a.db.ExecContext(ctx, query, id)
	if err != nil {
		return err
	}
	rows, _ := result.RowsAffected()
	if rows == 0 {
		return errors.ErrNotFound
	}
	return nil
}
