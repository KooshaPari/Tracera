package ports

import (
	"context"
	"github.com/google/uuid"
	"github.com/org/microservice/internal/domain/entities"
)

// Repository port - outbound interface (Dependency Inversion)
type Repository interface {
	Save(ctx context.Context, entity *entities.Entity) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.Entity, error)
	Delete(ctx context.Context, id uuid.UUID) error
}

// EventPublisher port - for event-driven architecture
type EventPublisher interface {
	Publish(ctx context.Context, subject string, data []byte) error
}
