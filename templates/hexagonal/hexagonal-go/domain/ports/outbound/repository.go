package outbound

import (
	"context"

	"hexagonal-go/domain/entities"
	"hexagonal-go/domain/valueobjects"
)

// Repository defines the outbound port for entity persistence
type Repository interface {
	// Save persists an entity
	Save(ctx context.Context, entity *entities.Entity) error

	// FindByID retrieves an entity by ID
	FindByID(ctx context.Context, id string) (*entities.Entity, error)

	// Delete removes an entity
	Delete(ctx context.Context, id string) error

	// List returns all entities with pagination
	List(ctx context.Context, pagination valueobjects.Pagination) ([]*entities.Entity, error)
}
