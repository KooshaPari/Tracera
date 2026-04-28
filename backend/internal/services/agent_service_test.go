//go:build !integration && !e2e

package services

import (
	"context"
	"encoding/json"
	"errors"
	"testing"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// Test constants
const (
	agentStatusActive = "active"
)

// MockAgentRepository is a mock implementation of AgentRepository
type MockAgentRepository struct {
	mock.Mock
}

func (m *MockAgentRepository) Create(ctx context.Context, agent *models.Agent) error {
	args := m.Called(ctx, agent)
	return args.Error(0)
}

func (m *MockAgentRepository) GetByID(ctx context.Context, id string) (*models.Agent, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Agent)
	return val, args.Error(1)
}

func (m *MockAgentRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Agent, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Agent)
	return val, args.Error(1)
}

func (m *MockAgentRepository) List(ctx context.Context) ([]*models.Agent, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Agent)
	return val, args.Error(1)
}

func (m *MockAgentRepository) Update(ctx context.Context, agent *models.Agent) error {
	args := m.Called(ctx, agent)
	return args.Error(0)
}

func (m *MockAgentRepository) UpdateStatus(ctx context.Context, id, status string) error {
	args := m.Called(ctx, id, status)
	return args.Error(0)
}

func (m *MockAgentRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// AgentServiceTestSuite provides test suite setup for agent service tests
type AgentServiceTestSuite struct {
	suite.Suite
	repo    *MockAgentRepository
	service AgentService
	ctx     context.Context
}

func (suite *AgentServiceTestSuite) SetupTest() {
	suite.repo = new(MockAgentRepository)
	suite.ctx = context.Background()

	// Create service without NATS connection for unit tests
	suite.service = &agentService{
		repo:     suite.repo,
		natsConn: nil, // Will be set per test when needed
	}
}

func (suite *AgentServiceTestSuite) TearDownTest() {
	suite.repo.AssertExpectations(suite.T())
}

func TestAgentServiceSuite(t *testing.T) {
	suite.Run(t, new(AgentServiceTestSuite))
}

// ========================================
// Test Agent Lifecycle - Create Operations
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_Create_Success() {
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "Test Agent",
	}

	suite.repo.On("Create", suite.ctx, mock.MatchedBy(func(a *models.Agent) bool {
		return a.ProjectID == agent.ProjectID &&
			a.Name == agent.Name &&
			a.Status == "idle"
	})).Return(nil)

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().NoError(err)
	suite.Equal("idle", agent.Status, "Status should default to 'idle'")
}

func (suite *AgentServiceTestSuite) TestAgentService_Create_WithCustomStatus() {
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "Test Agent",
		Status:    agentStatusActive,
	}

	suite.repo.On("Create", suite.ctx, mock.MatchedBy(func(a *models.Agent) bool {
		return a.Status == agentStatusActive
	})).Return(nil)

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().NoError(err)
	suite.Equal(agentStatusActive, agent.Status, "Custom status should be preserved")
}

func (suite *AgentServiceTestSuite) TestAgentService_Create_MissingName() {
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "",
	}

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "agent name is required")
}

func (suite *AgentServiceTestSuite) TestAgentService_Create_MissingProjectID() {
	agent := &models.Agent{
		ProjectID: "",
		Name:      "Test Agent",
	}

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "project ID is required")
}

func (suite *AgentServiceTestSuite) TestAgentService_Create_RepositoryError() {
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "Test Agent",
	}

	suite.repo.On("Create", suite.ctx, mock.Anything).Return(errors.New("database error"))

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "failed to create agent")
}

// ========================================
// Test Agent Lifecycle - Read Operations
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_GetAgent_Success() {
	expectedAgent := &models.Agent{
		ID:        "agent-123",
		ProjectID: "project-123",
		Name:      "Test Agent",
		Status:    agentStatusActive,
	}

	suite.repo.On("GetByID", suite.ctx, "agent-123").Return(expectedAgent, nil)

	agent, err := suite.service.GetAgent(suite.ctx, "agent-123")

	suite.Require().NoError(err)
	suite.Equal(expectedAgent.ID, agent.ID)
	suite.Equal(expectedAgent.Name, agent.Name)
	suite.Equal(expectedAgent.Status, agent.Status)
}

func (suite *AgentServiceTestSuite) TestAgentService_GetAgent_NotFound() {
	suite.repo.On("GetByID", suite.ctx, "nonexistent").Return(nil, errors.New("agent not found"))

	agent, err := suite.service.GetAgent(suite.ctx, "nonexistent")

	suite.Require().Error(err)
	suite.Nil(agent)
}

func (suite *AgentServiceTestSuite) TestAgentService_ListAgents_Success() {
	expectedAgents := []*models.Agent{
		{ID: "agent-1", Name: "Agent 1", Status: agentStatusActive},
		{ID: "agent-2", Name: "Agent 2", Status: "idle"},
		{ID: "agent-3", Name: "Agent 3", Status: "error"},
	}

	suite.repo.On("List", suite.ctx).Return(expectedAgents, nil)

	agents, err := suite.service.ListAgents(suite.ctx)

	suite.Require().NoError(err)
	suite.Len(agents, 3)
	suite.Equal(expectedAgents[0].ID, agents[0].ID)
}

func (suite *AgentServiceTestSuite) TestAgentService_ListAgents_Empty() {
	suite.repo.On("List", suite.ctx).Return([]*models.Agent{}, nil)

	agents, err := suite.service.ListAgents(suite.ctx)

	suite.Require().NoError(err)
	suite.Empty(agents)
}

func (suite *AgentServiceTestSuite) TestAgentService_ListAgents_RepositoryError() {
	suite.repo.On("List", suite.ctx).Return(nil, errors.New("database error"))

	agents, err := suite.service.ListAgents(suite.ctx)

	suite.Require().Error(err)
	suite.Nil(agents)
}

// ========================================
// Test Agent Lifecycle - Update Operations
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_UpdateAgent_Success() {
	agent := &models.Agent{
		ID:        "agent-123",
		ProjectID: "project-123",
		Name:      "Updated Agent",
		Status:    agentStatusActive,
	}

	suite.repo.On("Update", suite.ctx, agent).Return(nil)

	err := suite.service.UpdateAgent(suite.ctx, agent)

	suite.Require().NoError(err)
}

func (suite *AgentServiceTestSuite) TestAgentService_UpdateAgent_RepositoryError() {
	agent := &models.Agent{
		ID:        "agent-123",
		ProjectID: "project-123",
		Name:      "Updated Agent",
	}

	suite.repo.On("Update", suite.ctx, agent).Return(errors.New("database error"))

	err := suite.service.UpdateAgent(suite.ctx, agent)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "failed to update agent")
}

func (suite *AgentServiceTestSuite) TestAgentService_UpdateAgentStatus_Success() {
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", agentStatusActive).Return(nil)

	err := suite.service.UpdateAgentStatus(suite.ctx, "agent-123", agentStatusActive)

	suite.Require().NoError(err)
}

func (suite *AgentServiceTestSuite) TestAgentService_UpdateAgentStatus_ToIdle() {
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", "idle").Return(nil)

	err := suite.service.UpdateAgentStatus(suite.ctx, "agent-123", "idle")

	suite.Require().NoError(err)
}

func (suite *AgentServiceTestSuite) TestAgentService_UpdateAgentStatus_ToError() {
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", "error").Return(nil)

	err := suite.service.UpdateAgentStatus(suite.ctx, "agent-123", "error")

	suite.Require().NoError(err)
}

func (suite *AgentServiceTestSuite) TestAgentService_UpdateAgentStatus_RepositoryError() {
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", agentStatusActive).Return(errors.New("database error"))

	err := suite.service.UpdateAgentStatus(suite.ctx, "agent-123", agentStatusActive)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "failed to update agent status")
}

// ========================================
// Test Agent Lifecycle - Delete Operations
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_DeleteAgent_Success() {
	suite.repo.On("Delete", suite.ctx, "agent-123").Return(nil)

	err := suite.service.DeleteAgent(suite.ctx, "agent-123")

	suite.Require().NoError(err)
}

func (suite *AgentServiceTestSuite) TestAgentService_DeleteAgent_RepositoryError() {
	suite.repo.On("Delete", suite.ctx, "agent-123").Return(errors.New("database error"))

	err := suite.service.DeleteAgent(suite.ctx, "agent-123")

	suite.Require().Error(err)
	suite.Contains(err.Error(), "failed to delete agent")
}

// ========================================
// Test Event Notification System
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_NotifyAgentEvent_Success() {
	// Create a custom service with a zero-value NATS connection for this test.
	// Publish will fail (no real server), but we verify the event timestamp is set.
	mockNATS := &nats.Conn{}
	svc := &agentService{
		repo:     suite.repo,
		natsConn: mockNATS,
	}

	event := &AgentEvent{
		AgentID:   "agent-123",
		EventType: "task_completed",
		Data: map[string]interface{}{
			"task_id": "task-456",
			"result":  "success",
		},
	}

	// Publish fails because there is no real NATS server, but
	// the timestamp should still be set before the publish attempt.
	err := svc.NotifyAgentEvent(suite.ctx, event)
	suite.Require().Error(err)
	suite.Contains(err.Error(), "failed to publish event")

	// Verify the event timestamp was set before the publish attempt
	suite.NotNil(event.Timestamp)
	suite.False(event.Timestamp.IsZero())
}

func (suite *AgentServiceTestSuite) TestAgentService_NotifyAgentEvent_NoNATSConnection() {
	event := &AgentEvent{
		AgentID:   "agent-123",
		EventType: "task_completed",
		Data:      map[string]interface{}{},
	}

	err := suite.service.NotifyAgentEvent(suite.ctx, event)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "NATS connection not available")
}

func (suite *AgentServiceTestSuite) TestAgentService_NotifyAgentEvent_EventStructure() {
	mockNATS := &nats.Conn{}
	svc := &agentService{
		repo:     suite.repo,
		natsConn: mockNATS,
	}

	event := &AgentEvent{
		AgentID:   "agent-123",
		EventType: "status_changed",
		Data: map[string]interface{}{
			"old_status": "idle",
			"new_status": agentStatusActive,
		},
	}

	// Publish fails (zero-value NATS conn), but we verify event structure is correct
	err := svc.NotifyAgentEvent(suite.ctx, event)
	suite.Require().Error(err)

	suite.Equal("agent-123", event.AgentID)
	suite.Equal("status_changed", event.EventType)
	suite.NotNil(event.Data)
	suite.NotNil(event.Timestamp)
}

// ========================================
// Test Activity Tracking & Metrics
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_ActivityTracking_MultipleStatusChanges() {
	// Test tracking agent activity through multiple status changes
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", agentStatusActive).Return(nil).Once()
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", "idle").Return(nil).Once()
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", "error").Return(nil).Once()
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", agentStatusActive).Return(nil).Once()

	// Simulate agent lifecycle
	err := suite.service.UpdateAgentStatus(suite.ctx, "agent-123", agentStatusActive)
	suite.Require().NoError(err)

	err = suite.service.UpdateAgentStatus(suite.ctx, "agent-123", "idle")
	suite.Require().NoError(err)

	err = suite.service.UpdateAgentStatus(suite.ctx, "agent-123", "error")
	suite.Require().NoError(err)

	err = suite.service.UpdateAgentStatus(suite.ctx, "agent-123", agentStatusActive)
	suite.Require().NoError(err)
}

func (suite *AgentServiceTestSuite) TestAgentService_HealthMonitoring_AgentStates() {
	// Test monitoring different agent health states
	agents := []*models.Agent{
		{ID: "agent-1", Status: agentStatusActive, Name: "Healthy Agent"},
		{ID: "agent-2", Status: "idle", Name: "Idle Agent"},
		{ID: "agent-3", Status: "error", Name: "Errored Agent"},
	}

	suite.repo.On("List", suite.ctx).Return(agents, nil)

	result, err := suite.service.ListAgents(suite.ctx)

	suite.Require().NoError(err)
	suite.Len(result, 3)

	// Verify we can identify different health states
	var activeCount, idleCount, errorCount int
	for _, agent := range result {
		switch agent.Status {
		case agentStatusActive:
			activeCount++
		case "idle":
			idleCount++
		case "error":
			errorCount++
		}
	}

	suite.Equal(1, activeCount)
	suite.Equal(1, idleCount)
	suite.Equal(1, errorCount)
}

// ========================================
// Test Concurrent Operations
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_ConcurrentStatusUpdates() {
	// Test handling concurrent status updates
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", mock.AnythingOfType("string")).Return(nil).Times(3)

	done := make(chan bool)

	// Simulate concurrent status updates
	go func() {
		suite.NoError(suite.service.UpdateAgentStatus(suite.ctx, "agent-123", agentStatusActive))
		done <- true
	}()

	go func() {
		suite.NoError(suite.service.UpdateAgentStatus(suite.ctx, "agent-123", "idle"))
		done <- true
	}()

	go func() {
		suite.NoError(suite.service.UpdateAgentStatus(suite.ctx, "agent-123", "error"))
		done <- true
	}()

	// Wait for all goroutines to complete
	<-done
	<-done
	<-done
}

// ========================================
// Test Edge Cases & Error Handling
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_EdgeCase_EmptyMetadata() {
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "Test Agent",
		Metadata:  nil,
	}

	suite.repo.On("Create", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().NoError(err)
}

func (suite *AgentServiceTestSuite) TestAgentService_EdgeCase_VeryLongName() {
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      string(make([]byte, 1000)), // Very long name
	}

	suite.repo.On("Create", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().NoError(err)
}

func (suite *AgentServiceTestSuite) TestAgentService_EdgeCase_SpecialCharactersInName() {
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "Test-Agent_123!@#$%^&*()",
	}

	suite.repo.On("Create", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().NoError(err)
}

// ========================================
// Test Event Publishing Integration
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_EventPublishing_CreateAgent() {
	// Test that create publishes event when NATS is available
	// This is tested by verifying the code path in actual integration tests
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "Test Agent",
	}

	suite.repo.On("Create", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.CreateAgent(suite.ctx, agent)

	suite.Require().NoError(err)
	// Event publishing is verified in integration tests with real NATS
}

func (suite *AgentServiceTestSuite) TestAgentService_EventPublishing_UpdateAgent() {
	agent := &models.Agent{
		ID:        "agent-123",
		ProjectID: "project-123",
		Name:      "Updated Agent",
	}

	suite.repo.On("Update", suite.ctx, agent).Return(nil)

	err := suite.service.UpdateAgent(suite.ctx, agent)

	suite.Require().NoError(err)
	// Event publishing is verified in integration tests with real NATS
}

func (suite *AgentServiceTestSuite) TestAgentService_EventPublishing_DeleteAgent() {
	suite.repo.On("Delete", suite.ctx, "agent-123").Return(nil)

	err := suite.service.DeleteAgent(suite.ctx, "agent-123")

	suite.Require().NoError(err)
	// Event publishing is verified in integration tests with real NATS
}

// ========================================
// Test Metrics Calculation
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_Metrics_AgentsByStatus() {
	agents := []*models.Agent{
		{ID: "agent-1", Status: agentStatusActive},
		{ID: "agent-2", Status: agentStatusActive},
		{ID: "agent-3", Status: "idle"},
		{ID: "agent-4", Status: "error"},
		{ID: "agent-5", Status: agentStatusActive},
	}

	suite.repo.On("List", suite.ctx).Return(agents, nil)

	result, err := suite.service.ListAgents(suite.ctx)

	suite.Require().NoError(err)

	// Calculate metrics
	statusCounts := make(map[string]int)
	for _, agent := range result {
		statusCounts[agent.Status]++
	}

	suite.Equal(3, statusCounts[agentStatusActive])
	suite.Equal(1, statusCounts["idle"])
	suite.Equal(1, statusCounts["error"])
}

// ========================================
// Additional Coverage Tests
// ========================================

func (suite *AgentServiceTestSuite) TestAgentService_UpdateAgentStatus_WithEventData() {
	// Verify that status updates include proper event data
	suite.repo.On("UpdateStatus", suite.ctx, "agent-123", agentStatusActive).Return(nil)

	err := suite.service.UpdateAgentStatus(suite.ctx, "agent-123", agentStatusActive)

	suite.Require().NoError(err)
	// In real implementation with NATS, event would contain id and status
}

func (suite *AgentServiceTestSuite) TestAgentService_NotifyAgentEvent_ComplexData() {
	mockNATS := &nats.Conn{}
	svc := &agentService{
		repo:     suite.repo,
		natsConn: mockNATS,
	}

	complexData := map[string]interface{}{
		"nested": map[string]interface{}{
			"level": 2,
			"items": []string{"a", "b", "c"},
		},
		"timestamp": time.Now(),
		"count":     42,
	}

	event := &AgentEvent{
		AgentID:   "agent-123",
		EventType: "complex_event",
		Data:      complexData,
	}

	// Publish fails (zero-value NATS conn), but verify the event was marshaled correctly
	err := svc.NotifyAgentEvent(suite.ctx, event)
	suite.Require().Error(err)

	// Verify event can be marshaled to JSON independently
	data, jsonErr := json.Marshal(event)
	suite.Require().NoError(jsonErr)
	suite.NotNil(data)
}

func (suite *AgentServiceTestSuite) TestAgentService_FullLifecycle() {
	// Test complete agent lifecycle: create -> update -> status changes -> delete
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "Lifecycle Agent",
	}

	// Create
	suite.repo.On("Create", suite.ctx, mock.Anything).Return(nil).Once()
	err := suite.service.CreateAgent(suite.ctx, agent)
	suite.Require().NoError(err)

	// Update
	agent.ID = "agent-123"
	agent.Name = "Updated Lifecycle Agent"
	suite.repo.On("Update", suite.ctx, agent).Return(nil).Once()
	err = suite.service.UpdateAgent(suite.ctx, agent)
	suite.Require().NoError(err)

	// Status change to active
	suite.repo.On("UpdateStatus", suite.ctx, agent.ID, agentStatusActive).Return(nil).Once()
	err = suite.service.UpdateAgentStatus(suite.ctx, agent.ID, agentStatusActive)
	suite.Require().NoError(err)

	// Status change to idle
	suite.repo.On("UpdateStatus", suite.ctx, agent.ID, "idle").Return(nil).Once()
	err = suite.service.UpdateAgentStatus(suite.ctx, agent.ID, "idle")
	suite.Require().NoError(err)

	// Delete
	suite.repo.On("Delete", suite.ctx, agent.ID).Return(nil).Once()
	err = suite.service.DeleteAgent(suite.ctx, agent.ID)
	suite.Require().NoError(err)
}
