//go:build !integration && !e2e

package graph

import (
	"context"
	"testing"
)

type testContextKey string

const otherContextKey testContextKey = "other-key"

// TestWithProjectContext tests adding project context to context
func TestWithProjectContext(t *testing.T) {
	ctx := context.Background()
	projectCtx := NewProjectContext("test-project", "workspace-123")

	newCtx := WithProjectContext(ctx, projectCtx)

	if newCtx == ctx {
		t.Error("expected new context to be different from original")
	}
}

// TestGetProjectContext tests retrieving project context
func TestGetProjectContext(t *testing.T) {
	ctx := context.Background()
	projectCtx := NewProjectContext("test-project", "workspace-123")

	newCtx := WithProjectContext(ctx, projectCtx)
	retrieved := GetProjectContext(newCtx)

	if retrieved == nil {
		t.Fatal("expected GetProjectContext to return non-nil value")
	}
	if retrieved.ProjectID != projectCtx.ProjectID {
		t.Errorf("expected ProjectID %s, got %s", projectCtx.ProjectID, retrieved.ProjectID)
	}
	if retrieved.WorkspaceID != projectCtx.WorkspaceID {
		t.Errorf("expected WorkspaceID %s, got %s", projectCtx.WorkspaceID, retrieved.WorkspaceID)
	}
	if retrieved.Namespace != projectCtx.Namespace {
		t.Errorf("expected Namespace %s, got %s", projectCtx.Namespace, retrieved.Namespace)
	}
}

// TestGetProjectContextNilOnMissingContext tests GetProjectContext returns nil when context is missing
func TestGetProjectContextNilOnMissingContext(t *testing.T) {
	ctx := context.Background()
	retrieved := GetProjectContext(ctx)

	if retrieved != nil {
		t.Errorf("expected GetProjectContext to return nil when context is missing, got %v", retrieved)
	}
}

// TestGetProjectContextWithNonProjectContextValue tests type assertion failure
func TestGetProjectContextWithNonProjectContextValue(t *testing.T) {
	ctx := context.Background()
	ctx = context.WithValue(ctx, ProjectContextKeyValue, "not-a-project-context")

	retrieved := GetProjectContext(ctx)
	if retrieved != nil {
		t.Error("expected GetProjectContext to return nil for non-ProjectContext value")
	}
}

// TestGetProjectID tests retrieving project ID from context
func TestGetProjectID(t *testing.T) {
	ctx := context.Background()
	expectedProjectID := "test-project-123"
	projectCtx := NewProjectContext(expectedProjectID, "workspace-456")

	newCtx := WithProjectContext(ctx, projectCtx)
	projectID := GetProjectID(newCtx)

	if projectID != expectedProjectID {
		t.Errorf("expected ProjectID %s, got %s", expectedProjectID, projectID)
	}
}

// TestGetProjectIDEmpty tests GetProjectID returns empty string when context is missing
func TestGetProjectIDEmpty(t *testing.T) {
	ctx := context.Background()
	projectID := GetProjectID(ctx)

	if projectID != "" {
		t.Errorf("expected empty ProjectID, got %s", projectID)
	}
}

// TestGetProjectIDEmptyProjectContext tests GetProjectID with empty project ID in context
func TestGetProjectIDEmptyProjectContext(t *testing.T) {
	ctx := context.Background()
	projectCtx := NewProjectContext("", "workspace-789")

	newCtx := WithProjectContext(ctx, projectCtx)
	projectID := GetProjectID(newCtx)

	if projectID != "" {
		t.Errorf("expected empty ProjectID, got %s", projectID)
	}
}

// TestGetNamespace tests retrieving namespace from context
func TestGetNamespace(t *testing.T) {
	ctx := context.Background()
	projectCtx := NewProjectContext("bifrost", "workspace-123")

	newCtx := WithProjectContext(ctx, projectCtx)
	ns := GetNamespace(newCtx)

	if ns != NamespaceBifrost {
		t.Errorf("expected NamespaceBifrost, got %s", ns)
	}
}

// TestGetNamespaceDefault tests GetNamespace returns default namespace when context is missing
func TestGetNamespaceDefault(t *testing.T) {
	ctx := context.Background()
	ns := GetNamespace(ctx)

	if ns != NamespaceDefault {
		t.Errorf("expected NamespaceDefault, got %s", ns)
	}
}

// TestGetNamespaceWithUnknownProject tests GetNamespace with unknown project
func TestGetNamespaceWithUnknownProject(t *testing.T) {
	ctx := context.Background()
	projectCtx := NewProjectContext("unknown-project", "workspace-123")

	newCtx := WithProjectContext(ctx, projectCtx)
	ns := GetNamespace(newCtx)

	if ns != NamespaceDefault {
		t.Errorf("expected NamespaceDefault, got %s", ns)
	}
}

// TestContextWithMultipleValues tests context with multiple values
func TestContextWithMultipleValues(t *testing.T) {
	ctx := context.Background()
	ctx = context.WithValue(ctx, otherContextKey, "other-value")

	projectCtx := NewProjectContext("test-project", "workspace-123")
	newCtx := WithProjectContext(ctx, projectCtx)

	// Verify other value is still there
	otherValue := newCtx.Value(otherContextKey)
	if otherValue != "other-value" {
		t.Error("expected other context value to be preserved")
	}

	// Verify project context is there
	retrieved := GetProjectContext(newCtx)
	if retrieved == nil {
		t.Fatal("expected GetProjectContext to return non-nil value")
	}
}

// TestContextIsolation tests that different contexts don't interfere
func TestContextIsolation(t *testing.T) {
	ctx1 := context.Background()
	ctx2 := context.Background()

	projectCtx1 := NewProjectContext("project-1", "workspace-1")
	projectCtx2 := NewProjectContext("project-2", "workspace-2")

	ctx1 = WithProjectContext(ctx1, projectCtx1)
	ctx2 = WithProjectContext(ctx2, projectCtx2)

	retrieved1 := GetProjectContext(ctx1)
	retrieved2 := GetProjectContext(ctx2)

	if retrieved1.ProjectID != "project-1" {
		t.Errorf("expected project-1 in ctx1, got %s", retrieved1.ProjectID)
	}
	if retrieved2.ProjectID != "project-2" {
		t.Errorf("expected project-2 in ctx2, got %s", retrieved2.ProjectID)
	}
}

// TestProjectContextKeyValue tests constant value
func TestProjectContextKeyValue(t *testing.T) {
	expected := ProjectContextKey("project_context")
	if ProjectContextKeyValue != expected {
		t.Errorf("expected key %s, got %s", expected, ProjectContextKeyValue)
	}
}

// TestWithProjectContextNilProjectContext tests WithProjectContext with nil project context
func TestWithProjectContextNilProjectContext(t *testing.T) {
	ctx := context.Background()
	newCtx := WithProjectContext(ctx, nil)

	retrieved := GetProjectContext(newCtx)
	if retrieved != nil {
		t.Error("expected GetProjectContext to return nil when WithProjectContext was called with nil")
	}
}

// TestGetProjectIDWithNilProjectContext tests GetProjectID when context was set to nil
func TestGetProjectIDWithNilProjectContext(t *testing.T) {
	ctx := context.Background()
	newCtx := WithProjectContext(ctx, nil)

	projectID := GetProjectID(newCtx)
	if projectID != "" {
		t.Errorf("expected empty ProjectID when context is nil, got %s", projectID)
	}
}

// TestGetNamespaceWithNilProjectContext tests GetNamespace when context was set to nil
func TestGetNamespaceWithNilProjectContext(t *testing.T) {
	ctx := context.Background()
	newCtx := WithProjectContext(ctx, nil)

	ns := GetNamespace(newCtx)
	if ns != NamespaceDefault {
		t.Errorf("expected NamespaceDefault when context is nil, got %s", ns)
	}
}

// TestContextChaining tests chaining multiple context operations
func TestContextChaining(t *testing.T) {
	ctx := context.Background()

	// Chain multiple WithProjectContext calls (last one wins)
	projectCtx1 := NewProjectContext("project-1", "workspace-1")
	projectCtx2 := NewProjectContext("project-2", "workspace-2")

	ctx = WithProjectContext(ctx, projectCtx1)
	ctx = WithProjectContext(ctx, projectCtx2)

	retrieved := GetProjectContext(ctx)
	if retrieved.ProjectID != "project-2" {
		t.Errorf("expected project-2 (last set), got %s", retrieved.ProjectID)
	}
}

// TestGetProjectContextAllFields tests all fields of retrieved context
func TestGetProjectContextAllFields(t *testing.T) {
	ctx := context.Background()
	projectCtx := NewProjectContext("test-proj", "test-workspace")

	newCtx := WithProjectContext(ctx, projectCtx)
	retrieved := GetProjectContext(newCtx)

	if retrieved.ProjectID == "" {
		t.Error("ProjectID should not be empty")
	}
	if retrieved.WorkspaceID == "" {
		t.Error("WorkspaceID should not be empty")
	}
	if retrieved.Namespace == "" {
		t.Error("Namespace should not be empty")
	}
}

// BenchmarkWithProjectContext benchmarks context creation with project context
func BenchmarkWithProjectContext(b *testing.B) {
	ctx := context.Background()
	projectCtx := NewProjectContext("bench-project", "bench-workspace")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		WithProjectContext(ctx, projectCtx)
	}
}

// BenchmarkGetProjectContext benchmarks project context retrieval
func BenchmarkGetProjectContext(b *testing.B) {
	ctx := context.Background()
	projectCtx := NewProjectContext("bench-project", "bench-workspace")
	ctx = WithProjectContext(ctx, projectCtx)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		GetProjectContext(ctx)
	}
}

// BenchmarkGetProjectID benchmarks project ID retrieval
func BenchmarkGetProjectID(b *testing.B) {
	ctx := context.Background()
	projectCtx := NewProjectContext("bench-project", "bench-workspace")
	ctx = WithProjectContext(ctx, projectCtx)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		GetProjectID(ctx)
	}
}

// BenchmarkGetNamespace benchmarks namespace retrieval
func BenchmarkGetNamespace(b *testing.B) {
	ctx := context.Background()
	projectCtx := NewProjectContext("bench-project", "bench-workspace")
	ctx = WithProjectContext(ctx, projectCtx)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		GetNamespace(ctx)
	}
}
