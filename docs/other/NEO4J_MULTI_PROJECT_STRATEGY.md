# Neo4j Aura Multi-Project Sharing Strategy

## Recommended Approach: Hybrid Label + Property-Based Isolation

**Why this is best:**
- ✅ Query performance (labels are indexed)
- ✅ Data isolation (properties enforce boundaries)
- ✅ Scalability (supports 4+ projects)
- ✅ Flexibility (easy to add new projects)
- ✅ Auditability (clear project ownership)

## Implementation

### Schema Design

```cypher
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

// Create project-scoped models
CREATE (:Model:Bifrost {
  project_id: "proj_bifrost_001",
  id: "model_gpt4_001",
  name: "gpt-4",
  version: "1.0",
  provider: "openai",
  created_at: timestamp()
})

CREATE (:Model:MyApp {
  project_id: "proj_myapp_001",
  id: "model_gpt4_002",
  name: "gpt-4",
  version: "2.0",
  provider: "openai",
  created_at: timestamp()
})

// Link models to projects
MATCH (p:Project {id: "proj_bifrost_001"}), (m:Model {id: "model_gpt4_001"})
CREATE (p)-[:OWNS]->(m)
```

### Query Patterns

```cypher
// Get all models for a project (fast - uses label index)
MATCH (m:Model:Bifrost {project_id: "proj_bifrost_001"})
RETURN m

// Get project with all its models
MATCH (p:Project {id: "proj_bifrost_001"})-[:OWNS]->(m:Model)
RETURN p, m

// Cross-project comparison (when needed)
MATCH (m:Model {name: "gpt-4"})
RETURN m.project_id, m.version, m.provider
ORDER BY m.version DESC
```

### Node Allocation (200K limit)

```
Total: 200,000 nodes

Project Overhead:
- 1 Project node per project = 4 nodes (for 4 projects)

Per-Project Allocation (49,000 nodes each):
- Models: 5,000 nodes
- Embeddings: 20,000 nodes
- Relationships: 10,000 nodes
- Metadata: 14,000 nodes

Scaling:
- 4 projects: 196,000 nodes (98% utilization)
- 3 projects: 147,000 nodes (73% utilization)
- 2 projects: 98,000 nodes (49% utilization)
```

## Implementation in Go

```go
// Project context
type ProjectContext struct {
    ProjectID string
    ProjectLabel string // "Bifrost", "MyApp", etc.
}

// Query with project isolation
func GetModels(ctx context.Context, projectID string) ([]Model, error) {
    query := `
    MATCH (m:Model {project_id: $projectId})
    RETURN m.id, m.name, m.version
    `
    
    result, err := session.Run(ctx, query, map[string]interface{}{
        "projectId": projectID,
    })
    
    // Process results...
}

// Ensure project isolation
func ValidateProjectAccess(projectID string, userProject string) error {
    if projectID != userProject {
        return fmt.Errorf("unauthorized: project mismatch")
    }
    return nil
}
```

## Benefits

✅ **Performance**: Labels are indexed, queries are fast
✅ **Isolation**: project_id property prevents cross-project leaks
✅ **Scalability**: Supports 4+ projects with 200K node limit
✅ **Auditability**: Clear ownership via OWNS relationships
✅ **Flexibility**: Easy to add new projects
✅ **Consistency**: Enforced via application logic

## Migration Path

1. Start with single project (Bifrost)
2. Add project_id to all nodes
3. Add project labels to node types
4. Create Project nodes
5. Create OWNS relationships
6. Add project validation in queries
7. Scale to additional projects

## Monitoring

```cypher
// Check node distribution
MATCH (n) RETURN labels(n)[0] as type, n.project_id as project, count(*) as count
GROUP BY type, project
ORDER BY project, type

// Check for orphaned nodes
MATCH (n) WHERE NOT EXISTS(n.project_id)
RETURN count(n) as orphaned_nodes
```

## Cost Optimization

- **Storage**: ~1 byte per property per node
- **Query**: Label-based filtering = O(1) lookup
- **Relationships**: OWNS relationships = minimal overhead
- **Total**: ~200K nodes = ~200MB storage (Aura free tier)

