# Neo4j Multi-Project Quick Reference

## 🎯 Best Approach: Hybrid Label + Property

**One-liner:** Use labels for fast queries, properties for isolation, relationships for ownership.

---

## 📋 Quick Setup (25 minutes)

### Step 1: Create Project Nodes (2 min)
```cypher
CREATE (:Project {
  id: "proj_bifrost_001",
  name: "bifrost",
  created_at: timestamp()
})
```

### Step 2: Create Indexes (2 min)
```cypher
CREATE INDEX FOR (m:Model) ON (m.project_id)
CREATE INDEX FOR (m:Model) ON (m.id)
```

### Step 3: Add project_id to Nodes (5 min)
```cypher
MATCH (m:Model)
SET m.project_id = "proj_bifrost_001"
```

### Step 4: Create OWNS Relationships (5 min)
```cypher
MATCH (p:Project {id: "proj_bifrost_001"}), (m:Model {project_id: "proj_bifrost_001"})
CREATE (p)-[:OWNS]->(m)
```

### Step 5: Go Integration (10 min)
```go
// Add to context
ctx := context.WithValue(context.Background(), "project_id", "proj_bifrost_001")

// Query with isolation
query := `MATCH (m:Model {project_id: $projectId}) RETURN m`
result, _ := session.Run(ctx, query, map[string]interface{}{
    "projectId": projectID,
})
```

---

## 🔍 Query Patterns

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

### Find Orphaned Nodes
```cypher
MATCH (n) 
WHERE NOT exists(n.project_id)
RETURN count(n) as orphaned_count
```

---

## 📊 Node Allocation

```
Total: 200,000 nodes

4 Projects × 50,000 nodes each:
├── Models:        5,000
├── Embeddings:   15,000
├── Relationships: 15,000
└── Metadata:     15,000
```

---

## ✅ Comparison

| Feature | Label | Relationship | Hybrid ✅ |
|---------|-------|--------------|----------|
| Speed | ⚡⚡⚡ | ⚡ | ⚡⚡⚡ |
| Isolation | ⚠️ | ⚠️ | ✅ |
| Auditability | ⚠️ | ✅ | ✅ |
| Scalability | ⚠️ | ⚠️ | ✅ |
| Setup | 5 min | 15 min | 20 min |

---

## 🔒 Security

```go
// 1. Extract project from auth
projectID := getProjectFromAuth(token)

// 2. Add to context
ctx := WithProjectID(context.Background(), projectID)

// 3. Validate in queries
query := `MATCH (m:Model {project_id: $projectId}) RETURN m`

// 4. Reject mismatches
if model.ProjectID != requestProjectID {
    return error("unauthorized")
}
```

---

## 🚀 Implementation Checklist

- [ ] Create Project nodes
- [ ] Create indexes
- [ ] Add project_id to all nodes
- [ ] Create OWNS relationships
- [ ] Add ProjectContext to Go
- [ ] Add ProjectContextMiddleware
- [ ] Update queries with project_id
- [ ] Test project isolation
- [ ] Deploy to staging
- [ ] Monitor node distribution
- [ ] Deploy to production

---

## 📚 Full Documentation

1. **NEO4J_MULTI_PROJECT_STRATEGY.md** - Detailed strategy
2. **NEO4J_TRACERTM_IMPLEMENTATION.md** - Go integration
3. **NEO4J_APPROACH_COMPARISON.md** - Why hybrid is best

---

## 💡 Key Points

✅ **Labels** = Fast indexed queries (O(1))
✅ **Properties** = Data isolation (project_id)
✅ **Relationships** = Ownership tracking (OWNS)
✅ **Application** = Validation layer (security)

---

## 🎯 Why This Works

1. **Performance**: Label-indexed queries are fast
2. **Isolation**: project_id property prevents leaks
3. **Auditability**: OWNS relationships track ownership
4. **Scalability**: Supports 4+ projects
5. **Flexibility**: Easy to add new projects
6. **Security**: Application-level validation

---

## ⚡ Performance Metrics

- Query speed: O(1) with label index
- Node allocation: 50K per project
- Total capacity: 4 projects
- Setup time: 25 minutes
- Maintenance: Low

---

## 🔧 Troubleshooting

**Problem**: Slow queries
**Solution**: Verify indexes exist
```cypher
SHOW INDEXES
```

**Problem**: Orphaned nodes
**Solution**: Add project_id to all nodes
```cypher
MATCH (n) WHERE NOT exists(n.project_id)
SET n.project_id = "proj_default_001"
```

**Problem**: Data leaks
**Solution**: Validate project_id in all queries
```go
if model.ProjectID != requestProjectID {
    return error("unauthorized")
}
```

---

## 📞 Support

Questions? Check:
1. NEO4J_MULTI_PROJECT_STRATEGY.md
2. NEO4J_TRACERTM_IMPLEMENTATION.md
3. NEO4J_APPROACH_COMPARISON.md

Ready to implement! 🚀

