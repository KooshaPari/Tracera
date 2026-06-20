# Neo4j Complete Setup Guide

## Local Development (Docker)

```bash
# Start Neo4j
docker run -d \
  --name neo4j \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  -v neo4j_data:/data \
  neo4j:latest

# Access browser
# http://localhost:7474
# Username: neo4j
# Password: password
```

## Production Setup (Neo4j Aura)

### 1. Create Neo4j Aura Account
- Go to https://console.neo4j.io
- Sign up with GitHub/Google
- Create new instance

### 2. Get Connection String
```
Connection String: neo4j+s://host:port
Username: neo4j
Password: (auto-generated)
```

### 3. Environment Variables
```bash
export NEO4J_URI="neo4j+s://host:port"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

## Go Integration

### 1. Install Package
```bash
go get github.com/neo4j/neo4j-go-driver/v5
```

### 2. Create Neo4j Client

```go
// backend/internal/graph/client.go
package graph

import (
    "github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

type GraphClient struct {
    driver neo4j.DriverWithContext
}

func NewGraphClient(uri, user, password string) (*GraphClient, error) {
    driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(user, password, ""))
    if err != nil {
        return nil, err
    }
    
    return &GraphClient{driver: driver}, nil
}

func (g *GraphClient) Query(ctx context.Context, query string, params map[string]interface{}) (neo4j.ResultWithContext, error) {
    session := g.driver.NewSession(ctx, neo4j.SessionConfig{})
    defer session.Close(ctx)
    
    return session.Run(ctx, query, params)
}

func (g *GraphClient) Close(ctx context.Context) error {
    return g.driver.Close(ctx)
}
```

### 3. Initialize in main.go

```go
// backend/main.go
graphClient, err := graph.NewGraphClient(
    os.Getenv("NEO4J_URI"),
    os.Getenv("NEO4J_USER"),
    os.Getenv("NEO4J_PASSWORD"),
)
if err != nil {
    log.Fatal("Failed to connect to Neo4j:", err)
}
defer graphClient.Close(context.Background())
```

## Multi-Project Setup (Hybrid Approach)

### 1. Create Project Nodes
```cypher
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
```

### 2. Create Indexes
```cypher
CREATE INDEX FOR (m:Model) ON (m.project_id)
CREATE INDEX FOR (m:Model) ON (m.id)
CREATE INDEX FOR (p:Project) ON (p.id)
```

### 3. Add project_id to Nodes
```cypher
MATCH (m:Model)
SET m.project_id = "proj_bifrost_001"
```

### 4. Create OWNS Relationships
```cypher
MATCH (p:Project {id: "proj_bifrost_001"}), (m:Model {project_id: "proj_bifrost_001"})
CREATE (p)-[:OWNS]->(m)
```

## Go Integration for Multi-Project

```go
// backend/internal/graph/project_context.go
package graph

import "context"

type ProjectContextKey string
const ProjectIDKey ProjectContextKey = "project_id"

func WithProjectID(ctx context.Context, projectID string) context.Context {
    return context.WithValue(ctx, ProjectIDKey, projectID)
}

func GetProjectID(ctx context.Context) string {
    projectID, ok := ctx.Value(ProjectIDKey).(string)
    if !ok {
        return ""
    }
    return projectID
}

// Query with project isolation
func (g *GraphClient) GetModels(ctx context.Context) ([]Model, error) {
    projectID := GetProjectID(ctx)
    
    query := `
    MATCH (m:Model {project_id: $projectId})
    RETURN m.id, m.name, m.version
    `
    
    result, err := g.Query(ctx, query, map[string]interface{}{
        "projectId": projectID,
    })
    
    if err != nil {
        return nil, err
    }
    
    var models []Model
    for result.Next(ctx) {
        record := result.Record()
        models = append(models, Model{
            ID:      record.Values[0].(string),
            Name:    record.Values[1].(string),
            Version: record.Values[2].(string),
        })
    }
    
    return models, result.Err()
}
```

## Query Patterns

### Get All Models for Project
```cypher
MATCH (m:Model:Bifrost {project_id: "proj_bifrost_001"})
RETURN m
```

### Get Project with Models
```cypher
MATCH (p:Project {id: "proj_bifrost_001"})-[:OWNS]->(m:Model)
RETURN p, collect(m) as models
```

### Check Node Distribution
```cypher
MATCH (n) 
RETURN labels(n)[0] as type, n.project_id as project, count(*) as count
GROUP BY type, project
```

## Monitoring

### Neo4j Browser
- Query performance
- Node/relationship count
- Memory usage
- Connected clients

### Aura Dashboard
- Database size
- Query throughput
- Error rates
- Backup status

## Performance Tuning

### Connection Pooling
```go
driver, _ := neo4j.NewDriverWithContext(
    uri,
    neo4j.BasicAuth(user, password, ""),
    func(config *neo4j.Config) {
        config.MaxConnectionPoolSize = 50
    },
)
```

### Query Optimization
```cypher
-- Use EXPLAIN to analyze queries
EXPLAIN MATCH (m:Model {project_id: $projectId}) RETURN m

-- Create indexes for frequently queried properties
CREATE INDEX FOR (m:Model) ON (m.project_id)
```

## Troubleshooting

### Connection Issues
```bash
# Test connection
cypher-shell -a neo4j+s://host:port -u neo4j -p password "RETURN 1"
```

### Query Issues
```cypher
-- Check query performance
PROFILE MATCH (m:Model {project_id: $projectId}) RETURN m
```

## Cost

- **Local**: Free (Docker)
- **Aura Free Tier**:
  - 200K nodes
  - 1 instance
  - Perfect for development
- **Aura Pro**: $0.06/hour

## Next Steps

1. Set up local Neo4j with Docker
2. Create GraphClient struct in Go
3. Implement multi-project setup
4. Add ProjectContext middleware
5. Test project isolation
6. Deploy to Aura for production

See NEO4J_MULTI_PROJECT_STRATEGY.md for detailed multi-project implementation.

