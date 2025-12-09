# Neo4j Multi-Project Implementation for TraceRTM

## Quick Start

### 1. Add Project Context to Go Backend

```go
// backend/internal/graph/project_context.go
package graph

import "context"

type ProjectContextKey string

const ProjectIDKey ProjectContextKey = "project_id"

// WithProjectID adds project ID to context
func WithProjectID(ctx context.Context, projectID string) context.Context {
    return context.WithValue(ctx, ProjectIDKey, projectID)
}

// GetProjectID retrieves project ID from context
func GetProjectID(ctx context.Context) string {
    projectID, ok := ctx.Value(ProjectIDKey).(string)
    if !ok {
        return ""
    }
    return projectID
}
```

### 2. Update Neo4j Queries

```go
// backend/internal/graph/models.go
func (s *Service) GetModels(ctx context.Context) ([]Model, error) {
    projectID := GetProjectID(ctx)
    
    query := `
    MATCH (m:Model {project_id: $projectId})
    RETURN m.id, m.name, m.version, m.provider
    ORDER BY m.created_at DESC
    `
    
    result, err := s.session.Run(ctx, query, map[string]interface{}{
        "projectId": projectID,
    })
    
    if err != nil {
        return nil, err
    }
    
    var models []Model
    for result.Next(ctx) {
        record := result.Record()
        models = append(models, Model{
            ID:       record.Values[0].(string),
            Name:     record.Values[1].(string),
            Version:  record.Values[2].(string),
            Provider: record.Values[3].(string),
        })
    }
    
    return models, result.Err()
}
```

### 3. Initialize Projects in Neo4j

```cypher
// backend/migrations/neo4j_init.cypher
// Create project nodes
CREATE (:Project {
  id: "proj_bifrost_001",
  name: "bifrost",
  created_at: timestamp(),
  status: "active"
})

CREATE (:Project {
  id: "proj_myapp_001",
  name: "myapp",
  created_at: timestamp(),
  status: "active"
})

// Create indexes for performance
CREATE INDEX FOR (m:Model) ON (m.project_id)
CREATE INDEX FOR (m:Model) ON (m.id)
CREATE INDEX FOR (p:Project) ON (p.id)
```

### 4. Add Project Validation Middleware

```go
// backend/internal/middleware/project_context.go
func ProjectContextMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        // Get project from auth token or header
        projectID := c.Request().Header.Get("X-Project-ID")
        
        if projectID == "" {
            return echo.NewHTTPError(400, "X-Project-ID header required")
        }
        
        // Add to context
        ctx := WithProjectID(c.Request().Context(), projectID)
        c.SetRequest(c.Request().WithContext(ctx))
        
        return next(c)
    }
}
```

### 5. Register Middleware in main.go

```go
// backend/main.go
e.Use(middleware.ProjectContextMiddleware)
```

## Node Allocation for TraceRTM

```
Total: 200,000 nodes

Per Project (50,000 nodes):
├── Models: 5,000
├── Embeddings: 15,000
├── Relationships: 15,000
├── Metadata: 15,000
└── Reserved: 0

Supports: 4 concurrent projects
```

## Query Examples

```cypher
// Get all models for Bifrost project
MATCH (m:Model {project_id: "proj_bifrost_001"})
RETURN m

// Get project with models
MATCH (p:Project {id: "proj_bifrost_001"})-[:OWNS]->(m:Model)
RETURN p, collect(m) as models

// Cross-project comparison
MATCH (m:Model {name: "gpt-4"})
RETURN m.project_id, m.version, m.provider
ORDER BY m.version DESC

// Check node distribution
MATCH (n) 
RETURN labels(n)[0] as type, n.project_id as project, count(*) as count
GROUP BY type, project
```

## Testing

```go
// backend/tests/graph_test.go
func TestProjectIsolation(t *testing.T) {
    ctx := WithProjectID(context.Background(), "proj_bifrost_001")
    
    models, err := service.GetModels(ctx)
    assert.NoError(t, err)
    
    // Verify all models belong to project
    for _, m := range models {
        assert.Equal(t, "proj_bifrost_001", m.ProjectID)
    }
}
```

## Deployment Checklist

- [ ] Add project_id to all Neo4j nodes
- [ ] Create Project nodes for each project
- [ ] Create OWNS relationships
- [ ] Add indexes for performance
- [ ] Update Go queries with project_id filter
- [ ] Add ProjectContextMiddleware
- [ ] Test project isolation
- [ ] Deploy to staging
- [ ] Monitor node distribution
- [ ] Deploy to production

## Monitoring

```cypher
// Check node count per project
MATCH (n) 
WHERE exists(n.project_id)
RETURN n.project_id, count(*) as node_count
ORDER BY node_count DESC

// Check for orphaned nodes
MATCH (n) 
WHERE NOT exists(n.project_id)
RETURN count(n) as orphaned_count
```

## Cost

- **Storage**: ~200MB for 200K nodes
- **Queries**: Fast (label-indexed)
- **Relationships**: Minimal overhead
- **Total**: Fits in Aura free tier

