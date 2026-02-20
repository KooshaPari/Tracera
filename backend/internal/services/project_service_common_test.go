//go:build !integration && !e2e

package services

import (
	"context"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// Mock project repository
type MockProjectRepository struct {
	mock.Mock
}

func (m *MockProjectRepository) Create(ctx context.Context, project *models.Project) error {
	args := m.Called(ctx, project)
	return args.Error(0)
}

func (m *MockProjectRepository) GetByID(ctx context.Context, id string) (*models.Project, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Project)
	return val, args.Error(1)
}

func (m *MockProjectRepository) List(ctx context.Context) ([]*models.Project, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Project)
	return val, args.Error(1)
}

func (m *MockProjectRepository) Update(ctx context.Context, project *models.Project) error {
	args := m.Called(ctx, project)
	return args.Error(0)
}

func (m *MockProjectRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// ProjectServiceTestSuite provides test suite setup for project service tests
type ProjectServiceTestSuite struct {
	suite.Suite
	repo    *MockProjectRepository
	service ProjectService
	ctx     context.Context
}

func (suite *ProjectServiceTestSuite) SetupTest() {
	suite.repo = new(MockProjectRepository)
	suite.ctx = context.Background()
	suite.service = NewProjectService(suite.repo)
}

func (suite *ProjectServiceTestSuite) TearDownTest() {
	suite.repo.AssertExpectations(suite.T())
}
