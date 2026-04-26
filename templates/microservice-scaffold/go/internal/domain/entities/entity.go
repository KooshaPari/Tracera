package entities

import (
	"time"
	"github.com/google/uuid"
)

type Entity struct {
	ID        uuid.UUID
	CreatedAt time.Time
	UpdatedAt time.Time
}

func NewEntity() *Entity {
	return &Entity{
		ID:        uuid.New(),
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
}

func (e *Entity) Touch() {
	e.UpdatedAt = time.Now()
}
