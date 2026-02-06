//go:build unit

package search

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestBuildSearchQuery_Empty(t *testing.T) {
	assert.Empty(t, BuildSearchQuery(""))
	assert.Empty(t, BuildSearchQuery("   "))
}

func TestBuildSearchQuery_SingleWord(t *testing.T) {
	q := BuildSearchQuery("auth")
	assert.Equal(t, "auth", q)
}

func TestBuildSearchQuery_MultipleWords(t *testing.T) {
	q := BuildSearchQuery("user authentication")
	assert.Equal(t, "user & authentication", q)
}

func TestBuildSearchQuery_Trimmed(t *testing.T) {
	q := BuildSearchQuery("  login flow  ")
	assert.Equal(t, "login & flow", q)
}

func TestBuildSearchQuery_ManyWords(t *testing.T) {
	q := BuildSearchQuery("a b c d e")
	assert.Equal(t, "a & b & c & d & e", q)
}

func TestVectorToString_Empty(t *testing.T) {
	assert.Equal(t, "[]", vectorToString(nil))
	assert.Equal(t, "[]", vectorToString([]float32{}))
}

func TestVectorToString_Single(t *testing.T) {
	out := vectorToString([]float32{0.1})
	assert.Equal(t, "[0.100000]", out)
}

func TestVectorToString_Multiple(t *testing.T) {
	out := vectorToString([]float32{0.1, -0.2, 0.5})
	assert.Equal(t, "[0.100000,-0.200000,0.500000]", out)
}

func TestMapFullTextResults_Empty(t *testing.T) {
	out := mapFullTextResults(nil, 0.1)
	assert.NotNil(t, out)
	assert.Empty(t, out)
}

func TestMapFullTextResults_FiltersByMinScore(t *testing.T) {
	rows := []fullTextRow{
		{ID: "1", Score: 0.9, Title: "a", ProjectID: "p", Type: "t", Status: "s", Priority: "1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "2", Score: 0.3, Title: "b", ProjectID: "p", Type: "t", Status: "s", Priority: "1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "3", Score: 0.5, Title: "c", ProjectID: "p", Type: "t", Status: "s", Priority: "1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
	}
	out := mapFullTextResults(rows, 0.5)
	require.Len(t, out, 2)
	assert.Equal(t, "1", out[0].ID)
	assert.Equal(t, "3", out[1].ID)
	assert.Equal(t, 0.9, out[0].Score)
	assert.Equal(t, 0.5, out[1].Score)
}

func TestMapFullTextResults_AllPass(t *testing.T) {
	now := time.Now()
	rows := []fullTextRow{
		{ID: "a", Score: 0.8, Title: "x", ProjectID: "p", Type: "t", Status: "s", Priority: "1", CreatedAt: now, UpdatedAt: now},
	}
	out := mapFullTextResults(rows, 0.1)
	require.Len(t, out, 1)
	assert.Equal(t, "a", out[0].ID)
	assert.Equal(t, "x", out[0].Title)
	assert.Equal(t, 0.8, out[0].Score)
}

func TestBuildFullTextParams_EmptyProject(t *testing.T) {
	req := &Request{ProjectID: ""}
	p1, p2, p3 := buildFullTextParams(req)
	assert.Equal(t, "", p1)
	assert.Nil(t, p2)
	assert.Nil(t, p3)
}

func TestBuildFullTextParams_WithProject(t *testing.T) {
	req := &Request{ProjectID: "proj-123"}
	p1, p2, p3 := buildFullTextParams(req)
	assert.Equal(t, "proj-123", p1)
	assert.Nil(t, p2)
	assert.Nil(t, p3)
}

func TestBuildFullTextParams_WithItemTypes(t *testing.T) {
	req := &Request{ProjectID: "p", ItemTypes: []string{"task", "epic"}}
	p1, p2, p3 := buildFullTextParams(req)
	assert.Equal(t, "p", p1)
	assert.Equal(t, []string{"task", "epic"}, p2)
	assert.Nil(t, p3)
}

func TestBuildFullTextParams_WithStatus(t *testing.T) {
	req := &Request{ProjectID: "p", Status: []string{"done"}}
	p1, p2, p3 := buildFullTextParams(req)
	assert.Equal(t, "p", p1)
	assert.Nil(t, p2)
	assert.Equal(t, []string{"done"}, p3)
}

func TestMergeResults_Empty(t *testing.T) {
	e := &Engine{}
	out := e.mergeResults(nil, nil, 0.6, 0.4)
	assert.NotNil(t, out)
	assert.Empty(t, out)
}

func TestMergeResults_FullTextOnly(t *testing.T) {
	e := &Engine{}
	ft := []Result{
		{ID: "1", Score: 1.0},
		{ID: "2", Score: 0.8},
	}
	out := e.mergeResults(ft, nil, 0.6, 0.4)
	require.Len(t, out, 2)
	assert.InDelta(t, 0.6, out[0].Score, 0.001)
	assert.InDelta(t, 0.48, out[1].Score, 0.001)
}

func TestMergeResults_VectorOnly(t *testing.T) {
	e := &Engine{}
	vec := []Result{
		{ID: "1", Score: 0.9},
	}
	out := e.mergeResults(nil, vec, 0.6, 0.4)
	require.Len(t, out, 1)
	assert.InDelta(t, 0.36, out[0].Score, 0.001)
}

func TestMergeResults_Dedupe(t *testing.T) {
	e := &Engine{}
	ft := []Result{{ID: "1", Score: 1.0}}
	vec := []Result{{ID: "1", Score: 0.8}}
	out := e.mergeResults(ft, vec, 0.6, 0.4)
	require.Len(t, out, 1)
	assert.InDelta(t, 0.6+0.32, out[0].Score, 0.001)
}

func TestMergeResults_Mixed(t *testing.T) {
	e := &Engine{}
	ft := []Result{{ID: "1", Score: 1.0}, {ID: "2", Score: 0.5}}
	vec := []Result{{ID: "2", Score: 0.5}, {ID: "3", Score: 0.9}}
	out := e.mergeResults(ft, vec, 0.6, 0.4)
	require.Len(t, out, 3)
}

func TestNewSearchEngine(t *testing.T) {
	e := NewSearchEngine(nil)
	require.NotNil(t, e)
	assert.Nil(t, e.pool)
	assert.False(t, e.rerankEnabled)
}

func TestNewSearchEngineWithConfig_NilReranker(t *testing.T) {
	cfg := &EngineConfig{Pool: nil, Reranker: nil, RerankEnabled: true}
	e := NewSearchEngineWithConfig(cfg)
	require.NotNil(t, e)
	assert.False(t, e.rerankEnabled)
}

func TestNewSearchEngineWithConfig_WithReranker(t *testing.T) {
	cfg := &EngineConfig{Pool: nil, Reranker: &struct{}{}, RerankEnabled: true}
	e := NewSearchEngineWithConfig(cfg)
	require.NotNil(t, e)
	assert.True(t, e.rerankEnabled)
}

func TestNewEngine(t *testing.T) {
	e := NewEngine(nil)
	require.NotNil(t, e)
}

func TestNewEngineWithConfig(t *testing.T) {
	e := NewEngineWithConfig(&EngineConfig{})
	require.NotNil(t, e)
}

func TestSearchTypes(t *testing.T) {
	assert.Equal(t, Type("fulltext"), TypeFullText)
	assert.Equal(t, Type("vector"), TypeVector)
	assert.Equal(t, Type("hybrid"), TypeHybrid)
	assert.Equal(t, Type("fuzzy"), TypeFuzzy)
	assert.Equal(t, Type("phonetic"), TypePhonetic)
	assert.Equal(t, TypeFullText, SearchTypeFullText)
	assert.Equal(t, TypeVector, SearchTypeVector)
}

func TestApplyCrossSearchDefaults(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{Limit: 0, MinScore: 0, FuzzyThreshold: 0}
	applyCrossSearchDefaults(req)
	assert.Equal(t, crossSearchDefaultLimit, req.Limit)
	assert.Equal(t, crossSearchDefaultMinScore, req.MinScore)
	assert.Equal(t, crossSearchDefaultFuzzyThreshold, req.FuzzyThreshold)
}

func TestApplyCrossSearchDefaults_CapLimit(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{Limit: 200}
	applyCrossSearchDefaults(req)
	assert.Equal(t, crossSearchMaxLimit, req.Limit)
}

func TestResolvePerspectives_Empty(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{Perspectives: nil}
	out := resolvePerspectives(req)
	require.NotEmpty(t, out)
	assert.Contains(t, out, "feature")
	assert.Contains(t, out, "api")
}

func TestResolvePerspectives_Explicit(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{Perspectives: []string{"a", "b"}}
	out := resolvePerspectives(req)
	assert.Equal(t, []string{"a", "b"}, out)
}

func TestNewCrossPerspectiveResponse(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{Query: "q", ProjectID: "p"}
	out := newCrossPerspectiveResponse(req)
	require.NotNil(t, out)
	assert.Equal(t, "q", out.Query)
	assert.Equal(t, "p", out.ProjectID)
	assert.NotEmpty(t, out.ExecutedAt)
	assert.Empty(t, out.PerspectiveGroups)
}

func TestGetCurrentTimestamp(t *testing.T) {
	s := getCurrentTimestamp()
	assert.NotEmpty(t, s)
	assert.Len(t, s, 20)
	assert.Contains(t, s, "T")
}

func TestTriggerReindex(t *testing.T) {
	cs := &CrossPerspectiveSearcher{}
	err := cs.TriggerReindex(nil, "")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not yet implemented")
}

func TestBuildFuzzySearchParams_EmptyProject(t *testing.T) {
	req := &Request{ProjectID: ""}
	proj, types, status := buildFuzzySearchParams(req)
	assert.Nil(t, proj)
	assert.Nil(t, types)
	assert.Nil(t, status)
}

func TestBuildFuzzySearchParams_WithProject(t *testing.T) {
	req := &Request{ProjectID: "p1"}
	proj, types, status := buildFuzzySearchParams(req)
	assert.Equal(t, "p1", proj)
	assert.Nil(t, types)
	assert.Nil(t, status)
}

func TestBuildFuzzySearchParams_WithFilters(t *testing.T) {
	req := &Request{ProjectID: "p", ItemTypes: []string{"task"}, Status: []string{"done"}}
	proj, types, status := buildFuzzySearchParams(req)
	assert.Equal(t, "p", proj)
	assert.Equal(t, []string{"task"}, types)
	assert.Equal(t, []string{"done"}, status)
}
