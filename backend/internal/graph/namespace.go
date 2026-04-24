package graph

// ProjectNamespace represents a project namespace in the shared Neo4j instance
type ProjectNamespace string

const (
	// NamespaceBifrost is the namespace for the Bifrost project.
	NamespaceBifrost ProjectNamespace = "bifrost"
	// NamespaceVibeProxy is the namespace for the VibeProxy project.
	NamespaceVibeProxy ProjectNamespace = "vibeproxy"
	// NamespaceJarvis is the namespace for the Jarvis project.
	NamespaceJarvis ProjectNamespace = "jarvis"
	// NamespaceTrace is the namespace for the Traceability project.
	NamespaceTrace ProjectNamespace = "trace"
	// NamespaceDefault is the default namespace.
	NamespaceDefault ProjectNamespace = "default"
)

// ProjectContext holds project-specific information for Neo4j queries
type ProjectContext struct {
	ProjectID   string
	Namespace   ProjectNamespace
	WorkspaceID string
}

// GetProjectNamespace returns the namespace for a given project ID
func GetProjectNamespace(projectID string) ProjectNamespace {
	// Map project IDs to namespaces
	// This can be extended based on your project structure
	switch projectID {
	case "bifrost":
		return NamespaceBifrost
	case "vibeproxy":
		return NamespaceVibeProxy
	case "jarvis":
		return NamespaceJarvis
	case "trace":
		return NamespaceTrace
	default:
		return NamespaceDefault
	}
}

// NewProjectContext creates a new project context
func NewProjectContext(projectID, workspaceID string) *ProjectContext {
	return &ProjectContext{
		ProjectID:   projectID,
		Namespace:   GetProjectNamespace(projectID),
		WorkspaceID: workspaceID,
	}
}
