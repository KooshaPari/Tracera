//go:build integration
// +build integration

package handlers

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/testutil"
)

const graphStreamBenchmarkTimeout = 5 * time.Second

func TestStreamGraphIncremental(t *testing.T) {
	// Setup test infrastructure
	testInfra := testutil.SetupTestInfrastructure(t)
	defer testInfra.Cleanup()

	handler := NewGraphStreamHandler(testInfra.DB, testInfra.Pool)

	// Create test project
	project := &models.Project{
		ID:          "test-project",
		Name:        "Test Project",
		Description: "Test",
	}
	require.NoError(t, testInfra.DB.Create(project).Error)

	// Create test items with positions
	items := []models.Item{
		{
			ID:        "item-1",
			ProjectID: project.ID,
			Type:      "requirement",
			Title:     "Item 1",
			Status:    "active",
			PositionX: floatPtr(100),
			PositionY: floatPtr(100),
		},
		{
			ID:        "item-2",
			ProjectID: project.ID,
			Type:      "requirement",
			Title:     "Item 2",
			Status:    "active",
			PositionX: floatPtr(200),
			PositionY: floatPtr(200),
		},
		{
			ID:        "item-3",
			ProjectID: project.ID,
			Type:      "requirement",
			Title:     "Item 3",
			Status:    "active",
			PositionX: floatPtr(300),
			PositionY: floatPtr(300),
		},
	}

	for _, item := range items {
		require.NoError(t, testInfra.DB.Create(&item).Error)
	}

	// Create test links
	link := &models.Link{
		ID:       "link-1",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "relates_to",
	}
	require.NoError(t, testInfra.DB.Create(link).Error)

	// Test streaming endpoint
	t.Run("streams graph data in NDJSON format", func(t *testing.T) {
		e := echo.New()
		req := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(`{
			"viewport": {
				"minX": 0,
				"minY": 0,
				"maxX": 400,
				"maxY": 400
			},
			"zoom": 1.0,
			"bufferPx": 500
		}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)

		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/projects/:project_id/graph/stream")
		c.SetParamNames("project_id")
		c.SetParamValues(project.ID)

		err := handler.StreamGraphIncremental(c)
		require.NoError(t, err)

		// Verify response
		assert.Equal(t, http.StatusOK, rec.Code)
		assert.Equal(t, "application/x-ndjson", rec.Header().Get("Content-Type"))

		// Parse NDJSON response
		chunks := parseNDJSONResponse(t, rec.Body.Bytes())

		// Verify chunks
		assert.NotEmpty(t, chunks, "should have chunks")

		// Check for metadata chunk
		var hasMetadata bool
		var hasNodes bool
		var hasEdges bool
		var hasComplete bool

		nodeCount := 0
		edgeCount := 0

		for _, chunk := range chunks {
			switch chunk.Type {
			case "metadata":
				hasMetadata = true
				metadata := chunk.Data.(map[string]interface{})
				assert.Equal(t, project.ID, metadata["projectId"])
				assert.Greater(t, metadata["totalNodes"], float64(0))
			case "node":
				hasNodes = true
				nodeCount++
			case "edge":
				hasEdges = true
				edgeCount++
			case "complete":
				hasComplete = true
			}
		}

		assert.True(t, hasMetadata, "should have metadata chunk")
		assert.True(t, hasNodes, "should have node chunks")
		assert.True(t, hasEdges, "should have edge chunks")
		assert.True(t, hasComplete, "should have complete chunk")

		assert.Equal(t, 3, nodeCount, "should have 3 nodes")
		assert.Equal(t, 1, edgeCount, "should have 1 edge")
	})

	t.Run("respects viewport bounds", func(t *testing.T) {
		e := echo.New()
		req := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(`{
			"viewport": {
				"minX": 0,
				"minY": 0,
				"maxX": 150,
				"maxY": 150
			},
			"zoom": 1.0,
			"bufferPx": 0
		}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)

		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/projects/:project_id/graph/stream")
		c.SetParamNames("project_id")
		c.SetParamValues(project.ID)

		err := handler.StreamGraphIncremental(c)
		require.NoError(t, err)

		chunks := parseNDJSONResponse(t, rec.Body.Bytes())

		// Count nodes (should only have item-1 at 100,100)
		nodeCount := 0
		for _, chunk := range chunks {
			if chunk.Type == "node" {
				nodeCount++
			}
		}

		assert.Equal(t, 1, nodeCount, "should only have nodes within viewport")
	})

	t.Run("includes progress updates", func(t *testing.T) {
		e := echo.New()
		req := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(`{
			"viewport": {
				"minX": 0,
				"minY": 0,
				"maxX": 400,
				"maxY": 400
			},
			"zoom": 1.0
		}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)

		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/projects/:project_id/graph/stream")
		c.SetParamNames("project_id")
		c.SetParamValues(project.ID)

		err := handler.StreamGraphIncremental(c)
		require.NoError(t, err)

		chunks := parseNDJSONResponse(t, rec.Body.Bytes())

		// Check for progress info in chunks
		hasProgress := false
		for _, chunk := range chunks {
			if chunk.Progress != nil {
				hasProgress = true
				assert.GreaterOrEqual(t, chunk.Progress.Current, 0)
				assert.Greater(t, chunk.Progress.Total, 0)
				assert.GreaterOrEqual(t, chunk.Progress.Percentage, float64(0))
				assert.LessOrEqual(t, chunk.Progress.Percentage, float64(100))
			}
		}

		assert.True(t, hasProgress, "should have progress updates")
	})
}

func TestStreamGraphPrefetch(t *testing.T) {
	testInfra := testutil.SetupTestInfrastructure(t)
	defer testInfra.Cleanup()

	handler := NewGraphStreamHandler(testInfra.DB, testInfra.Pool)

	// Create test data
	project := &models.Project{
		ID:   "test-project",
		Name: "Test Project",
	}
	require.NoError(t, testInfra.DB.Create(project).Error)

	// Create items in different regions
	items := []models.Item{
		{
			ID:        "north-item",
			ProjectID: project.ID,
			Type:      "requirement",
			Title:     "North Item",
			PositionX: floatPtr(500),
			PositionY: floatPtr(-500), // North of current viewport
		},
		{
			ID:        "south-item",
			ProjectID: project.ID,
			Type:      "requirement",
			Title:     "South Item",
			PositionX: floatPtr(500),
			PositionY: floatPtr(1500), // South of current viewport
		},
	}

	for _, item := range items {
		require.NoError(t, testInfra.DB.Create(&item).Error)
	}

	t.Run("prefetches data in specified direction", func(t *testing.T) {
		e := echo.New()
		req := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(`{
			"currentViewport": {
				"minX": 0,
				"minY": 0,
				"maxX": 1000,
				"maxY": 1000
			},
			"direction": "north",
			"velocity": 0
		}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)

		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/projects/:project_id/graph/stream/prefetch")
		c.SetParamNames("project_id")
		c.SetParamValues(project.ID)

		err := handler.StreamGraphPrefetch(c)
		require.NoError(t, err)

		chunks := parseNDJSONResponse(t, rec.Body.Bytes())

		// Should find north item
		foundNorth := false
		for _, chunk := range chunks {
			if chunk.Type == "node" {
				nodeData := chunk.Data.(map[string]interface{})
				if nodeData["id"] == "north-item" {
					foundNorth = true
				}
			}
		}

		assert.True(t, foundNorth, "should prefetch north item")
	})
}

func TestGetStreamStats(t *testing.T) {
	testInfra := testutil.SetupTestInfrastructure(t)
	defer testInfra.Cleanup()

	handler := NewGraphStreamHandler(testInfra.DB, testInfra.Pool)

	// Create test project with items
	project := &models.Project{
		ID:   "test-project",
		Name: "Test Project",
	}
	require.NoError(t, testInfra.DB.Create(project).Error)

	for i := 0; i < 10; i++ {
		item := &models.Item{
			ID:        fmt.Sprintf("item-%d", i),
			ProjectID: project.ID,
			Type:      "requirement",
			Title:     fmt.Sprintf("Item %d", i),
		}
		require.NoError(t, testInfra.DB.Create(item).Error)
	}

	t.Run("returns stream statistics", func(t *testing.T) {
		e := echo.New()
		req := httptest.NewRequest(http.MethodGet, "/", nil)

		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/projects/:project_id/graph/stream/stats")
		c.SetParamNames("project_id")
		c.SetParamValues(project.ID)

		err := handler.GetStreamStats(c)
		require.NoError(t, err)

		assert.Equal(t, http.StatusOK, rec.Code)

		var stats map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &stats)
		require.NoError(t, err)

		assert.Equal(t, project.ID, stats["projectId"])
		assert.Equal(t, float64(10), stats["totalNodes"])
		assert.NotZero(t, stats["estimatedBytes"])
		assert.NotZero(t, stats["estimatedTimeMs"])
		assert.NotZero(t, stats["recommendedChunkSize"])
	})
}

func TestCalculatePrefetchViewport(t *testing.T) {
	handler := &GraphStreamHandler{}

	current := ViewportBounds{
		MinX: 0,
		MinY: 0,
		MaxX: 1000,
		MaxY: 1000,
	}

	tests := []struct {
		name      string
		direction string
		velocity  float64
		expected  ViewportBounds
	}{
		{
			name:      "north",
			direction: "north",
			velocity:  0,
			expected: ViewportBounds{
				MinX: 0,
				MinY: -1000,
				MaxX: 1000,
				MaxY: 0,
			},
		},
		{
			name:      "south",
			direction: "south",
			velocity:  0,
			expected: ViewportBounds{
				MinX: 0,
				MinY: 1000,
				MaxX: 1000,
				MaxY: 2000,
			},
		},
		{
			name:      "east",
			direction: "east",
			velocity:  0,
			expected: ViewportBounds{
				MinX: 1000,
				MinY: 0,
				MaxX: 2000,
				MaxY: 1000,
			},
		},
		{
			name:      "west",
			direction: "west",
			velocity:  0,
			expected: ViewportBounds{
				MinX: -1000,
				MinY: 0,
				MaxX: 0,
				MaxY: 1000,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := handler.calculatePrefetchViewport(current, tt.direction, tt.velocity)
			assert.Equal(t, tt.expected.MinX, result.MinX)
			assert.Equal(t, tt.expected.MinY, result.MinY)
			assert.Equal(t, tt.expected.MaxX, result.MaxX)
			assert.Equal(t, tt.expected.MaxY, result.MaxY)
		})
	}
}

func TestStreamChunkFormat(t *testing.T) {
	handler := &GraphStreamHandler{}

	t.Run("sends chunk with correct format", func(t *testing.T) {
		e := echo.New()
		req := httptest.NewRequest(http.MethodPost, "/", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		chunk := StreamChunk{
			Type: "node",
			Data: NodeData{
				ID:    "test-node",
				Type:  "requirement",
				Label: "Test",
				Position: Position{
					X: 100,
					Y: 200,
				},
			},
			Timestamp: time.Now().UnixMilli(),
		}

		err := handler.sendChunk(c, chunk)
		require.NoError(t, err)

		// Verify JSON format
		var parsed StreamChunk
		lines := strings.Split(strings.TrimSpace(rec.Body.String()), "\n")
		require.Len(t, lines, 1)

		err = json.Unmarshal([]byte(lines[0]), &parsed)
		require.NoError(t, err)

		assert.Equal(t, chunk.Type, parsed.Type)
		assert.NotZero(t, parsed.Timestamp)
	})
}

// Helper functions

func parseNDJSONResponse(t *testing.T, body []byte) []StreamChunk {
	var chunks []StreamChunk

	scanner := bufio.NewScanner(bytes.NewReader(body))
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}

		var chunk StreamChunk
		err := json.Unmarshal([]byte(line), &chunk)
		require.NoError(t, err, "failed to parse chunk: %s", line)

		chunks = append(chunks, chunk)
	}

	require.NoError(t, scanner.Err())
	return chunks
}

func floatPtr(f float64) *float64 {
	return &f
}

// Benchmark tests

func BenchmarkStreamGraphIncremental(b *testing.B) {
	testInfra := testutil.SetupTestInfrastructureBenchmark(b)
	defer testInfra.Cleanup()

	handler := NewGraphStreamHandler(testInfra.DB, testInfra.Pool)

	// Create test project with many items
	project := &models.Project{
		ID:   "bench-project",
		Name: "Benchmark Project",
	}
	testInfra.DB.Create(project)

	// Create 1000 items
	for i := 0; i < 1000; i++ {
		item := &models.Item{
			ID:        fmt.Sprintf("item-%d", i),
			ProjectID: project.ID,
			Type:      "requirement",
			Title:     fmt.Sprintf("Item %d", i),
			PositionX: floatPtr(float64(i % 100 * 10)),
			PositionY: floatPtr(float64(i / 100 * 10)),
		}
		testInfra.DB.Create(item)
	}

	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		e := echo.New()
		req := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(`{
			"viewport": {"minX": 0, "minY": 0, "maxX": 1000, "maxY": 1000},
			"zoom": 1.0
		}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)

		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/projects/:project_id/graph/stream")
		c.SetParamNames("project_id")
		c.SetParamValues(project.ID)

		// Add context with timeout
		ctx, cancel := context.WithTimeout(context.Background(), graphStreamBenchmarkTimeout)
		req = req.WithContext(ctx)
		c.SetRequest(req)

		handler.StreamGraphIncremental(c)
		cancel()
	}
}
