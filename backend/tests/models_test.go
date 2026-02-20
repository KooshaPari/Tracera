package tests

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"gorm.io/datatypes"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestItemBeforeCreate(t *testing.T) {
	item := &models.Item{
		ProjectID:   "test-project",
		Title:       "Test Item",
		Description: "Test Description",
		Type:        "feature",
		Status:      "open",
		Priority:    models.PriorityHigh,
	}

	err := item.BeforeCreate(nil)
	assert.NoError(t, err)
	assert.NotEmpty(t, item.ID, "ID should be generated")
	assert.Len(t, item.ID, 36, "ID should be UUID format")
}

func TestItemBeforeCreateWithExistingID(t *testing.T) {
	existingID := "existing-id"
	item := &models.Item{
		ID:       existingID,
		Title:    "Test Item",
		Type:     "feature",
		Status:   "open",
		Priority: models.PriorityMedium,
	}

	err := item.BeforeCreate(nil)
	assert.NoError(t, err)
	assert.Equal(t, existingID, item.ID, "Existing ID should be preserved")
}

func TestLinkBeforeCreate(t *testing.T) {
	link := &models.Link{
		SourceID: "source-123",
		TargetID: "target-456",
		Type:     "depends_on",
		Metadata: datatypes.JSON([]byte(`{"key": "value"}`)),
	}

	err := link.BeforeCreate(nil)
	assert.NoError(t, err)
	assert.NotEmpty(t, link.ID, "ID should be generated")
	assert.Len(t, link.ID, 36, "ID should be UUID format")
}

func TestProjectBeforeCreate(t *testing.T) {
	project := &models.Project{
		Name:        "Test Project",
		Description: "Test Description",
		Metadata:    datatypes.JSON([]byte(`{}`)),
	}

	err := project.BeforeCreate(nil)
	assert.NoError(t, err)
	assert.NotEmpty(t, project.ID, "ID should be generated")
	assert.Len(t, project.ID, 36, "ID should be UUID format")
}

func TestAgentBeforeCreate(t *testing.T) {
	agent := &models.Agent{
		ProjectID: "project-123",
		Name:      "Test Agent",
		Status:    "active",
		Metadata:  datatypes.JSON([]byte(`{"version": "1.0"}`)),
	}

	err := agent.BeforeCreate(nil)
	assert.NoError(t, err)
	assert.NotEmpty(t, agent.ID, "ID should be generated")
	assert.Len(t, agent.ID, 36, "ID should be UUID format")
}

func TestItemFields(t *testing.T) {
	now := time.Now()
	item := models.Item{
		ID:          "test-id",
		ProjectID:   "project-123",
		Title:       "Feature Request",
		Description: "Add new feature",
		Type:        "feature",
		Status:      "in_progress",
		Priority:    models.PriorityHigh,
		Metadata:    datatypes.JSON([]byte(`{"tags": ["backend"]}`)),
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	assert.Equal(t, "test-id", item.ID)
	assert.Equal(t, "project-123", item.ProjectID)
	assert.Equal(t, "Feature Request", item.Title)
	assert.Equal(t, "Add new feature", item.Description)
	assert.Equal(t, "feature", item.Type)
	assert.Equal(t, "in_progress", item.Status)
	assert.Equal(t, models.PriorityHigh, item.Priority)
	assert.NotNil(t, item.Metadata)
}

func TestLinkFields(t *testing.T) {
	now := time.Now()
	link := models.Link{
		ID:        "link-123",
		SourceID:  "item-1",
		TargetID:  "item-2",
		Type:      "implements",
		Metadata:  datatypes.JSON([]byte(`{"confidence": 0.95}`)),
		CreatedAt: now,
		UpdatedAt: now,
	}

	assert.Equal(t, "link-123", link.ID)
	assert.Equal(t, "item-1", link.SourceID)
	assert.Equal(t, "item-2", link.TargetID)
	assert.Equal(t, "implements", link.Type)
	assert.NotNil(t, link.Metadata)
}

func TestProjectFields(t *testing.T) {
	now := time.Now()
	project := models.Project{
		ID:          "project-123",
		Name:        "TraceRTM",
		Description: "Requirements traceability matrix",
		Metadata:    datatypes.JSON([]byte(`{"repo": "github.com/..."}`)),
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	assert.Equal(t, "project-123", project.ID)
	assert.Equal(t, "TraceRTM", project.Name)
	assert.Equal(t, "Requirements traceability matrix", project.Description)
	assert.NotNil(t, project.Metadata)
}

func TestAgentFields(t *testing.T) {
	now := time.Now()
	agent := models.Agent{
		ID:        "agent-123",
		ProjectID: "project-123",
		Name:      "Code Analyzer",
		Status:    "idle",
		Metadata:  datatypes.JSON([]byte(`{"model": "gpt-4"}`)),
		CreatedAt: now,
		UpdatedAt: now,
	}

	assert.Equal(t, "agent-123", agent.ID)
	assert.Equal(t, "project-123", agent.ProjectID)
	assert.Equal(t, "Code Analyzer", agent.Name)
	assert.Equal(t, "idle", agent.Status)
	assert.NotNil(t, agent.Metadata)
}
