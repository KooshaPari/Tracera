package graph

import (
	"context"
)

// ProjectContextKey is the key for storing project context in context
type ProjectContextKey string

const (
	// ProjectContextKeyValue is the context key for project metadata.
	ProjectContextKeyValue ProjectContextKey = "project_context"
)

// WithProjectContext adds project context to a context
func WithProjectContext(ctx context.Context, projectCtx *ProjectContext) context.Context {
	return context.WithValue(ctx, ProjectContextKeyValue, projectCtx)
}

// GetProjectContext retrieves project context from a context
func GetProjectContext(ctx context.Context) *ProjectContext {
	projectCtx, ok := ctx.Value(ProjectContextKeyValue).(*ProjectContext)
	if !ok {
		return nil
	}
	return projectCtx
}

// GetProjectID retrieves project ID from context
func GetProjectID(ctx context.Context) string {
	projectCtx := GetProjectContext(ctx)
	if projectCtx == nil {
		return ""
	}
	return projectCtx.ProjectID
}

// GetNamespace retrieves namespace from context
func GetNamespace(ctx context.Context) ProjectNamespace {
	projectCtx := GetProjectContext(ctx)
	if projectCtx == nil {
		return NamespaceDefault
	}
	return projectCtx.Namespace
}
