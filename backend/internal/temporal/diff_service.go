// Package temporal provides temporal/diff and workflow-related services.
// Package temporal contains services for temporal versioning and diffs.
package temporal

import (
	"cmp"
	"context"
	"encoding/json"
	"fmt"
	"slices"
	"time"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/kooshapari/tracertm-backend/internal/db"
)

// Significance thresholds for field change counting
const (
	significanceManyModifiedThreshold = 3
	significanceSomeModifiedThreshold = 1
)

// DiffChangeType represents the type of change in a diff
type DiffChangeType string

const (
	// DiffChangeTypeAdded indicates an item was added.
	DiffChangeTypeAdded DiffChangeType = "added"
	// DiffChangeTypeRemoved indicates an item was removed.
	DiffChangeTypeRemoved DiffChangeType = "removed"
	// DiffChangeTypeModified indicates an item was modified.
	DiffChangeTypeModified DiffChangeType = "modified"
)

// DiffSignificance represents the impact level of a change
type DiffSignificance string

const (
	// DiffSignificanceMinor indicates a low-impact change.
	DiffSignificanceMinor DiffSignificance = "minor"
	// DiffSignificanceModerate indicates a medium-impact change.
	DiffSignificanceModerate DiffSignificance = "moderate"
	// DiffSignificanceMajor indicates a high-impact change.
	DiffSignificanceMajor DiffSignificance = "major"
	// DiffSignificanceBreaking indicates a breaking change.
	DiffSignificanceBreaking DiffSignificance = "breaking"
)

// FieldChange represents a change to a single field
type FieldChange struct {
	Field      string      `json:"field"`
	OldValue   interface{} `json:"old_value"`
	NewValue   interface{} `json:"new_value"`
	ChangeType string      `json:"change_type"` // added, removed, modified
}

// DiffItem represents an item in a diff
type DiffItem struct {
	ItemID       string           `json:"item_id"`
	Type         string           `json:"type"`
	Title        string           `json:"title"`
	ChangeType   DiffChangeType   `json:"change_type"`
	FieldChanges []FieldChange    `json:"field_changes,omitempty"`
	Significance DiffSignificance `json:"significance"`
}

// DiffStatistics represents statistics about a diff
type DiffStatistics struct {
	TotalChanges   int `json:"total_changes"`
	AddedCount     int `json:"added_count"`
	RemovedCount   int `json:"removed_count"`
	ModifiedCount  int `json:"modified_count"`
	UnchangedCount int `json:"unchanged_count"`
}

// VersionDiff represents the result of comparing two versions
type VersionDiff struct {
	VersionA       string         `json:"version_a"`
	VersionB       string         `json:"version_b"`
	VersionANumber int            `json:"version_a_number"`
	VersionBNumber int            `json:"version_b_number"`
	Added          []DiffItem     `json:"added"`
	Removed        []DiffItem     `json:"removed"`
	Modified       []DiffItem     `json:"modified"`
	Unchanged      int            `json:"unchanged"`
	Stats          DiffStatistics `json:"stats"`
	ComputedAt     string         `json:"computed_at"`
}

// DiffService handles version diff calculations
type DiffService struct {
	pool    *pgxpool.Pool
	queries *db.Queries
}

// NewDiffService creates a new diff service
func NewDiffService(pool *pgxpool.Pool) *DiffService {
	return &DiffService{
		pool:    pool,
		queries: db.New(pool),
	}
}

// CalculateVersionDiff calculates the diff between two versions
func (s *DiffService) CalculateVersionDiff(ctx context.Context, versionAID, versionBID string) (*VersionDiff, error) {
	if _, _, err := parseVersionIDs(versionAID, versionBID); err != nil {
		return nil, err
	}

	// Fetch version snapshots
	snapshotA, err := s.getVersionSnapshot(ctx, versionAID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch version A snapshot: %w", err)
	}

	snapshotB, err := s.getVersionSnapshot(ctx, versionBID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch version B snapshot: %w", err)
	}

	itemsA, err := parseSnapshotData(snapshotA.Data, "A")
	if err != nil {
		return nil, err
	}
	itemsB, err := parseSnapshotData(snapshotB.Data, "B")
	if err != nil {
		return nil, err
	}

	diff := initVersionDiff(versionAID, versionBID, snapshotA, snapshotB)
	s.populateDiffItems(diff, itemsA, itemsB)
	finalizeDiff(diff)

	return diff, nil
}

func parseVersionIDs(versionAID, versionBID string) (pgtype.UUID, pgtype.UUID, error) {
	var versionAUUID, versionBUUID pgtype.UUID
	if err := versionAUUID.Scan(versionAID); err != nil {
		return pgtype.UUID{}, pgtype.UUID{}, fmt.Errorf("invalid version A ID: %w", err)
	}
	if err := versionBUUID.Scan(versionBID); err != nil {
		return pgtype.UUID{}, pgtype.UUID{}, fmt.Errorf("invalid version B ID: %w", err)
	}
	return versionAUUID, versionBUUID, nil
}

func parseSnapshotData(data []byte, label string) (map[string]map[string]interface{}, error) {
	items := make(map[string]map[string]interface{})
	if err := json.Unmarshal(data, &items); err != nil {
		return nil, fmt.Errorf("failed to parse version %s snapshot: %w", label, err)
	}
	return items, nil
}

func initVersionDiff(versionAID, versionBID string, snapshotA, snapshotB *VersionSnapshot) *VersionDiff {
	return &VersionDiff{
		VersionA:       versionAID,
		VersionB:       versionBID,
		VersionANumber: snapshotA.VersionNumber,
		VersionBNumber: snapshotB.VersionNumber,
		Added:          make([]DiffItem, 0),
		Removed:        make([]DiffItem, 0),
		Modified:       make([]DiffItem, 0),
		ComputedAt:     time.Now().UTC().Format(time.RFC3339),
	}
}

func (s *DiffService) populateDiffItems(
	diff *VersionDiff,
	itemsA map[string]map[string]interface{},
	itemsB map[string]map[string]interface{},
) {
	for itemID, itemB := range itemsB {
		itemA, exists := itemsA[itemID]
		if !exists {
			diffItem := s.createDiffItem(itemID, itemB, nil, DiffChangeTypeAdded)
			diff.Added = append(diff.Added, diffItem)
			continue
		}

		changes := s.detectFieldChanges(itemA, itemB)
		if len(changes) == 0 {
			diff.Unchanged++
			continue
		}

		diffItem := s.createDiffItem(itemID, itemB, itemA, DiffChangeTypeModified)
		diffItem.FieldChanges = changes
		diffItem.Significance = s.calculateSignificance(changes)
		diff.Modified = append(diff.Modified, diffItem)
	}

	for itemID, itemA := range itemsA {
		if _, exists := itemsB[itemID]; !exists {
			diffItem := s.createDiffItem(itemID, itemA, nil, DiffChangeTypeRemoved)
			diff.Removed = append(diff.Removed, diffItem)
		}
	}
}

func finalizeDiff(diff *VersionDiff) {
	diff.Stats = DiffStatistics{
		TotalChanges:   len(diff.Added) + len(diff.Removed) + len(diff.Modified),
		AddedCount:     len(diff.Added),
		RemovedCount:   len(diff.Removed),
		ModifiedCount:  len(diff.Modified),
		UnchangedCount: diff.Unchanged,
	}

	slices.SortFunc(diff.Added, func(a, b DiffItem) int {
		return cmp.Compare(a.Title, b.Title)
	})
	slices.SortFunc(diff.Removed, func(a, b DiffItem) int {
		return cmp.Compare(a.Title, b.Title)
	})
	slices.SortFunc(diff.Modified, func(a, b DiffItem) int {
		return cmp.Compare(a.Title, b.Title)
	})
}

// detectFieldChanges detects field-level changes between two items
func (s *DiffService) detectFieldChanges(itemA, itemB map[string]interface{}) []FieldChange {
	changes := make([]FieldChange, 0)

	// Check all fields in B
	for field, newValue := range itemB {
		oldValue, exists := itemA[field]
		if !exists {
			// Field was added
			changes = append(changes, FieldChange{
				Field:      field,
				OldValue:   nil,
				NewValue:   newValue,
				ChangeType: "added",
			})
		} else if !s.valuesEqual(oldValue, newValue) {
			// Field was modified
			changes = append(changes, FieldChange{
				Field:      field,
				OldValue:   oldValue,
				NewValue:   newValue,
				ChangeType: "modified",
			})
		}
	}

	// Check for removed fields (in A but not in B)
	for field, oldValue := range itemA {
		if _, exists := itemB[field]; !exists {
			changes = append(changes, FieldChange{
				Field:      field,
				OldValue:   oldValue,
				NewValue:   nil,
				ChangeType: "removed",
			})
		}
	}

	return changes
}

// valuesEqual checks if two values are equal
func (s *DiffService) valuesEqual(a, b interface{}) bool {
	aJSON, aErr := json.Marshal(a)
	bJSON, bErr := json.Marshal(b)
	if aErr != nil || bErr != nil {
		return false
	}
	return string(aJSON) == string(bJSON)
}

// createDiffItem creates a DiffItem from item data
func (s *DiffService) createDiffItem(itemID string, itemData, _ map[string]interface{}, changeType DiffChangeType) DiffItem {
	title, ok := itemData["title"].(string)
	if !ok {
		title = ""
	}
	itemType, ok := itemData["type"].(string)
	if !ok {
		itemType = ""
	}

	return DiffItem{
		ItemID:       itemID,
		Type:         itemType,
		Title:        title,
		ChangeType:   changeType,
		Significance: DiffSignificanceMinor,
	}
}

// calculateSignificance calculates the significance of changes
func (s *DiffService) calculateSignificance(changes []FieldChange) DiffSignificance {
	criticalFields := map[string]bool{
		"status":      true,
		"type":        true,
		"priority":    true,
		"description": true,
	}

	modifiedCount := 0
	hasCritical := false

	for _, change := range changes {
		if change.ChangeType == "modified" {
			modifiedCount++
			if criticalFields[change.Field] {
				hasCritical = true
			}
		}
	}

	if hasCritical {
		return DiffSignificanceMajor
	}

	if modifiedCount > significanceManyModifiedThreshold {
		return DiffSignificanceMajor
	}

	if modifiedCount > significanceSomeModifiedThreshold {
		return DiffSignificanceModerate
	}

	return DiffSignificanceMinor
}

// getVersionSnapshot retrieves a version snapshot
func (s *DiffService) getVersionSnapshot(_ context.Context, versionID string) (*VersionSnapshot, error) {
	// This would query the versions table and snapshots table
	// For now, returning a placeholder that would be implemented
	// based on the actual database schema

	var versionUUID pgtype.UUID
	if err := versionUUID.Scan(versionID); err != nil {
		return nil, fmt.Errorf("invalid version ID: %w", err)
	}

	// Query would be similar to:
	// SELECT v.id, v.version_number, s.data FROM versions v
	// JOIN snapshots s ON v.snapshot_id = s.id
	// WHERE v.id = $1

	// Placeholder implementation
	return &VersionSnapshot{
		ID:            versionID,
		VersionNumber: 0,
		Data:          []byte("{}"),
	}, nil
}

// VersionSnapshot represents a snapshot of items at a point in time
type VersionSnapshot struct {
	ID            string
	VersionNumber int
	Data          []byte // JSON-encoded items
}

// CompareVersions returns a summary comparison between two versions
func (s *DiffService) CompareVersions(ctx context.Context, versionAID, versionBID string) (map[string]interface{}, error) {
	diff, err := s.CalculateVersionDiff(ctx, versionAID, versionBID)
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"versionA": diff.VersionA,
		"versionB": diff.VersionB,
		"summary": map[string]interface{}{
			"added":     diff.Stats.AddedCount,
			"removed":   diff.Stats.RemovedCount,
			"modified":  diff.Stats.ModifiedCount,
			"unchanged": diff.Unchanged,
		},
		"computedAt": diff.ComputedAt,
	}, nil
}

// GetDiffBetweenSnapshots calculates diff between two raw snapshots
// This is useful for testing and caching scenarios
func (s *DiffService) GetDiffBetweenSnapshots(snapshotA, snapshotB map[string]map[string]interface{}) *VersionDiff {
	diff := &VersionDiff{
		Added:      make([]DiffItem, 0),
		Removed:    make([]DiffItem, 0),
		Modified:   make([]DiffItem, 0),
		ComputedAt: time.Now().UTC().Format(time.RFC3339),
	}

	// Find added and modified items
	for itemID, itemB := range snapshotB {
		itemA, exists := snapshotA[itemID]
		if !exists {
			// Item was added
			diffItem := s.createDiffItem(itemID, itemB, nil, DiffChangeTypeAdded)
			diff.Added = append(diff.Added, diffItem)
		} else {
			// Check if item was modified
			changes := s.detectFieldChanges(itemA, itemB)
			if len(changes) > 0 {
				diffItem := s.createDiffItem(itemID, itemB, itemA, DiffChangeTypeModified)
				diffItem.FieldChanges = changes
				diffItem.Significance = s.calculateSignificance(changes)
				diff.Modified = append(diff.Modified, diffItem)
			} else {
				diff.Unchanged++
			}
		}
	}

	// Find removed items
	for itemID, itemA := range snapshotA {
		if _, exists := snapshotB[itemID]; !exists {
			// Item was removed
			diffItem := s.createDiffItem(itemID, itemA, nil, DiffChangeTypeRemoved)
			diff.Removed = append(diff.Removed, diffItem)
		}
	}

	// Calculate statistics
	diff.Stats = DiffStatistics{
		TotalChanges:   len(diff.Added) + len(diff.Removed) + len(diff.Modified),
		AddedCount:     len(diff.Added),
		RemovedCount:   len(diff.Removed),
		ModifiedCount:  len(diff.Modified),
		UnchangedCount: diff.Unchanged,
	}

	// Sort for consistency
	slices.SortFunc(diff.Added, func(a, b DiffItem) int {
		return cmp.Compare(a.Title, b.Title)
	})
	slices.SortFunc(diff.Removed, func(a, b DiffItem) int {
		return cmp.Compare(a.Title, b.Title)
	})
	slices.SortFunc(diff.Modified, func(a, b DiffItem) int {
		return cmp.Compare(a.Title, b.Title)
	})

	return diff
}
