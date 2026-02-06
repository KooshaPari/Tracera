//go:build !ignore

// Package docservice provides the documentation service layer.
package docservice

import (
	"context"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Service provides documentation operations backed by Postgres.
type Service struct {
	pool *pgxpool.Pool
}

// NewService creates a Service.
func NewService(pool *pgxpool.Pool) *Service {
	return &Service{pool: pool}
}

// GetDocumentation fetches a documentation record by ID.
func (s *Service) GetDocumentation(_ context.Context, _ uuid.UUID) (interface{}, error) {
	return nil, nil
}

// IndexDocumentation indexes a documentation payload.
func (s *Service) IndexDocumentation(_ context.Context, _ interface{}) (interface{}, error) {
	return nil, nil
}

// ListDocumentation lists documentation for a project.
func (s *Service) ListDocumentation(_ context.Context, _ uuid.UUID, _, _ int) (interface{}, int, error) {
	return nil, 0, nil
}

// UpdateDocumentation updates an existing documentation record.
func (s *Service) UpdateDocumentation(_ context.Context, _ uuid.UUID, _ interface{}) (interface{}, error) {
	return nil, nil
}

// DeleteDocumentation removes a documentation record by ID.
func (s *Service) DeleteDocumentation(_ context.Context, _ uuid.UUID) error {
	return nil
}

// SearchDocumentation performs a search across documentation.
func (s *Service) SearchDocumentation(_ context.Context, _ uuid.UUID, _ string, _, _ int) (interface{}, int, error) {
	return nil, 0, nil
}

// IndexDocumentationRequest represents an indexing payload.
type IndexDocumentationRequest struct {
	ProjectID string
	Title     string
	Format    string
	Content   string
}

// ParsedDocument represents a parsed documentation record.
type ParsedDocument struct {
	ID      uuid.UUID
	Title   string
	Content string
}

// NewDocumentationRepository creates a documentation repository.
func NewDocumentationRepository(_ *pgxpool.Pool) interface{} {
	return nil
}
