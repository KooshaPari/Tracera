//go:build !integration && !e2e

package graph

import (
	"testing"
)

const testProjectBifrost = "bifrost"

// TestGetProjectNamespaceBifrost tests namespace mapping for bifrost project
func TestGetProjectNamespaceBifrost(t *testing.T) {
	ns := GetProjectNamespace("bifrost")
	if ns != NamespaceBifrost {
		t.Errorf("expected NamespaceBifrost, got %s", ns)
	}
}

// TestGetProjectNamespaceVibeProxy tests namespace mapping for vibeproxy project
func TestGetProjectNamespaceVibeProxy(t *testing.T) {
	ns := GetProjectNamespace("vibeproxy")
	if ns != NamespaceVibeProxy {
		t.Errorf("expected NamespaceVibeProxy, got %s", ns)
	}
}

// TestGetProjectNamespaceJarvis tests namespace mapping for jarvis project
func TestGetProjectNamespaceJarvis(t *testing.T) {
	ns := GetProjectNamespace("jarvis")
	if ns != NamespaceJarvis {
		t.Errorf("expected NamespaceJarvis, got %s", ns)
	}
}

// TestGetProjectNamespaceTrace tests namespace mapping for trace project
func TestGetProjectNamespaceTrace(t *testing.T) {
	ns := GetProjectNamespace("trace")
	if ns != NamespaceTrace {
		t.Errorf("expected NamespaceTrace, got %s", ns)
	}
}

// TestGetProjectNamespaceDefault tests namespace mapping for unknown project
func TestGetProjectNamespaceDefault(t *testing.T) {
	ns := GetProjectNamespace("unknown-project")
	if ns != NamespaceDefault {
		t.Errorf("expected NamespaceDefault, got %s", ns)
	}
}

// TestGetProjectNamespaceEmpty tests namespace mapping for empty project ID
func TestGetProjectNamespaceEmpty(t *testing.T) {
	ns := GetProjectNamespace("")
	if ns != NamespaceDefault {
		t.Errorf("expected NamespaceDefault for empty project ID, got %s", ns)
	}
}

// TestGetProjectNamespaceCaseSensitive tests case sensitivity
func TestGetProjectNamespaceCaseSensitive(t *testing.T) {
	ns := GetProjectNamespace("BIFROST")
	if ns == NamespaceBifrost {
		t.Error("project namespace lookup should be case-sensitive")
	}
	if ns != NamespaceDefault {
		t.Errorf("expected NamespaceDefault for uppercase project ID, got %s", ns)
	}
}

// TestProjectNamespaceConstantValues tests constant string values
func TestProjectNamespaceConstantValues(t *testing.T) {
	testCases := []struct {
		expected ProjectNamespace
		value    ProjectNamespace
		name     string
	}{
		{NamespaceBifrost, ProjectNamespace("bifrost"), "bifrost"},
		{NamespaceVibeProxy, ProjectNamespace("vibeproxy"), "vibeproxy"},
		{NamespaceJarvis, ProjectNamespace("jarvis"), "jarvis"},
		{NamespaceTrace, ProjectNamespace("trace"), "trace"},
		{NamespaceDefault, ProjectNamespace("default"), "default"},
	}

	for _, tc := range testCases {
		if tc.expected != tc.value {
			t.Errorf("namespace %s: expected %s, got %s", tc.name, tc.expected, tc.value)
		}
	}
}

// TestNewProjectContext tests ProjectContext creation
func TestNewProjectContext(t *testing.T) {
	projectID := "test-project-123"
	workspaceID := "workspace-456"

	ctx := NewProjectContext(projectID, workspaceID)

	if ctx == nil {
		t.Fatal("expected ProjectContext to be initialized")
	}
	if ctx.ProjectID != projectID {
		t.Errorf("expected ProjectID %s, got %s", projectID, ctx.ProjectID)
	}
	if ctx.WorkspaceID != workspaceID {
		t.Errorf("expected WorkspaceID %s, got %s", workspaceID, ctx.WorkspaceID)
	}
	if ctx.Namespace != NamespaceDefault {
		t.Errorf("expected NamespaceDefault for unknown project, got %s", ctx.Namespace)
	}
}

// TestNewProjectContextBifrost tests ProjectContext with bifrost project
func TestNewProjectContextBifrost(t *testing.T) {
	ctx := NewProjectContext(testProjectBifrost, "workspace-123")

	if ctx.ProjectID != testProjectBifrost {
		t.Errorf("expected ProjectID bifrost, got %s", ctx.ProjectID)
	}
	if ctx.Namespace != NamespaceBifrost {
		t.Errorf("expected NamespaceBifrost, got %s", ctx.Namespace)
	}
}

// TestNewProjectContextTrace tests ProjectContext with trace project
func TestNewProjectContextTrace(t *testing.T) {
	ctx := NewProjectContext("trace", "workspace-789")

	if ctx.ProjectID != "trace" {
		t.Errorf("expected ProjectID trace, got %s", ctx.ProjectID)
	}
	if ctx.Namespace != NamespaceTrace {
		t.Errorf("expected NamespaceTrace, got %s", ctx.Namespace)
	}
}

// TestNewProjectContextEmptyProjectID tests ProjectContext with empty project ID
func TestNewProjectContextEmptyProjectID(t *testing.T) {
	ctx := NewProjectContext("", "workspace-000")

	if ctx.ProjectID != "" {
		t.Errorf("expected empty ProjectID, got %s", ctx.ProjectID)
	}
	if ctx.WorkspaceID != "workspace-000" {
		t.Errorf("expected WorkspaceID workspace-000, got %s", ctx.WorkspaceID)
	}
	if ctx.Namespace != NamespaceDefault {
		t.Errorf("expected NamespaceDefault for empty project ID, got %s", ctx.Namespace)
	}
}

// TestNewProjectContextEmptyWorkspaceID tests ProjectContext with empty workspace ID
func TestNewProjectContextEmptyWorkspaceID(t *testing.T) {
	ctx := NewProjectContext("test-project", "")

	if ctx.ProjectID != "test-project" {
		t.Errorf("expected ProjectID test-project, got %s", ctx.ProjectID)
	}
	if ctx.WorkspaceID != "" {
		t.Errorf("expected empty WorkspaceID, got %s", ctx.WorkspaceID)
	}
}

// TestNewProjectContextBothEmpty tests ProjectContext with both empty values
func TestNewProjectContextBothEmpty(t *testing.T) {
	ctx := NewProjectContext("", "")

	if ctx.ProjectID != "" {
		t.Errorf("expected empty ProjectID, got %s", ctx.ProjectID)
	}
	if ctx.WorkspaceID != "" {
		t.Errorf("expected empty WorkspaceID, got %s", ctx.WorkspaceID)
	}
	if ctx.Namespace != NamespaceDefault {
		t.Errorf("expected NamespaceDefault, got %s", ctx.Namespace)
	}
}

// TestProjectContextStructure tests ProjectContext field values
func TestProjectContextStructure(t *testing.T) {
	projectID := "test-id"
	workspaceID := "work-id"
	ctx := NewProjectContext(projectID, workspaceID)

	if ctx.ProjectID == "" {
		t.Error("ProjectContext.ProjectID should not be empty")
	}
	if ctx.WorkspaceID == "" {
		t.Error("ProjectContext.WorkspaceID should not be empty")
	}
	if ctx.Namespace == "" {
		t.Error("ProjectContext.Namespace should not be empty")
	}
}

// TestGetProjectNamespaceMultipleWknownProjects tests all known projects
func TestGetProjectNamespaceMultipleKnownProjects(t *testing.T) {
	knownProjects := map[string]ProjectNamespace{
		"bifrost":   NamespaceBifrost,
		"vibeproxy": NamespaceVibeProxy,
		"jarvis":    NamespaceJarvis,
		"trace":     NamespaceTrace,
	}

	for projectID, expectedNS := range knownProjects {
		ns := GetProjectNamespace(projectID)
		if ns != expectedNS {
			t.Errorf("project %s: expected %s, got %s", projectID, expectedNS, ns)
		}
	}
}

// TestProjectContextNamespaceMapping tests ProjectContext correctly maps namespaces
func TestProjectContextNamespaceMapping(t *testing.T) {
	testCases := []struct {
		projectID         string
		expectedNamespace ProjectNamespace
	}{
		{"bifrost", NamespaceBifrost},
		{"vibeproxy", NamespaceVibeProxy},
		{"jarvis", NamespaceJarvis},
		{"trace", NamespaceTrace},
		{"unknown", NamespaceDefault},
		{"", NamespaceDefault},
	}

	for _, tc := range testCases {
		ctx := NewProjectContext(tc.projectID, "workspace")
		if ctx.Namespace != tc.expectedNamespace {
			t.Errorf("project %q: expected %s, got %s", tc.projectID, tc.expectedNamespace, ctx.Namespace)
		}
	}
}
