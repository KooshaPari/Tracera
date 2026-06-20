package services

import (
	"context"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// MockItemService for testing handlers and other services
type MockItemService struct {
	OnCreateItem   func(ctx context.Context, item *models.Item) error
	OnCreateBatch  func(ctx context.Context, items []*models.Item) error
	OnGetItem      func(ctx context.Context, id string) (*models.Item, error)
	OnGetWithLinks func(ctx context.Context, id string) (*ItemWithLinks, error)
	OnListItems    func(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error)
	OnCount        func(ctx context.Context, filter repository.ItemFilter) (int64, error)
	OnUpdateItem   func(ctx context.Context, item *models.Item) error
	OnUpdateStatus func(ctx context.Context, id, status string) error
	OnUpdateBatch  func(ctx context.Context, items []*models.Item) error
	OnDeleteItem   func(ctx context.Context, id string) error
	OnDeleteBatch  func(ctx context.Context, ids []string) error
	OnValidate     func(ctx context.Context, item *models.Item) error
	OnItemExists   func(ctx context.Context, id string) (bool, error)
	OnGetItemStats func(ctx context.Context, projectID string) (*ItemStats, error)
}

// CreateItem implements ItemService.CreateItem for testing.
func (m *MockItemService) CreateItem(ctx context.Context, item *models.Item) error {
	if m.OnCreateItem != nil {
		return m.OnCreateItem(ctx, item)
	}
	return nil
}

// CreateBatch implements ItemService.CreateBatch for testing.
func (m *MockItemService) CreateBatch(ctx context.Context, items []*models.Item) error {
	if m.OnCreateBatch != nil {
		return m.OnCreateBatch(ctx, items)
	}
	return nil
}

// GetItem implements ItemService.GetItem for testing.
func (m *MockItemService) GetItem(ctx context.Context, id string) (*models.Item, error) {
	if m.OnGetItem != nil {
		return m.OnGetItem(ctx, id)
	}
	return nil, nil
}

// GetWithLinks implements ItemService.GetWithLinks for testing.
func (m *MockItemService) GetWithLinks(ctx context.Context, id string) (*ItemWithLinks, error) {
	if m.OnGetWithLinks != nil {
		return m.OnGetWithLinks(ctx, id)
	}
	return nil, nil
}

// ListItems implements ItemService.ListItems for testing.
func (m *MockItemService) ListItems(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	if m.OnListItems != nil {
		return m.OnListItems(ctx, filter)
	}
	return nil, nil
}

// Count implements ItemService.Count for testing.
func (m *MockItemService) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	if m.OnCount != nil {
		return m.OnCount(ctx, filter)
	}
	return 0, nil
}

// UpdateItem implements ItemService.UpdateItem for testing.
func (m *MockItemService) UpdateItem(ctx context.Context, item *models.Item) error {
	if m.OnUpdateItem != nil {
		return m.OnUpdateItem(ctx, item)
	}
	return nil
}

// UpdateStatus implements ItemService.UpdateStatus for testing.
func (m *MockItemService) UpdateStatus(ctx context.Context, id, status string) error {
	if m.OnUpdateStatus != nil {
		return m.OnUpdateStatus(ctx, id, status)
	}
	return nil
}

// UpdateBatch implements ItemService.UpdateBatch for testing.
func (m *MockItemService) UpdateBatch(ctx context.Context, items []*models.Item) error {
	if m.OnUpdateBatch != nil {
		return m.OnUpdateBatch(ctx, items)
	}
	return nil
}

// DeleteItem implements ItemService.DeleteItem for testing.
func (m *MockItemService) DeleteItem(ctx context.Context, id string) error {
	if m.OnDeleteItem != nil {
		return m.OnDeleteItem(ctx, id)
	}
	return nil
}

// DeleteBatch implements ItemService.DeleteBatch for testing.
func (m *MockItemService) DeleteBatch(ctx context.Context, ids []string) error {
	if m.OnDeleteBatch != nil {
		return m.OnDeleteBatch(ctx, ids)
	}
	return nil
}

// Validate implements ItemService.Validate for testing.
func (m *MockItemService) Validate(ctx context.Context, item *models.Item) error {
	if m.OnValidate != nil {
		return m.OnValidate(ctx, item)
	}
	return nil
}

// ItemExists implements ItemService.ItemExists for testing.
func (m *MockItemService) ItemExists(ctx context.Context, id string) (bool, error) {
	if m.OnItemExists != nil {
		return m.OnItemExists(ctx, id)
	}
	return true, nil
}

// GetItemStats implements ItemService.GetItemStats for testing.
func (m *MockItemService) GetItemStats(ctx context.Context, projectID string) (*ItemStats, error) {
	if m.OnGetItemStats != nil {
		return m.OnGetItemStats(ctx, projectID)
	}
	return nil, nil
}

// MockLinkService for testing
type MockLinkService struct {
	CreateLinkFunc          func(ctx context.Context, link *models.Link) error
	GetLinkFunc             func(ctx context.Context, id string) (*models.Link, error)
	ListLinksFunc           func(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error)
	UpdateLinkFunc          func(ctx context.Context, link *models.Link) error
	DeleteLinkFunc          func(ctx context.Context, id string) error
	GetItemDependenciesFunc func(ctx context.Context, itemID string) (*DependencyGraph, error)
}

// CreateLink implements LinkService.CreateLink for testing.
func (m *MockLinkService) CreateLink(ctx context.Context, link *models.Link) error {
	if m.CreateLinkFunc != nil {
		return m.CreateLinkFunc(ctx, link)
	}
	return nil
}

// GetLink implements LinkService.GetLink for testing.
func (m *MockLinkService) GetLink(ctx context.Context, id string) (*models.Link, error) {
	if m.GetLinkFunc != nil {
		return m.GetLinkFunc(ctx, id)
	}
	return nil, nil
}

// ListLinks implements LinkService.ListLinks for testing.
func (m *MockLinkService) ListLinks(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
	if m.ListLinksFunc != nil {
		return m.ListLinksFunc(ctx, filter)
	}
	return nil, nil
}

// UpdateLink implements LinkService.UpdateLink for testing.
func (m *MockLinkService) UpdateLink(ctx context.Context, link *models.Link) error {
	if m.UpdateLinkFunc != nil {
		return m.UpdateLinkFunc(ctx, link)
	}
	return nil
}

// DeleteLink implements LinkService.DeleteLink for testing.
func (m *MockLinkService) DeleteLink(ctx context.Context, id string) error {
	if m.DeleteLinkFunc != nil {
		return m.DeleteLinkFunc(ctx, id)
	}
	return nil
}

// GetItemDependencies implements LinkService.GetItemDependencies for testing.
func (m *MockLinkService) GetItemDependencies(ctx context.Context, itemID string) (*DependencyGraph, error) {
	if m.GetItemDependenciesFunc != nil {
		return m.GetItemDependenciesFunc(ctx, itemID)
	}
	return nil, nil
}
