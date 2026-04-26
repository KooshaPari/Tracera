package queries

import (
	"context"
	"github.com/google/uuid"
	"github.com/org/microservice/internal/domain/errors"
	"github.com/org/microservice/internal/domain/ports"
)

type QueryHandler struct {
	repo ports.Repository
}

func NewQueryHandler(repo ports.Repository) *QueryHandler {
	return &QueryHandler{repo: repo}
}

// GetByIDQuery - CQRS Query for retrieving entity
type GetByIDQuery struct {
	ID string
}

func (h *QueryHandler) HandleGetByID(ctx context.Context, query GetByIDQuery) (interface{}, error) {
	id, err := uuid.Parse(query.ID)
	if err != nil {
		return nil, &errors.DomainError{
			Err:     errors.ErrInvalidInput,
			Field:   "id",
			Code:    "INVALID_ID",
			Message: "invalid UUID format",
		}
	}

	entity, err := h.repo.FindByID(ctx, id)
	if err != nil {
		return nil, err
	}

	return entity, nil
}
