//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	opCreate       = "Create"
	opGetByID      = "GetByID"
	opList         = "List"
	opUpdate       = "Update"
	opDelete       = "Delete"
	opUpdateStatus = "UpdateStatus"
)

// TestItemService_ListItems tests ListItems method
func TestItemService_ListItems(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		filter := repository.ItemFilter{
			ProjectID: stringPtr("project-1"),
		}

		expectedItems := []*models.Item{
			{ID: "item-1", ProjectID: "project-1", Title: "Item 1"},
			{ID: "item-2", ProjectID: "project-1", Title: "Item 2"},
		}

		mockRepo.On("List", ctx, filter).Return(expectedItems, nil)

		items, err := service.ListItems(ctx, filter)
		require.NoError(t, err)
		assert.Equal(t, 2, len(items))
		assert.Equal(t, expectedItems, items)
		mockRepo.AssertExpectations(t)
	})

	t.Run("repository error", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		filter := repository.ItemFilter{}

		mockRepo.On("List", ctx, filter).Return(nil, errors.New("repository error"))

		items, err := service.ListItems(ctx, filter)
		assert.Error(t, err)
		assert.Nil(t, items)
		mockRepo.AssertExpectations(t)
	})

	t.Run("empty results", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		filter := repository.ItemFilter{
			ProjectID: stringPtr("empty-project"),
		}

		mockRepo.On("List", ctx, filter).Return([]*models.Item{}, nil)

		items, err := service.ListItems(ctx, filter)
		require.NoError(t, err)
		assert.Equal(t, 0, len(items))
		mockRepo.AssertExpectations(t)
	})
}

// TestItemService_UpdateItem tests UpdateItem method
func TestItemService_UpdateItem(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		item := &models.Item{
			ID:        "item-1",
			ProjectID: "project-1",
			Title:     "Updated Title",
		}

		mockRepo.On("Update", ctx, item).Return(nil)

		err := service.UpdateItem(ctx, item)
		require.NoError(t, err)
		mockRepo.AssertExpectations(t)
	})

	t.Run("empty item ID", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		item := &models.Item{
			ID:        "",
			ProjectID: "project-1",
			Title:     "Test",
		}

		err := service.UpdateItem(ctx, item)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "item ID is required")
		mockRepo.AssertNotCalled(t, "Update")
	})

	t.Run("repository error", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		item := &models.Item{
			ID:        "item-1",
			ProjectID: "project-1",
			Title:     "Test",
		}

		mockRepo.On("Update", ctx, item).Return(errors.New("repository error"))

		err := service.UpdateItem(ctx, item)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "failed to update item")
		mockRepo.AssertExpectations(t)
	})
}

type projectServiceCase struct {
	name         string
	operation    string
	input        interface{}
	mockSetup    func(*MockProjectRepository)
	wantErr      bool
	errContains  string
	validateResp func(*testing.T, interface{})
}

func projectServiceCases(ctx context.Context) []projectServiceCase {
	return append(
		append(projectServiceCreateCases(ctx), projectServiceReadCases(ctx)...),
		append(projectServiceUpdateCases(ctx), projectServiceDeleteCases(ctx)...)...,
	)
}

func projectServiceCreateCases(ctx context.Context) []projectServiceCase {
	return []projectServiceCase{
		{
			name:      "CreateProject success",
			operation: opCreate,
			input: &models.Project{
				Name:        "Test Project",
				Description: "Test Description",
			},
			mockSetup: func(m *MockProjectRepository) {
				m.On("Create", ctx, &models.Project{
					Name:        "Test Project",
					Description: "Test Description",
				}).Return(nil)
			},
		},
		{
			name:      "CreateProject empty name",
			operation: opCreate,
			input: &models.Project{
				Name: "",
			},
			mockSetup:   func(_ *MockProjectRepository) {},
			wantErr:     true,
			errContains: "project name is required",
		},
	}
}

func projectServiceReadCases(ctx context.Context) []projectServiceCase {
	return []projectServiceCase{
		{
			name:      "GetProject success",
			operation: opGetByID,
			input:     "project-1",
			mockSetup: func(m *MockProjectRepository) {
				m.On("GetByID", ctx, "project-1").Return(&models.Project{
					ID:   "project-1",
					Name: "Test Project",
				}, nil)
			},
			validateResp: func(t *testing.T, resp interface{}) {
				project := resp.(*models.Project)
				assert.Equal(t, "project-1", project.ID)
				assert.Equal(t, "Test Project", project.Name)
			},
		},
		{
			name:      "GetProject not found",
			operation: opGetByID,
			input:     "nonexistent",
			mockSetup: func(m *MockProjectRepository) {
				m.On("GetByID", ctx, "nonexistent").Return(nil, errors.New("not found"))
			},
			wantErr: true,
		},
		{
			name:      "ListProjects success",
			operation: opList,
			input:     nil,
			mockSetup: func(m *MockProjectRepository) {
				m.On("List", ctx).Return([]*models.Project{
					{ID: "project-1", Name: "Project 1"},
					{ID: "project-2", Name: "Project 2"},
				}, nil)
			},
			validateResp: func(t *testing.T, resp interface{}) {
				projects := resp.([]*models.Project)
				assert.Equal(t, 2, len(projects))
			},
		},
	}
}

func projectServiceUpdateCases(ctx context.Context) []projectServiceCase {
	return []projectServiceCase{
		{
			name:      "UpdateProject success",
			operation: opUpdate,
			input: &models.Project{
				ID:   "project-1",
				Name: "Updated Name",
			},
			mockSetup: func(m *MockProjectRepository) {
				m.On("Update", ctx, &models.Project{
					ID:   "project-1",
					Name: "Updated Name",
				}).Return(nil)
			},
		},
		{
			name:      "UpdateProject empty ID",
			operation: opUpdate,
			input: &models.Project{
				ID:   "",
				Name: "Test",
			},
			mockSetup:   func(_ *MockProjectRepository) {},
			wantErr:     true,
			errContains: "project ID is required",
		},
	}
}

func projectServiceDeleteCases(ctx context.Context) []projectServiceCase {
	return []projectServiceCase{
		{
			name:      "DeleteProject success",
			operation: opDelete,
			input:     "project-1",
			mockSetup: func(m *MockProjectRepository) {
				m.On("Delete", ctx, "project-1").Return(nil)
			},
		},
	}
}

func runProjectServiceCase(ctx context.Context, t *testing.T, tc projectServiceCase) {
	t.Helper()
	mockRepo := new(MockProjectRepository)
	service := NewProjectService(mockRepo)
	tc.mockSetup(mockRepo)

	var err error
	var result interface{}

	switch tc.operation {
	case opCreate:
		err = service.CreateProject(ctx, tc.input.(*models.Project))
	case opGetByID:
		result, err = service.GetProject(ctx, tc.input.(string))
	case opList:
		result, err = service.ListProjects(ctx)
	case opUpdate:
		err = service.UpdateProject(ctx, tc.input.(*models.Project))
	case opDelete:
		err = service.DeleteProject(ctx, tc.input.(string))
	}

	if tc.wantErr {
		assert.Error(t, err)
		if tc.errContains != "" {
			assert.Contains(t, err.Error(), tc.errContains)
		}
	} else {
		require.NoError(t, err)
		if tc.validateResp != nil {
			tc.validateResp(t, result)
		}
	}

	mockRepo.AssertExpectations(t)
}

// TestProjectService_AllMethods tests all project service methods
func TestProjectService_AllMethods(t *testing.T) {
	ctx := context.Background()

	for _, tc := range projectServiceCases(ctx) {
		t.Run(tc.name, func(t *testing.T) {
			runProjectServiceCase(ctx, t, tc)
		})
	}
}

type agentServiceCase struct {
	name         string
	operation    string
	input        interface{}
	extraInput   string
	mockSetup    func(*MockAgentRepositoryExtended)
	wantErr      bool
	errContains  string
	validateResp func(*testing.T, interface{})
}

func agentServiceCases(ctx context.Context) []agentServiceCase {
	return append(
		append(agentServiceCreateCases(ctx), agentServiceReadCases(ctx)...),
		append(agentServiceUpdateCases(ctx), agentServiceDeleteCases(ctx)...)...,
	)
}

func agentServiceCreateCases(ctx context.Context) []agentServiceCase {
	return []agentServiceCase{
		{
			name:      "CreateAgent success",
			operation: opCreate,
			input: &models.Agent{
				Name:      "Test Agent",
				ProjectID: "project-1",
			},
			mockSetup: func(m *MockAgentRepositoryExtended) {
				m.On("Create", ctx, &models.Agent{
					Name:      "Test Agent",
					ProjectID: "project-1",
					Status:    "idle",
				}).Return(nil)
			},
			validateResp: func(t *testing.T, resp interface{}) {
				agent := resp.(*models.Agent)
				assert.Equal(t, "idle", agent.Status)
			},
		},
		{
			name:      "CreateAgent empty name",
			operation: opCreate,
			input: &models.Agent{
				Name:      "",
				ProjectID: "project-1",
			},
			mockSetup:   func(_ *MockAgentRepositoryExtended) {},
			wantErr:     true,
			errContains: "agent name is required",
		},
		{
			name:      "CreateAgent empty project ID",
			operation: opCreate,
			input: &models.Agent{
				Name:      "Test Agent",
				ProjectID: "",
			},
			mockSetup:   func(_ *MockAgentRepositoryExtended) {},
			wantErr:     true,
			errContains: "project ID is required",
		},
	}
}

func agentServiceReadCases(ctx context.Context) []agentServiceCase {
	return []agentServiceCase{
		{
			name:      "GetAgent success",
			operation: opGetByID,
			input:     "agent-1",
			mockSetup: func(m *MockAgentRepositoryExtended) {
				m.On("GetByID", ctx, "agent-1").Return(&models.Agent{
					ID:        "agent-1",
					Name:      "Test Agent",
					ProjectID: "project-1",
				}, nil)
			},
			validateResp: func(t *testing.T, resp interface{}) {
				agent := resp.(*models.Agent)
				assert.Equal(t, "agent-1", agent.ID)
			},
		},
		{
			name:      "ListAgents success",
			operation: opList,
			input:     nil,
			mockSetup: func(m *MockAgentRepositoryExtended) {
				m.On("List", ctx).Return([]*models.Agent{
					{ID: "agent-1", Name: "Agent 1"},
					{ID: "agent-2", Name: "Agent 2"},
				}, nil)
			},
			validateResp: func(t *testing.T, resp interface{}) {
				agents := resp.([]*models.Agent)
				assert.Equal(t, 2, len(agents))
			},
		},
	}
}

func agentServiceUpdateCases(ctx context.Context) []agentServiceCase {
	return []agentServiceCase{
		{
			name:      "UpdateAgent success",
			operation: opUpdate,
			input: &models.Agent{
				ID:   "agent-1",
				Name: "Updated Name",
			},
			mockSetup: func(m *MockAgentRepositoryExtended) {
				m.On("Update", ctx, &models.Agent{
					ID:   "agent-1",
					Name: "Updated Name",
				}).Return(nil)
			},
		},
		{
			name:       "UpdateAgentStatus success",
			operation:  opUpdateStatus,
			input:      "agent-1",
			extraInput: "active",
			mockSetup: func(m *MockAgentRepositoryExtended) {
				m.On("UpdateStatus", ctx, "agent-1", "active").Return(nil)
			},
		},
	}
}

func agentServiceDeleteCases(ctx context.Context) []agentServiceCase {
	return []agentServiceCase{
		{
			name:      "DeleteAgent success",
			operation: opDelete,
			input:     "agent-1",
			mockSetup: func(m *MockAgentRepositoryExtended) {
				m.On("Delete", ctx, "agent-1").Return(nil)
			},
		},
	}
}

func runAgentServiceCase(ctx context.Context, t *testing.T, tc agentServiceCase) {
	t.Helper()
	mockRepo := new(MockAgentRepositoryExtended)
	service := NewAgentService(mockRepo, nil)
	tc.mockSetup(mockRepo)

	var err error
	var result interface{}

	switch tc.operation {
	case opCreate:
		agent := tc.input.(*models.Agent)
		err = service.CreateAgent(ctx, agent)
		result = agent
	case opGetByID:
		result, err = service.GetAgent(ctx, tc.input.(string))
	case opList:
		result, err = service.ListAgents(ctx)
	case opUpdate:
		err = service.UpdateAgent(ctx, tc.input.(*models.Agent))
	case opUpdateStatus:
		err = service.UpdateAgentStatus(ctx, tc.input.(string), tc.extraInput)
	case opDelete:
		err = service.DeleteAgent(ctx, tc.input.(string))
	}

	if tc.wantErr {
		assert.Error(t, err)
		if tc.errContains != "" {
			assert.Contains(t, err.Error(), tc.errContains)
		}
	} else {
		require.NoError(t, err)
		if tc.validateResp != nil {
			tc.validateResp(t, result)
		}
	}

	mockRepo.AssertExpectations(t)
}

// TestAgentService_AllMethods tests all agent service methods
func TestAgentService_AllMethods(t *testing.T) {
	ctx := context.Background()

	for _, tc := range agentServiceCases(ctx) {
		t.Run(tc.name, func(t *testing.T) {
			runAgentServiceCase(ctx, t, tc)
		})
	}
}

type linkServiceCase struct {
	name         string
	operation    string
	input        interface{}
	mockSetup    func(ctx context.Context, mockRepo *MockLinkRepository)
	validateResp func(*testing.T, interface{})
}

func linkServiceCases() []linkServiceCase {
	return append(linkServiceReadCases(), linkServiceWriteCases()...)
}

func linkServiceReadCases() []linkServiceCase {
	return []linkServiceCase{
		{
			name:      "GetLink success",
			operation: opGetByID,
			input:     "link-1",
			mockSetup: func(ctx context.Context, mockRepo *MockLinkRepository) {
				expectedLink := &models.Link{
					ID:       "link-1",
					SourceID: "item-1",
					TargetID: "item-2",
					Type:     "depends_on",
				}
				mockRepo.On("GetByID", ctx, "link-1").Return(expectedLink, nil)
			},
			validateResp: func(t *testing.T, resp interface{}) {
				link := resp.(*models.Link)
				assert.Equal(t, "link-1", link.ID)
			},
		},
		{
			name:      "ListLinks success",
			operation: opList,
			input: repository.LinkFilter{
				SourceID: stringPtr("item-1"),
			},
			mockSetup: func(ctx context.Context, mockRepo *MockLinkRepository) {
				expectedLinks := []*models.Link{
					{ID: "link-1", SourceID: "item-1", TargetID: "item-2"},
					{ID: "link-2", SourceID: "item-1", TargetID: "item-3"},
				}
				mockRepo.On("List", ctx, repository.LinkFilter{
					SourceID: stringPtr("item-1"),
				}).Return(expectedLinks, nil)
			},
			validateResp: func(t *testing.T, resp interface{}) {
				links := resp.([]*models.Link)
				assert.Equal(t, 2, len(links))
			},
		},
	}
}

func linkServiceWriteCases() []linkServiceCase {
	return []linkServiceCase{
		{
			name:      "UpdateLink success",
			operation: opUpdate,
			input: &models.Link{
				ID:       "link-1",
				SourceID: "item-1",
				TargetID: "item-2",
				Type:     "depends_on",
			},
			mockSetup: func(ctx context.Context, mockRepo *MockLinkRepository) {
				link := &models.Link{
					ID:       "link-1",
					SourceID: "item-1",
					TargetID: "item-2",
					Type:     "depends_on",
				}
				mockRepo.On("Update", ctx, link).Return(nil)
			},
		},
		{
			name:      "DeleteLink success",
			operation: opDelete,
			input:     "link-1",
			mockSetup: func(ctx context.Context, mockRepo *MockLinkRepository) {
				mockRepo.On("Delete", ctx, "link-1").Return(nil)
			},
		},
	}
}

func runLinkServiceCase(ctx context.Context, t *testing.T, tc linkServiceCase) {
	t.Helper()
	mockRepo := new(MockLinkRepository)
	mockItemRepo := new(MockItemRepository)
	service := NewLinkService(mockRepo, mockItemRepo, nil)
	tc.mockSetup(ctx, mockRepo)

	var err error
	var result interface{}

	switch tc.operation {
	case opGetByID:
		result, err = service.GetLink(ctx, tc.input.(string))
	case opList:
		result, err = service.ListLinks(ctx, tc.input.(repository.LinkFilter))
	case opUpdate:
		err = service.UpdateLink(ctx, tc.input.(*models.Link))
	case opDelete:
		err = service.DeleteLink(ctx, tc.input.(string))
	}

	require.NoError(t, err)
	if tc.validateResp != nil {
		tc.validateResp(t, result)
	}
	mockRepo.AssertExpectations(t)
}

// TestLinkService_AllMethods tests all link service methods
func TestLinkService_AllMethods(t *testing.T) {
	ctx := context.Background()

	for _, tc := range linkServiceCases() {
		t.Run(tc.name, func(t *testing.T) {
			runLinkServiceCase(ctx, t, tc)
		})
	}
}
