package storybook

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// Repository defines the interface for persisting components.
type Repository interface {
	SaveComponent(ctx context.Context, component *LibraryComponent) error
	GetComponent(ctx context.Context, id string) (*LibraryComponent, error)
	GetComponentByName(ctx context.Context, projectID, name string) (*LibraryComponent, error)
	ListComponents(ctx context.Context, projectID string) ([]LibraryComponent, error)
	DeleteComponent(ctx context.Context, id string) error
	SaveVariant(ctx context.Context, variant *ComponentVariant) error
	GetVariants(ctx context.Context, componentID string) ([]ComponentVariant, error)
	GetLastSyncTime(ctx context.Context, projectID string) (time.Time, error)
	UpdateLastSyncTime(ctx context.Context, projectID string, syncTime time.Time) error
}

// Indexer handles the indexing of Storybook components.
type Indexer struct {
	client *Client
	repo   Repository
	db     *gorm.DB
}

// NewIndexer creates a new component indexer.
func NewIndexer(client *Client, repo Repository, db *gorm.DB) *Indexer {
	return &Indexer{
		client: client,
		repo:   repo,
		db:     db,
	}
}

// IndexComponents synchronizes components from Storybook to the database.
func (idx *Indexer) IndexComponents(ctx context.Context, req *ComponentLibraryIndexRequest) (*SyncResult, error) {
	startTime := time.Now()
	result := &SyncResult{
		StartTime: startTime,
		Errors:    make([]SyncError, 0),
	}

	// Fetch stories from Storybook
	stories, err := idx.client.FetchStoriesJSON(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch stories: %w", err)
	}

	result.TotalStories = len(stories.Stories)
	result.Components = make([]LibraryComponent, 0, result.TotalStories)

	// Process each story
	for storyID, story := range stories.Stories {
		component, err := idx.extractAndSaveComponent(ctx, req.ProjectID, storyID, &story, req.IncludeScreenshots)
		if err != nil {
			result.FailedComponents++
			result.Errors = append(result.Errors, SyncError{
				ComponentName: story.Title,
				Message:       err.Error(),
				Timestamp:     time.Now(),
			})
			continue
		}

		if component == nil {
			continue
		}

		// Check if this is a new or updated component
		existingComponent, err := idx.repo.GetComponent(ctx, component.ID)
		if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
			result.FailedComponents++
			continue
		}

		if existingComponent == nil {
			result.CreatedComponents++
		} else {
			result.UpdatedComponents++
		}

		result.Components = append(result.Components, *component)
	}

	// Update last sync time
	if err := idx.repo.UpdateLastSyncTime(ctx, req.ProjectID, startTime); err != nil {
		return nil, fmt.Errorf("failed to update sync time: %w", err)
	}

	result.EndTime = time.Now()
	return result, nil
}

// extractAndSaveComponent extracts component information from a story and saves it.
func (idx *Indexer) extractAndSaveComponent(
	ctx context.Context,
	projectID string,
	storyID string,
	story *StoryEntry,
	includeScreenshots bool,
) (*LibraryComponent, error) {
	// Skip non-component stories
	if !isValidComponentStory(story) {
		return nil, nil
	}

	// Extract component information
	componentName := idx.client.ExtractComponentName(story.Title)
	if componentName == "" {
		return nil, fmt.Errorf("could not extract component name from title: %s", story.Title)
	}

	component := idx.buildLibraryComponent(projectID, storyID, componentName, story)
	// Extract variants
	variants, err := idx.extractVariants(ctx, storyID, story, componentName)
	if err != nil {
		return nil, fmt.Errorf("failed to extract variants: %w", err)
	}

	if err := idx.attachComponentData(component, story, variants, includeScreenshots, storyID); err != nil {
		return nil, err
	}

	// Save component to repository
	if err := idx.repo.SaveComponent(ctx, component); err != nil {
		return nil, fmt.Errorf("failed to save component: %w", err)
	}

	if err := idx.saveComponentVariants(ctx, storyID, story, component.ID, variants, includeScreenshots); err != nil {
		return nil, err
	}

	return component, nil
}

func (idx *Indexer) buildLibraryComponent(projectID, storyID, componentName string, story *StoryEntry) *LibraryComponent {
	now := time.Now()
	return &LibraryComponent{
		ID:            uuid.New().String(),
		ProjectID:     projectID,
		Name:          componentName,
		Title:         story.Title,
		Description:   idx.client.ExtractComponentDocumentation(story),
		Category:      idx.client.ExtractCategory(story.Title),
		SourceFile:    story.ImportPath,
		StorybookPath: storyID,
		LastSyncedAt:  now,
		CreatedAt:     now,
		UpdatedAt:     now,
	}
}

func (idx *Indexer) attachComponentData(
	component *LibraryComponent, story *StoryEntry, variants []ComponentVariant,
	includeScreenshots bool, storyID string,
) error {
	props := idx.client.ExtractPropsFromArgTypes(story.ArgTypes)
	propsJSON, err := json.Marshal(props)
	if err != nil {
		return fmt.Errorf("failed to marshal props: %w", err)
	}
	component.Props = propsJSON

	variantsJSON, err := json.Marshal(variants)
	if err != nil {
		return fmt.Errorf("failed to marshal variants: %w", err)
	}
	component.Variants = variantsJSON

	tagsJSON, err := json.Marshal(story.Tags)
	if err != nil {
		return fmt.Errorf("failed to marshal tags: %w", err)
	}
	component.Tags = tagsJSON

	metadataJSON, err := json.Marshal(story.Parameters)
	if err != nil {
		return fmt.Errorf("failed to marshal metadata: %w", err)
	}
	component.Metadata = metadataJSON

	if includeScreenshots {
		screenshotURL := idx.client.GetScreenshotURL(story, storyID)
		screenshots := map[string]string{
			"default": screenshotURL,
		}
		screenshotsJSON, err := json.Marshal(screenshots)
		if err != nil {
			return fmt.Errorf("failed to marshal screenshots: %w", err)
		}
		component.Screenshots = screenshotsJSON
	}

	return nil
}

func (idx *Indexer) saveComponentVariants(
	ctx context.Context,
	storyID string,
	story *StoryEntry,
	componentID string,
	variants []ComponentVariant,
	includeScreenshots bool,
) error {
	now := time.Now()
	for _, variant := range variants {
		variantEntity := &ComponentVariant{
			ID:          uuid.New().String(),
			ComponentID: componentID,
			Name:        variant.Name,
			Title:       variant.Title,
			StorybookID: storyID,
			Args:        variant.Args,
			Description: variant.Description,
			CreatedAt:   now,
			UpdatedAt:   now,
		}

		if includeScreenshots {
			variantEntity.ScreenshotURL = idx.client.GetScreenshotURL(story, storyID)
		}

		if err := idx.repo.SaveVariant(ctx, variantEntity); err != nil {
			return fmt.Errorf("failed to save variant: %w", err)
		}
	}

	return nil
}

// extractVariants extracts component variants from story arguments.
func (idx *Indexer) extractVariants(
	_ context.Context,
	storyID string,
	story *StoryEntry,
	componentName string,
) ([]ComponentVariant, error) {
	variants := []ComponentVariant{idx.createDefaultVariant(storyID, story, componentName)}

	if story.Parameters != nil {
		idx.extractParameterVariations(storyID, story.Parameters, componentName, &variants)
	}

	return variants, nil
}

// createDefaultVariant creates the default variant from story args
func (idx *Indexer) createDefaultVariant(storyID string, story *StoryEntry, componentName string) ComponentVariant {
	return ComponentVariant{
		Name:        "Default",
		Title:       componentName + " - Default",
		StorybookID: storyID,
		Args:        story.Args,
		Description: "Default variant of " + componentName,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
}

// extractParameterVariations extracts variations from story parameters
func (idx *Indexer) extractParameterVariations(
	storyID string,
	parameters map[string]interface{},
	componentName string,
	variants *[]ComponentVariant,
) {
	variations, ok := parameters["variations"]
	if !ok {
		return
	}

	variationsMap, ok := variations.(map[string]interface{})
	if !ok {
		return
	}

	for varName, varConfig := range variationsMap {
		idx.extractSingleVariation(storyID, componentName, varName, varConfig, variants)
	}
}

// extractSingleVariation extracts a single variation
func (idx *Indexer) extractSingleVariation(
	storyID, componentName, varName string,
	varConfig interface{},
	variants *[]ComponentVariant,
) {
	varConfigMap, ok := varConfig.(map[string]interface{})
	if !ok {
		return
	}

	variant := ComponentVariant{
		Name:        varName,
		Title:       componentName + " - " + varName,
		StorybookID: storyID,
		Description: varName + " variant of " + componentName,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	if args, ok := varConfigMap["args"]; ok {
		if argsMap, ok := args.(map[string]interface{}); ok {
			variant.Args = argsMap
		}
	}

	*variants = append(*variants, variant)
}

// isValidComponentStory checks if a story represents a valid component.
func isValidComponentStory(story *StoryEntry) bool {
	// Skip stories without a proper title
	if story.Title == "" || story.Name == "" {
		return false
	}

	// Skip documentation-only entries
	if story.Parameters != nil {
		if docsOnly, ok := story.Parameters["docsOnly"]; ok {
			if docsOnlyBool, ok := docsOnly.(bool); ok && docsOnlyBool {
				return false
			}
		}
	}

	return true
}

// GetSyncStatus returns the last sync status for a project.
func (idx *Indexer) GetSyncStatus(ctx context.Context, projectID string) (time.Time, error) {
	return idx.repo.GetLastSyncTime(ctx, projectID)
}

// ReindexProject reindexes all components for a project.
func (idx *Indexer) ReindexProject(ctx context.Context, projectID string, baseURL string) (*SyncResult, error) {
	// Delete existing components
	components, err := idx.repo.ListComponents(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to list existing components: %w", err)
	}

	for _, component := range components {
		if err := idx.repo.DeleteComponent(ctx, component.ID); err != nil {
			return nil, fmt.Errorf("failed to delete component: %w", err)
		}
	}

	// Reindex
	req := &ComponentLibraryIndexRequest{
		ProjectID:          projectID,
		StorybookBaseURL:   baseURL,
		IncludeScreenshots: true,
		Categories:         nil,
		Tags:               nil,
	}

	return idx.IndexComponents(ctx, req)
}

// GormLibraryComponent represents the GORM model for library components.
type GormLibraryComponent struct {
	ID            string         `gorm:"primaryKey" json:"id"`
	ProjectID     string         `gorm:"index" json:"project_id"`
	Name          string         `gorm:"index" json:"name"`
	Title         string         `json:"title"`
	Description   string         `json:"description"`
	Category      string         `json:"category"`
	SourceFile    string         `json:"source_file"`
	StorybookPath string         `json:"storybook_path"`
	Props         datatypes.JSON `json:"props"`
	Variants      datatypes.JSON `json:"variants"`
	Dependencies  datatypes.JSON `json:"dependencies"`
	Screenshots   datatypes.JSON `json:"screenshots"`
	Documentation string         `json:"documentation"`
	Tags          datatypes.JSON `json:"tags"`
	Metadata      datatypes.JSON `json:"metadata"`
	LastSyncedAt  time.Time      `json:"last_synced_at"`
	CreatedAt     time.Time      `json:"created_at"`
	UpdatedAt     time.Time      `json:"updated_at"`
}

// TableName specifies the table name for the model.
func (GormLibraryComponent) TableName() string {
	return "library_components"
}

// GormComponentVariant represents the GORM model for component variants.
type GormComponentVariant struct {
	ID            string         `gorm:"primaryKey" json:"id"`
	ComponentID   string         `gorm:"index" json:"component_id"`
	Name          string         `json:"name"`
	Title         string         `json:"title"`
	StorybookID   string         `json:"storybook_id"`
	Args          datatypes.JSON `json:"args"`
	ScreenshotURL string         `json:"screenshot_url"`
	Description   string         `json:"description"`
	CreatedAt     time.Time      `json:"created_at"`
	UpdatedAt     time.Time      `json:"updated_at"`
}

// TableName specifies the table name for the model.
func (GormComponentVariant) TableName() string {
	return "component_variants"
}
