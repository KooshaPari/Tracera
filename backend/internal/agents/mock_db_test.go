package agents

import (
	"encoding/json"
	"errors"
	"fmt"
	"sync"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// MockGormDB provides a mock implementation for testing GORM operations
type MockGormDB struct {
	mu                   sync.RWMutex
	agents               map[string]*models.Agent
	tasks                map[string]*TaskStore
	locks                map[string]*AgentLock
	teams                map[string]*AgentTeam
	versions             map[string]*ItemVersion
	conflicts            map[string]*ConflictRecord
	memberships          map[string]*AgentTeamMembership
	shouldErrorOn        map[string]bool
	saveCalls            []interface{}
	queryCalls           []string
	updateCalls          []string
	deleteCalls          []string
	transactionCalls     int
	lastError            error
	rowsAffected         int64
	allowTransactionFail bool
	transactionFailCount int
	lastModelArg         interface{}
	whereConditions      []string
	Error                error
}

// TaskStore represents task storage structure
type TaskStore struct {
	ID        string `gorm:"primaryKey"`
	ProjectID string `gorm:"index"`
	Status    string `gorm:"index"`
	Priority  int    `gorm:"index"`
	Data      []byte `gorm:"type:jsonb"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

// NewMockGormDB creates a new mock database instance
func NewMockGormDB() *MockGormDB {
	return &MockGormDB{
		agents:          make(map[string]*models.Agent),
		tasks:           make(map[string]*TaskStore),
		locks:           make(map[string]*AgentLock),
		teams:           make(map[string]*AgentTeam),
		versions:        make(map[string]*ItemVersion),
		conflicts:       make(map[string]*ConflictRecord),
		memberships:     make(map[string]*AgentTeamMembership),
		shouldErrorOn:   make(map[string]bool),
		saveCalls:       make([]interface{}, 0),
		queryCalls:      make([]string, 0),
		updateCalls:     make([]string, 0),
		deleteCalls:     make([]string, 0),
		whereConditions: make([]string, 0),
		rowsAffected:    0,
	}
}

// Mock GORM DB interface implementation

// Save mocks GORM Save
func (m *MockGormDB) Save(value interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.saveCalls = append(m.saveCalls, value)

	// Check for error simulation
	if m.shouldErrorOn["save"] {
		m.lastError = errors.New("mock save error")
		m.Error = m.lastError
		return m
	}

	switch v := value.(type) {
	case *models.Agent:
		m.agents[v.ID] = v
		m.rowsAffected = 1
	case *TaskStore:
		m.tasks[v.ID] = v
		m.rowsAffected = 1
	case *AgentLock:
		m.locks[v.ID] = v
		m.rowsAffected = 1
	case *AgentTeam:
		m.teams[v.ID] = v
		m.rowsAffected = 1
	case *ItemVersion:
		m.versions[v.ID] = v
		m.rowsAffected = 1
	case *ConflictRecord:
		m.conflicts[v.ID] = v
		m.rowsAffected = 1
	case *AgentTeamMembership:
		m.memberships[v.ID] = v
		m.rowsAffected = 1
	}

	m.Error = nil
	return m
}

// Model mocks GORM Model
func (m *MockGormDB) Model(value interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.lastModelArg = value
	return m
}

// Where mocks GORM Where
func (m *MockGormDB) Where(query interface{}, args ...interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.whereConditions = append(m.whereConditions, fmt.Sprintf("%v %v", query, args))
	return m
}

// Update mocks GORM Update
func (m *MockGormDB) Update(column string, value interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.updateCalls = append(m.updateCalls, fmt.Sprintf("%s=%v", column, value))

	if m.shouldErrorOn["update"] {
		m.lastError = errors.New("mock update error")
		m.Error = m.lastError
		return m
	}

	m.rowsAffected = 1
	m.Error = nil
	return m
}

// Updates mocks GORM Updates (for map-based updates)
func (m *MockGormDB) Updates(values interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	if valMap, ok := values.(map[string]interface{}); ok {
		for k, v := range valMap {
			m.updateCalls = append(m.updateCalls, fmt.Sprintf("%s=%v", k, v))
		}
	}

	if m.shouldErrorOn["updates"] {
		m.lastError = errors.New("mock updates error")
		m.Error = m.lastError
		return m
	}

	m.rowsAffected = 1
	m.Error = nil
	return m
}

// Delete mocks GORM Delete
func (m *MockGormDB) Delete(value interface{}, _ ...interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.deleteCalls = append(m.deleteCalls, fmt.Sprintf("%T", value))

	if m.shouldErrorOn["delete"] {
		m.lastError = errors.New("mock delete error")
		m.Error = m.lastError
		return m
	}

	m.rowsAffected = 1
	m.Error = nil
	return m
}

// Find mocks GORM Find
func (m *MockGormDB) Find(dest interface{}, _ ...interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.shouldErrorOn["find"] {
		m.lastError = errors.New("mock find error")
		m.Error = m.lastError
		return m
	}

	// Handle different destination types
	switch v := dest.(type) {
	case *[]TaskStore:
		for _, task := range m.tasks {
			*v = append(*v, *task)
		}
	case *[]models.Agent:
		for _, agent := range m.agents {
			*v = append(*v, *agent)
		}
	}

	m.Error = nil
	return m
}

// First mocks GORM First
func (m *MockGormDB) First(_ interface{}, _ ...interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.shouldErrorOn["first"] {
		m.Error = errors.New("record not found")
		return m
	}

	m.Error = nil
	return m
}

// Last mocks GORM Last
func (m *MockGormDB) Last(_ interface{}, _ ...interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.shouldErrorOn["last"] {
		m.Error = errors.New("record not found")
		return m
	}

	m.Error = nil
	return m
}

// Count mocks GORM Count
func (m *MockGormDB) Count(count *int64) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	*count = int64(len(m.agents))
	m.Error = nil
	return m
}

// Table mocks GORM Table
func (m *MockGormDB) Table(_ string, _ ...interface{}) *MockGormDB {
	return m
}

// Omit mocks GORM Omit
func (m *MockGormDB) Omit(_ ...string) *MockGormDB {
	return m
}

// Select mocks GORM Select
func (m *MockGormDB) Select(_ interface{}, _ ...interface{}) *MockGormDB {
	return m
}

// Preload mocks GORM Preload
func (m *MockGormDB) Preload(_ string, _ ...interface{}) *MockGormDB {
	return m
}

// Clauses mocks GORM Clauses
func (m *MockGormDB) Clauses(_ ...interface{}) *MockGormDB {
	return m
}

// Session mocks GORM Session
func (m *MockGormDB) Session(_ *interface{}) *MockGormDB {
	return m
}

// Limit mocks GORM Limit
func (m *MockGormDB) Limit(_ int) *MockGormDB {
	return m
}

// Offset mocks GORM Offset
func (m *MockGormDB) Offset(_ int) *MockGormDB {
	return m
}

// Order mocks GORM Order
func (m *MockGormDB) Order(_ interface{}, _ ...bool) *MockGormDB {
	return m
}

// Distinct mocks GORM Distinct
func (m *MockGormDB) Distinct(_ ...interface{}) *MockGormDB {
	return m
}

// Group mocks GORM Group
func (m *MockGormDB) Group(_ string) *MockGormDB {
	return m
}

// Having mocks GORM Having
func (m *MockGormDB) Having(_ interface{}, _ ...interface{}) *MockGormDB {
	return m
}

// Joins mocks GORM Joins
func (m *MockGormDB) Joins(_ string, _ ...interface{}) *MockGormDB {
	return m
}

// Scan mocks GORM Scan
func (m *MockGormDB) Scan(_ interface{}) *MockGormDB {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.shouldErrorOn["scan"] {
		m.Error = errors.New("mock scan error")
		return m
	}

	m.Error = nil
	return m
}

// RowsAffected returns the rows affected by last operation
func (m *MockGormDB) RowsAffected() int64 {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.rowsAffected
}

// Mock Helper Methods

// SetShouldError configures the mock to return an error for specific operations
func (m *MockGormDB) SetShouldError(operation string, shouldError bool) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.shouldErrorOn[operation] = shouldError
}

// GetSaveCalls returns all Save calls made to the mock
func (m *MockGormDB) GetSaveCalls() []interface{} {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.saveCalls
}

// GetUpdateCalls returns all Update calls made to the mock
func (m *MockGormDB) GetUpdateCalls() []string {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.updateCalls
}

// GetAgents returns all stored agents
func (m *MockGormDB) GetAgents() map[string]*models.Agent {
	m.mu.RLock()
	defer m.mu.RUnlock()
	agents := make(map[string]*models.Agent)
	for k, v := range m.agents {
		agents[k] = v
	}
	return agents
}

// GetTasks returns all stored tasks
func (m *MockGormDB) GetTasks() map[string]*TaskStore {
	m.mu.RLock()
	defer m.mu.RUnlock()
	tasks := make(map[string]*TaskStore)
	for k, v := range m.tasks {
		tasks[k] = v
	}
	return tasks
}

// GetLocks returns all stored locks
func (m *MockGormDB) GetLocks() map[string]*AgentLock {
	m.mu.RLock()
	defer m.mu.RUnlock()
	locks := make(map[string]*AgentLock)
	for k, v := range m.locks {
		locks[k] = v
	}
	return locks
}

// GetTeams returns all stored teams
func (m *MockGormDB) GetTeams() map[string]*AgentTeam {
	m.mu.RLock()
	defer m.mu.RUnlock()
	teams := make(map[string]*AgentTeam)
	for k, v := range m.teams {
		teams[k] = v
	}
	return teams
}

// GetTransactionCalls returns the number of transaction calls
func (m *MockGormDB) GetTransactionCalls() int {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.transactionCalls
}

// Reset clears all stored data
func (m *MockGormDB) Reset() {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.agents = make(map[string]*models.Agent)
	m.tasks = make(map[string]*TaskStore)
	m.locks = make(map[string]*AgentLock)
	m.teams = make(map[string]*AgentTeam)
	m.versions = make(map[string]*ItemVersion)
	m.conflicts = make(map[string]*ConflictRecord)
	m.memberships = make(map[string]*AgentTeamMembership)
	m.shouldErrorOn = make(map[string]bool)
	m.saveCalls = make([]interface{}, 0)
	m.updateCalls = make([]string, 0)
	m.deleteCalls = make([]string, 0)
	m.whereConditions = make([]string, 0)
	m.rowsAffected = 0
}

// AddAgent adds a test agent to the mock database
func (m *MockGormDB) AddAgent(agent *models.Agent) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.agents[agent.ID] = agent
}

// AddTask adds a test task to the mock database
func (m *MockGormDB) AddTask(task *TaskStore) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.tasks[task.ID] = task
}

// AddLock adds a test lock to the mock database
func (m *MockGormDB) AddLock(lock *AgentLock) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.locks[lock.ID] = lock
}

// AddTeam adds a test team to the mock database
func (m *MockGormDB) AddTeam(team *AgentTeam) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.teams[team.ID] = team
}

// SetTransactionFailure configures transaction to fail
func (m *MockGormDB) SetTransactionFailure(allowFail bool, failCount int) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.allowTransactionFail = allowFail
	m.transactionFailCount = failCount
}

// LogError stores the error for later retrieval
func (m *MockGormDB) LogError(err error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.lastError = err
}

// TestHelpers provides helper functions for agent coordinator testing
type TestHelpers struct {
	db       *MockGormDB
	protocol *Protocol
}

// NewTestHelpers creates a new test helpers instance
func NewTestHelpers() *TestHelpers {
	return &TestHelpers{
		db:       NewMockGormDB(),
		protocol: NewProtocol(),
	}
}

// GetMockDB returns the underlying mock database
func (th *TestHelpers) GetMockDB() *MockGormDB {
	return th.db
}

// CreateTestAgent creates a test agent for testing
func (th *TestHelpers) CreateTestAgent(id, name, projectID string) *RegisteredAgent {
	return &RegisteredAgent{
		ID:        id,
		Name:      name,
		ProjectID: projectID,
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{Name: "analyze", Version: "1.0", Description: "Code analysis"},
			{Name: "generate", Version: "1.0", Description: "Code generation"},
		},
		LastHeartbeat: time.Now(),
		Metadata:      make(map[string]interface{}),
	}
}

// CreateTestTask creates a test task for testing
func (th *TestHelpers) CreateTestTask(id, projectID, taskType string, priority TaskPriority) *Task {
	return &Task{
		ID:                   id,
		ProjectID:            projectID,
		Type:                 taskType,
		Priority:             priority,
		Status:               TaskStatusPending,
		CreatedAt:            time.Now(),
		MaxRetries:           3,
		Timeout:              30 * time.Second,
		RequiredCapabilities: []string{"analyze"},
		Parameters:           make(map[string]interface{}),
		Metadata:             make(map[string]interface{}),
	}
}

// CreateTestLock creates a test lock for testing
func (th *TestHelpers) CreateTestLock(id, itemID, agentID string, lockType LockType) *AgentLock {
	return &AgentLock{
		ID:       id,
		ItemID:   itemID,
		AgentID:  agentID,
		LockType: lockType,
		Version:  1,
		ExpireAt: time.Now().Add(5 * time.Minute),
		Metadata: make(map[string]interface{}),
	}
}

// CreateTestTeam creates a test team for testing
func (th *TestHelpers) CreateTestTeam(id, projectID, name string) *AgentTeam {
	return &AgentTeam{
		ID:        id,
		ProjectID: projectID,
		Name:      name,
		Roles: map[string]TeamRole{
			"admin": {
				Name:        "admin",
				Permissions: []string{"read", "write", "delete", "lock"},
				Priority:    100,
			},
			"developer": {
				Name:        "developer",
				Permissions: []string{"read", "write"},
				Priority:    50,
			},
		},
		Metadata: make(map[string]interface{}),
	}
}

// CreateTestConflict creates a test conflict for testing
func (th *TestHelpers) CreateTestConflict(id, itemID string, agents []string) *ConflictRecord {
	return &ConflictRecord{
		ID:                 id,
		ItemID:             itemID,
		ConflictingAgents:  agents,
		ConflictType:       "concurrent_modification",
		ResolutionStrategy: ResolutionLastWriteWins,
		ResolutionStatus:   "pending",
		ConflictData:       make(map[string]interface{}),
		CreatedAt:          time.Now(),
	}
}

// SerializeTask converts a Task to JSON for storage
func SerializeTask(task *Task) []byte {
	data, _ := json.Marshal(task)
	return data
}

// DeserializeTask converts JSON back to a Task
func DeserializeTask(data []byte) (*Task, error) {
	var task Task
	err := json.Unmarshal(data, &task)
	return &task, err
}

// NewMockDB creates a legacy mock DB using the new MockGormDB
// This maintains backward compatibility
func NewMockDB() *MockGormDB {
	return NewMockGormDB()
}
