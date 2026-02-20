# Requirements Traceability - Deep Dive: Graph Databases

## Why Graph Databases for Requirements Traceability?

Traditional relational databases struggle with:
- **Deep traversals**: Finding all descendants 10 levels deep
- **Complex relationships**: Multiple relationship types
- **Path queries**: Finding shortest path between requirements
- **Pattern matching**: Finding specific graph patterns

Graph databases excel at:
- **Relationship-first**: Relationships are first-class citizens
- **Traversal performance**: O(1) for relationship traversal
- **Flexible schema**: Easy to add new relationship types
- **Query expressiveness**: Natural graph query languages

## Neo4j for Requirements Traceability

### Data Model

```cypher
// Node types
(:Requirement {
  id: "REQ-001",
  type: "Epic",
  title: "User Authentication",
  status: "Active",
  priority: "High",
  created_at: datetime(),
  updated_at: datetime()
})

// Relationship types
(:Requirement)-[:DECOMPOSES_TO]->(:Requirement)
(:Requirement)-[:IMPLEMENTS]->(:Code)
(:Requirement)-[:TESTS]->(:TestCase)
(:Requirement)-[:VALIDATES]->(:Requirement)
(:Requirement)-[:DEPENDS_ON]->(:Requirement)
(:Requirement)-[:BLOCKS]->(:Requirement)
```

### Cypher Query Patterns

#### Pattern 1: Find All Descendants
```cypher
// Find all requirements decomposed from an epic
MATCH (epic:Requirement {id: "EPIC-001"})-[:DECOMPOSES_TO*]->(child)
RETURN epic, child
```

#### Pattern 2: Impact Analysis
```cypher
// Find all requirements affected by a change
MATCH (req:Requirement {id: "REQ-123"})<-[:DEPENDS_ON*]-(dependent)
RETURN req, dependent
ORDER BY dependent.priority DESC
```

#### Pattern 3: Coverage Analysis
```cypher
// Find requirements without test cases
MATCH (req:Requirement)
WHERE NOT (req)-[:TESTS]->(:TestCase)
RETURN req.id, req.title, req.type
```

#### Pattern 4: Traceability Path
```cypher
// Find shortest path from epic to code
MATCH path = shortestPath(
  (epic:Requirement {type: "Epic"})-[*]-(code:Code)
)
RETURN path
```

#### Pattern 5: Orphaned Requirements
```cypher
// Find requirements with no incoming or outgoing links
MATCH (req:Requirement)
WHERE NOT (req)-[]-()
RETURN req
```

#### Pattern 6: Circular Dependencies
```cypher
// Detect circular dependencies
MATCH (req:Requirement)-[:DEPENDS_ON*]->(req)
RETURN req
```

#### Pattern 7: Requirement Hierarchy Depth
```cypher
// Find maximum depth of requirement hierarchy
MATCH path = (root:Requirement)-[:DECOMPOSES_TO*]->(leaf)
WHERE NOT (root)<-[:DECOMPOSES_TO]-()
  AND NOT (leaf)-[:DECOMPOSES_TO]->()
RETURN root.id, length(path) as depth
ORDER BY depth DESC
LIMIT 1
```

#### Pattern 8: Cross-Domain Traceability
```cypher
// Find all artifacts linked to a requirement
MATCH (req:Requirement {id: "REQ-001"})-[r]->(artifact)
RETURN type(r) as relationship, labels(artifact) as artifact_type, artifact
```

### Advanced Patterns

#### Pattern 9: Temporal Queries
```cypher
// Find requirements active at a specific time
MATCH (req:Requirement)
WHERE req.valid_from <= datetime('2024-01-01')
  AND (req.valid_to IS NULL OR req.valid_to > datetime('2024-01-01'))
RETURN req
```

#### Pattern 10: Aggregation Queries
```cypher
// Count requirements by type and status
MATCH (req:Requirement)
RETURN req.type, req.status, count(*) as count
ORDER BY req.type, req.status
```

#### Pattern 11: Subgraph Extraction
```cypher
// Extract subgraph for a specific epic
MATCH path = (epic:Requirement {id: "EPIC-001"})-[:DECOMPOSES_TO*]->(child)
WITH collect(path) as paths
CALL apoc.graph.fromPaths(paths, 'subgraph', {})
YIELD graph
RETURN graph
```

## SQLite with Graph Schema

For lightweight deployments, SQLite can support graph queries:

### Schema Design
```sql
CREATE TABLE nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    properties JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE edges (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    properties JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES nodes(id),
    FOREIGN KEY (target_id) REFERENCES nodes(id)
);

CREATE INDEX idx_edges_source ON edges(source_id);
CREATE INDEX idx_edges_target ON edges(target_id);
CREATE INDEX idx_edges_type ON edges(edge_type);
```

### Recursive Queries (SQLite 3.8.3+)
```sql
-- Find all descendants
WITH RECURSIVE descendants(id, level) AS (
  SELECT id, 0 FROM nodes WHERE id = 'EPIC-001'
  UNION ALL
  SELECT e.target_id, d.level + 1
  FROM descendants d
  JOIN edges e ON d.id = e.source_id
  WHERE e.edge_type = 'DECOMPOSES_TO'
)
SELECT * FROM nodes WHERE id IN (SELECT id FROM descendants);
```

### Graph Algorithms in SQLite

#### Transitive Closure
```sql
-- Precompute transitive closure for performance
CREATE TABLE transitive_closure (
    ancestor_id TEXT,
    descendant_id TEXT,
    distance INTEGER,
    PRIMARY KEY (ancestor_id, descendant_id)
);

-- Populate transitive closure
WITH RECURSIVE closure(ancestor, descendant, dist) AS (
  SELECT source_id, target_id, 1 FROM edges WHERE edge_type = 'DECOMPOSES_TO'
  UNION ALL
  SELECT c.ancestor, e.target_id, c.dist + 1
  FROM closure c
  JOIN edges e ON c.descendant = e.source_id
  WHERE e.edge_type = 'DECOMPOSES_TO' AND c.dist < 10
)
INSERT INTO transitive_closure SELECT * FROM closure;
```

## Hybrid Approach: SQLite + Neo4j

### Strategy
- **SQLite**: Primary storage, CRUD operations, versioning
- **Neo4j**: Complex graph queries, visualization, analytics

### Synchronization
```python
class HybridStorage:
    def __init__(self, sqlite_path: str, neo4j_uri: str):
        self.sqlite = SQLiteStorage(sqlite_path)
        self.neo4j = Neo4jStorage(neo4j_uri)
    
    def create_requirement(self, req: Requirement):
        # Write to SQLite (source of truth)
        self.sqlite.create_requirement(req)
        # Sync to Neo4j (for queries)
        self.neo4j.create_node(req)
    
    def create_link(self, link: Link):
        self.sqlite.create_link(link)
        self.neo4j.create_relationship(link)
    
    def query_graph(self, cypher: str):
        # Use Neo4j for complex queries
        return self.neo4j.query(cypher)
```

## Performance Considerations

### Neo4j Performance
- **Index**: Create indexes on frequently queried properties
- **Constraints**: Unique constraints for IDs
- **Query optimization**: Use EXPLAIN to analyze queries
- **Caching**: Enable query caching

```cypher
// Create indexes
CREATE INDEX req_id FOR (r:Requirement) ON (r.id);
CREATE INDEX req_type FOR (r:Requirement) ON (r.type);
CREATE INDEX req_status FOR (r:Requirement) ON (r.status);

// Create constraints
CREATE CONSTRAINT req_id_unique FOR (r:Requirement) REQUIRE r.id IS UNIQUE;
```

### SQLite Performance
- **Indexes**: On foreign keys and frequently queried columns
- **Materialized views**: For complex queries
- **Batch operations**: Use transactions for bulk inserts
- **WAL mode**: Write-Ahead Logging for concurrency

```sql
-- Enable WAL mode
PRAGMA journal_mode=WAL;

-- Optimize for read-heavy workloads
PRAGMA cache_size=-64000;  -- 64MB cache
PRAGMA temp_store=MEMORY;
```

## Graph Visualization

### Export to Visualization Tools
- **Gephi**: Export as GEXF format
- **Cytoscape**: Export as GraphML
- **D3.js**: Export as JSON
- **Neo4j Browser**: Native visualization

### Example: Export to JSON
```python
def export_graph_json(storage: GraphStorage, root_id: str):
    nodes = []
    edges = []
    
    # BFS traversal
    visited = set()
    queue = [root_id]
    
    while queue:
        node_id = queue.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)
        
        node = storage.get_node(node_id)
        nodes.append({"id": node.id, "label": node.title, "type": node.type})
        
        for edge in storage.get_edges(node_id):
            edges.append({
                "source": edge.source_id,
                "target": edge.target_id,
                "type": edge.edge_type
            })
            queue.append(edge.target_id)
    
    return {"nodes": nodes, "edges": edges}
```

