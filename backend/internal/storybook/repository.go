package storybook

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// RepositoryImpl implements the Repository interface using GORM.
type RepositoryImpl struct {
	db *gorm.DB
}

// NewRepository creates a new repository implementation.
func NewRepository(db *gorm.DB) Repository {
	return &RepositoryImpl{db: db}
}

// SaveComponent saves or updates a component.
func (r *RepositoryImpl) SaveComponent(ctx context.Context, component *LibraryComponent) error {
	if component.ID == "" {
		return errors.New("component ID is required")
	}

	// Convert to GORM model
	gormComponent := &GormLibraryComponent{
		ID:            component.ID,
		ProjectID:     component.ProjectID,
		Name:          component.Name,
		Title:         component.Title,
		Description:   component.Description,
		Category:      component.Category,
		SourceFile:    component.SourceFile,
		StorybookPath: component.StorybookPath,
		Props:         datatypes.JSON(component.Props),
		Variants:      datatypes.JSON(component.Variants),
		Dependencies:  datatypes.JSON(component.Dependencies),
		Screenshots:   datatypes.JSON(component.Screenshots),
		Documentation: component.Documentation,
		Tags:          datatypes.JSON(component.Tags),
		Metadata:      datatypes.JSON(component.Metadata),
		LastSyncedAt:  component.LastSyncedAt,
		CreatedAt:     component.CreatedAt,
		UpdatedAt:     component.UpdatedAt,
	}

	// Use GORM's upsert pattern
	result := r.db.WithContext(ctx).Clauses().Save(gormComponent)
	if result.Error != nil {
		return fmt.Errorf("failed to save component: %w", result.Error)
	}

	return nil
}

// GetComponent retrieves a component by ID.
func (r *RepositoryImpl) GetComponent(ctx context.Context, id string) (*LibraryComponent, error) {
	var gormComponent GormLibraryComponent
	result := r.db.WithContext(ctx).Where("id = ?", id).First(&gormComponent)

	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return nil, gorm.ErrRecordNotFound
		}
		return nil, fmt.Errorf("failed to get component: %w", result.Error)
	}

	// Convert back to domain model
	component := &LibraryComponent{
		ID:            gormComponent.ID,
		ProjectID:     gormComponent.ProjectID,
		Name:          gormComponent.Name,
		Title:         gormComponent.Title,
		Description:   gormComponent.Description,
		Category:      gormComponent.Category,
		SourceFile:    gormComponent.SourceFile,
		StorybookPath: gormComponent.StorybookPath,
		Props:         []byte(gormComponent.Props),
		Variants:      []byte(gormComponent.Variants),
		Dependencies:  []byte(gormComponent.Dependencies),
		Screenshots:   []byte(gormComponent.Screenshots),
		Documentation: gormComponent.Documentation,
		Tags:          []byte(gormComponent.Tags),
		Metadata:      []byte(gormComponent.Metadata),
		LastSyncedAt:  gormComponent.LastSyncedAt,
		CreatedAt:     gormComponent.CreatedAt,
		UpdatedAt:     gormComponent.UpdatedAt,
	}

	return component, nil
}

// GetComponentByName retrieves a component by project ID and name.
func (r *RepositoryImpl) GetComponentByName(ctx context.Context, projectID, name string) (*LibraryComponent, error) {
	var gormComponent GormLibraryComponent
	result := r.db.WithContext(ctx).
		Where("project_id = ? AND name = ?", projectID, name).
		First(&gormComponent)

	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return nil, gorm.ErrRecordNotFound
		}
		return nil, fmt.Errorf("failed to get component: %w", result.Error)
	}

	component := &LibraryComponent{
		ID:            gormComponent.ID,
		ProjectID:     gormComponent.ProjectID,
		Name:          gormComponent.Name,
		Title:         gormComponent.Title,
		Description:   gormComponent.Description,
		Category:      gormComponent.Category,
		SourceFile:    gormComponent.SourceFile,
		StorybookPath: gormComponent.StorybookPath,
		Props:         []byte(gormComponent.Props),
		Variants:      []byte(gormComponent.Variants),
		Dependencies:  []byte(gormComponent.Dependencies),
		Screenshots:   []byte(gormComponent.Screenshots),
		Documentation: gormComponent.Documentation,
		Tags:          []byte(gormComponent.Tags),
		Metadata:      []byte(gormComponent.Metadata),
		LastSyncedAt:  gormComponent.LastSyncedAt,
		CreatedAt:     gormComponent.CreatedAt,
		UpdatedAt:     gormComponent.UpdatedAt,
	}

	return component, nil
}

// ListComponents retrieves all components for a project.
func (r *RepositoryImpl) ListComponents(ctx context.Context, projectID string) ([]LibraryComponent, error) {
	var gormComponents []GormLibraryComponent
	result := r.db.WithContext(ctx).
		Where("project_id = ?", projectID).
		Order("created_at DESC").
		Find(&gormComponents)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to list components: %w", result.Error)
	}

	components := make([]LibraryComponent, len(gormComponents))
	for i, gc := range gormComponents {
		components[i] = LibraryComponent{
			ID:            gc.ID,
			ProjectID:     gc.ProjectID,
			Name:          gc.Name,
			Title:         gc.Title,
			Description:   gc.Description,
			Category:      gc.Category,
			SourceFile:    gc.SourceFile,
			StorybookPath: gc.StorybookPath,
			Props:         []byte(gc.Props),
			Variants:      []byte(gc.Variants),
			Dependencies:  []byte(gc.Dependencies),
			Screenshots:   []byte(gc.Screenshots),
			Documentation: gc.Documentation,
			Tags:          []byte(gc.Tags),
			Metadata:      []byte(gc.Metadata),
			LastSyncedAt:  gc.LastSyncedAt,
			CreatedAt:     gc.CreatedAt,
			UpdatedAt:     gc.UpdatedAt,
		}
	}

	return components, nil
}

// DeleteComponent deletes a component by ID.
func (r *RepositoryImpl) DeleteComponent(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Where("id = ?", id).Delete(&GormLibraryComponent{})
	if result.Error != nil {
		return fmt.Errorf("failed to delete component: %w", result.Error)
	}

	return nil
}

// SaveVariant saves or updates a component variant.
func (r *RepositoryImpl) SaveVariant(ctx context.Context, variant *ComponentVariant) error {
	if variant.ID == "" {
		return errors.New("variant ID is required")
	}

	gormVariant := &GormComponentVariant{
		ID:            variant.ID,
		ComponentID:   variant.ComponentID,
		Name:          variant.Name,
		Title:         variant.Title,
		StorybookID:   variant.StorybookID,
		Args:          datatypes.JSON(mustMarshal(variant.Args)),
		ScreenshotURL: variant.ScreenshotURL,
		Description:   variant.Description,
		CreatedAt:     variant.CreatedAt,
		UpdatedAt:     variant.UpdatedAt,
	}

	result := r.db.WithContext(ctx).Save(gormVariant)
	if result.Error != nil {
		return fmt.Errorf("failed to save variant: %w", result.Error)
	}

	return nil
}

// GetVariants retrieves all variants for a component.
func (r *RepositoryImpl) GetVariants(ctx context.Context, componentID string) ([]ComponentVariant, error) {
	var gormVariants []GormComponentVariant
	result := r.db.WithContext(ctx).
		Where("component_id = ?", componentID).
		Order("created_at ASC").
		Find(&gormVariants)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to get variants: %w", result.Error)
	}

	variants := make([]ComponentVariant, len(gormVariants))
	for i, gv := range gormVariants {
		args := make(map[string]interface{})
		if len(gv.Args) > 0 {
			if err := json.Unmarshal([]byte(gv.Args), &args); err != nil {
				slog.Warn("failed to unmarshal variant args", "variant_id", gv.ID, "error", err)
			}
		}

		variants[i] = ComponentVariant{
			ID:            gv.ID,
			ComponentID:   gv.ComponentID,
			Name:          gv.Name,
			Title:         gv.Title,
			StorybookID:   gv.StorybookID,
			Args:          args,
			ScreenshotURL: gv.ScreenshotURL,
			Description:   gv.Description,
			CreatedAt:     gv.CreatedAt,
			UpdatedAt:     gv.UpdatedAt,
		}
	}

	return variants, nil
}

// GetLastSyncTime retrieves the last sync time for a project.
func (r *RepositoryImpl) GetLastSyncTime(ctx context.Context, projectID string) (time.Time, error) {
	var gormComponent GormLibraryComponent
	result := r.db.WithContext(ctx).
		Where("project_id = ?", projectID).
		Order("last_synced_at DESC").
		First(&gormComponent)

	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return time.Time{}, nil // Return zero time if no components exist
		}
		return time.Time{}, fmt.Errorf("failed to get last sync time: %w", result.Error)
	}

	return gormComponent.LastSyncedAt, nil
}

// UpdateLastSyncTime updates the last sync time for a project.
func (r *RepositoryImpl) UpdateLastSyncTime(ctx context.Context, projectID string, syncTime time.Time) error {
	result := r.db.WithContext(ctx).
		Model(&GormLibraryComponent{}).
		Where("project_id = ?", projectID).
		Update("last_synced_at", syncTime)

	if result.Error != nil {
		return fmt.Errorf("failed to update sync time: %w", result.Error)
	}

	return nil
}

// Helper functions

// mustMarshal marshals a value to JSON, returning empty JSON if it fails.
func mustMarshal(v interface{}) []byte {
	if v == nil {
		return []byte("{}")
	}

	// Try to marshal
	if b, ok := v.([]byte); ok {
		return b
	}

	// Return empty object for any other type
	return []byte("{}")
}
