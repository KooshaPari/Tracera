package queries

import (
	"context"

	"hexagonal-go/domain/entities"
	"hexagonal-go/domain/ports/outbound"
	"hexagonal-go/domain/valueobjects"
)

// QueryHandler handles read operations (CQRS Queries)
type QueryHandler struct {
	repo outbound.Repository
}

// NewQueryHandler creates a new query handler
func NewQueryHandler(repo outbound.Repository) *QueryHandler {
	return &QueryHandler{repo: repo}
}

// GetByIDQuery retrieves an entity by ID
type GetByIDQuery struct {
	ID string
}

// Handle executes the get by ID query
func (h *QueryHandler) HandleGetByID(ctx context.Context, query GetByIDQuery) (*entities.Entity, error) {
	return h.repo.FindByID(ctx, query.ID)
}

// ListQuery returns paginated entities
type ListQuery struct {
	Page     int
	PageSize int
}

// Handle executes the list query
func (h *QueryHandler) HandleList(ctx context.Context, query ListQuery) ([]*entities.Entity, error) {
	pagination := valueobjects.Pagination{
		Page:     query.Page,
		PageSize: query.PageSize,
	}
	if pagination.Page == 0 {
		pagination = valueobjects.DefaultPagination()
	}
	return h.repo.List(ctx, pagination)
}
