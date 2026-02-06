//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestE2E_ComplexGraph_ImpactAnalysis tests impact analysis on complex graph
func TestE2E_ComplexGraph_ImpactAnalysis(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "impact.user@test.com")

	// Create diamond dependency pattern:
	//     A
	//    / \
	//   B   C
	//    \ /
	//     D
	//     |
	//     E

	itemNames := []string{"A", "B", "C", "D", "E"}
	itemIDs := make(map[string]string)

	for _, name := range itemNames {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      "Impact Item " + name,
			"type":       "task",
			"metadata": map[string]interface{}{
				"priority": 3,
			},
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var itemResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&itemResp)
		resp.Body.Close()
		itemIDs[name] = itemResp.ID
	}

	// Create dependency links
	dependencies := []struct {
		source string
		target string
	}{
		{"A", "B"},
		{"A", "C"},
		{"B", "D"},
		{"C", "D"},
		{"D", "E"},
	}

	for _, dep := range dependencies {
		linkReq := map[string]interface{}{
			"source_id": itemIDs[dep.source],
			"target_id": itemIDs[dep.target],
			"type":      "blocks",
		}
		linkBody, _ := json.Marshal(linkReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		resp.Body.Close()
	}

	// Analyze impact of changing item A (should affect all downstream)
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemIDs["A"]+"/impact", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)

	var impactResp struct {
		DirectImpact   []string `json:"direct_impact"`
		IndirectImpact []string `json:"indirect_impact"`
		TotalAffected  int      `json:"total_affected"`
	}
	json.NewDecoder(resp.Body).Decode(&impactResp)
	resp.Body.Close()

	// A should affect B and C directly
	assert.Equal(t, 2, len(impactResp.DirectImpact))
	assert.Contains(t, impactResp.DirectImpact, itemIDs["B"])
	assert.Contains(t, impactResp.DirectImpact, itemIDs["C"])

	// Total affected should include D and E
	assert.Equal(t, 4, impactResp.TotalAffected)

	// Analyze impact of changing item D (should only affect E)
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemIDs["D"]+"/impact", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err = client.Do(req)
	require.NoError(t, err)

	var dImpactResp struct {
		DirectImpact  []string `json:"direct_impact"`
		TotalAffected int      `json:"total_affected"`
	}
	json.NewDecoder(resp.Body).Decode(&dImpactResp)
	resp.Body.Close()

	assert.Equal(t, 1, len(dImpactResp.DirectImpact))
	assert.Contains(t, dImpactResp.DirectImpact, itemIDs["E"])
}

// TestE2E_ComplexGraph_DependencyAnalysis tests dependency analysis
func TestE2E_ComplexGraph_DependencyAnalysis(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "dependency.user@test.com")

	// Create multi-level dependency tree
	//   Level 0: [A]
	//   Level 1: [B, C, D]
	//   Level 2: [E, F]
	//   Level 3: [G]

	itemNames := []string{"A", "B", "C", "D", "E", "F", "G"}
	itemIDs := make(map[string]string)

	for _, name := range itemNames {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      "Dep Item " + name,
			"type":       "task",
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var itemResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&itemResp)
		resp.Body.Close()
		itemIDs[name] = itemResp.ID
	}

	// Create dependencies
	dependencies := []struct {
		source string
		target string
	}{
		{"B", "A"},
		{"C", "A"},
		{"D", "A"},
		{"E", "B"},
		{"E", "C"},
		{"F", "D"},
		{"G", "E"},
		{"G", "F"},
	}

	for _, dep := range dependencies {
		linkReq := map[string]interface{}{
			"source_id": itemIDs[dep.source],
			"target_id": itemIDs[dep.target],
			"type":      "depends_on",
		}
		linkBody, _ := json.Marshal(linkReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		resp.Body.Close()
	}

	// Analyze dependencies of item G (leaf node)
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemIDs["G"]+"/dependencies?all=true", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)

	var depsResp struct {
		DirectDependencies []string `json:"direct_dependencies"`
		AllDependencies    []string `json:"all_dependencies"`
		DependencyLevels   int      `json:"dependency_levels"`
	}
	json.NewDecoder(resp.Body).Decode(&depsResp)
	resp.Body.Close()

	// G directly depends on E and F
	assert.Equal(t, 2, len(depsResp.DirectDependencies))

	// G transitively depends on all items
	assert.Equal(t, 6, len(depsResp.AllDependencies))

	// Should have 3 levels: E/F -> B/C/D -> A
	assert.Equal(t, 3, depsResp.DependencyLevels)
}

// TestE2E_ComplexGraph_CriticalPath tests critical path calculation
func TestE2E_ComplexGraph_CriticalPath(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "critical.user@test.com")

	// Create project with estimated durations
	itemData := []struct {
		name     string
		duration int
	}{
		{"Start", 0},
		{"Task1", 5},
		{"Task2", 3},
		{"Task3", 8},
		{"Task4", 2},
		{"End", 0},
	}

	itemIDs := make(map[string]string)

	for _, data := range itemData {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      data.name,
			"type":       "task",
			"metadata": map[string]interface{}{
				"estimated_hours": data.duration,
			},
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var itemResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&itemResp)
		resp.Body.Close()
		itemIDs[data.name] = itemResp.ID
	}

	// Create dependencies forming two paths:
	// Path 1: Start -> Task1 -> Task3 -> End (5 + 8 = 13 hours)
	// Path 2: Start -> Task2 -> Task4 -> End (3 + 2 = 5 hours)
	dependencies := []struct {
		source string
		target string
	}{
		{"Start", "Task1"},
		{"Start", "Task2"},
		{"Task1", "Task3"},
		{"Task2", "Task4"},
		{"Task3", "End"},
		{"Task4", "End"},
	}

	for _, dep := range dependencies {
		linkReq := map[string]interface{}{
			"source_id": itemIDs[dep.source],
			"target_id": itemIDs[dep.target],
			"type":      "precedes",
		}
		linkBody, _ := json.Marshal(linkReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		resp.Body.Close()
	}

	// Calculate critical path
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID+"/critical-path", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)

	var pathResp struct {
		CriticalPath   []string `json:"critical_path"`
		TotalDuration  int      `json:"total_duration"`
		AlternatePaths int      `json:"alternate_paths"`
	}
	json.NewDecoder(resp.Body).Decode(&pathResp)
	resp.Body.Close()

	// Critical path should be the longer path
	assert.Equal(t, 13, pathResp.TotalDuration)
	assert.Contains(t, pathResp.CriticalPath, itemIDs["Task1"])
	assert.Contains(t, pathResp.CriticalPath, itemIDs["Task3"])
	assert.NotContains(t, pathResp.CriticalPath, itemIDs["Task2"])
	assert.NotContains(t, pathResp.CriticalPath, itemIDs["Task4"])
}

// TestE2E_LargeGraph_Performance tests performance with large graph
func TestE2E_LargeGraph_Performance(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance test in short mode")
	}

	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 120 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "perf.user@test.com")

	// Create large graph: 200 items with complex interconnections
	itemCount := 200
	itemIDs := make([]string, itemCount)

	t.Log("Creating 200 items...")
	createStart := time.Now()

	for i := 0; i < itemCount; i++ {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      fmt.Sprintf("Perf Item %d", i),
			"type":       "task",
			"metadata": map[string]interface{}{
				"index": i,
			},
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var itemResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&itemResp)
		resp.Body.Close()
		itemIDs[i] = itemResp.ID
	}

	createDuration := time.Since(createStart)
	t.Logf("Created 200 items in %v", createDuration)

	// Create interconnections
	t.Log("Creating 400 links...")
	linkStart := time.Now()

	links := make([]map[string]interface{}, 0)
	for i := 0; i < itemCount-1; i++ {
		// Each item links to next item
		links = append(links, map[string]interface{}{
			"source_id": itemIDs[i],
			"target_id": itemIDs[i+1],
			"type":      "next",
		})

		// Every 10th item also links to item 10 ahead
		if i < itemCount-10 && i%10 == 0 {
			links = append(links, map[string]interface{}{
				"source_id": itemIDs[i],
				"target_id": itemIDs[i+10],
				"type":      "skip",
			})
		}
	}

	bulkReq := map[string]interface{}{
		"links": links,
	}
	bulkBody, _ := json.Marshal(bulkReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links/bulk", bytes.NewBuffer(bulkBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	linkDuration := time.Since(linkStart)
	t.Logf("Created links in %v", linkDuration)

	// Test graph traversal performance
	t.Log("Testing graph traversal...")
	traversalStart := time.Now()

	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemIDs[0]+"/graph?depth=50", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err = client.Do(req)
	require.NoError(t, err)

	var graphResp struct {
		Nodes []struct {
			ID string `json:"id"`
		} `json:"nodes"`
		Edges []struct {
			SourceID string `json:"source_id"`
		} `json:"edges"`
	}
	json.NewDecoder(resp.Body).Decode(&graphResp)
	resp.Body.Close()

	traversalDuration := time.Since(traversalStart)
	t.Logf("Graph traversal completed in %v", traversalDuration)
	t.Logf("Retrieved %d nodes and %d edges", len(graphResp.Nodes), len(graphResp.Edges))

	// Performance assertions
	assert.Less(t, createDuration, 60*time.Second, "Item creation too slow")
	assert.Less(t, linkDuration, 30*time.Second, "Link creation too slow")
	assert.Less(t, traversalDuration, 5*time.Second, "Graph traversal too slow")

	// Test search performance
	t.Log("Testing search performance...")
	searchStart := time.Now()

	searchReq := map[string]interface{}{
		"query":      "Perf Item",
		"project_id": projectID,
		"limit":      50,
	}
	searchBody, _ := json.Marshal(searchReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	var searchResp struct {
		Results []struct {
			ID string `json:"id"`
		} `json:"results"`
	}
	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	searchDuration := time.Since(searchStart)
	t.Logf("Search completed in %v, found %d results", searchDuration, len(searchResp.Results))

	assert.Less(t, searchDuration, 2*time.Second, "Search too slow")
	assert.GreaterOrEqual(t, len(searchResp.Results), 50)
}
