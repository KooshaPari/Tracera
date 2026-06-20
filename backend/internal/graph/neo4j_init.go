package graph

import (
	"context"
	"fmt"
	"log/slog"
)

// InitializeNeo4j initializes Neo4j with multi-project setup
func InitializeNeo4j(ctx context.Context, uri, user, password string) (*Neo4jClient, error) {
	// Create client
	client, err := NewNeo4jClient(ctx, uri, user, password)
	if err != nil {
		return nil, fmt.Errorf("failed to create Neo4j client: %w", err)
	}

	// Create indexes
	err = client.CreateIndexes(ctx)
	if err != nil {
		slog.Error("Warning: failed to create indexes", "error", err)
		// Don't fail on index creation errors
	}

	// Create project nodes for all namespaces
	projects := []struct {
		id        string
		namespace ProjectNamespace
	}{
		{"bifrost", NamespaceBifrost},
		{"vibeproxy", NamespaceVibeProxy},
		{"jarvis", NamespaceJarvis},
		{"trace", NamespaceTrace},
	}

	for _, proj := range projects {
		projectCtx := NewProjectContext(proj.id, "default")
		err := client.CreateProjectNode(ctx, projectCtx)
		if err != nil {
			slog.Error("Warning: failed to create project node for", "error", proj.id, "error", err)
			// Don't fail if project already exists
		}
	}

	return client, nil
}

// VerifyNeo4jSetup verifies that Neo4j is properly set up
func VerifyNeo4jSetup(ctx context.Context, client *Neo4jClient) error {
	// Check connection
	err := client.HealthCheck(ctx)
	if err != nil {
		return fmt.Errorf("Neo4j health check failed: %w", err)
	}

	return nil
}
