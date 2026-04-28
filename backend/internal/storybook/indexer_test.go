package storybook

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/require"
	"gorm.io/gorm"
)

// MockRepository is a mock implementation of the Repository interface.
type MockRepository struct {
	components map[string]*LibraryComponent
	variants   map[string][]*ComponentVariant
	syncTimes  map[string]time.Time
}

// NewMockRepository creates a new mock repository.
func NewMockRepository() *MockRepository {
	return &MockRepository{
		components: make(map[string]*LibraryComponent),
		variants:   make(map[string][]*ComponentVariant),
		syncTimes:  make(map[string]time.Time),
	}
}

func (m *MockRepository) SaveComponent(_ context.Context, component *LibraryComponent) error {
	m.components[component.ID] = component
	return nil
}

func (m *MockRepository) GetComponent(_ context.Context, id string) (*LibraryComponent, error) {
	if comp, ok := m.components[id]; ok {
		return comp, nil
	}
	return nil, gorm.ErrRecordNotFound
}

func (m *MockRepository) GetComponentByName(_ context.Context, projectID, name string) (*LibraryComponent, error) {
	for _, comp := range m.components {
		if comp.ProjectID == projectID && comp.Name == name {
			return comp, nil
		}
	}
	return nil, gorm.ErrRecordNotFound
}

func (m *MockRepository) ListComponents(_ context.Context, projectID string) ([]LibraryComponent, error) {
	var result []LibraryComponent
	for _, comp := range m.components {
		if comp.ProjectID == projectID {
			result = append(result, *comp)
		}
	}
	return result, nil
}

func (m *MockRepository) DeleteComponent(_ context.Context, id string) error {
	delete(m.components, id)
	delete(m.variants, id)
	return nil
}

func (m *MockRepository) SaveVariant(_ context.Context, variant *ComponentVariant) error {
	if _, ok := m.variants[variant.ComponentID]; !ok {
		m.variants[variant.ComponentID] = make([]*ComponentVariant, 0)
	}
	m.variants[variant.ComponentID] = append(m.variants[variant.ComponentID], variant)
	return nil
}

func (m *MockRepository) GetVariants(_ context.Context, componentID string) ([]ComponentVariant, error) {
	if variants, ok := m.variants[componentID]; ok {
		result := make([]ComponentVariant, len(variants))
		for i, v := range variants {
			result[i] = *v
		}
		return result, nil
	}
	return []ComponentVariant{}, nil
}

func (m *MockRepository) GetLastSyncTime(_ context.Context, projectID string) (time.Time, error) {
	if t, ok := m.syncTimes[projectID]; ok {
		return t, nil
	}
	return time.Time{}, nil
}

func (m *MockRepository) UpdateLastSyncTime(_ context.Context, projectID string, syncTime time.Time) error {
	m.syncTimes[projectID] = syncTime
	return nil
}

func TestIsValidComponentStory(t *testing.T) {
	tests := []struct {
		name     string
		story    *StoryEntry
		expected bool
	}{
		{
			name: "valid story",
			story: &StoryEntry{
				Title: "Components/Button",
				Name:  "Button",
			},
			expected: true,
		},
		{
			name: "story without title",
			story: &StoryEntry{
				Name: "Button",
			},
			expected: false,
		},
		{
			name: "story without name",
			story: &StoryEntry{
				Title: "Components/Button",
			},
			expected: false,
		},
		{
			name: "docs only story",
			story: &StoryEntry{
				Title: "Components/Button",
				Name:  "Button",
				Parameters: map[string]interface{}{
					"docsOnly": true,
				},
			},
			expected: false,
		},
		{
			name: "regular story with docs",
			story: &StoryEntry{
				Title: "Components/Button",
				Name:  "Button",
				Parameters: map[string]interface{}{
					"docsOnly": false,
				},
			},
			expected: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := isValidComponentStory(tt.story)
			if result != tt.expected {
				t.Errorf("isValidComponentStory() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func TestIndexerExtractVariants(t *testing.T) {
	client, err := NewClient(&Config{BaseURL: "http://localhost:6006"})
	require.NoError(t, err)
	mockRepo := NewMockRepository()
	indexer := NewIndexer(client, mockRepo, nil)

	story := &StoryEntry{
		Title: "Components/Button",
		Name:  "Button",
		Args: map[string]interface{}{
			"label": "Click me",
			"size":  "medium",
		},
		Parameters: map[string]interface{}{
			"variations": map[string]interface{}{
				"Large": map[string]interface{}{
					"args": map[string]interface{}{
						"label": "Large Button",
						"size":  "large",
					},
				},
				"Small": map[string]interface{}{
					"args": map[string]interface{}{
						"label": "Small Button",
						"size":  "small",
					},
				},
			},
		},
	}

	ctx := context.Background()
	variants, err := indexer.extractVariants(ctx, "components-button--primary", story, "Button")
	if err != nil {
		t.Fatalf("extractVariants() failed: %v", err)
	}

	// Should have default + 2 variations = 3 variants
	if len(variants) != 3 {
		t.Errorf("Expected 3 variants, got %d", len(variants))
	}

	// Check default variant
	if variants[0].Name != "Default" {
		t.Errorf("Expected first variant to be 'Default', got %s", variants[0].Name)
	}

	// Check variations
	variationNames := make(map[string]bool)
	for _, v := range variants[1:] {
		variationNames[v.Name] = true
	}

	if !variationNames["Large"] {
		t.Error("Large variant not found")
	}
	if !variationNames["Small"] {
		t.Error("Small variant not found")
	}
}

func TestGormModelTableNames(t *testing.T) {
	tests := []struct {
		name     string
		model    interface{}
		expected string
	}{
		{
			name:     "library component",
			model:    GormLibraryComponent{},
			expected: "library_components",
		},
		{
			name:     "component variant",
			model:    GormComponentVariant{},
			expected: "component_variants",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tabler, ok := tt.model.(interface{ TableName() string }); ok {
				result := tabler.TableName()
				if result != tt.expected {
					t.Errorf("TableName() = %s, want %s", result, tt.expected)
				}
			} else {
				t.Error("Model does not implement TableName")
			}
		})
	}
}

func TestMustMarshal(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected string
	}{
		{
			name:     "nil input",
			input:    nil,
			expected: "{}",
		},
		{
			name:     "byte slice input",
			input:    []byte(`{"key":"value"}`),
			expected: `{"key":"value"}`,
		},
		{
			name:     "other type input",
			input:    "string",
			expected: "{}",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := string(mustMarshal(tt.input))
			if result != tt.expected {
				t.Errorf("mustMarshal() = %s, want %s", result, tt.expected)
			}
		})
	}
}

func TestExtractAndSaveComponent(t *testing.T) {
	client, mockRepo, indexer := setupIndexerTest(t)
	_ = client
	projectID := uuid.New().String()
	story := buildButtonStory()

	ctx := context.Background()
	component, err := indexer.extractAndSaveComponent(
		ctx,
		projectID,
		"components-button--primary",
		story,
		false,
	)
	if err != nil {
		t.Fatalf("extractAndSaveComponent() failed: %v", err)
	}

	if component == nil {
		t.Fatal("Expected component, got nil")
	}

	verifyComponentFields(t, component, projectID)

	// Verify component was saved to repository
	savedComponent, err := mockRepo.GetComponent(ctx, component.ID)
	if err != nil {
		t.Fatalf("Failed to retrieve saved component: %v", err)
	}

	if savedComponent == nil {
		t.Fatal("Saved component is nil")
	}

	verifySavedProps(t, savedComponent)
}

func setupIndexerTest(t *testing.T) (*Client, *MockRepository, *Indexer) {
	t.Helper()
	client, err := NewClient(&Config{BaseURL: "http://localhost:6006"})
	require.NoError(t, err)
	mockRepo := NewMockRepository()
	indexer := NewIndexer(client, mockRepo, nil)
	return client, mockRepo, indexer
}

func buildButtonStory() *StoryEntry {
	return &StoryEntry{
		Title:      "Components/Button",
		Name:       "Button",
		ImportPath: "src/components/Button.tsx",
		Args: map[string]interface{}{
			"label": "Click me",
		},
		ArgTypes: map[string]ArgType{
			"label": {
				Name:        "label",
				Description: "Button label",
				Required:    true,
				Type: &TypeInfo{
					Name: "string",
				},
			},
		},
		Tags: []string{"component", "button"},
		Parameters: map[string]interface{}{
			"docs": map[string]interface{}{
				"description": "A reusable button component",
			},
		},
	}
}

func verifyComponentFields(t *testing.T, component *LibraryComponent, projectID string) {
	t.Helper()

	if component.ProjectID != projectID {
		t.Errorf("Expected project ID %s, got %s", projectID, component.ProjectID)
	}
	if component.Name != "Button" {
		t.Errorf("Expected component name 'Button', got %s", component.Name)
	}
	if component.SourceFile != "src/components/Button.tsx" {
		t.Errorf("Expected source file 'src/components/Button.tsx', got %s", component.SourceFile)
	}
}

func verifySavedProps(t *testing.T, savedComponent *LibraryComponent) {
	t.Helper()

	var props []PropSchema
	if err := json.Unmarshal(savedComponent.Props, &props); err != nil {
		t.Fatalf("Failed to unmarshal props: %v", err)
	}
	if len(props) == 0 {
		t.Fatal("Expected at least one prop")
	}
	if props[0].Name != "label" {
		t.Errorf("Expected prop name 'label', got %s", props[0].Name)
	}
}
