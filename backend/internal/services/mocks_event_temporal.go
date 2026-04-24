package services

import (
	"context"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// MockTemporalService for testing
type MockTemporalService struct {
	GetItemVersionFunc   func(ctx context.Context, itemID string, version int) (*models.Item, error)
	ListItemVersionsFunc func(ctx context.Context, itemID string) ([]*VersionInfo, error)
	GetItemAtTimeFunc    func(ctx context.Context, itemID string, timestamp time.Time) (*models.Item, error)
}

// GetItemVersion implements TemporalService.GetItemVersion for testing.
func (m *MockTemporalService) GetItemVersion(ctx context.Context, itemID string, version int) (*models.Item, error) {
	if m.GetItemVersionFunc != nil {
		return m.GetItemVersionFunc(ctx, itemID, version)
	}
	return nil, nil
}

// ListItemVersions implements TemporalService.ListItemVersions for testing.
func (m *MockTemporalService) ListItemVersions(ctx context.Context, itemID string) ([]*VersionInfo, error) {
	if m.ListItemVersionsFunc != nil {
		return m.ListItemVersionsFunc(ctx, itemID)
	}
	return nil, nil
}

// GetItemAtTime implements TemporalService.GetItemAtTime for testing.
func (m *MockTemporalService) GetItemAtTime(ctx context.Context, itemID string, timestamp time.Time) (*models.Item, error) {
	if m.GetItemAtTimeFunc != nil {
		return m.GetItemAtTimeFunc(ctx, itemID, timestamp)
	}
	return nil, nil
}

// MockEventService for testing
type MockEventService struct {
	PublishItemEventFunc    func(ctx context.Context, event *ItemEvent) error
	PublishLinkEventFunc    func(ctx context.Context, event *LinkEvent) error
	PublishProjectEventFunc func(ctx context.Context, event *ProjectEvent) error
	PublishAgentEventFunc   func(ctx context.Context, event *AgentEventType) error
}

// PublishItemEvent implements EventService.PublishItemEvent for testing.
func (m *MockEventService) PublishItemEvent(ctx context.Context, event *ItemEvent) error {
	if m.PublishItemEventFunc != nil {
		return m.PublishItemEventFunc(ctx, event)
	}
	return nil
}

// PublishLinkEvent implements EventService.PublishLinkEvent for testing.
func (m *MockEventService) PublishLinkEvent(ctx context.Context, event *LinkEvent) error {
	if m.PublishLinkEventFunc != nil {
		return m.PublishLinkEventFunc(ctx, event)
	}
	return nil
}

// PublishProjectEvent implements EventService.PublishProjectEvent for testing.
func (m *MockEventService) PublishProjectEvent(ctx context.Context, event *ProjectEvent) error {
	if m.PublishProjectEventFunc != nil {
		return m.PublishProjectEventFunc(ctx, event)
	}
	return nil
}

// PublishAgentEvent implements EventService.PublishAgentEvent for testing.
func (m *MockEventService) PublishAgentEvent(ctx context.Context, event *AgentEventType) error {
	if m.PublishAgentEventFunc != nil {
		return m.PublishAgentEventFunc(ctx, event)
	}
	return nil
}

// SubscribeToItemEvents implements EventService.SubscribeToItemEvents for testing.
func (m *MockEventService) SubscribeToItemEvents(_ context.Context, _ ItemEventHandler) error {
	return nil
}

// SubscribeToLinkEvents implements EventService.SubscribeToLinkEvents for testing.
func (m *MockEventService) SubscribeToLinkEvents(_ context.Context, _ LinkEventHandler) error {
	return nil
}

// SubscribeToProjectEvents implements EventService.SubscribeToProjectEvents for testing.
func (m *MockEventService) SubscribeToProjectEvents(_ context.Context, _ ProjectEventHandler) error {
	return nil
}

// SubscribeToAgentEvents implements EventService.SubscribeToAgentEvents for testing.
func (m *MockEventService) SubscribeToAgentEvents(_ context.Context, _ AgentEventHandler) error {
	return nil
}
