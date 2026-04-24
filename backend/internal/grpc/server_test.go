//go:build !integration

package grpc

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	pb "github.com/kooshapari/tracertm-backend/pkg/proto/tracertm/v1"
)

// mockItemRepo implements repository.ItemRepository for testing
type mockItemRepo struct {
	items map[string]*models.Item
	err   error
}

func (m *mockItemRepo) Create(_ context.Context, _ *models.Item) error { return m.err }
func (m *mockItemRepo) GetByID(_ context.Context, id string) (*models.Item, error) {
	if m.err != nil {
		return nil, m.err
	}
	item, ok := m.items[id]
	if !ok {
		return nil, errors.New("not found")
	}
	return item, nil
}

func (m *mockItemRepo) GetByProjectID(_ context.Context, _ string) ([]*models.Item, error) {
	return nil, m.err
}

func (m *mockItemRepo) List(_ context.Context, _ repository.ItemFilter) ([]*models.Item, error) {
	return nil, m.err
}
func (m *mockItemRepo) Update(_ context.Context, _ *models.Item) error { return m.err }
func (m *mockItemRepo) Delete(_ context.Context, _ string) error       { return m.err }
func (m *mockItemRepo) Count(_ context.Context, _ repository.ItemFilter) (int64, error) {
	return 0, m.err
}

// mockLinkRepo implements repository.LinkRepository for testing
type mockLinkRepo struct {
	sourceLinks map[string][]*models.Link
	targetLinks map[string][]*models.Link
	err         error
}

func (m *mockLinkRepo) Create(_ context.Context, _ *models.Link) error { return m.err }
func (m *mockLinkRepo) GetByID(_ context.Context, _ string) (*models.Link, error) {
	return nil, m.err
}

func (m *mockLinkRepo) GetBySourceID(_ context.Context, sourceID string) ([]*models.Link, error) {
	if m.err != nil {
		return nil, m.err
	}
	return m.sourceLinks[sourceID], nil
}

func (m *mockLinkRepo) GetByTargetID(_ context.Context, targetID string) ([]*models.Link, error) {
	if m.err != nil {
		return nil, m.err
	}
	return m.targetLinks[targetID], nil
}

func (m *mockLinkRepo) List(_ context.Context, _ repository.LinkFilter) ([]*models.Link, error) {
	return nil, m.err
}
func (m *mockLinkRepo) Update(_ context.Context, _ *models.Link) error { return m.err }
func (m *mockLinkRepo) Delete(_ context.Context, _ string) error       { return m.err }
func (m *mockLinkRepo) DeleteByItemID(_ context.Context, _ string) error {
	return m.err
}

func TestNewGraphServiceServer(t *testing.T) {
	itemRepo := &mockItemRepo{}
	linkRepo := &mockLinkRepo{}

	server := NewGraphServiceServer(itemRepo, linkRepo, nil)
	require.NotNil(t, server)
	assert.Equal(t, itemRepo, server.itemRepo)
	assert.Equal(t, linkRepo, server.linkRepo)
	assert.Nil(t, server.graphSvc)
}

func TestValidateAnalyzeImpactRequest(t *testing.T) {
	tests := []struct {
		name    string
		req     *pb.AnalyzeImpactRequest
		wantErr bool
		errMsg  string
	}{
		{
			name:    "missing item_id",
			req:     &pb.AnalyzeImpactRequest{ProjectId: "p1", Direction: "upstream"},
			wantErr: true,
			errMsg:  "item_id is required",
		},
		{
			name:    "missing project_id",
			req:     &pb.AnalyzeImpactRequest{ItemId: "i1", Direction: "upstream"},
			wantErr: true,
			errMsg:  "project_id is required",
		},
		{
			name:    "invalid direction",
			req:     &pb.AnalyzeImpactRequest{ItemId: "i1", ProjectId: "p1", Direction: "sideways"},
			wantErr: true,
			errMsg:  "direction must be",
		},
		{
			name:    "valid upstream",
			req:     &pb.AnalyzeImpactRequest{ItemId: "i1", ProjectId: "p1", Direction: "upstream"},
			wantErr: false,
		},
		{
			name:    "valid downstream",
			req:     &pb.AnalyzeImpactRequest{ItemId: "i1", ProjectId: "p1", Direction: "downstream"},
			wantErr: false,
		},
		{
			name:    "valid both",
			req:     &pb.AnalyzeImpactRequest{ItemId: "i1", ProjectId: "p1", Direction: "both"},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateAnalyzeImpactRequest(tt.req)
			if tt.wantErr {
				require.Error(t, err)
				assert.Contains(t, err.Error(), tt.errMsg)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestIsValidImpactDirection(t *testing.T) {
	assert.True(t, isValidImpactDirection("upstream"))
	assert.True(t, isValidImpactDirection("downstream"))
	assert.True(t, isValidImpactDirection("both"))
	assert.False(t, isValidImpactDirection(""))
	assert.False(t, isValidImpactDirection("invalid"))
	assert.False(t, isValidImpactDirection("UPSTREAM"))
}

func TestFilterLinksByType(t *testing.T) {
	links := []*models.Link{
		{ID: "1", Type: "depends_on"},
		{ID: "2", Type: "implements"},
		{ID: "3", Type: "tests"},
		{ID: "4", Type: "depends_on"},
	}

	tests := []struct {
		name      string
		linkTypes []string
		wantCount int
	}{
		{"no filter returns all", nil, 4},
		{"empty filter returns all", []string{}, 4},
		{"filter depends_on", []string{"depends_on"}, 2},
		{"filter implements", []string{"implements"}, 1},
		{"filter multiple types", []string{"depends_on", "tests"}, 3},
		{"filter non-existent type", []string{"nonexistent"}, 0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := filterLinksByType(links, tt.linkTypes)
			assert.Len(t, result, tt.wantCount)
		})
	}
}

func TestGetRelatedID(t *testing.T) {
	link := &models.Link{SourceID: "src", TargetID: "tgt"}

	assert.Equal(t, "tgt", getRelatedID(link, "src"))
	assert.Equal(t, "src", getRelatedID(link, "tgt"))
	assert.Equal(t, "src", getRelatedID(link, "other"))
}

func TestIdentifyCriticalPaths(t *testing.T) {
	tests := []struct {
		name      string
		items     []*pb.ImpactedItem
		wantCount int
	}{
		{
			name:      "empty items",
			items:     []*pb.ImpactedItem{},
			wantCount: 0,
		},
		{
			name: "all below threshold",
			items: []*pb.ImpactedItem{
				{Id: "a", ImpactScore: 0.3},
				{Id: "b", ImpactScore: 0.1},
			},
			wantCount: 0,
		},
		{
			name: "some above threshold",
			items: []*pb.ImpactedItem{
				{Id: "a", ImpactScore: 1.0},
				{Id: "b", ImpactScore: 0.3},
				{Id: "c", ImpactScore: 0.6},
			},
			wantCount: 2,
		},
		{
			name: "at threshold not included",
			items: []*pb.ImpactedItem{
				{Id: "a", ImpactScore: 0.5},
			},
			wantCount: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := identifyCriticalPaths(tt.items)
			assert.Len(t, result, tt.wantCount)
		})
	}
}

func TestBuildImpactedItem(t *testing.T) {
	item := &models.Item{
		ID:    "item-1",
		Type:  "feature",
		Title: "Test Feature",
	}

	result := buildImpactedItem(item, 1, "depends_on")
	assert.Equal(t, "item-1", result.Id)
	assert.Equal(t, "feature", result.Type)
	assert.Equal(t, "Test Feature", result.Title)
	assert.Equal(t, int32(1), result.Depth)
	assert.Equal(t, "depends_on", result.LinkType)
	assert.InEpsilon(t, 1.0, result.ImpactScore, 1e-9)

	result2 := buildImpactedItem(item, 2, "implements")
	assert.InEpsilon(t, 0.5, result2.ImpactScore, 1e-9)

	result3 := buildImpactedItem(item, 4, "tests")
	assert.InEpsilon(t, 0.25, result3.ImpactScore, 1e-9)
}

func TestUpdateImpactCounts(t *testing.T) {
	result := &impactAnalysisResult{
		impactedItems: make([]*pb.ImpactedItem, 0),
		itemsByType:   make(map[string]int32),
		itemsByDepth:  make(map[string]int32),
	}

	updateImpactCounts(result, "feature", 1)
	updateImpactCounts(result, "feature", 2)
	updateImpactCounts(result, "bug", 1)

	assert.Equal(t, int32(2), result.itemsByType["feature"])
	assert.Equal(t, int32(1), result.itemsByType["bug"])
	assert.Equal(t, int32(2), result.itemsByDepth["1"])
	assert.Equal(t, int32(1), result.itemsByDepth["2"])
}

func TestEnqueueImpactItem(t *testing.T) {
	visited := map[string]bool{"existing": true}
	queue := make([]impactQueueItem, 0)

	// Add new item
	queue = enqueueImpactItem(queue, visited, "new-item", 1, "depends_on")
	assert.Len(t, queue, 1)
	assert.True(t, visited["new-item"])

	// Try to add already-visited item
	queue = enqueueImpactItem(queue, visited, "existing", 1, "depends_on")
	assert.Len(t, queue, 1) // should not grow

	// Try to add the same new item again
	queue = enqueueImpactItem(queue, visited, "new-item", 2, "implements")
	assert.Len(t, queue, 1) // should not grow
}

func TestInitImpactQueue(t *testing.T) {
	links := []*models.Link{
		{SourceID: "root", TargetID: "a", Type: "depends_on"},
		{SourceID: "b", TargetID: "root", Type: "implements"},
	}
	visited := map[string]bool{"root": true}

	queue := initImpactQueue(links, "root", visited)
	assert.Len(t, queue, 2)
	assert.True(t, visited["a"])
	assert.True(t, visited["b"])
}

func TestStreamGraphUpdates_MissingProjectID(t *testing.T) {
	server := &GraphServiceServer{}
	req := &pb.StreamGraphUpdatesRequest{ProjectId: ""}

	err := server.StreamGraphUpdates(req, nil)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "project_id is required")
}

func TestStreamGraphUpdates_Unimplemented(t *testing.T) {
	server := &GraphServiceServer{}
	req := &pb.StreamGraphUpdatesRequest{ProjectId: "proj-1"}

	err := server.StreamGraphUpdates(req, nil)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "streaming not yet implemented")
}
