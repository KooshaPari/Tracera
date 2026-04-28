package services

import (
	"context"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// MockProjectService for testing
type MockProjectService struct {
	OnCreateProject          func(ctx context.Context, project *models.Project) error
	OnCreateProjectWithItems func(ctx context.Context, project *models.Project, items []*models.Item) error
	OnGetProject             func(ctx context.Context, id string) (*models.Project, error)
	OnListProjects           func(ctx context.Context) ([]*models.Project, error)
	OnUpdateProject          func(ctx context.Context, project *models.Project) error
	OnUpdateProjectAndItems  func(ctx context.Context, project *models.Project, items []*models.Item) error
	OnDeleteProject          func(ctx context.Context, id string) error
	OnDeleteProjectWithItems func(ctx context.Context, projectID string) error
	OnGetProjectStats        func(ctx context.Context, projectID string) (*ProjectStats, error)
}

// CreateProject implements ProjectService.CreateProject for testing.
func (m *MockProjectService) CreateProject(ctx context.Context, project *models.Project) error {
	if m.OnCreateProject != nil {
		return m.OnCreateProject(ctx, project)
	}
	return nil
}

// CreateProjectWithItems implements ProjectService.CreateProjectWithItems for testing.
func (m *MockProjectService) CreateProjectWithItems(ctx context.Context, project *models.Project, items []*models.Item) error {
	if m.OnCreateProjectWithItems != nil {
		return m.OnCreateProjectWithItems(ctx, project, items)
	}
	return nil
}

// UpdateProjectAndItems implements ProjectService.UpdateProjectAndItems for testing.
func (m *MockProjectService) UpdateProjectAndItems(ctx context.Context, project *models.Project, items []*models.Item) error {
	if m.OnUpdateProjectAndItems != nil {
		return m.OnUpdateProjectAndItems(ctx, project, items)
	}
	return nil
}

// DeleteProjectWithItems implements ProjectService.DeleteProjectWithItems for testing.
func (m *MockProjectService) DeleteProjectWithItems(ctx context.Context, projectID string) error {
	if m.OnDeleteProjectWithItems != nil {
		return m.OnDeleteProjectWithItems(ctx, projectID)
	}
	return nil
}

// GetProject implements ProjectService.GetProject for testing.
func (m *MockProjectService) GetProject(ctx context.Context, id string) (*models.Project, error) {
	if m.OnGetProject != nil {
		return m.OnGetProject(ctx, id)
	}
	return nil, nil
}

// ListProjects implements ProjectService.ListProjects for testing.
func (m *MockProjectService) ListProjects(ctx context.Context) ([]*models.Project, error) {
	if m.OnListProjects != nil {
		return m.OnListProjects(ctx)
	}
	return nil, nil
}

// UpdateProject implements ProjectService.UpdateProject for testing.
func (m *MockProjectService) UpdateProject(ctx context.Context, project *models.Project) error {
	if m.OnUpdateProject != nil {
		return m.OnUpdateProject(ctx, project)
	}
	return nil
}

// DeleteProject implements ProjectService.DeleteProject for testing.
func (m *MockProjectService) DeleteProject(ctx context.Context, id string) error {
	if m.OnDeleteProject != nil {
		return m.OnDeleteProject(ctx, id)
	}
	return nil
}

// GetProjectStats implements ProjectService.GetProjectStats for testing.
func (m *MockProjectService) GetProjectStats(ctx context.Context, projectID string) (*ProjectStats, error) {
	if m.OnGetProjectStats != nil {
		return m.OnGetProjectStats(ctx, projectID)
	}
	return nil, nil
}

// MockAgentService for testing
type MockAgentService struct {
	CreateAgentFunc       func(ctx context.Context, agent *models.Agent) error
	GetAgentFunc          func(ctx context.Context, id string) (*models.Agent, error)
	ListAgentsFunc        func(ctx context.Context) ([]*models.Agent, error)
	UpdateAgentFunc       func(ctx context.Context, agent *models.Agent) error
	UpdateAgentStatusFunc func(ctx context.Context, id, status string) error
	DeleteAgentFunc       func(ctx context.Context, id string) error
	NotifyAgentEventFunc  func(ctx context.Context, event *AgentEvent) error
}

// CreateAgent implements AgentService.CreateAgent for testing.
func (m *MockAgentService) CreateAgent(ctx context.Context, agent *models.Agent) error {
	if m.CreateAgentFunc != nil {
		return m.CreateAgentFunc(ctx, agent)
	}
	return nil
}

// GetAgent implements AgentService.GetAgent for testing.
func (m *MockAgentService) GetAgent(ctx context.Context, id string) (*models.Agent, error) {
	if m.GetAgentFunc != nil {
		return m.GetAgentFunc(ctx, id)
	}
	return nil, nil
}

// ListAgents implements AgentService.ListAgents for testing.
func (m *MockAgentService) ListAgents(ctx context.Context) ([]*models.Agent, error) {
	if m.ListAgentsFunc != nil {
		return m.ListAgentsFunc(ctx)
	}
	return nil, nil
}

// UpdateAgent implements AgentService.UpdateAgent for testing.
func (m *MockAgentService) UpdateAgent(ctx context.Context, agent *models.Agent) error {
	if m.UpdateAgentFunc != nil {
		return m.UpdateAgentFunc(ctx, agent)
	}
	return nil
}

// UpdateAgentStatus implements AgentService.UpdateAgentStatus for testing.
func (m *MockAgentService) UpdateAgentStatus(ctx context.Context, id, status string) error {
	if m.UpdateAgentStatusFunc != nil {
		return m.UpdateAgentStatusFunc(ctx, id, status)
	}
	return nil
}

// DeleteAgent implements AgentService.DeleteAgent for testing.
func (m *MockAgentService) DeleteAgent(ctx context.Context, id string) error {
	if m.DeleteAgentFunc != nil {
		return m.DeleteAgentFunc(ctx, id)
	}
	return nil
}

// NotifyAgentEvent implements AgentService.NotifyAgentEvent for testing.
func (m *MockAgentService) NotifyAgentEvent(ctx context.Context, event *AgentEvent) error {
	if m.NotifyAgentEventFunc != nil {
		return m.NotifyAgentEventFunc(ctx, event)
	}
	return nil
}
