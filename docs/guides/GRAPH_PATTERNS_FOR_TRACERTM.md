# Graph Database Patterns Tailored for TracertRTM

## Project Context

TracertRTM uses:
- SQLAlchemy ORM for relational data (Items, Links, Projects)
- FastAPI for REST/WebSocket APIs
- Existing graph models (Graph, GraphNode, GraphType)
- Specification models (ADR, Contract, Feature, Scenario)
- Integration models (GitHub, Linear, webhooks)

## Architecture Decision: Hybrid Neo4j + RDF

**Recommendation**: Use Neo4j as primary graph store with RDF for semantic validation.

**Why**:
1. Your existing Item/Link model maps directly to Neo4j property graph
2. Cypher queries align with existing GraphService patterns
3. RDF adds semantic compliance checking without breaking existing architecture
4. Both support Python integration cleanly
5. You can phase implementation: start Neo4j, add RDF later

---

## Pattern 1: Migrating Existing Graph Model to Neo4j

Your current SQLAlchemy models:

```python
# Current: SQL-backed graph
class Graph(Base, TimestampMixin):
    __tablename__ = "graphs"
    id: str  # UUID
    project_id: str  # Foreign key
    graph_type: str  # "dependency", "architecture", "test"
    root_item_id: str  # Optional root
    graph_rules: dict  # Validation rules
    graph_metadata: dict  # Custom metadata

class Link(Base, TimestampMixin):
    __tablename__ = "links"
    source_item_id: str
    target_item_id: str
    link_type: str  # "implements", "tests", "depends_on"
    link_metadata: dict
```

### Neo4j Mapping

```python
# src/tracertm/services/neo4j_graph_migration.py
from neo4j import GraphDatabase
from sqlalchemy.orm import Session
from tracertm.models.graph import Graph
from tracertm.models.link import Link
from tracertm.models.item import Item
from datetime import datetime

class Neo4jGraphMigration:
    """Migrate existing graph structure to Neo4j."""

    def __init__(self, driver, db_session: Session):
        self.driver = driver
        self.db_session = db_session

    def migrate_graph(self, graph_id: str) -> Dict[str, Any]:
        """Migrate single graph from SQL to Neo4j."""
        graph = self.db_session.query(Graph).filter(Graph.id == graph_id).first()
        if not graph:
            return {"error": "Graph not found"}

        # Get all items in this graph
        links = self.db_session.query(Link).filter(Link.graph_id == graph_id).all()
        item_ids = set()
        for link in links:
            item_ids.add(link.source_item_id)
            item_ids.add(link.target_item_id)

        items = self.db_session.query(Item).filter(Item.id.in_(item_ids)).all()

        # Create Neo4j graph structure
        with self.driver.session() as session:
            # Create graph node
            session.write_transaction(
                self._create_graph_node,
                graph_id, graph.name, graph.graph_type, graph.project_id
            )

            # Create item nodes
            for item in items:
                session.write_transaction(
                    self._create_item_node,
                    item.id, item.title, item.item_type, item.status
                )

            # Create relationships
            for link in links:
                session.write_transaction(
                    self._create_link_relationship,
                    link.source_item_id,
                    link.link_type,
                    link.target_item_id,
                    link.link_metadata,
                    graph_id
                )

        return {"migrated": len(items), "links": len(links), "graph_id": graph_id}

    @staticmethod
    def _create_graph_node(tx, graph_id, name, graph_type, project_id):
        """Create graph root node."""
        query = """
        CREATE (g:TraceabilityGraph {
            id: $id,
            name: $name,
            type: $type,
            project_id: $project_id,
            created_at: datetime()
        })
        RETURN g
        """
        return tx.run(query, {
            "id": graph_id,
            "name": name,
            "type": graph_type,
            "project_id": project_id
        }).single()

    @staticmethod
    def _create_item_node(tx, item_id, title, item_type, status):
        """Create item node (Requirement, TestCase, Design, etc.)."""
        # Map item_type to Neo4j label
        label_map = {
            "requirement": "Requirement",
            "test": "TestCase",
            "design": "Design",
            "feature": "Feature",
            "component": "Component",
            "process": "Process"
        }

        label = label_map.get(item_type, "Item")

        query = f"""
        CREATE (i:{label} {{
            id: $id,
            title: $title,
            status: $status,
            created_at: datetime()
        }})
        RETURN i
        """
        return tx.run(query, {
            "id": item_id,
            "title": title,
            "status": status
        }).single()

    @staticmethod
    def _create_link_relationship(
        tx, source_id, rel_type, target_id, metadata, graph_id
    ):
        """Create relationship between items."""
        rel_type_map = {
            "implements": "IMPLEMENTS",
            "tests": "TESTS",
            "depends_on": "DEPENDS_ON",
            "addresses": "ADDRESSES",
            "verifies": "VERIFIES",
            "guides": "GUIDES"
        }

        cypher_rel = rel_type_map.get(rel_type, rel_type.upper())

        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        CREATE (source)-[r:{cypher_rel} {{
            metadata: $metadata,
            graph_id: $graph_id,
            created_at: datetime()
        }}]->(target)
        RETURN r
        """
        return tx.run(query, {
            "source_id": source_id,
            "target_id": target_id,
            "metadata": metadata,
            "graph_id": graph_id
        }).single()

    def migrate_all_graphs(self) -> Dict[str, Any]:
        """Migrate all graphs from database."""
        graphs = self.db_session.query(Graph).all()
        results = []

        for graph in graphs:
            result = self.migrate_graph(graph.id)
            results.append(result)

        return {
            "total_graphs": len(graphs),
            "migration_results": results,
            "timestamp": datetime.now().isoformat()
        }
```

---

## Pattern 2: Bi-Directional Sync with Existing Database

Keep SQLAlchemy as source of truth, use Neo4j for queries.

```python
# src/tracertm/services/graph_sync_service.py
from sqlalchemy.orm import Session
from neo4j import GraphDatabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BiDirectionalGraphSync:
    """
    Keep SQLAlchemy and Neo4j in sync.

    SQLAlchemy = source of truth for transactional data
    Neo4j = query optimization layer
    """

    def __init__(self, db_session: Session, neo4j_driver):
        self.db = db_session
        self.driver = neo4j_driver

    def on_item_created(self, item_id: str, title: str, item_type: str, status: str):
        """Called when Item created in database."""
        with self.driver.session() as session:
            session.write_transaction(
                self._sync_item_node,
                item_id, title, item_type, status
            )
        logger.info(f"Synced new item {item_id} to Neo4j")

    def on_item_updated(self, item_id: str, updates: dict):
        """Called when Item updated in database."""
        with self.driver.session() as session:
            session.write_transaction(
                self._update_item_node,
                item_id, updates
            )
        logger.info(f"Updated item {item_id} in Neo4j")

    def on_item_deleted(self, item_id: str):
        """Called when Item deleted in database."""
        with self.driver.session() as session:
            session.write_transaction(
                self._delete_item_node,
                item_id
            )
        logger.info(f"Deleted item {item_id} from Neo4j")

    def on_link_created(
        self,
        link_id: str,
        source_id: str,
        target_id: str,
        link_type: str,
        metadata: dict
    ):
        """Called when Link created in database."""
        with self.driver.session() as session:
            session.write_transaction(
                self._sync_link,
                source_id, target_id, link_type, metadata
            )
        logger.info(f"Synced link {link_id} to Neo4j")

    @staticmethod
    def _sync_item_node(tx, item_id, title, item_type, status):
        """Sync item to Neo4j."""
        label_map = {
            "requirement": "Requirement",
            "test": "TestCase",
            "design": "Design",
            "feature": "Feature",
            "component": "Component"
        }
        label = label_map.get(item_type, "Item")

        query = f"""
        MERGE (i:{label} {{id: $id}})
        SET i.title = $title, i.status = $status, i.synced_at = datetime()
        RETURN i
        """
        return tx.run(query, {"id": item_id, "title": title, "status": status})

    @staticmethod
    def _update_item_node(tx, item_id, updates):
        """Update item properties in Neo4j."""
        set_clause = ", ".join([f"i.{k} = ${k}" for k in updates.keys()])
        query = f"""
        MATCH (i {{id: $id}})
        SET {set_clause}, i.synced_at = datetime()
        RETURN i
        """
        params = {"id": item_id, **updates}
        return tx.run(query, params)

    @staticmethod
    def _delete_item_node(tx, item_id):
        """Delete item from Neo4j."""
        query = """
        MATCH (i {id: $id})
        DETACH DELETE i
        """
        return tx.run(query, {"id": item_id})

    @staticmethod
    def _sync_link(tx, source_id, target_id, link_type, metadata):
        """Create/update link in Neo4j."""
        rel_type = link_type.upper()
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{rel_type}]->(target)
        SET r.metadata = $metadata, r.synced_at = datetime()
        RETURN r
        """
        return tx.run(query, {
            "source_id": source_id,
            "target_id": target_id,
            "metadata": metadata
        })


# Integration with SQLAlchemy event listeners
from sqlalchemy import event
from tracertm.models.item import Item
from tracertm.models.link import Link

class SyncListeners:
    """Register SQLAlchemy event listeners for Neo4j sync."""

    @staticmethod
    def register_item_listeners(sync_service: BiDirectionalGraphSync):
        """Register listeners for Item model."""

        @event.listens_for(Item, "after_insert")
        def receive_after_insert(mapper, connection, target):
            sync_service.on_item_created(
                target.id,
                target.title,
                target.item_type,
                target.status
            )

        @event.listens_for(Item, "after_update")
        def receive_after_update(mapper, connection, target):
            sync_service.on_item_updated(
                target.id,
                {"title": target.title, "status": target.status}
            )

        @event.listens_for(Item, "after_delete")
        def receive_after_delete(mapper, connection, target):
            sync_service.on_item_deleted(target.id)

    @staticmethod
    def register_link_listeners(sync_service: BiDirectionalGraphSync):
        """Register listeners for Link model."""

        @event.listens_for(Link, "after_insert")
        def receive_after_insert(mapper, connection, target):
            sync_service.on_link_created(
                target.id,
                target.source_item_id,
                target.target_item_id,
                target.link_type,
                target.link_metadata
            )
```

---

## Pattern 3: Traceability Queries for Your Use Cases

### Use Case 1: Feature Coverage Analysis

```cypher
# Get all features and their test coverage
MATCH (feature:Feature)
OPTIONAL MATCH (feature)-[:IMPLEMENTS]->(req:Requirement)
OPTIONAL MATCH (req)-[:VERIFIED_BY]->(test:TestCase)
WITH feature, count(distinct req) as req_count, count(distinct test) as test_count
RETURN
    feature.id,
    feature.name,
    req_count as requirements,
    test_count as tests,
    CASE
        WHEN req_count = 0 THEN 'N/A'
        ELSE apoc.math.round(100.0 * test_count / req_count, 1)
    END as coverage_pct
ORDER BY coverage_pct DESC
```

### Use Case 2: Requirement Traceability Matrix

```cypher
# Generate requirement x test verification matrix
MATCH (req:Requirement)
OPTIONAL MATCH (req)-[v:VERIFIED_BY]->(test:TestCase)
WITH req, collect({
    test_id: test.id,
    test_name: test.name,
    coverage: v.coverage
}) as tests
RETURN
    req.id as requirement_id,
    req.title as requirement_title,
    req.status,
    tests,
    size(tests) as test_count
ORDER BY req.id
```

### Use Case 3: Impact of ADR Decision

```cypher
# Find all requirements and tests affected by ADR change
MATCH (adr:Design {id: 'ADR-001'})
CALL apoc.path.expandConfig(adr, {
    relationshipFilter: 'ADDRESSES|IMPLEMENTS|VERIFIES',
    minLevel: 1,
    maxLevel: 3
})
YIELD path
WITH [n in nodes(path) | {
    id: n.id,
    type: labels(n)[0],
    status: n.status
}] as impacted_chain
RETURN impacted_chain
```

### Use Case 4: Requirement Dependency Analysis

```cypher
# Find blocking dependencies (critical path)
MATCH (req:Requirement)
WHERE req.priority = 'CRITICAL'
OPTIONAL MATCH (req)-[:DEPENDS_ON]->(blocker:Requirement)
OPTIONAL MATCH (blocker)-[:VERIFIED_BY]->(test)
WITH req, blocker, count(test) as test_count
RETURN
    req.id,
    req.title,
    collect({
        blocker_id: blocker.id,
        blocker_title: blocker.title,
        tests_written: test_count
    }) as blockers
ORDER BY size(blockers) DESC
```

### Use Case 5: Specification Completeness

```cypher
# Check which requirements lack design or tests
MATCH (req:Requirement {status: 'APPROVED'})
RETURN {
    requirement_id: req.id,
    requirement_title: req.title,
    has_design: EXISTS((req)<-[:ADDRESSES]-(design:Design)),
    has_tests: EXISTS((req)-[:VERIFIED_BY]->(test:TestCase)),
    gap_type: CASE
        WHEN NOT EXISTS((req)<-[:ADDRESSES]-(:Design)) AND
             NOT EXISTS((req)-[:VERIFIED_BY]->(:TestCase))
        THEN 'ORPHANED'
        WHEN NOT EXISTS((req)<-[:ADDRESSES]-(:Design))
        THEN 'NO_DESIGN'
        WHEN NOT EXISTS((req)-[:VERIFIED_BY]->(:TestCase))
        THEN 'NO_TESTS'
        ELSE 'COMPLETE'
    END
} as completeness
ORDER BY requirement_id
```

---

## Pattern 4: Integration with FastAPI Routes

```python
# src/tracertm/api/routers/graph_traceability.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from tracertm.services.graph_traceability_service import GraphTraceabilityService
from tracertm.api.deps import get_db_session, get_current_user

router = APIRouter(prefix="/api/v1/traceability", tags=["traceability"])

def get_graph_service():
    driver = GraphDatabase.driver(
        "neo4j://localhost:7687",
        auth=("neo4j", "password")
    )
    return GraphTraceabilityService(driver)

@router.get("/requirements/{req_id}/coverage")
async def get_requirement_coverage(
    req_id: str,
    project_id: Optional[str] = Query(None),
    graph_service: GraphTraceabilityService = Depends(get_graph_service),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive coverage for requirement.

    Returns:
    - test_count: Number of tests verifying this requirement
    - avg_coverage: Average coverage percentage
    - test_ids: List of test IDs
    """
    coverage = graph_service.get_requirement_coverage(req_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return coverage

@router.get("/features/{feature_id}/coverage-matrix")
async def get_feature_coverage_matrix(
    feature_id: str,
    graph_service: GraphTraceabilityService = Depends(get_graph_service),
    current_user = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get requirement-test coverage matrix for feature.

    Shows which tests cover which requirements.
    """
    # Custom query for feature matrix
    with graph_service.driver.session() as session:
        query = """
        MATCH (f:Feature {id: $feature_id})
        OPTIONAL MATCH (f)-[:IMPLEMENTS]->(req:Requirement)
        OPTIONAL MATCH (req)-[v:VERIFIED_BY]->(test:TestCase)
        RETURN {
            requirement_id: req.id,
            requirement_title: req.title,
            tests: collect({
                test_id: test.id,
                test_name: test.name,
                coverage: v.coverage
            })
        } as matrix_row
        """
        results = session.run(query, {"feature_id": feature_id}).data()
    return results

@router.get("/projects/{project_id}/dependency-graph")
async def get_project_dependency_graph(
    project_id: str,
    max_depth: int = Query(2, ge=1, le=5),
    graph_service: GraphTraceabilityService = Depends(get_graph_service),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get requirement dependency graph for project.

    Returns graph structure with nodes and edges.
    """
    with graph_service.driver.session() as session:
        # Get all requirements in project
        req_query = """
        MATCH (r:Requirement {project_id: $project_id})
        RETURN r.id, r.title, r.priority
        """
        requirements = session.run(req_query, {"project_id": project_id}).data()

        # Get all dependency relationships
        dep_query = """
        MATCH (r1:Requirement {project_id: $project_id})-[:DEPENDS_ON]->(r2:Requirement)
        RETURN r1.id as source, r2.id as target
        """
        dependencies = session.run(dep_query, {"project_id": project_id}).data()

    return {
        "nodes": requirements,
        "edges": dependencies,
        "project_id": project_id
    }

@router.post("/requirements/{req_id}/impact-analysis")
async def analyze_requirement_impact(
    req_id: str,
    max_depth: int = Query(4, ge=1, le=6),
    graph_service: GraphTraceabilityService = Depends(get_graph_service),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze impact of changing a requirement.

    Shows all affected tests, designs, and dependent requirements.
    """
    impacts = graph_service.find_impact_chain(req_id, max_depth)

    return {
        "requirement_id": req_id,
        "impact_chains": impacts,
        "total_impact_paths": len(impacts),
        "max_depth": max([len(chain.get("node_ids", [])) for chain in impacts])
    }

@router.get("/projects/{project_id}/compliance-report")
async def generate_compliance_report(
    project_id: str,
    graph_service: GraphTraceabilityService = Depends(get_graph_service),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate traceability compliance report for project.

    Includes:
    - Total requirements
    - Verified requirements
    - Coverage percentage
    - Unverified gaps
    """
    report = graph_service.generate_traceability_report(project_id)
    return {
        **report,
        "compliance_status": "COMPLIANT" if report["coverage_percentage"] >= 80 else "NON_COMPLIANT"
    }

@router.get("/requirements/search")
async def search_requirements(
    query: str,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    graph_service: GraphTraceabilityService = Depends(get_graph_service),
    current_user = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Full-text search for requirements with filters.
    """
    with graph_service.driver.session() as session:
        search_query = """
        CALL db.index.fulltext.queryNodes('idx_requirement_search', $query)
        YIELD node as r
        WHERE 1=1
        """
        params = {"query": query}

        if project_id:
            search_query += " AND r.project_id = $project_id"
            params["project_id"] = project_id

        if status:
            search_query += " AND r.status = $status"
            params["status"] = status

        if priority:
            search_query += " AND r.priority = $priority"
            params["priority"] = priority

        search_query += """
        RETURN {
            id: r.id,
            title: r.title,
            status: r.status,
            priority: r.priority
        } as requirement
        LIMIT 50
        """

        results = session.run(search_query, params).data()

    return [r["requirement"] for r in results]
```

---

## Pattern 5: Monitoring and Health Checks

```python
# src/tracertm/services/graph_health_service.py
from neo4j import GraphDatabase
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GraphHealthService:
    """Monitor Neo4j health and sync status."""

    def __init__(self, driver):
        self.driver = driver

    def health_check(self) -> Dict[str, Any]:
        """Check overall graph health."""
        try:
            with self.driver.session() as session:
                # Test connectivity
                result = session.run("RETURN 1")
                result.single()

                # Get stats
                stats_result = session.run("""
                MATCH (n) RETURN count(n) as node_count
                """)
                node_count = stats_result.single()["node_count"]

                rel_result = session.run("""
                MATCH ()-[r]-() RETURN count(r) as rel_count
                """)
                rel_count = rel_result.single()["rel_count"]

            return {
                "status": "HEALTHY",
                "connected": True,
                "node_count": node_count,
                "relationship_count": rel_count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "UNHEALTHY",
                "connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_sync_status(self) -> Dict[str, Any]:
        """Check sync status between database and Neo4j."""
        with self.driver.session() as session:
            # Count requirements and other entities
            results = session.run("""
            MATCH (n)
            RETURN labels(n)[0] as type, count(n) as count
            UNION ALL
            MATCH ()-[r]-()
            RETURN type(r) as type, count(r) as count
            """)

            sync_stats = {}
            for record in results:
                sync_stats[record["type"]] = record["count"]

        return {
            "entity_counts": sync_stats,
            "last_checked": datetime.now().isoformat()
        }

    def find_indexing_gaps(self) -> List[str]:
        """Identify properties that should be indexed."""
        gaps = []

        with self.driver.session() as session:
            # Check which properties are frequently queried
            slow_queries = session.run("""
            SHOW INDEXES
            YIELD name, state
            WHERE state != "ONLINE"
            RETURN name
            """)

            for record in slow_queries:
                gaps.append(record["name"])

        return gaps
```

---

## Deployment Guide for TracertRTM

### 1. Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15-community
    environment:
      NEO4J_AUTH: neo4j/tracertm-password-change-in-prod
      NEO4J_apoc_export_file_enabled: "true"
      NEO4J_apoc_import_file_enabled: "true"
    ports:
      - "7687:7687"  # Bolt
      - "7474:7474"  # Browser
      - "7473:7473"  # HTTPS
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7474"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Optional: RDF store for semantic validation
  rdf-store:
    image: eclipse/rdf4j-server:latest
    ports:
      - "8080:8080"
    volumes:
      - rdf_data:/data

volumes:
  neo4j_data:
  neo4j_logs:
  rdf_data:
```

### 2. Environment Configuration

```bash
# .env
NEO4J_URI=neo4j://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-secure-password
NEO4J_DATABASE=tracertm

# RDF settings (optional)
RDF_STORAGE_PATH=/data/rdf
RDF_ENABLE_SEMANTIC_VALIDATION=true

# Sync settings
GRAPH_SYNC_ENABLED=true
GRAPH_SYNC_INTERVAL_MINUTES=60
```

### 3. Initial Setup Script

```bash
#!/bin/bash
# scripts/setup-graph-db.sh

set -e

echo "Setting up Neo4j for TracertRTM..."

# Wait for Neo4j to be ready
until curl -f http://localhost:7474 > /dev/null; do
    echo "Waiting for Neo4j..."
    sleep 2
done

echo "Neo4j is ready!"

# Run schema creation
python -m tracertm.scripts.initialize_graph_schema

# Migrate existing data
python -m tracertm.scripts.migrate_to_neo4j

# Verify sync
python -m tracertm.scripts.verify_sync_integrity

echo "Graph database setup complete!"
```

---

## Testing Guide

```python
# tests/unit/services/test_graph_traceability_service.py
import pytest
from neo4j import GraphDatabase
from neo4j.testing import Neo4jTestEnvironment
from tracertm.services.graph_traceability_service import GraphTraceabilityService

@pytest.fixture
def neo4j_test_driver():
    """Create test Neo4j instance."""
    env = Neo4jTestEnvironment()
    driver = env.driver()
    yield driver
    env.close()

@pytest.fixture
def graph_service(neo4j_test_driver):
    return GraphTraceabilityService(neo4j_test_driver)

def test_create_requirement(graph_service):
    """Test creating requirement node."""
    success = graph_service.sync_requirement_from_db(
        "REQ-001",
        "Test Requirement",
        "APPROVED",
        "HIGH"
    )
    assert success

def test_get_requirement_coverage(graph_service):
    """Test coverage calculation."""
    # Setup
    graph_service.sync_requirement_from_db("REQ-001", "Req", "APPROVED")
    graph_service.create_verification_link("REQ-001", "TEST-001", 0.95)

    # Test
    coverage = graph_service.get_requirement_coverage("REQ-001")
    assert coverage["test_count"] == 1
    assert coverage["avg_coverage"] == 0.95

def test_impact_analysis(graph_service):
    """Test impact chain finding."""
    # Create chain: REQ-001 -> REQ-002 -> TEST-001
    graph_service.sync_requirement_from_db("REQ-001", "Req 1", "APPROVED")
    graph_service.sync_requirement_from_db("REQ-002", "Req 2", "APPROVED")

    # Add relationships
    with graph_service.driver.session() as session:
        session.write_transaction(
            lambda tx: tx.run(
                "MATCH (a {id: 'REQ-001'}) MATCH (b {id: 'REQ-002'}) "
                "CREATE (a)-[:DEPENDS_ON]->(b)"
            )
        )

    # Test impact
    impacts = graph_service.find_impact_chain("REQ-001", max_depth=2)
    assert len(impacts) > 0
```

---

## Key Takeaways

1. **Start Simple**: Begin with Neo4j property graph mapping (immediate benefit)
2. **Sync Strategy**: Use SQLAlchemy event listeners for real-time sync
3. **Query Optimization**: Full-text indexes for search, composite indexes for filters
4. **Semantic Layer**: Add RDF/OWL for compliance checking (future enhancement)
5. **Monitoring**: Regular health checks and sync verification
6. **Testing**: Test graph queries thoroughly before production

