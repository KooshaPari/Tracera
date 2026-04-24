package graph

import (
	"context"
	"fmt"
	"log/slog"
	"net/url"
	"strings"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

// Neo4jClient represents a Neo4j graph database client with multi-project support
type Neo4jClient struct {
	driver neo4j.DriverWithContext
}

// normalizeNeo4jURI normalizes Neo4j URI by ensuring it has a port
// Neo4j Cloud URIs often come without ports, so we add :7687 if missing
func normalizeNeo4jURI(uri string) string {
	// If URI is empty, return as-is
	if uri == "" {
		return uri
	}

	// Parse the URI
	parsed, err := url.Parse(uri)
	if err != nil {
		// If parsing fails, return original URI
		return uri
	}

	// If port is missing and it's a neo4j:// or neo4j+s:// scheme, add default port
	if parsed.Port() == "" {
		// For neo4j:// and neo4j+s:// schemes, default port is 7687
		if strings.HasPrefix(parsed.Scheme, "neo4j") {
			if parsed.Host != "" {
				parsed.Host += ":7687"
			}
		}
	}

	return parsed.String()
}

// NewNeo4jClient creates a new Neo4j client
func NewNeo4jClient(ctx context.Context, uri, user, password string) (*Neo4jClient, error) {
	// Normalize URI to ensure it has a port
	normalizedURI := normalizeNeo4jURI(uri)

	driver, err := neo4j.NewDriverWithContext(normalizedURI, neo4j.BasicAuth(user, password, ""))
	if err != nil {
		return nil, fmt.Errorf("failed to create Neo4j driver: %w", err)
	}

	// Verify connection
	err = driver.VerifyConnectivity(ctx)
	if err != nil {
		closeNeo4jDriver(ctx, driver)
		return nil, fmt.Errorf("failed to verify Neo4j connection: %w", err)
	}

	return &Neo4jClient{driver: driver}, nil
}

func closeNeo4jDriver(ctx context.Context, driver neo4j.DriverWithContext) {
	if driver == nil {
		return
	}
	if err := driver.Close(ctx); err != nil {
		slog.Error("failed to close neo4j driver", "error", err)
	}
}

func closeNeo4jSession(ctx context.Context, session neo4j.SessionWithContext) {
	if session == nil {
		return
	}
	if err := session.Close(ctx); err != nil {
		slog.Error("failed to close neo4j session", "error", err)
	}
}

// Close closes the Neo4j driver connection
func (c *Neo4jClient) Close(ctx context.Context) error {
	return c.driver.Close(ctx)
}

// ExecuteQuery executes a Cypher query with project isolation
func (c *Neo4jClient) ExecuteQuery(
	ctx context.Context, projectCtx *ProjectContext, query string, params map[string]interface{},
) (neo4j.ResultWithContext, error) {
	// Add project_id to params for isolation
	if params == nil {
		params = make(map[string]interface{})
	}
	params["projectId"] = projectCtx.ProjectID
	params["namespace"] = string(projectCtx.Namespace)

	session := c.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeNeo4jSession(ctx, session)

	return session.Run(ctx, query, params)
}

// CreateProjectNode creates a project node in Neo4j
func (c *Neo4jClient) CreateProjectNode(ctx context.Context, projectCtx *ProjectContext) error {
	query := `
	CREATE (:Project {
		id: $projectId,
		namespace: $namespace,
		workspace_id: $workspaceId,
		created_at: timestamp(),
		status: "active"
	})
	`

	session := c.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeNeo4jSession(ctx, session)

	_, err := session.Run(ctx, query, map[string]interface{}{
		"projectId":   projectCtx.ProjectID,
		"namespace":   string(projectCtx.Namespace),
		"workspaceId": projectCtx.WorkspaceID,
	})

	return err
}

// CreateIndexes creates indexes for project isolation and performance
// Note: Index creation failures are non-blocking - we log warnings but don't fail
func (c *Neo4jClient) CreateIndexes(ctx context.Context) error {
	// Try multiple Neo4j versions of index syntax
	queries := [][]string{
		// Neo4j 5.x+ syntax (correct syntax with node labels)
		{
			"CREATE INDEX idx_project_id IF NOT EXISTS FOR (n:Node) ON (n.project_id)",
			"CREATE INDEX idx_namespace IF NOT EXISTS FOR (n:Node) ON (n.namespace)",
			"CREATE INDEX idx_project_type IF NOT EXISTS FOR (n:Node) ON (n.project_id, n.type)",
		},
		// Neo4j 4.x syntax (with labels)
		{
			"CREATE INDEX idx_project_id IF NOT EXISTS FOR (n:Item) ON (n.project_id)",
			"CREATE INDEX idx_namespace IF NOT EXISTS FOR (n:Item) ON (n.namespace)",
			"CREATE INDEX idx_project_type IF NOT EXISTS FOR (n:Item) ON (n.project_id, n.type)",
		},
		// Alternative syntax for older versions
		{
			"CREATE INDEX idx_project_id FOR (n:Node) ON (n.project_id)",
			"CREATE INDEX idx_namespace FOR (n:Node) ON (n.namespace)",
			"CREATE INDEX idx_project_type FOR (n:Node) ON (n.project_id, n.type)",
		},
	}

	session := c.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeNeo4jSession(ctx, session)

	// Try each syntax variant until one works
	for _, queryset := range queries {
		success := true
		for _, query := range queryset {
			_, err := session.Run(ctx, query, nil)
			if err != nil {
				// Continue to next syntax variant if this one fails
				slog.Error("Index query failed (will try alternative syntax)", "error", err)
				success = false
				break
			}
		}
		if success {
			// All queries succeeded with this syntax
			return nil
		}
	}

	// Index creation is non-critical - log warning but don't fail startup
	slog.Warn("Warning: Could not create Neo4j indexes with any syntax variant. Indexes will still work with existing data.")
	return nil
}

// HealthCheck verifies Neo4j connection is healthy
func (c *Neo4jClient) HealthCheck(ctx context.Context) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeNeo4jSession(ctx, session)

	result, err := session.Run(ctx, "RETURN 1", nil)
	if err != nil {
		return err
	}

	_, err = result.Single(ctx)
	return err
}

// GetDriver returns the underlying Neo4j driver
func (c *Neo4jClient) GetDriver() neo4j.DriverWithContext {
	return c.driver
}
