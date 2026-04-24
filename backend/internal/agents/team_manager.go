package agents

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// TeamManager manages agent teams and roles
type TeamManager struct {
	db *gorm.DB
	mu sync.RWMutex
}

// NewTeamManager creates a new team manager
func NewTeamManager(db *gorm.DB) *TeamManager {
	return &TeamManager{
		db: db,
	}
}

// CreateTeam creates a new agent team
func (tm *TeamManager) CreateTeam(_ context.Context, team *AgentTeam) error {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	if team.ID == "" {
		team.ID = uuid.New().String()
	}
	team.CreatedAt = time.Now()
	team.UpdatedAt = time.Now()

	if err := tm.db.Create(team).Error; err != nil {
		return fmt.Errorf("failed to create team: %w", err)
	}

	return nil
}

// AddTeamMember adds an agent to a team with a role
func (tm *TeamManager) AddTeamMember(_ context.Context, teamID, agentID, roleName string) error {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	// Verify team exists
	var team AgentTeam
	if err := tm.db.First(&team, "id = ?", teamID).Error; err != nil {
		return fmt.Errorf("team not found: %w", err)
	}

	// Verify role exists in team
	if _, exists := team.Roles[roleName]; !exists {
		return fmt.Errorf("role %s not found in team", roleName)
	}

	membership := &AgentTeamMembership{
		ID:        uuid.New().String(),
		TeamID:    teamID,
		AgentID:   agentID,
		RoleName:  roleName,
		JoinedAt:  time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := tm.db.Create(membership).Error; err != nil {
		return fmt.Errorf("failed to add team member: %w", err)
	}

	return nil
}

// GetAgentPermissions returns the permissions for an agent based on their team roles
func (tm *TeamManager) GetAgentPermissions(_ context.Context, agentID string) ([]string, int, error) {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	memberships, err := tm.fetchMemberships(agentID)
	if err != nil {
		return nil, 0, err
	}

	permissionSet, maxPriority := tm.collectPermissions(memberships)
	return permissionsFromSet(permissionSet), maxPriority, nil
}

func (tm *TeamManager) fetchMemberships(agentID string) ([]AgentTeamMembership, error) {
	var memberships []AgentTeamMembership
	if err := tm.db.Where("agent_id = ?", agentID).Find(&memberships).Error; err != nil {
		return nil, fmt.Errorf("failed to get memberships: %w", err)
	}
	return memberships, nil
}

func (tm *TeamManager) collectPermissions(memberships []AgentTeamMembership) (map[string]bool, int) {
	permissionSet := make(map[string]bool)
	maxPriority := 0

	for _, membership := range memberships {
		team, err := tm.fetchTeam(membership.TeamID)
		if err != nil {
			continue
		}
		role, exists := team.Roles[membership.RoleName]
		if !exists {
			continue
		}
		for _, perm := range role.Permissions {
			permissionSet[perm] = true
		}
		if role.Priority > maxPriority {
			maxPriority = role.Priority
		}
	}

	return permissionSet, maxPriority
}

func (tm *TeamManager) fetchTeam(teamID string) (*AgentTeam, error) {
	var team AgentTeam
	if err := tm.db.First(&team, "id = ?", teamID).Error; err != nil {
		return nil, err
	}
	return &team, nil
}

func permissionsFromSet(permissionSet map[string]bool) []string {
	permissions := make([]string, 0, len(permissionSet))
	for perm := range permissionSet {
		permissions = append(permissions, perm)
	}
	return permissions
}

// HasPermission checks if an agent has a specific permission
func (tm *TeamManager) HasPermission(ctx context.Context, agentID, permission string) (bool, error) {
	permissions, _, err := tm.GetAgentPermissions(ctx, agentID)
	if err != nil {
		return false, err
	}

	for _, perm := range permissions {
		if perm == permission || perm == "*" {
			return true, nil
		}
	}

	return false, nil
}
