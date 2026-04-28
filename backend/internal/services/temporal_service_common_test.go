package services

import (
	"context"

	"github.com/stretchr/testify/mock"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Mock repositories
type mockBranchRepository struct {
	mock.Mock
}

func (m *mockBranchRepository) Create(ctx context.Context, branch interface{}) error {
	args := m.Called(ctx, branch)
	return args.Error(0)
}

func (m *mockBranchRepository) GetByID(ctx context.Context, id string) (interface{}, error) {
	args := m.Called(ctx, id)
	return args.Get(0), args.Error(1)
}

func (m *mockBranchRepository) ListByProject(ctx context.Context, projectID string) ([]interface{}, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]interface{})
	return val, args.Error(1)
}

func (m *mockBranchRepository) Update(ctx context.Context, branch interface{}) error {
	args := m.Called(ctx, branch)
	return args.Error(0)
}

func (m *mockBranchRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockVersionRepository struct {
	mock.Mock
}

func (m *mockVersionRepository) Create(ctx context.Context, version interface{}) error {
	args := m.Called(ctx, version)
	return args.Error(0)
}

func (m *mockVersionRepository) GetByID(ctx context.Context, id string) (interface{}, error) {
	args := m.Called(ctx, id)
	return args.Get(0), args.Error(1)
}

func (m *mockVersionRepository) ListByBranch(ctx context.Context, branchID string) ([]interface{}, error) {
	args := m.Called(ctx, branchID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]interface{})
	return val, args.Error(1)
}

func (m *mockVersionRepository) Update(ctx context.Context, version interface{}) error {
	args := m.Called(ctx, version)
	return args.Error(0)
}

func (m *mockVersionRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockItemVersionRepository struct {
	mock.Mock
}

func (m *mockItemVersionRepository) Create(ctx context.Context, snapshot interface{}) error {
	args := m.Called(ctx, snapshot)
	return args.Error(0)
}

func (m *mockItemVersionRepository) GetByItemAndVersion(ctx context.Context, itemID, versionID string) (interface{}, error) {
	args := m.Called(ctx, itemID, versionID)
	return args.Get(0), args.Error(1)
}

func (m *mockItemVersionRepository) GetHistory(ctx context.Context, itemID, branchID string) ([]interface{}, error) {
	args := m.Called(ctx, itemID, branchID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]interface{})
	return val, args.Error(1)
}

func (m *mockItemVersionRepository) Update(ctx context.Context, snapshot interface{}) error {
	args := m.Called(ctx, snapshot)
	return args.Error(0)
}

func (m *mockItemVersionRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockAlternativeRepository struct {
	mock.Mock
}

func (m *mockAlternativeRepository) Create(ctx context.Context, alt interface{}) error {
	args := m.Called(ctx, alt)
	return args.Error(0)
}

func (m *mockAlternativeRepository) GetByID(ctx context.Context, id string) (interface{}, error) {
	args := m.Called(ctx, id)
	return args.Get(0), args.Error(1)
}

func (m *mockAlternativeRepository) ListByBase(ctx context.Context, baseItemID string) ([]interface{}, error) {
	args := m.Called(ctx, baseItemID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]interface{})
	return val, args.Error(1)
}

func (m *mockAlternativeRepository) Update(ctx context.Context, alt interface{}) error {
	args := m.Called(ctx, alt)
	return args.Error(0)
}

func (m *mockAlternativeRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockMergeRepository struct {
	mock.Mock
}

func (m *mockMergeRepository) Create(ctx context.Context, mr interface{}) error {
	args := m.Called(ctx, mr)
	return args.Error(0)
}

func (m *mockMergeRepository) GetByID(ctx context.Context, id string) (interface{}, error) {
	args := m.Called(ctx, id)
	return args.Get(0), args.Error(1)
}

func (m *mockMergeRepository) ListByProject(ctx context.Context, projectID string, status string) ([]interface{}, error) {
	args := m.Called(ctx, projectID, status)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]interface{})
	return val, args.Error(1)
}

func (m *mockMergeRepository) Update(ctx context.Context, mr interface{}) error {
	args := m.Called(ctx, mr)
	return args.Error(0)
}

func (m *mockMergeRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockItemRepository struct {
	mock.Mock
}

func (m *mockItemRepository) Create(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *mockItemRepository) GetByID(ctx context.Context, id string) (*models.Item, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Item)
	return val, args.Error(1)
}

func (m *mockItemRepository) Update(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *mockItemRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *mockItemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *mockItemRepository) List(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *mockItemRepository) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	args := m.Called(ctx, filter)
	val, _ := args.Get(0).(int64)
	return val, args.Error(1)
}
