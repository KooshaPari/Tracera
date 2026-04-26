package commands

import (
	"context"
	"github.com/google/uuid"
	"github.com/org/microservice/internal/domain/errors"
	"github.com/org/microservice/internal/domain/ports"
)

type CommandHandler struct {
	repo ports.Repository
}

func NewCommandHandler(repo ports.Repository) *CommandHandler {
	return &CommandHandler{repo: repo}
}

// CreateCommand - CQRS Command for creating entities
type CreateCommand struct {
	Name string
}

func (h *CommandHandler) HandleCreate(ctx context.Context, cmd CreateCommand) (*Result, error) {
	if cmd.Name == "" {
		return nil, &errors.DomainError{
			Err:     errors.ErrInvalidInput,
			Field:   "name",
			Code:    "INVALID_NAME",
			Message: "name is required",
		}
	}

	entity := &entities.Entity{
		ID:        uuid.New(),
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := h.repo.Save(ctx, entity); err != nil {
		return nil, err
	}

	return &Result{ID: entity.ID.String()}, nil
}

type Result struct {
	ID string
}
