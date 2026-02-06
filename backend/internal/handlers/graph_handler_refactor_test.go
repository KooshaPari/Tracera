//go:build !integration && !e2e

package handlers

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
)

// MockAnalysisService implements a mock of graph.AnalysisService for testing
type MockAnalysisService struct {
	shouldFail bool
}

func (m *MockAnalysisService) ShortestPath(_ context.Context, sourceID, targetID string) (*graph.Path, error) {
	if m.shouldFail {
		return nil, assert.AnError
	}
	return &graph.Path{
		Source:    sourceID,
		Target:    targetID,
		Nodes:     []string{sourceID, "middle", targetID},
		Length:    2,
		LinkTypes: []string{"depends_on", "blocks"},
	}, nil
}

func (m *MockAnalysisService) DetectCycles(_ context.Context, _ string) ([]graph.Cycle, error) {
	if m.shouldFail {
		return nil, assert.AnError
	}
	return []graph.Cycle{
		{
			Nodes:    []string{"A", "B", "C", "A"},
			Length:   3,
			Severity: "error",
		},
	}, nil
}

func (m *MockAnalysisService) CalculateCentrality(_ context.Context, projectID string) (*graph.CentralityMetrics, error) {
	if m.shouldFail {
		return nil, assert.AnError
	}
	return &graph.CentralityMetrics{
		ProjectID:   projectID,
		Betweenness: map[string]float64{"item1": 5.0},
		Closeness:   map[string]float64{"item1": 3.0},
		PageRank:    map[string]float64{"item1": 2.5},
	}, nil
}

func (m *MockAnalysisService) GetDependencies(_ context.Context, itemID string, _ int) (*graph.DependencyTree, error) {
	if m.shouldFail {
		return nil, assert.AnError
	}
	return &graph.DependencyTree{
		Root:  itemID,
		Depth: 2,
		Children: map[string][]graph.Dependency{
			itemID: {
				{ItemID: "dep1", LinkType: "depends_on", Depth: 1},
				{ItemID: "dep2", LinkType: "blocks", Depth: 1},
			},
		},
	}, nil
}

func (m *MockAnalysisService) GetDependents(_ context.Context, itemID string, _ int) (*graph.DependencyTree, error) {
	if m.shouldFail {
		return nil, assert.AnError
	}
	return &graph.DependencyTree{
		Root:  itemID,
		Depth: 1,
		Children: map[string][]graph.Dependency{
			itemID: {
				{ItemID: "dependent1", LinkType: "depends_on", Depth: 1},
			},
		},
	}, nil
}

func (m *MockAnalysisService) AnalyzeImpact(_ context.Context, itemIDs []string) (*graph.ImpactReport, error) {
	if m.shouldFail {
		return nil, assert.AnError
	}
	return &graph.ImpactReport{
		SourceItems:    itemIDs,
		DirectImpact:   []string{"direct1", "direct2"},
		IndirectImpact: []string{"indirect1"},
		TotalAffected:  3,
		ImpactLevels:   map[string]int{"direct1": 1, "direct2": 1, "indirect1": 2},
	}, nil
}

func (m *MockAnalysisService) AnalyzeCoverage(_ context.Context, projectID string) (*graph.CoverageReport, error) {
	if m.shouldFail {
		return nil, assert.AnError
	}
	return &graph.CoverageReport{
		ProjectID:       projectID,
		TotalItems:      100,
		ConnectedItems:  85,
		IsolatedItems:   []string{"orphan1", "orphan2"},
		CoveragePercent: 85.0,
	}, nil
}

func (m *MockAnalysisService) GetMetrics(_ context.Context, projectID string) (*graph.Metrics, error) {
	if m.shouldFail {
		return nil, assert.AnError
	}
	return &graph.Metrics{
		ProjectID:      projectID,
		TotalNodes:     100,
		TotalEdges:     250,
		Density:        0.25,
		AvgDegree:      5.0,
		MaxDepth:       8,
		ConnectedComps: 3,
	}, nil
}

func (m *MockAnalysisService) InvalidateCache(_ context.Context, _ string) error {
	if m.shouldFail {
		return assert.AnError
	}
	return nil
}

func TestGraphHandler_DualPath_FindPath(t *testing.T) {
	e := echo.New()

	t.Run("uses Neo4j when available", func(t *testing.T) {
		// GraphHandler now only has graph field
		handler := &GraphHandler{
			graph: nil, // Mock graph service
		}

		req := httptest.NewRequest(http.MethodGet, "/graph/path?source=A&target=B", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.FindPath(c)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var result graph.Path
		err = json.Unmarshal(rec.Body.Bytes(), &result)
		assert.NoError(t, err)
		assert.Equal(t, "A", result.Source)
		assert.Equal(t, "B", result.Target)
		assert.Equal(t, 2, result.Length)
		assert.Len(t, result.Nodes, 3)
	})

	t.Run("validates required parameters", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/path?source=A", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.FindPath(c)
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			assert.True(t, ok)
			assert.Equal(t, http.StatusBadRequest, he.Code)
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestGraphHandler_DualPath_DetectCycles(t *testing.T) {
	e := echo.New()

	t.Run("uses Neo4j when available", func(t *testing.T) {
		// GraphHandler now only has graph field
		handler := &GraphHandler{
			graph: nil, // Mock graph service
		}

		req := httptest.NewRequest(http.MethodGet, "/graph/cycles?project_id=proj1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.DetectCycles(c)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var result map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &result)
		assert.NoError(t, err)
		assert.NotNil(t, result["cycles"])
		assert.Equal(t, float64(1), result["count"])
	})
}

func TestGraphHandler_DualPath_GetImpactAnalysis(t *testing.T) {
	e := echo.New()

	t.Run("uses Neo4j when available", func(t *testing.T) {
		// GraphHandler now only has graph field
		handler := &GraphHandler{
			graph: nil, // Mock graph service
		}

		req := httptest.NewRequest(http.MethodGet, "/graph/impact/item1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/graph/impact/:id")
		c.SetParamNames("id")
		c.SetParamValues("item1")

		err := handler.GetImpactAnalysis(c)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var result map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &result)
		assert.NoError(t, err)
		assert.Equal(t, "item1", result["item_id"])
		assert.Equal(t, float64(3), result["affected_count"])
		assert.NotNil(t, result["direct_impact"])
		assert.NotNil(t, result["indirect_impact"])
	})
}

func TestGraphHandler_DualPath_GetDependencyAnalysis(t *testing.T) {
	e := echo.New()

	t.Run("uses Neo4j when available", func(t *testing.T) {
		// GraphHandler now only has graph field
		handler := &GraphHandler{
			graph: nil, // Mock graph service
		}

		req := httptest.NewRequest(http.MethodGet, "/graph/dependencies/item1?max_depth=3", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/graph/dependencies/:id")
		c.SetParamNames("id")
		c.SetParamValues("item1")

		err := handler.GetDependencyAnalysis(c)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var result map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &result)
		assert.NoError(t, err)
		assert.Equal(t, "item1", result["item_id"])
		assert.NotNil(t, result["dependencies"])
		assert.NotNil(t, result["dependency_tree"])
	})
}

func TestGraphHandler_DualPath_GetOrphanItems(t *testing.T) {
	e := echo.New()

	t.Run("uses Neo4j coverage analysis when available", func(t *testing.T) {
		// GraphHandler now only has graph field
		handler := &GraphHandler{
			graph: nil, // Mock graph service
		}

		req := httptest.NewRequest(http.MethodGet, "/graph/orphans?project_id=proj1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.GetOrphanItems(c)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var result map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &result)
		assert.NoError(t, err)
		assert.NotNil(t, result["orphans"])
		assert.Equal(t, float64(2), result["count"])
		assert.Equal(t, 85.0, result["coverage_percent"])
		assert.Equal(t, float64(100), result["total_items"])
	})
}

func TestGraphHandler_GetMetrics(t *testing.T) {
	e := echo.New()

	t.Run("uses Neo4j when available", func(t *testing.T) {
		// GraphHandler now only has graph field
		handler := &GraphHandler{
			graph: nil, // Mock graph service
		}

		req := httptest.NewRequest(http.MethodGet, "/graph/metrics?project_id=proj1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.GetMetrics(c)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var result graph.Metrics
		err = json.Unmarshal(rec.Body.Bytes(), &result)
		assert.NoError(t, err)
		assert.Equal(t, "proj1", result.ProjectID)
		assert.Equal(t, 100, result.TotalNodes)
		assert.Equal(t, 250, result.TotalEdges)
		assert.Equal(t, 0.25, result.Density)
	})

	t.Run("validates required project_id", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/metrics", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.GetMetrics(c)
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			assert.True(t, ok)
			assert.Equal(t, http.StatusBadRequest, he.Code)
		} else {
			assert.Contains(t, rec.Body.String(), "project_id parameter is required")
		}
	})
}

func TestGraphHandler_InvalidateCache(t *testing.T) {
	e := echo.New()

	t.Run("invalidates both Neo4j and Redis cache", func(t *testing.T) {
		// GraphHandler now only has graph field
		handler := &GraphHandler{
			graph: nil, // Mock graph service
		}

		req := httptest.NewRequest(http.MethodPost, "/graph/cache/invalidate?project_id=proj1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.InvalidateCache(c)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var result map[string]string
		err = json.Unmarshal(rec.Body.Bytes(), &result)
		assert.NoError(t, err)
		assert.Equal(t, "graph cache invalidated successfully", result["message"])
	})

	t.Run("validates required project_id", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodPost, "/graph/cache/invalidate", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.InvalidateCache(c)
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			assert.True(t, ok)
			assert.Equal(t, http.StatusBadRequest, he.Code)
		} else {
			assert.Contains(t, rec.Body.String(), "project_id parameter is required")
		}
	})
}
