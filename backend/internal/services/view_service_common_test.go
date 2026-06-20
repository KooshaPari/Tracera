package services

import (
	"context"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// MockViewRepository is a mock implementation of ViewRepository
type MockViewRepository struct {
	mock.Mock
}

func (m *MockViewRepository) Create(ctx context.Context, view *models.View) error {
	args := m.Called(ctx, view)
	return args.Error(0)
}

func (m *MockViewRepository) GetByID(ctx context.Context, id string) (*models.View, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.View)
	return val, args.Error(1)
}

func (m *MockViewRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.View, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.View)
	return val, args.Error(1)
}

func (m *MockViewRepository) List(ctx context.Context) ([]*models.View, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.View)
	return val, args.Error(1)
}

func (m *MockViewRepository) Update(ctx context.Context, view *models.View) error {
	args := m.Called(ctx, view)
	return args.Error(0)
}

func (m *MockViewRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockViewRepository) CountItemsByView(ctx context.Context, viewID string) (int64, error) {
	args := m.Called(ctx, viewID)
	val, _ := args.Get(0).(int64)
	return val, args.Error(1)
}

// ViewServiceTestSuite provides test suite setup for view service tests
type ViewServiceTestSuite struct {
	suite.Suite
	repo    *MockViewRepository
	cache   *MockCache
	service ViewService
	ctx     context.Context
}

func (suite *ViewServiceTestSuite) SetupTest() {
	suite.repo = new(MockViewRepository)
	suite.cache = new(MockCache)
	suite.ctx = context.Background()
	suite.service = NewViewServiceImpl(suite.repo, suite.cache, nil)
}

func (suite *ViewServiceTestSuite) TearDownTest() {
	suite.repo.AssertExpectations(suite.T())
}
