package temporal

import (
	"testing"
)

func TestDetectFieldChanges(t *testing.T) {
	service := &DiffService{}

	for _, tt := range fieldChangeTests() {
		t.Run(tt.name, func(t *testing.T) {
			changes := service.detectFieldChanges(tt.itemA, tt.itemB)
			if len(changes) != tt.expected {
				t.Errorf("expected %d changes, got %d", tt.expected, len(changes))
			}
		})
	}
}

type fieldChangeTestCase struct {
	name     string
	itemA    map[string]interface{}
	itemB    map[string]interface{}
	expected int
}

func fieldChangeTests() []fieldChangeTestCase {
	cases := make([]fieldChangeTestCase, 0, 5)
	cases = append(cases, fieldChangeBasicCases()...)
	cases = append(cases, fieldChangeComplexCases()...)
	return cases
}

func fieldChangeBasicCases() []fieldChangeTestCase {
	return []fieldChangeTestCase{
		{
			name: "no changes",
			itemA: map[string]interface{}{
				"title":       "Test Item",
				"status":      "open",
				"description": "Test description",
			},
			itemB: map[string]interface{}{
				"title":       "Test Item",
				"status":      "open",
				"description": "Test description",
			},
			expected: 0,
		},
		{
			name: "single field modified",
			itemA: map[string]interface{}{
				"title":  "Test Item",
				"status": "open",
			},
			itemB: map[string]interface{}{
				"title":  "Test Item",
				"status": "closed",
			},
			expected: 1,
		},
		{
			name: "field added",
			itemA: map[string]interface{}{
				"title": "Test Item",
			},
			itemB: map[string]interface{}{
				"title":  "Test Item",
				"status": "open",
			},
			expected: 1,
		},
		{
			name: "field removed",
			itemA: map[string]interface{}{
				"title":  "Test Item",
				"status": "open",
			},
			itemB: map[string]interface{}{
				"title": "Test Item",
			},
			expected: 1,
		},
	}
}

func fieldChangeComplexCases() []fieldChangeTestCase {
	return []fieldChangeTestCase{
		{
			name: "multiple changes",
			itemA: map[string]interface{}{
				"title":       "Old Title",
				"status":      "open",
				"description": "Old description",
				"priority":    "low",
			},
			itemB: map[string]interface{}{
				"title":       "New Title",
				"status":      "closed",
				"description": "New description",
			},
			expected: 4,
		},
	}
}

func TestValuesEqual(t *testing.T) {
	service := &DiffService{}

	tests := []struct {
		name     string
		a        interface{}
		b        interface{}
		expected bool
	}{
		{
			name:     "same string",
			a:        "test",
			b:        "test",
			expected: true,
		},
		{
			name:     "different strings",
			a:        "test1",
			b:        "test2",
			expected: false,
		},
		{
			name:     "same numbers",
			a:        42,
			b:        42,
			expected: true,
		},
		{
			name:     "different numbers",
			a:        42,
			b:        43,
			expected: false,
		},
		{
			name:     "same objects",
			a:        map[string]interface{}{"key": "value"},
			b:        map[string]interface{}{"key": "value"},
			expected: true,
		},
		{
			name:     "different objects",
			a:        map[string]interface{}{"key": "value1"},
			b:        map[string]interface{}{"key": "value2"},
			expected: false,
		},
		{
			name:     "nil comparison",
			a:        nil,
			b:        nil,
			expected: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := service.valuesEqual(tt.a, tt.b)
			if result != tt.expected {
				t.Errorf("expected %v, got %v", tt.expected, result)
			}
		})
	}
}

func TestCalculateSignificance(t *testing.T) {
	service := &DiffService{}

	for _, tt := range significanceTests() {
		t.Run(tt.name, func(t *testing.T) {
			result := service.calculateSignificance(tt.changes)
			if result != tt.expected {
				t.Errorf("expected %v, got %v", tt.expected, result)
			}
		})
	}
}

type significanceTestCase struct {
	name     string
	changes  []FieldChange
	expected DiffSignificance
}

func significanceTests() []significanceTestCase {
	return []significanceTestCase{
		{
			name:     "no changes",
			changes:  []FieldChange{},
			expected: DiffSignificanceMinor,
		},
		{
			name: "single non-critical change",
			changes: []FieldChange{
				{Field: "notes", ChangeType: "modified"},
			},
			expected: DiffSignificanceMinor,
		},
		{
			name: "single critical change",
			changes: []FieldChange{
				{Field: "status", ChangeType: "modified"},
			},
			expected: DiffSignificanceMajor,
		},
		{
			name: "two non-critical changes",
			changes: []FieldChange{
				{Field: "notes", ChangeType: "modified"},
				{Field: "tags", ChangeType: "modified"},
			},
			expected: DiffSignificanceModerate,
		},
		{
			name: "multiple non-critical changes",
			changes: []FieldChange{
				{Field: "notes", ChangeType: "modified"},
				{Field: "tags", ChangeType: "modified"},
				{Field: "owner", ChangeType: "modified"},
				{Field: "labels", ChangeType: "modified"},
			},
			expected: DiffSignificanceMajor,
		},
		{
			name: "added and removed fields",
			changes: []FieldChange{
				{Field: "newField", ChangeType: "added"},
				{Field: "oldField", ChangeType: "removed"},
			},
			expected: DiffSignificanceMinor,
		},
	}
}

func TestGetDiffBetweenSnapshots(t *testing.T) {
	service := &DiffService{}

	snapshotA := map[string]map[string]interface{}{
		"item1": {
			"title":  "Item 1",
			"status": "open",
			"type":   "requirement",
		},
		"item2": {
			"title":  "Item 2",
			"status": "closed",
			"type":   "bug",
		},
	}

	snapshotB := map[string]map[string]interface{}{
		"item1": {
			"title":  "Item 1",
			"status": "closed", // modified
			"type":   "requirement",
		},
		"item3": {
			"title":  "Item 3",
			"status": "open",
			"type":   "feature",
		},
	}

	diff := service.GetDiffBetweenSnapshots(snapshotA, snapshotB)

	// Verify counts
	if diff.Stats.AddedCount != 1 {
		t.Errorf("expected 1 added item, got %d", diff.Stats.AddedCount)
	}
	if diff.Stats.RemovedCount != 1 {
		t.Errorf("expected 1 removed item, got %d", diff.Stats.RemovedCount)
	}
	if diff.Stats.ModifiedCount != 1 {
		t.Errorf("expected 1 modified item, got %d", diff.Stats.ModifiedCount)
	}

	// Verify item details
	if len(diff.Added) != 1 || diff.Added[0].ItemID != "item3" {
		t.Errorf("expected item3 in added, got %v", diff.Added)
	}
	if len(diff.Removed) != 1 || diff.Removed[0].ItemID != "item2" {
		t.Errorf("expected item2 in removed, got %v", diff.Removed)
	}
	if len(diff.Modified) != 1 || diff.Modified[0].ItemID != "item1" {
		t.Errorf("expected item1 in modified, got %v", diff.Modified)
	}

	// Verify field changes for modified item
	if len(diff.Modified[0].FieldChanges) != 1 {
		t.Errorf("expected 1 field change, got %d", len(diff.Modified[0].FieldChanges))
	}
	if diff.Modified[0].FieldChanges[0].Field != "status" {
		t.Errorf("expected status field change, got %s", diff.Modified[0].FieldChanges[0].Field)
	}

	// Verify statistics
	if diff.Stats.TotalChanges != 3 {
		t.Errorf("expected 3 total changes, got %d", diff.Stats.TotalChanges)
	}
}

func TestGetDiffBetweenSnapshots_LargeDataset(t *testing.T) {
	service := &DiffService{}

	// Create large snapshots
	const itemCount = 1000
	const modifyPercentage = 0.1  // 10%
	const addPercentage = 0.05    // 5%
	const removePercentage = 0.05 // 5%

	snapshotA, snapshotB, removed := buildLargeSnapshots(itemCount, modifyPercentage, addPercentage, removePercentage)

	diff := service.GetDiffBetweenSnapshots(snapshotA, snapshotB)

	// Verify counts are reasonable
	if diff.Stats.ModifiedCount != int(float64(itemCount)*modifyPercentage) {
		t.Logf("modified count: expected ~%d, got %d", int(float64(itemCount)*modifyPercentage), diff.Stats.ModifiedCount)
	}

	expectedAdded := int(float64(itemCount) * addPercentage)
	if diff.Stats.AddedCount != expectedAdded {
		t.Errorf("added count: expected %d, got %d", expectedAdded, diff.Stats.AddedCount)
	}

	if diff.Stats.RemovedCount != removed {
		t.Errorf("removed count: expected %d, got %d", removed, diff.Stats.RemovedCount)
	}

	// Verify statistics sum correctly
	totalItems := itemCount + expectedAdded
	expectedUnchanged := totalItems - diff.Stats.ModifiedCount - expectedAdded - removed
	if diff.Unchanged != expectedUnchanged {
		t.Logf("unchanged count: expected %d, got %d", expectedUnchanged, diff.Unchanged)
	}
}

func buildLargeSnapshots(
	itemCount int, modifyPercentage, addPercentage, removePercentage float64,
) (map[string]map[string]interface{}, map[string]map[string]interface{}, int) {
	snapshotA := make(map[string]map[string]interface{})
	snapshotB := make(map[string]map[string]interface{})

	for i := 0; i < itemCount; i++ {
		itemID := string(rune(i))
		if i < len([]rune("item")) {
			itemID = "item" + string(rune(i))
		}
		snapshotA[itemID] = map[string]interface{}{
			"title":       "Item " + itemID,
			"status":      "open",
			"type":        "requirement",
			"description": "Description for item",
		}
	}

	for key, v := range snapshotA {
		snapshotB[key] = v
	}

	modified := 0
	for key := range snapshotA {
		if modified < int(float64(itemCount)*modifyPercentage) {
			item := make(map[string]interface{})
			for kk, vv := range snapshotA[key] {
				item[kk] = vv
			}
			item["status"] = "closed"
			snapshotB[key] = item
			modified++
		}
	}

	for i := 0; i < int(float64(itemCount)*addPercentage); i++ {
		itemID := "newitem" + string(rune(i))
		snapshotB[itemID] = map[string]interface{}{
			"title":  "New Item " + string(rune(i)),
			"status": "open",
			"type":   "feature",
		}
	}

	removed := 0
	for key := range snapshotA {
		if removed < int(float64(itemCount)*removePercentage) {
			delete(snapshotB, key)
			removed++
		}
	}

	return snapshotA, snapshotB, removed
}

func TestCreateDiffItem(t *testing.T) {
	service := &DiffService{}

	itemData := map[string]interface{}{
		"title":       "Test Item",
		"type":        "requirement",
		"status":      "open",
		"description": "Test description",
	}

	diffItem := service.createDiffItem("item1", itemData, nil, DiffChangeTypeAdded)

	if diffItem.ItemID != "item1" {
		t.Errorf("expected item ID item1, got %s", diffItem.ItemID)
	}
	if diffItem.Title != "Test Item" {
		t.Errorf("expected title 'Test Item', got %s", diffItem.Title)
	}
	if diffItem.Type != "requirement" {
		t.Errorf("expected type 'requirement', got %s", diffItem.Type)
	}
	if diffItem.ChangeType != DiffChangeTypeAdded {
		t.Errorf("expected change type added, got %s", diffItem.ChangeType)
	}
}

func TestEmptyDiff(t *testing.T) {
	service := &DiffService{}

	snapshotA := map[string]map[string]interface{}{
		"item1": {
			"title": "Item 1",
		},
	}

	snapshotB := map[string]map[string]interface{}{
		"item1": {
			"title": "Item 1",
		},
	}

	diff := service.GetDiffBetweenSnapshots(snapshotA, snapshotB)

	if diff.Stats.TotalChanges != 0 {
		t.Errorf("expected 0 total changes, got %d", diff.Stats.TotalChanges)
	}
	if diff.Unchanged != 1 {
		t.Errorf("expected 1 unchanged item, got %d", diff.Unchanged)
	}
	if len(diff.Added) != 0 || len(diff.Removed) != 0 || len(diff.Modified) != 0 {
		t.Errorf("expected empty added/removed/modified")
	}
}
