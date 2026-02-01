# Neo4j Community Detection Queries
## Ready-to-Use Cypher for Your Traceability Graph

---

## Overview

These queries implement community detection algorithms from Neo4j Graph Data Science (GDS) library. They identify naturally occurring clusters in your dependency graph that can be used for automatic aggregation.

**Prerequisites:**
- Neo4j 4.4+
- Neo4j Graph Data Science library installed
- Graph projection created for your item/link data

---

## Setup: Create Graph Projection

```cypher
// Create projection including all relationships
CALL gds.graph.project(
  'traceability_graph',
  ['Item'],                    // Node labels
  ['LINKS_TO', 'DEPENDS_ON', 'IMPLEMENTS', 'TESTS'],  // Relationship types
  {
    relationshipProperties: ['type', 'weight'],
    nodeProperties: ['type', 'status']
  }
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;

// Verify projection
CALL gds.graph.list()
WHERE graphName = 'traceability_graph'
RETURN *;
```

---

## Algorithm 1: Louvain Community Detection

**Best for:** Balanced, accurate clustering; most commonly used

**Complexity:** O(n log n) where n = node count

**Parameters:**
- `maxIterations`: 10 (default) - iterations to stabilize
- `tolerance`: 0.0001 - stopping criterion
- `relationshipWeightProperty`: 'weight' (optional)

### Query 1A: Basic Louvain with Statistics

```cypher
// Run Louvain algorithm and get statistics
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId, intermediateCommunityIds
WITH gds.util.asNode(nodeId) as node, communityId, intermediateCommunityIds
RETURN
  node.id as itemId,
  node.type as itemType,
  communityId,
  size(intermediateCommunityIds) as hierarchyDepth
ORDER BY communityId, itemId
LIMIT 100;
```

### Query 1B: Get Community Statistics

```cypher
// Get statistics about detected communities
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) as node, communityId
WITH communityId, collect(node) as members, count(*) as size
RETURN
  communityId,
  size,
  [m IN members | m.type] as types,
  [m IN members | m.id][0..3] as sampleMembers
ORDER BY size DESC;
```

### Query 1C: Write Communities Back to Graph

```cypher
// Write detected communities back to database for persistence
CALL gds.louvain.write(
  'traceability_graph',
  {
    writeProperty: 'community_id',
    maxIterations: 10,
    seed: 42  // For reproducible results
  }
)
YIELD communityCount, modularity, ranLevels
RETURN communityCount, modularity, ranLevels;

// Verify written properties
MATCH (n:Item)
WHERE n.community_id IS NOT NULL
RETURN count(DISTINCT n.community_id) as totalCommunities;
```

### Query 1D: Hierarchical Communities (Multi-level)

```cypher
// Get hierarchical community structure
CALL gds.louvain.stream(
  'traceability_graph',
  { includeIntermediateCommunities: true }
)
YIELD nodeId, communityId, intermediateCommunityIds
WITH gds.util.asNode(nodeId) as node, communityId, intermediateCommunityIds
RETURN
  node.id,
  node.type,
  'Level 0' as level,
  communityId as community
UNION ALL
WITH gds.util.asNode(nodeId) as node, intermediateCommunityIds
UNWIND range(0, size(intermediateCommunityIds) - 1) as level
RETURN
  node.id,
  node.type,
  'Level ' + (level + 1) as level,
  intermediateCommunityIds[level] as community
ORDER BY level, community;
```

---

## Algorithm 2: Label Propagation

**Best for:** Fast, distributed; works with directed graphs

**Complexity:** O(k * m) where k = iterations, m = edges

**Use when:** Louvain is too slow, need near-real-time results

### Query 2A: Basic Label Propagation

```cypher
CALL gds.labelPropagation.stream('traceability_graph')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) as node, communityId
RETURN
  node.id as itemId,
  node.type as itemType,
  communityId
ORDER BY communityId, itemId;
```

### Query 2B: Label Propagation with Seed Communities

```cypher
// Initialize with existing community assignments if available
CALL gds.labelPropagation.stream(
  'traceability_graph',
  {
    seedProperty: 'existing_community',  // Existing cluster assignments
    maxIterations: 5
  }
)
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) as node, communityId
RETURN
  node.id,
  node.type,
  communityId
ORDER BY communityId;
```

### Query 2C: Compare Communities Over Time

```cypher
// Track how communities change between runs
WITH datetime() as runTime
CALL gds.labelPropagation.stream('traceability_graph')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) as node, communityId, runTime
MATCH (node)-[r:COMMUNITY_HISTORY]->()
SET r.validUntil = runTime
CREATE (node)-[:COMMUNITY_HISTORY {
  communityId: communityId,
  detectedAt: runTime,
  algorithm: 'label_propagation'
}]->(h:CommunityHistory)
SET h.id = randomUuid()
RETURN count(h) as communitiesDetected;
```

---

## Algorithm 3: Weakly Connected Components (WCC)

**Best for:** Finding disconnected subgraphs, islands in graph

**Use when:** You want to separate the graph into independent regions

### Query 3A: Find Connected Components

```cypher
CALL gds.wcc.stream('traceability_graph')
YIELD nodeId, componentId
WITH gds.util.asNode(nodeId) as node, componentId
RETURN
  componentId,
  count(*) as size,
  collect(node.id)[0..5] as sample
ORDER BY size DESC;
```

### Query 3B: Identify Isolated Regions

```cypher
// Find and highlight isolated connected components
CALL gds.wcc.stream('traceability_graph')
YIELD nodeId, componentId
WITH componentId, count(*) as size
WHERE size < 5  // Small isolated regions
RETURN componentId, size;
```

---

## Algorithm Comparison Queries

### Query 4A: Compare Louvain vs Label Propagation

```cypher
// Run both algorithms and compare results
CALL {
  CALL gds.louvain.stream('traceability_graph')
  YIELD nodeId, communityId
  RETURN nodeId, 'louvain' as algorithm, communityId
}
UNION ALL
CALL {
  CALL gds.labelPropagation.stream('traceability_graph')
  YIELD nodeId, communityId
  RETURN nodeId, 'labelPropagation' as algorithm, communityId
}
WITH *
MATCH (n) WHERE id(n) = nodeId
RETURN
  n.id as itemId,
  algorithm,
  communityId
ORDER BY itemId, algorithm;
```

### Query 4B: Modularity Calculation

```cypher
// Calculate modularity score (higher = better clustering)
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) as node, communityId
RETURN
  'Louvain Modularity' as metric,
  gds.modularity('traceability_graph', communityId) as score;
```

---

## Integration Queries: Convert Communities to Aggregates

### Query 5A: Create Aggregate Items from Communities

```cypher
// Create virtual aggregate items representing communities
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId)) as members
CREATE (aggregate:AggregateItem {
  id: 'aggregate-' + communityId,
  title: 'Community ' + communityId + ' (' + size(members) + ')',
  type: 'community_aggregate',
  childCount: size(members),
  memberIds: [m.id in members],
  aggregation_algorithm: 'louvain',
  detected_at: datetime(),
  status: 'active'
})
RETURN aggregate;
```

### Query 5B: Create CONTAINS Relationships

```cypher
// Link aggregate items to their members
MATCH (agg:AggregateItem)
WHERE agg.aggregation_algorithm = 'louvain'
WITH agg, agg.memberIds as memberIds
UNWIND memberIds as memberId
MATCH (item:Item {id: memberId})
CREATE (agg)-[:CONTAINS]->(item)
RETURN count(*) as relationshipsCreated;
```

### Query 5C: Create EXTERNAL Relationships

```cypher
// Create edges from aggregates to external communities
MATCH (agg1:AggregateItem)-[:CONTAINS]->(item1:Item)
MATCH (item1)-[link:LINKS_TO|DEPENDS_ON|IMPLEMENTS|TESTS]->(item2:Item)
MATCH (agg2:AggregateItem)-[:CONTAINS]->(item2)
WHERE agg1 <> agg2
CREATE (agg1)-[:EXTERNAL_LINK {
  type: type(link),
  count: 1
}]->(agg2)
RETURN count(*) as externalLinks;

// Merge duplicates and count
MATCH (agg1:AggregateItem)-[link:EXTERNAL_LINK]->(agg2:AggregateItem)
WITH agg1, agg2, type(link) as linkType, count(*) as count
SET link.count = count
RETURN agg1.id, agg2.id, linkType, link.count;
```

---

## Export Queries: For Frontend Integration

### Query 6A: Export Communities for React Flow

```cypher
// Export as JSON structure for frontend
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH communityId, collect({
  nodeId: nodeId,
  nodeLabel: (gds.util.asNode(nodeId)).id,
  type: (gds.util.asNode(nodeId)).type
}) as members
RETURN {
  communityId: communityId,
  size: size(members),
  members: members
} as community
ORDER BY communityId;
```

### Query 6B: Export Full Aggregation Metadata

```cypher
// Complete export for REST API
MATCH (item:Item)
WITH item
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WHERE id(item) = nodeId
WITH item, communityId, collect(item) as groupItems
RETURN {
  communityId: communityId,
  size: count(groupItems),
  label: 'Community ' + communityId + ' (' + count(groupItems) + ')',
  items: [i.id in groupItems | i.id],
  types: distinct([i.type in groupItems | i.type]),
  status: 'detected'
} as aggregation;
```

### Query 6C: REST API Endpoint Template

```cypher
// Template for REST API that returns communities
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId)) as members
WITH communityId, members, size(members) as memberCount
RETURN {
  id: 'community-' + communityId,
  type: 'community_aggregate',
  label: 'Cluster ' + communityId,
  nodeCount: memberCount,
  childNodeIds: [m.id in members],
  externalIncoming: 0,  // Will be computed separately
  externalOutgoing: 0,  // Will be computed separately
  algorithm: 'louvain',
  confidence: 0.95
} as aggregateNode;
```

---

## Incremental Update Queries

### Query 7A: Check If Communities Changed

```cypher
// Compare current communities with previous run
MATCH (n:Item)
WHERE n.community_id IS NOT NULL
WITH n.community_id as old_community, count(*) as old_size
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) as node, communityId
WITH communityId, count(*) as new_size
MATCH (item:Item {community_id: old_community})
RETURN
  old_community,
  communityId as new_community,
  old_size,
  new_size,
  abs(old_size - new_size) as size_change,
  CASE WHEN old_size <> new_size THEN 'CHANGED' ELSE 'STABLE' END as status;
```

### Query 7B: Update Only Changed Communities

```cypher
// Only update items that moved to different communities
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) as node, communityId
WHERE node.community_id <> communityId
SET node.community_id = communityId,
    node.community_changed_at = datetime()
RETURN count(*) as itemsUpdated;
```

---

## Performance Tuning Queries

### Query 8A: Check Graph Density

```cypher
// Understand graph characteristics (impacts algorithm choice)
CALL {
  MATCH (n:Item) RETURN count(n) as nodeCount
}
CALL {
  MATCH ()-[]->() RETURN count(*) as relationshipCount
}
RETURN
  nodeCount,
  relationshipCount,
  relationshipCount * 1.0 / (nodeCount * (nodeCount - 1)) as density,
  CASE
    WHEN relationshipCount * 1.0 / (nodeCount * (nodeCount - 1)) > 0.5 THEN 'DENSE (use Louvain)'
    WHEN relationshipCount * 1.0 / (nodeCount * (nodeCount - 1)) > 0.1 THEN 'MODERATE (use LPA)'
    ELSE 'SPARSE (use WCC)'
  END as recommendation;
```

### Query 8B: Find Algorithm Bottlenecks

```cypher
// Identify nodes with unusually high degree (might slow down computation)
MATCH (n:Item)
WITH n, size((n)--()) as degree
WHERE degree > 50  // High threshold
RETURN
  n.id,
  n.type,
  degree
ORDER BY degree DESC
LIMIT 20;
```

---

## Validation Queries

### Query 9A: Validate Community Quality

```cypher
// Metrics to assess community detection quality
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId)) as members
WITH communityId, members, size(members) as size
WHERE size > 1  // Ignore isolated nodes
RETURN
  communityId,
  size,
  CASE
    WHEN size < 3 THEN 'VERY_SMALL'
    WHEN size < 10 THEN 'SMALL'
    WHEN size < 50 THEN 'MEDIUM'
    ELSE 'LARGE'
  END as category,
  count(*) as count_in_category
ORDER BY size DESC;
```

### Query 9B: Check Member Cohesion

```cypher
// For each community, calculate how tightly connected members are
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH communityId, collect(nodeId) as nodeIds
MATCH (n)-[r]->(m)
WHERE id(n) IN nodeIds AND id(m) IN nodeIds
WITH communityId, count(r) as internal_links
MATCH (n)-[r]->(m)
WHERE id(n) IN nodeIds AND id(m) NOT IN nodeIds
WITH communityId, internal_links, count(r) as external_links
RETURN
  communityId,
  internal_links,
  external_links,
  internal_links * 1.0 / (internal_links + external_links) as cohesion_ratio
ORDER BY cohesion_ratio DESC;
```

---

## Example Workflow: End-to-End

```cypher
// Step 1: Project graph
CALL gds.graph.project(
  'traceability_graph',
  ['Item'],
  ['LINKS_TO', 'DEPENDS_ON', 'IMPLEMENTS', 'TESTS']
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;

// Step 2: Run community detection
CALL gds.louvain.write(
  'traceability_graph',
  { writeProperty: 'community_id' }
)
YIELD communityCount, modularity
RETURN communityCount, modularity;

// Step 3: Create aggregates
CALL gds.louvain.stream('traceability_graph')
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId)) as members
CREATE (aggregate:AggregateItem {
  id: 'aggregate-' + communityId,
  title: 'Community ' + communityId,
  childCount: size(members),
  memberIds: [m.id in members]
});

// Step 4: Export for API
MATCH (agg:AggregateItem)
RETURN collect({
  id: agg.id,
  label: agg.title,
  childCount: agg.childCount,
  childNodeIds: agg.memberIds,
  type: 'community_aggregate'
}) as aggregates;
```

---

## API Response Format

```json
{
  "aggregates": [
    {
      "id": "aggregate-0",
      "label": "Community 0 (42 items)",
      "aggregateType": "community-detection",
      "childNodeIds": [
        "component-button",
        "component-alert",
        "component-modal",
        "...",
      ],
      "childCount": 42,
      "externalIncoming": 8,
      "externalOutgoing": 12,
      "internalConnections": 156,
      "algorithm": "louvain",
      "modularity": 0.68,
      "confidence": 0.95,
      "detectedAt": "2026-01-24T10:30:00Z"
    },
    {
      "id": "aggregate-1",
      "label": "Community 1 (28 items)",
      "..."
    }
  ]
}
```

---

## Troubleshooting

### Issue: Graph Projection Fails

```cypher
// Check existing projections
CALL gds.graph.list() YIELD graphName;

// Drop and recreate if needed
CALL gds.graph.drop('traceability_graph', false)
YIELD graphName;

// Recreate with simpler parameters
CALL gds.graph.project(
  'traceability_graph',
  'Item',
  'LINKS_TO'
)
YIELD graphName;
```

### Issue: Community Detection Takes Too Long

```cypher
// Use faster algorithm
CALL gds.labelPropagation.stream(
  'traceability_graph',
  { maxIterations: 5 }  // Reduce iterations
)
YIELD nodeId, communityId
RETURN *;
```

### Issue: Too Many/Too Few Communities

```cypher
// Adjust resolution parameter (higher = more communities)
CALL gds.louvain.stream(
  'traceability_graph',
  { tolerance: 0.001 }  // Higher tolerance = fewer iterations = fewer communities
)
YIELD nodeId, communityId
RETURN *;
```

---

## Scheduled Update Script

```cypher
// Schedule this to run periodically (e.g., daily via cron)
CALL {
  CALL gds.graph.project(
    'traceability_graph',
    ['Item'],
    ['LINKS_TO', 'DEPENDS_ON', 'IMPLEMENTS', 'TESTS']
  )
  YIELD graphName
}
CALL gds.louvain.write(
  'traceability_graph',
  { writeProperty: 'community_id' }
)
YIELD communityCount, modularity
WITH communityCount, modularity
CALL {
  MATCH (item:Item)
  WHERE item.community_id IS NOT NULL
  RETURN count(*) as updated
}
CALL gds.graph.drop('traceability_graph')
YIELD graphName
RETURN
  'Community detection completed' as status,
  communityCount as clusters_found,
  modularity as quality_score,
  updated as items_updated,
  datetime() as timestamp;
```

---

## References

- [Neo4j GDS Louvain](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/)
- [Neo4j GDS Label Propagation](https://neo4j.com/docs/graph-data-science/current/algorithms/label-propagation/)
- [Neo4j GDS WCC](https://neo4j.com/docs/graph-data-science/current/algorithms/wcc/)
- [Modularity in Community Detection](https://en.wikipedia.org/wiki/Modularity_(networks))

---

**Last Updated:** January 24, 2026
**Status:** Ready for Neo4j Integration
