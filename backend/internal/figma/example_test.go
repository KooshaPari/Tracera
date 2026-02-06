package figma

import (
	"context"
	"errors"
	"testing"
	"time"
)

// Test constants
const (
	testProjectID = "test-project-id"
	testFileKey   = "test-file-key"
)

// MockSyncRepository implements SyncRepository for testing
type MockSyncRepository struct {
	states map[string]*SyncState
}

func NewMockSyncRepository() *MockSyncRepository {
	return &MockSyncRepository{
		states: make(map[string]*SyncState),
	}
}

func (m *MockSyncRepository) GetSyncState(_ context.Context, syncID string) (*SyncState, error) {
	if state, ok := m.states[syncID]; ok {
		return state, nil
	}
	return nil, errors.New("sync state not found")
}

func (m *MockSyncRepository) GetSyncStateByNode(_ context.Context, projectID, fileKey, nodeID string) (*SyncState, error) {
	for _, state := range m.states {
		if state.ProjectID == projectID && state.FileKey == fileKey && state.NodeID == nodeID {
			return state, nil
		}
	}
	return nil, errors.New("sync state not found")
}

func (m *MockSyncRepository) ListSyncStates(_ context.Context, projectID string, _ map[string]interface{}) ([]*SyncState, error) {
	var results []*SyncState
	for _, state := range m.states {
		if state.ProjectID == projectID {
			results = append(results, state)
		}
	}
	return results, nil
}

func (m *MockSyncRepository) UpsertSyncState(_ context.Context, state *SyncState) error {
	m.states[state.ID] = state
	return nil
}

func (m *MockSyncRepository) UpdateSyncStatus(_ context.Context, syncID string, status SyncStatus) error {
	if state, ok := m.states[syncID]; ok {
		state.SyncStatus = status
		state.UpdatedAt = time.Now()
		return nil
	}
	return errors.New("sync state not found")
}

func (m *MockSyncRepository) UpdateSyncTimestamp(_ context.Context, syncID string, timestamp time.Time) error {
	if state, ok := m.states[syncID]; ok {
		state.LastSyncedAt = &timestamp
		state.UpdatedAt = time.Now()
		return nil
	}
	return errors.New("sync state not found")
}

func (m *MockSyncRepository) DeleteSyncState(_ context.Context, syncID string) error {
	delete(m.states, syncID)
	return nil
}

// MockComponentRepository implements ComponentRepository for testing
type MockComponentRepository struct {
	components map[string]*LibraryComponent
}

func NewMockComponentRepository() *MockComponentRepository {
	return &MockComponentRepository{
		components: make(map[string]*LibraryComponent),
	}
}

func (m *MockComponentRepository) GetComponent(_ context.Context, componentID string) (*LibraryComponent, error) {
	if comp, ok := m.components[componentID]; ok {
		return comp, nil
	}
	return nil, errors.New("component not found")
}

func (m *MockComponentRepository) ListComponents(_ context.Context, projectID string) ([]*LibraryComponent, error) {
	var results []*LibraryComponent
	for _, comp := range m.components {
		if comp.ProjectID == projectID {
			results = append(results, comp)
		}
	}
	return results, nil
}

func (m *MockComponentRepository) UpsertComponent(_ context.Context, component *LibraryComponent) error {
	m.components[component.ID] = component
	return nil
}

func (m *MockComponentRepository) DeleteComponent(_ context.Context, componentID string) error {
	delete(m.components, componentID)
	return nil
}

// TestMapperNodeConversion tests converting a Figma node to a component
func TestMapperNodeConversion(t *testing.T) {
	projectID := testProjectID
	fileKey := testFileKey
	mapper := NewMapper(projectID, fileKey)

	node := &Node{
		ID:              "node-1",
		Name:            "Button/Primary",
		Type:            "COMPONENT",
		Description:     "Primary button component",
		IsMainComponent: true,
		ModifiedAt:      time.Now(),
		VariantGroupProperties: map[string]VariantProperty{
			"Size": {
				Type:    "BOOLEAN",
				Default: "Medium",
				Options: []string{"Small", "Medium", "Large"},
			},
			"State": {
				Type:    "BOOLEAN",
				Default: "Enabled",
				Options: []string{"Enabled", "Disabled", "Loading"},
			},
		},
	}

	component := mapper.MapNodeToComponent(node)

	if component.ID != node.ID {
		t.Errorf("Expected component ID %s, got %s", node.ID, component.ID)
	}

	if component.Name != node.Name {
		t.Errorf("Expected component name %s, got %s", node.Name, component.Name)
	}

	if component.Category != "Button" {
		t.Errorf("Expected category 'Button', got %s", component.Category)
	}

	if len(component.Variants) == 0 {
		t.Errorf("Expected variants to be extracted, got %d", len(component.Variants))
	}
}

// TestMapperVariantParsing tests variant name parsing
func TestMapperVariantParsing(t *testing.T) {
	variantName := "Button=Primary, Size=Large"
	props := ParseVariantName(variantName)

	if props["Button"] != "Primary" {
		t.Errorf("Expected Button=Primary, got %v", props)
	}

	if props["Size"] != "Large" {
		t.Errorf("Expected Size=Large, got %v", props)
	}

	// Test variant name reconstruction
	reconstructed := VariantNameFromProperties(props)
	reparsed := ParseVariantName(reconstructed)

	if reparsed["Button"] != props["Button"] || reparsed["Size"] != props["Size"] {
		t.Errorf("Variant parsing round-trip failed: %v -> %s -> %v", props, reconstructed, reparsed)
	}
}

// TestMapperComponentPath tests component path extraction
func TestMapperComponentPath(t *testing.T) {
	name := "Button/Primary/Large"
	path := ExtractComponentPath(name)

	if len(path) != 3 {
		t.Errorf("Expected path length 3, got %d", len(path))
	}

	expected := []string{"Button", "Primary", "Large"}
	for i, part := range path {
		if part != expected[i] {
			t.Errorf("Expected path part %s, got %s", expected[i], part)
		}
	}

	// Test path reconstruction
	reconstructed := BuildComponentPath(path)
	if reconstructed != name {
		t.Errorf("Expected %s, got %s", name, reconstructed)
	}
}

// TestMapperSyncStateCreation tests creating a sync state from a node
func TestMapperSyncStateCreation(t *testing.T) {
	projectID := testProjectID
	fileKey := testFileKey
	mapper := NewMapper(projectID, fileKey)

	componentID := "comp-123"
	node := &Node{
		ID:              "node-1",
		Name:            "Button",
		Type:            "COMPONENT",
		Description:     "Button component",
		IsMainComponent: true,
		ModifiedAt:      time.Now().Add(-1 * time.Hour),
	}

	syncState := mapper.MapNodeToSyncState(node, nil, &componentID)

	if syncState.ProjectID != projectID {
		t.Errorf("Expected project ID %s, got %s", projectID, syncState.ProjectID)
	}

	if syncState.NodeID != node.ID {
		t.Errorf("Expected node ID %s, got %s", node.ID, syncState.NodeID)
	}

	if syncState.SyncStatus != SyncStatusUnlinked {
		t.Errorf("Expected sync status %s, got %s", SyncStatusUnlinked, syncState.SyncStatus)
	}

	if syncState.FigmaURL == nil || *syncState.FigmaURL == "" {
		t.Errorf("Expected Figma URL to be generated")
	}
}

// TestMapperNormalization tests name normalization
func TestMapperNormalization(t *testing.T) {
	name := "  My Component  "
	normalized := NormalizeComponentName(name)

	if normalized != "my component" {
		t.Errorf("Expected 'my component', got %s", normalized)
	}
}

// TestSyncServiceInitialization tests creating a sync service
func TestSyncServiceInitialization(t *testing.T) {
	projectID := testProjectID
	fileKey := testFileKey
	config := SyncConfig{
		Enabled:            true,
		AutoSyncComponents: true,
		TrackVariants:      true,
	}

	syncService := NewSyncService(
		nil, // client will be set in actual use
		NewMockSyncRepository(),
		NewMockComponentRepository(),
		projectID,
		fileKey,
		config,
	)

	if syncService == nil {
		t.Errorf("Expected sync service to be created")
	}

	if syncService.GetActiveSyncs() != 0 {
		t.Errorf("Expected 0 active syncs, got %d", syncService.GetActiveSyncs())
	}
}

// TestComponentProperties tests extracting component properties
func TestComponentProperties(t *testing.T) {
	mapper := NewMapper("proj-1", "file-1")

	node := &Node{
		ID:              "node-1",
		Name:            "Button",
		Type:            "COMPONENT",
		Description:     "A button component",
		IsComponent:     true,
		IsMainComponent: true,
		Properties: map[string]interface{}{
			"custom_prop": "custom_value",
		},
		VariantGroupProperties: map[string]VariantProperty{
			"Size": {
				Type:    "STRING",
				Default: "Medium",
				Options: []string{"Small", "Medium", "Large"},
			},
		},
		DocumentationLinks: []DocumentationLink{
			{URI: "https://docs.example.com/button"},
		},
	}

	props := mapper.ExtractComponentProperties(node)

	if props["name"] != "Button" {
		t.Errorf("Expected name property")
	}

	if props["type"] != "COMPONENT" {
		t.Errorf("Expected type property")
	}

	if props["is_main_component"] != true {
		t.Errorf("Expected is_main_component property")
	}

	if variants, ok := props["variants"]; !ok {
		t.Errorf("Expected variants property")
	} else if variantMap, ok := variants.(map[string]interface{}); !ok || len(variantMap) != 1 {
		t.Errorf("Expected variant properties to be extracted")
	}
}

// TestComponentVariantExtraction tests extracting variants from nodes
func TestComponentVariantExtraction(t *testing.T) {
	mapper := NewMapper("proj-1", "file-1")

	node := &Node{
		ID:              "node-1",
		Name:            "Button",
		Type:            "COMPONENT",
		IsMainComponent: true,
		VariantGroupProperties: map[string]VariantProperty{
			"Size": {
				Type:    "STRING",
				Default: "Medium",
				Options: []string{"Small", "Medium", "Large"},
			},
			"State": {
				Type:    "STRING",
				Default: "Enabled",
				Options: []string{"Enabled", "Disabled"},
			},
		},
	}

	variants := mapper.extractVariants(node)

	// Should have Size variants
	sizeVariants := 0
	stateVariants := 0

	for _, v := range variants {
		if len(v.Properties) > 0 {
			if _, hasSizeKey := v.Properties["Size"]; hasSizeKey {
				sizeVariants++
			}
			if _, hasStateKey := v.Properties["State"]; hasStateKey {
				stateVariants++
			}
		}
	}

	if sizeVariants < 3 {
		t.Errorf("Expected at least 3 size variants, got %d", sizeVariants)
	}

	if stateVariants < 2 {
		t.Errorf("Expected at least 2 state variants, got %d", stateVariants)
	}
}
