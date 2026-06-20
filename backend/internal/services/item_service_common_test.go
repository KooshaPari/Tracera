//go:build !integration && !e2e

package services

import (
	"context"

	"github.com/nats-io/nats.go"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Mock repositories

type MockItemRepository struct {
	mock.Mock
}

func (m *MockItemRepository) Create(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *MockItemRepository) GetByID(ctx context.Context, id string) (*models.Item, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) List(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) Update(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *MockItemRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockItemRepository) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	args := m.Called(ctx, filter)
	val, _ := args.Get(0).(int64)
	return val, args.Error(1)
}

type MockLinkRepository struct {
	mock.Mock
}

func (m *MockLinkRepository) Create(ctx context.Context, link *models.Link) error {
	args := m.Called(ctx, link)
	return args.Error(0)
}

func (m *MockLinkRepository) GetByID(ctx context.Context, id string) (*models.Link, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Link)
	return val, args.Error(1)
}

func (m *MockLinkRepository) GetBySourceID(ctx context.Context, sourceID string) ([]*models.Link, error) {
	args := m.Called(ctx, sourceID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
}

func (m *MockLinkRepository) GetByTargetID(ctx context.Context, targetID string) ([]*models.Link, error) {
	args := m.Called(ctx, targetID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
}

func (m *MockLinkRepository) List(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
}

func (m *MockLinkRepository) Update(ctx context.Context, link *models.Link) error {
	args := m.Called(ctx, link)
	return args.Error(0)
}

func (m *MockLinkRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockLinkRepository) DeleteByItemID(ctx context.Context, itemID string) error {
	args := m.Called(ctx, itemID)
	return args.Error(0)
}

// ItemServiceTestSuite provides test suite setup for item service tests
type ItemServiceTestSuite struct {
	suite.Suite
	itemRepo    *MockItemRepository
	linkRepo    *MockLinkRepository
	redisClient *redis.Client
	natsConn    *nats.Conn
	service     ItemService
	ctx         context.Context
}

func (suite *ItemServiceTestSuite) SetupTest() {
	suite.itemRepo = new(MockItemRepository)
	suite.linkRepo = new(MockLinkRepository)
	suite.ctx = context.Background()

	// For unit tests, we test without Redis (nil client)
	// Integration tests should test with real Redis
	suite.redisClient = nil
	suite.natsConn = nil

	suite.service = NewItemService(suite.itemRepo, suite.linkRepo, suite.redisClient, suite.natsConn)
}

func (suite *ItemServiceTestSuite) TearDownTest() {
	suite.itemRepo.AssertExpectations(suite.T())
	suite.linkRepo.AssertExpectations(suite.T())
}
