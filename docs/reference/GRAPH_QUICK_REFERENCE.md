# Graph Database Quick Reference for Specification Traceability

## Database Selection Matrix

| Use Case | Recommended DB | Alternative | Query Language |
|----------|---|---|---|
| Fast transactional queries | Neo4j | ArangoDB | Cypher |
| Semantic reasoning/compliance | RDF/OWL | Neptune | SPARQL |
| Relationship analysis | Neo4j | TigerGraph | Cypher |
| Large-scale analytics | TigerGraph | Neptune | GSQL |
| Link prediction/ML | Embeddings (TransE) | RotatE | PyTorch |
| Audit trail/provenance | PROV model | Neo4j + audit | RDF + PROV-O |
| Version history | Temporal graphs | SQLAlchemy | Custom temporal |
| Multi-way relationships | Hypergraphs | Neo4j + expand | Python dict |

---

## Neo4j Cypher Quick Patterns

### Create Requirement Node
```cypher
CREATE (r:Requirement {
    id: 'REQ-001',
    title: 'User Login',
    status: 'APPROVED',
    priority: 'HIGH',
    created: datetime()
})
```

### Find All Unverified Requirements
```cypher
MATCH (r:Requirement {status: 'APPROVED'})
WHERE NOT (r)-[:VERIFIED_BY]->(:TestCase)
RETURN r.id, r.title
```

### Calculate Requirement-Test Coverage
```cypher
MATCH (r:Requirement)-[:VERIFIED_BY]->(t:TestCase)
WITH r, count(t) as test_count, avg(t.assertion_count) as avg_assertions
RETURN r.id, r.title, test_count, avg_assertions
ORDER BY test_count DESC
```

### Find Impact of Requirement Change
```cypher
MATCH (req:Requirement {id: 'REQ-001'})
CALL apoc.path.expandConfig(req, {
    relationshipFilter: 'DEPENDS_ON|ADDRESSES|IMPLEMENTS',
    minLevel: 1,
    maxLevel: 4,
    bfs: true
})
YIELD path
RETURN length(path) as depth, [n in nodes(path) | n.id] as affected_ids
ORDER BY depth
```

### Betweenness Centrality (Find Critical Requirements)
```cypher
MATCH (req:Requirement)
CALL apoc.algo.betweenness('Requirement', 'DEPENDS_ON', 'OUTGOING')
YIELD node, score
RETURN node.id, score
ORDER BY score DESC
LIMIT 10
```

### Requirement Version History
```cypher
MATCH (current:Requirement {id: 'REQ-001'})
OPTIONAL MATCH path = (current)-[:SUPERSEDES*]->(previous:Requirement)
RETURN length(path) as version,
       [n in nodes(path) | {id: n.id, updated: n.updated_at}] as history
ORDER BY version DESC
```

---

## SPARQL Quick Patterns (RDF)

### Find Requirements Without Design Justification
```sparql
PREFIX req: <http://example.org/requirement#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?req ?label
WHERE {
    ?req a req:Requirement ;
        req:hasStatus req:APPROVED ;
        rdfs:label ?label .
    FILTER NOT EXISTS { ?req req:addresses ?design . }
    FILTER NOT EXISTS { ?req req:verifiedBy ?test . }
}
```

### Requirement Dependency Chain (Transitive)
```sparql
PREFIX req: <http://example.org/requirement#>

SELECT ?start ?end (COUNT(DISTINCT ?step) as ?chain_length)
WHERE {
    ?start req:dependsOn+ ?end .
    FILTER (?start != ?end)
}
GROUP BY ?start ?end
HAVING (COUNT(DISTINCT ?step) > 1)
ORDER BY DESC(?chain_length)
```

### Coverage Metrics by Component
```sparql
PREFIX req: <http://example.org/requirement#>
PREFIX test: <http://example.org/test#>

SELECT ?component
       (COUNT(?req) as ?total_reqs)
       (COUNT(?test) as ?total_tests)
       (ROUND(100 * COUNT(?test) / COUNT(?req)) as ?coverage_pct)
WHERE {
    ?req a req:Requirement ;
        req:addresses ?component .
    OPTIONAL { ?test a test:TestCase ; test:tests ?component . }
}
GROUP BY ?component
ORDER BY DESC(?coverage_pct)
```

---

## Python Integration Examples

### Neo4j Basic Operations
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))

# Create node
with driver.session() as session:
    session.write_transaction(lambda tx: tx.run(
        "CREATE (r:Requirement {id: $id, title: $title})",
        id="REQ-001", title="User Login"
    ))

# Query
with driver.session() as session:
    result = session.read_transaction(lambda tx: tx.run(
        "MATCH (r:Requirement) WHERE r.status = $status RETURN r.id, r.title",
        status="APPROVED"
    ))
    for record in result:
        print(record["r.id"], record["r.title"])

driver.close()
```

### RDF/SPARQL Basic Operations
```python
from rdflib import Graph, Namespace, URIRef, Literal

graph = Graph()
req_ns = Namespace("http://example.org/requirement#")

# Add requirement
graph.add((
    req_ns.REQ001,
    URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
    req_ns.Requirement
))

# Query
results = graph.query("""
    PREFIX req: <http://example.org/requirement#>
    SELECT ?req WHERE { ?req a req:Requirement }
""")

for row in results:
    print(row.req)
```

### Impact Analysis
```python
# Neo4j impact propagation
def get_impacted_entities(driver, requirement_id):
    with driver.session() as session:
        query = """
        MATCH (r:Requirement {id: $req_id})
        CALL apoc.path.expandConfig(r, {
            relationshipFilter: 'DEPENDS_ON|ADDRESSES|TESTS',
            minLevel: 1,
            maxLevel: 4
        })
        YIELD path
        RETURN length(path) as depth, [n in nodes(path) | labels(n)[0]] as types
        """
        return session.run(query, req_id=requirement_id).data()

impacts = get_impacted_entities(driver, "REQ-001")
for impact in impacts:
    print(f"Depth {impact['depth']}: {impact['types']}")
```

---

## Common Cypher Mistakes & Fixes

| Issue | Wrong | Correct |
|-------|-------|---------|
| Wrong label syntax | `(r.Requirement)` | `(r:Requirement)` |
| Missing MATCH | `RETURN r.id` | `MATCH (r) RETURN r.id` |
| Comparing nodes | `a = b` | `a.id = b.id` |
| Missing relationship | `(a)--(b)` | `(a)-[:RELATES]->(b)` |
| String concatenation | `+ str` | `apoc.text.concat()` |
| Case sensitive | `WHERE status = 'Active'` | `WHERE status = 'ACTIVE'` |

---

## Common SPARQL Mistakes & Fixes

| Issue | Wrong | Correct |
|-------|-------|---------|
| Unbound namespace | `req:Requirement` | `PREFIX req: <...> req:Requirement` |
| Type mismatch | `COUNT(?x) > 5` | `HAVING (COUNT(?x) > 5)` |
| Missing optional | `?x ?prop ?value` | `OPTIONAL { ?x ?prop ?value }` |
| Not filtering null | `WHERE ?x = ?y` | `WHERE bound(?x) && bound(?y)` |
| Wrong transitive | `?a req:rel ?b` | `?a req:rel+ ?b` |

---

## Performance Tips

### Neo4j
1. Always use indexes for WHERE clause properties
2. Use `apoc.periodic.iterate` for bulk updates
3. Avoid expensive Cartesian products (use `with distinct`)
4. Use `EXPLAIN` before optimizing complex queries
5. Set `LIMIT` for large result sets
6. Use relationships instead of property searches

### RDF
1. Use FILTER after OPTIONAL to avoid nulls
2. Limit UNION queries (expensive)
3. Pre-compute transitive closures in materialized views
4. Index frequently searched properties
5. Use LIMIT in CONSTRUCT queries
6. Avoid string operations on URIs

### Hybrid (Neo4j + RDF)
1. Neo4j for hot path queries (coverage, dependencies)
2. RDF for compliance validation (rules, inference)
3. Sync daily from Neo4j → RDF for reasoning
4. Cache semantic query results (24-48 hours)
5. Use Neo4j for real-time, RDF for batch processing

---

## Monitoring Queries

### Check Index Usage
```cypher
SHOW INDEXES
YIELD name, type, populationPercent, state
RETURN name, type, populationPercent, state
```

### Find Slow Queries
```cypher
CALL dbms.queryJmx('jmxquery')
YIELD queryId, query, elapsedTimeInMs, allocatedBytes
WHERE elapsedTimeInMs > 1000
RETURN query, elapsedTimeInMs
ORDER BY elapsedTimeInMs DESC
```

### Check Database Size
```cypher
CALL db.stats.retrieve('KERNEL_STATS')
YIELD value
WHERE value.name = 'relationship-count'
RETURN value
```

### Node/Relationship Counts
```cypher
MATCH (n) RETURN labels(n) as type, count(n) as count
UNION ALL
MATCH ()-[r]-() RETURN type(r) as type, count(r) as count
```

---

## Deployment Checklist

- [ ] Neo4j instance running and accessible
- [ ] Indexes created for all hot-path properties
- [ ] Constraints enforced (uniqueness)
- [ ] Backup strategy configured
- [ ] Authentication enabled (not default credentials)
- [ ] APOC library installed
- [ ] RDF store configured (if using semantic layer)
- [ ] Sync service scheduled (if bidirectional)
- [ ] Monitoring alerts configured
- [ ] Query timeouts set (prevent runaway queries)
- [ ] Connection pooling configured
- [ ] Documentation updated
- [ ] Integration tests passing
- [ ] Performance benchmarks baseline established

---

## Troubleshooting

### Neo4j Connection Issues
```python
# Test connectivity
from neo4j
import GraphDatabase

try:
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
    with driver.session() as session:
        result = session.run("RETURN 1")
        print("Connected!")
    driver.close()
except Exception as e:
    print(f"Connection failed: {e}")
```

### Query Timeout
```cypher
-- Add LIMIT to reduce result set
MATCH (r:Requirement) RETURN r LIMIT 1000

-- Use index for filtering
CREATE INDEX idx_requirement_status FOR (r:Requirement) ON (r.status)
MATCH (r:Requirement {status: 'APPROVED'}) RETURN r
```

### Memory Issues
```cypher
-- Use CALL apoc.periodic.iterate for bulk operations
CALL apoc.periodic.iterate(
    "MATCH (r:Requirement) RETURN r",
    "SET r.updated = datetime()",
    {batchSize: 1000}
)
```

### RDF Query Slow
```sparql
-- Add FILTER conditions early
SELECT ?req WHERE {
    ?req a req:Requirement ;
         req:hasStatus req:APPROVED .  -- Filter early
    ?req req:verifiedBy ?test .
}

-- Limit result set
SELECT ?req WHERE { ... } LIMIT 100
```

---

## Resources

- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual
- RDF/SPARQL Spec: https://www.w3.org/TR/sparql11-query/
- rdflib Documentation: https://rdflib.readthedocs.io/
- APOC Library: https://neo4j.com/docs/apoc/current/
- Graph Algorithms: https://neo4j.com/docs/graph-data-science/

---

## Key Formulas

### Coverage Percentage
```
Coverage % = (Tests Verifying Requirement / Total Tests) × 100
```

### Impact Depth
```
Impact = Σ(number_of_affected_entities_at_each_level) × level_weight
```

### Requirement Criticality
```
Criticality = Betweenness_Centrality × Dependency_Count × Priority_Score
```

### Traceability Completeness
```
Completeness = (Requirements_with_Tests + Requirements_with_Design) / Total_Requirements
```

### Semantic Compliance Score
```
Compliance =
  0.4 × (Completeness_Score) +
  0.4 × (Test_Coverage_Ratio) +
  0.2 × (Design_Justification_Ratio)
```

