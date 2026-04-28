package figma

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"sync"
	"time"
)

// SyncRepository defines the interface for accessing sync state data
type SyncRepository interface {
	// GetSyncState retrieves a sync state by ID.
	GetSyncState(ctx context.Context, syncID string) (*SyncState, error)

	// GetSyncStateByNode retrieves sync state by project and node IDs.
	GetSyncStateByNode(ctx context.Context, projectID, fileKey, nodeID string) (*SyncState, error)

	// ListSyncStates retrieves sync states for a project.
	ListSyncStates(ctx context.Context, projectID string, filters map[string]interface{}) ([]*SyncState, error)

	// UpsertSyncState creates or updates a sync state.
	UpsertSyncState(ctx context.Context, state *SyncState) error

	// UpdateSyncStatus updates the sync status
	UpdateSyncStatus(ctx context.Context, syncID string, status SyncStatus) error

	// UpdateSyncTimestamp updates last sync time
	UpdateSyncTimestamp(ctx context.Context, syncID string, timestamp time.Time) error

	// DeleteSyncState deletes a sync state
	DeleteSyncState(ctx context.Context, syncID string) error
}

// ComponentRepository defines the interface for accessing component data
type ComponentRepository interface {
	// GetComponent retrieves a component by ID
	GetComponent(ctx context.Context, componentID string) (*LibraryComponent, error)

	// ListComponents retrieves components for a project
	ListComponents(ctx context.Context, projectID string) ([]*LibraryComponent, error)

	// UpsertComponent creates or updates a component
	UpsertComponent(ctx context.Context, component *LibraryComponent) error

	// DeleteComponent deletes a component
	DeleteComponent(ctx context.Context, componentID string) error
}

// SyncService manages synchronization between Figma designs and code
type SyncService struct {
	client        *Client
	syncRepo      SyncRepository
	componentRepo ComponentRepository
	mapper        *Mapper
	config        SyncConfig
	mutex         sync.RWMutex
	activeSyncs   map[string]context.CancelFunc
	logger        Logger
}

// Logger defines logging interface
type Logger interface {
	Info(msg string, fields ...interface{})
	Error(msg string, err error, fields ...interface{})
	Debug(msg string, fields ...interface{})
}

// NoOpLogger is a logger that does nothing
type NoOpLogger struct{}

// Info implements Logger.Info with no-op behavior.
func (n *NoOpLogger) Info(_ string, _ ...interface{}) {}

// Error implements Logger.Error with no-op behavior.
func (n *NoOpLogger) Error(_ string, _ error, _ ...interface{}) {}

// Debug implements Logger.Debug with no-op behavior.
func (n *NoOpLogger) Debug(_ string, _ ...interface{}) {}

// NewSyncService creates a new Figma sync service
func NewSyncService(
	client *Client,
	syncRepo SyncRepository,
	componentRepo ComponentRepository,
	projectID, fileKey string,
	config SyncConfig,
) *SyncService {
	return &SyncService{
		client:        client,
		syncRepo:      syncRepo,
		componentRepo: componentRepo,
		mapper:        NewMapper(projectID, fileKey),
		config:        config,
		activeSyncs:   make(map[string]context.CancelFunc),
		logger:        &NoOpLogger{},
	}
}

// SetLogger sets the logger for the sync service
func (service *SyncService) SetLogger(logger Logger) {
	service.logger = logger
}

// SyncComponents synchronizes all components from Figma
func (service *SyncService) SyncComponents(ctx context.Context, fileKey string) error {
	service.logger.Info("Starting component sync", "fileKey", fileKey)

	// Fetch file data to ensure file exists
	if _, err := service.client.GetFile(ctx, fileKey, WithGeometry()); err != nil {
		service.logger.Error("Failed to fetch file from Figma", err, "fileKey", fileKey)
		return fmt.Errorf("failed to fetch file: %w", err)
	}

	// Get all components in the file
	componentsData, err := service.client.GetComponents(ctx, fileKey)
	if err != nil {
		service.logger.Error("Failed to fetch components", err, "fileKey", fileKey)
		return fmt.Errorf("failed to fetch components: %w", err)
	}

	// Parse component data and extract node IDs
	nodeIDs := service.extractComponentNodeIDs(componentsData)
	if len(nodeIDs) == 0 {
		service.logger.Info("No components found in file", "fileKey", fileKey)
		return nil
	}

	// Get detailed node information
	nodes, err := service.client.GetNodes(ctx, fileKey, nodeIDs)
	if err != nil {
		service.logger.Error("Failed to fetch node details", err, "fileKey", fileKey)
		return fmt.Errorf("failed to fetch nodes: %w", err)
	}

	// Map nodes to components
	components := service.mapper.MapNodesToComponents(nodes)

	// Sync each component
	for _, component := range components {
		if err := service.syncComponent(ctx, fileKey, component); err != nil {
			service.logger.Error("Failed to sync component", err, "componentID", component.ID, "name", component.Name)
		}
	}

	service.logger.Info("Component sync completed", "fileKey", fileKey, "componentCount", len(components))
	return nil
}

// syncComponent synchronizes a single component
func (service *SyncService) syncComponent(ctx context.Context, fileKey string, component *LibraryComponent) error {
	if err := service.componentRepo.UpsertComponent(ctx, component); err != nil {
		return fmt.Errorf("failed to upsert component: %w", err)
	}

	existingSync, err := service.syncRepo.GetSyncStateByNode(ctx, component.ProjectID, fileKey, component.FigmaNodeID)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		return fmt.Errorf("failed to get sync state: %w", err)
	}

	syncState := service.createSyncState(component)
	if existingSync != nil {
		applyExistingSyncState(existingSync, syncState)
	}

	now := time.Now()
	syncState.LastSyncedAt = &now
	syncState.UpdatedAt = now

	if err := service.syncRepo.UpsertSyncState(ctx, syncState); err != nil {
		return fmt.Errorf("failed to upsert sync state: %w", err)
	}

	return nil
}

func (service *SyncService) createSyncState(component *LibraryComponent) *SyncState {
	return service.mapper.MapNodeToSyncState(&Node{
		ID:   component.FigmaNodeID,
		Name: component.Name,
		Type: "COMPONENT",
	}, nil, &component.ID)
}

func applyExistingSyncState(existingSync *SyncState, syncState *SyncState) {
	syncState.ID = existingSync.ID
	syncState.SyncStatus = existingSync.SyncStatus
	syncState.LastSyncedAt = existingSync.LastSyncedAt
	syncState.CodeModifiedAt = existingSync.CodeModifiedAt
	syncState.CodeVersion = existingSync.CodeVersion
	syncState.CreatedAt = existingSync.CreatedAt

	applyFigmaStatus(existingSync, syncState)
}

func applyFigmaStatus(existingSync *SyncState, syncState *SyncState) {
	if existingSync.FigmaModifiedAt == nil || syncState.FigmaModifiedAt == nil {
		return
	}
	if existingSync.FigmaModifiedAt.Before(*syncState.FigmaModifiedAt) {
		syncState.SyncStatus = SyncStatusOutdated
		if existingSync.CodeModifiedAt != nil && existingSync.CodeModifiedAt.After(*syncState.FigmaModifiedAt) {
			syncState.HasConflict = true
			syncState.SyncStatus = SyncStatusConflict
		}
		return
	}
	if existingSync.FigmaModifiedAt.Equal(*syncState.FigmaModifiedAt) {
		syncState.SyncStatus = SyncStatusSynced
	}
}

// CompareVersions compares Figma and code versions to detect conflicts
func (service *SyncService) CompareVersions(ctx context.Context, syncID string) (*SyncComparison, error) {
	syncState, err := service.syncRepo.GetSyncState(ctx, syncID)
	if err != nil {
		return nil, fmt.Errorf("failed to get sync state: %w", err)
	}

	comparison := &SyncComparison{
		NodeID: syncState.NodeID,
	}

	if syncState.FigmaModifiedAt != nil {
		comparison.FigmaModified = *syncState.FigmaModifiedAt
	}

	if syncState.CodeModifiedAt != nil {
		comparison.CodeModified = *syncState.CodeModifiedAt
	}

	// Determine sync status
	if syncState.FigmaModifiedAt == nil || syncState.CodeModifiedAt == nil {
		comparison.IsSynced = true
		return comparison, nil
	}

	// Check if Figma is outdated
	if syncState.FigmaModifiedAt.Before(*syncState.CodeModifiedAt) {
		comparison.IsOutdated = true
	}

	// Check for conflicts
	if syncState.HasConflict {
		comparison.HasConflict = true
		if syncState.ConflictDetails != nil {
			comparison.ConflictDetails = *syncState.ConflictDetails
		}
	}

	// Determine if synced
	comparison.IsSynced = !comparison.IsOutdated && !comparison.HasConflict

	return comparison, nil
}

// ResolveConflict resolves a conflict between Figma and code versions
func (service *SyncService) ResolveConflict(ctx context.Context, syncID string, resolution string) error {
	syncState, err := service.syncRepo.GetSyncState(ctx, syncID)
	if err != nil {
		return fmt.Errorf("failed to get sync state: %w", err)
	}

	if !syncState.HasConflict {
		return errors.New("no conflict to resolve")
	}

	newStatus := SyncStatusSynced

	switch resolution {
	case "figma_priority":
		// Use Figma as source of truth
		syncState.CodeModifiedAt = syncState.FigmaModifiedAt
		syncState.CodeVersion = syncState.FigmaVersion
	case "code_priority":
		// Use code as source of truth
		syncState.FigmaModifiedAt = syncState.CodeModifiedAt
		syncState.FigmaVersion = syncState.CodeVersion
	case "manual":
		// Mark as pending manual review
		newStatus = SyncStatusPending
	default:
		return fmt.Errorf("unknown resolution strategy: %s", resolution)
	}

	syncState.HasConflict = false
	syncState.ConflictDetails = nil
	syncState.SyncStatus = newStatus
	now := time.Now()
	syncState.LastSyncedAt = &now
	syncState.UpdatedAt = now

	if err := service.syncRepo.UpsertSyncState(ctx, syncState); err != nil {
		return fmt.Errorf("failed to update sync state: %w", err)
	}

	service.logger.Info("Conflict resolved", "syncID", syncID, "resolution", resolution)
	return nil
}

// SyncComponentUpdates synchronizes component updates from Figma
func (syncService *SyncService) SyncComponentUpdates(ctx context.Context, fileKey string) ([]string, error) {
	updatedIDs := make([]string, 0)

	// Get all sync states for this file
	syncStates, err := syncService.syncRepo.ListSyncStates(ctx, syncService.mapper.projectID, map[string]interface{}{
		"file_key": fileKey,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to list sync states: %w", err)
	}

	// Check each synced component for updates
	for _, syncState := range syncStates {
		if updatedID, synced := syncService.syncComponentIfUpdated(ctx, fileKey, syncState); synced {
			updatedIDs = append(updatedIDs, updatedID)
		}
	}

	syncService.logger.Info("Component updates synced", "fileKey", fileKey, "updatedCount", len(updatedIDs))
	return updatedIDs, nil
}

func (service *SyncService) syncComponentIfUpdated(
	ctx context.Context,
	fileKey string,
	syncState *SyncState,
) (string, bool) {
	if syncState.ComponentID == nil {
		return "", false
	}

	component, err := service.componentRepo.GetComponent(ctx, *syncState.ComponentID)
	if err != nil {
		service.logger.Error("Failed to get component", err, "componentID", *syncState.ComponentID)
		return "", false
	}

	nodes, err := service.client.GetNodes(ctx, fileKey, []string{component.FigmaNodeID})
	if err != nil {
		service.logger.Error("Failed to fetch node", err, "nodeID", component.FigmaNodeID)
		return "", false
	}

	updatedNode := nodes[component.FigmaNodeID]
	if updatedNode == nil {
		return "", false
	}

	if syncState.FigmaModifiedAt == nil || !updatedNode.ModifiedAt.After(*syncState.FigmaModifiedAt) {
		return "", false
	}

	if err := service.syncComponent(ctx, fileKey, component); err != nil {
		service.logger.Error("Failed to sync updated component", err, "componentID", component.ID)
		return "", false
	}

	return component.ID, true
}

// DetectOutdatedComponents detects components that are outdated compared to code
func (service *SyncService) DetectOutdatedComponents(ctx context.Context, projectID string) ([]string, error) {
	outdatedIDs := make([]string, 0)

	syncStates, err := service.syncRepo.ListSyncStates(ctx, projectID, map[string]interface{}{
		"sync_status": string(SyncStatusOutdated),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to list sync states: %w", err)
	}

	for _, syncState := range syncStates {
		if syncState.ComponentID != nil {
			outdatedIDs = append(outdatedIDs, *syncState.ComponentID)
		}
	}

	return outdatedIDs, nil
}

// DetectConflicts detects conflicts between Figma and code
func (service *SyncService) DetectConflicts(ctx context.Context, projectID string) ([]string, error) {
	conflictIDs := make([]string, 0)

	syncStates, err := service.syncRepo.ListSyncStates(ctx, projectID, map[string]interface{}{
		"has_conflict": true,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to list sync states: %w", err)
	}

	for _, syncState := range syncStates {
		conflictIDs = append(conflictIDs, syncState.ID)
	}

	return conflictIDs, nil
}

// extractComponentNodeIDs extracts node IDs from component data
func (service *SyncService) extractComponentNodeIDs(componentsData map[string]interface{}) []string {
	nodeIDs := make([]string, 0)

	if components, ok := componentsData["components"].(map[string]interface{}); ok {
		for nodeID := range components {
			nodeIDs = append(nodeIDs, nodeID)
		}
	}

	return nodeIDs
}

// Cancel cancels an active sync operation
func (service *SyncService) Cancel(syncID string) {
	service.mutex.Lock()
	defer service.mutex.Unlock()

	if cancel, ok := service.activeSyncs[syncID]; ok {
		cancel()
		delete(service.activeSyncs, syncID)
		service.logger.Info("Sync operation cancelled", "syncID", syncID)
	}
}

// CancelAll cancels all active sync operations
func (service *SyncService) CancelAll() {
	service.mutex.Lock()
	defer service.mutex.Unlock()

	for syncID, cancel := range service.activeSyncs {
		cancel()
		service.logger.Info("Sync operation cancelled", "syncID", syncID)
	}
	service.activeSyncs = make(map[string]context.CancelFunc)
}

// GetActiveSyncs returns the count of active syncs
func (service *SyncService) GetActiveSyncs() int {
	service.mutex.RLock()
	defer service.mutex.RUnlock()

	return len(service.activeSyncs)
}

// Close closes the sync service and cleans up resources
func (service *SyncService) Close() error {
	service.CancelAll()
	if service.client != nil {
		return service.client.Close()
	}
	return nil
}
