package commands

import (
	"context"

	"hexagonal-go/domain/entities"
	"hexagonal-go/domain/ports/inbound"
	"hexagonal-go/domain/ports/outbound"
)

// CommandHandler handles write operations (CQRS Commands)
type CommandHandler struct {
	repo outbound.Repository
}

// NewCommandHandler creates a new command handler
func NewCommandHandler(repo outbound.Repository) *CommandHandler {
	return &CommandHandler{repo: repo}
}

// CreateCommand creates a new entity
type CreateCommand struct {
	Name        string
	Description string
}

// Handle executes the create command
func (h *CommandHandler) Handle(ctx context.Context, cmd CreateCommand) (*entities.Entity, error) {
	entity := entities.NewExample(cmd.Name, cmd.Description)
	if err := entity.Validate(); err != nil {
		return nil, err
	}
	if err := h.repo.Save(ctx, entity); err != nil {
		return nil, err
	}
	return entity, nil
}

// UpdateCommand updates an existing entity
type UpdateCommand struct {
	ID          string
	Name        string
	Description string
}

// Handle executes the update command
func (h *CommandHandler) HandleUpdate(ctx context.Context, cmd UpdateCommand) (*entities.Entity, error) {
	entity, err := h.repo.FindByID(ctx, cmd.ID)
	if err != nil {
		return nil, err
	}

	example, ok := entity.(*entities.Example)
	if !ok {
		return nil, err
	}

	example.Name = cmd.Name
	example.Description = cmd.Description
	example.Touch()

	if err := h.repo.Save(ctx, example); err != nil {
		return nil, err
	}
	return example, nil
}

// DeleteCommand removes an entity
type DeleteCommand struct {
	ID string
}

// Handle executes the delete command
func (h *CommandHandler) HandleDelete(ctx context.Context, cmd DeleteCommand) error {
	return h.repo.Delete(ctx, cmd.ID)
}
