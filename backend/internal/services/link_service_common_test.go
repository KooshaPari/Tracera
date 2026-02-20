//go:build !integration && !e2e

package services

import (
	"context"

	"github.com/stretchr/testify/suite"
)

// LinkServiceTestSuite provides test suite setup for link service tests
type LinkServiceTestSuite struct {
	suite.Suite
	linkRepo *MockLinkRepository
	itemRepo *MockItemRepository
	service  LinkService
	ctx      context.Context
}

func (suite *LinkServiceTestSuite) SetupTest() {
	suite.linkRepo = new(MockLinkRepository)
	suite.itemRepo = new(MockItemRepository)
	suite.ctx = context.Background()
	suite.service = NewLinkService(suite.linkRepo, suite.itemRepo, nil)
}

func (suite *LinkServiceTestSuite) TearDownTest() {
	suite.linkRepo.AssertExpectations(suite.T())
	suite.itemRepo.AssertExpectations(suite.T())
}
