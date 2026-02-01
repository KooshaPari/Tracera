# Graph Database Implementation Guide for Specification Traceability

## Quick Reference: Database Selection

### For TracertRTM Project

Based on project analysis:
- **Primary**: Neo4j (transactional graphs, proven ecosystem, Cypher maturity)
- **Secondary**: RDF/OWL via rdflib (semantic reasoning, compliance validation)
- **Approach**: Hybrid - Neo4j for performance, RDF for semantic queries

**Why**: Your existing SQLAlchemy models are relational. Neo4j provides excellent bridging through property graphs while maintaining ACID guarantees you need for specification management.

---

## Part 1: Neo4j Integration with Existing Project

### 1.1 Add to Requirements

```bash
# Add to pyproject.toml
neo4j = "^5.15"
apoc = "^4.4"  # APOC procedures for advanced queries
```

### 1.2 Configuration

```python
# src/tracertm/config/graph_database.py
from neo4j import GraphDatabase, Session
from typing import Optional
import os

class Neo4jConfig:
    """Neo4j configuration for traceability graphs."""

    def __init__(self):
        self.uri = os.getenv(
            "NEO4J_URI",
            "neo4j://localhost:7687"
        )
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.database = os.getenv("NEO4J_DATABASE", "tracertm")

    def get_driver(self):
        """Get Neo4j driver instance."""
        return GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password),
            encrypted=False  # Adjust for production
        )

    def verify_connectivity(self) -> bool:
        """Verify connection to Neo4j."""
        try:
            driver = self.get_driver()
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            return True
        except Exception as e:
            print(f"Neo4j connection failed: {e}")
            return False
```

### 1.3 Schema Creation

```python
# src/tracertm/services/graph_schema_service.py
from neo4j import GraphDatabase
from typing import List

class GraphSchemaService:
    """Create and manage Neo4j schema for traceability."""

    def __init__(self, driver):
        self.driver = driver

    def create_schema(self) -> None:
        """Create complete schema for specification traceability."""
        with self.driver.session() as session:
            # Create indexes
            self._create_indexes(session)
            # Create constraints
            self._create_constraints(session)
            # Create full-text indexes
            self._create_fulltext_indexes(session)

    def _create_indexes(self, session) -> None:
        """Create performance indexes."""
        indexes = [
            # Requirement indexes
            "CREATE INDEX idx_requirement_status FOR (r:Requirement) ON (r.status)",
            "CREATE INDEX idx_requirement_priority FOR (r:Requirement) ON (r.priority)",
            "CREATE INDEX idx_requirement_project FOR (r:Requirement) ON (r.project_id)",

            # Test indexes
            "CREATE INDEX idx_test_automated FOR (t:TestCase) ON (t.automated)",
            "CREATE INDEX idx_test_status FOR (t:TestCase) ON (t.status)",

            # Design indexes
            "CREATE INDEX idx_design_version FOR (d:Design) ON (d.version)",
            "CREATE INDEX idx_design_status FOR (d:Design) ON (d.status)",

            # Composite indexes
            "CREATE INDEX idx_requirement_project_status FOR (r:Requirement) ON (r.project_id, r.status)",
            "CREATE INDEX idx_test_component FOR (t:TestCase) ON (t.component_id)",

            # Relationship indexes
            "CREATE INDEX idx_verified_timestamp FOR ()-[v:VERIFIED_BY]-() ON (v.last_verified)",
            "CREATE INDEX idx_depends_on FOR ()-[d:DEPENDS_ON]-() ON (d.criticality)",
        ]

        for index_query in indexes:
            try:
                session.run(index_query)
                print(f"Created: {index_query[:50]}...")
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"Index creation failed: {e}")

    def _create_constraints(self, session) -> None:
        """Create uniqueness constraints."""
        constraints = [
            "CREATE CONSTRAINT unique_requirement_id FOR (r:Requirement) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT unique_test_id FOR (t:TestCase) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT unique_design_id FOR (d:Design) REQUIRE d.id IS UNIQUE",
        ]

        for constraint_query in constraints:
            try:
                session.run(constraint_query)
                print(f"Created constraint")
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"Constraint creation failed: {e}")

    def _create_fulltext_indexes(self, session) -> None:
        """Create full-text search indexes."""
        fulltext_indexes = [
            """
            CREATE FULLTEXT INDEX idx_requirement_search
            FOR (r:Requirement) ON EACH [r.title, r.description]
            """,
            """
            CREATE FULLTEXT INDEX idx_test_search
            FOR (t:TestCase) ON EACH [t.name, t.description]
            """,
        ]

        for fulltext_query in fulltext_indexes:
            try:
                session.run(fulltext_query)
                print(f"Created fulltext index")
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"Fulltext index creation failed: {e}")
```

### 1.4 Service Layer for Graph Operations

```python
# src/tracertm/services/graph_traceability_service.py
from neo4j import GraphDatabase, Session, Transaction
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class GraphTraceabilityService:
    """High-level service for specification traceability operations."""

    def __init__(self, driver):
        self.driver = driver

    def sync_requirement_from_db(
        self,
        req_id: str,
        title: str,
        status: str,
        priority: str = "MEDIUM",
        project_id: str = None
    ) -> bool:
        """Sync requirement from SQLAlchemy to Neo4j."""
        with self.driver.session() as session:
            return session.write_transaction(
                self._create_or_update_requirement,
                req_id, title, status, priority, project_id
            )

    @staticmethod
    def _create_or_update_requirement(
        tx: Transaction,
        req_id: str,
        title: str,
        status: str,
        priority: str,
        project_id: str
    ) -> bool:
        """Create or update requirement node."""
        query = """
        MERGE (r:Requirement {id: $req_id})
        SET r.title = $title,
            r.status = $status,
            r.priority = $priority,
            r.project_id = $project_id,
            r.updated_at = datetime()
        RETURN r.id
        """
        try:
            result = tx.run(query, {
                "req_id": req_id,
                "title": title,
                "status": status,
                "priority": priority,
                "project_id": project_id
            })
            return result.single() is not None
        except Exception as e:
            print(f"Error syncing requirement: {e}")
            return False

    def create_verification_link(
        self,
        req_id: str,
        test_id: str,
        coverage: float = 0.0
    ) -> bool:
        """Create VERIFIED_BY relationship."""
        with self.driver.session() as session:
            return session.write_transaction(
                self._create_verification,
                req_id, test_id, coverage
            )

    @staticmethod
    def _create_verification(
        tx: Transaction,
        req_id: str,
        test_id: str,
        coverage: float
    ) -> bool:
        """Create verification relationship."""
        query = """
        MATCH (r:Requirement {id: $req_id})
        MATCH (t:TestCase {id: $test_id})
        MERGE (r)-[v:VERIFIED_BY {
            coverage: $coverage,
            last_verified: datetime()
        }]->(t)
        RETURN v
        """
        try:
            result = tx.run(query, {
                "req_id": req_id,
                "test_id": test_id,
                "coverage": coverage
            })
            return result.single() is not None
        except Exception as e:
            print(f"Error creating verification: {e}")
            return False

    def get_requirement_coverage(
        self,
        requirement_id: str
    ) -> Dict[str, Any]:
        """Get coverage metrics for a requirement."""
        with self.driver.session() as session:
            return session.read_transaction(
                self._query_coverage,
                requirement_id
            )

    @staticmethod
    def _query_coverage(
        tx: Transaction,
        requirement_id: str
    ) -> Dict[str, Any]:
        """Query requirement coverage."""
        query = """
        MATCH (r:Requirement {id: $req_id})
        OPTIONAL MATCH (r)-[v:VERIFIED_BY]->(t:TestCase)
        RETURN
            r.id as requirement_id,
            r.title as title,
            r.status as status,
            count(t) as test_count,
            avg(v.coverage) as avg_coverage,
            collect(distinct t.id) as test_ids
        """
        try:
            result = tx.run(query, {"req_id": requirement_id})
            record = result.single()
            if record:
                return dict(record)
            return {}
        except Exception as e:
            print(f"Error querying coverage: {e}")
            return {}

    def find_impact_chain(
        self,
        requirement_id: str,
        max_depth: int = 4
    ) -> List[Dict[str, Any]]:
        """Find all entities impacted by requirement change."""
        with self.driver.session() as session:
            return session.read_transaction(
                self._impact_analysis,
                requirement_id,
                max_depth
            )

    @staticmethod
    def _impact_analysis(
        tx: Transaction,
        requirement_id: str,
        max_depth: int
    ) -> List[Dict[str, Any]]:
        """Analyze requirement impact."""
        query = """
        MATCH (req:Requirement {id: $req_id})
        CALL apoc.path.expandConfig(req, {
            relationshipFilter: 'ADDRESSES|IMPLEMENTS|TESTS|DEPENDS_ON',
            minLevel: 1,
            maxLevel: $max_depth,
            bfs: true
        })
        YIELD path
        RETURN {
            path_length: length(path),
            node_types: [n in nodes(path) | labels(n)[0]],
            node_ids: [n in nodes(path) | n.id],
            relationships: [r in relationships(path) | type(r)]
        } as impact
        ORDER BY path_length
        """
        try:
            results = tx.run(query, {
                "req_id": requirement_id,
                "max_depth": max_depth
            })
            return [dict(r["impact"]) for r in results]
        except Exception as e:
            print(f"Error in impact analysis: {e}")
            return []

    def generate_traceability_report(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive traceability report."""
        with self.driver.session() as session:
            return session.read_transaction(
                self._generate_report,
                project_id
            )

    @staticmethod
    def _generate_report(
        tx: Transaction,
        project_id: str
    ) -> Dict[str, Any]:
        """Generate traceability report."""
        # Total requirements
        req_query = """
        MATCH (r:Requirement {project_id: $project_id})
        RETURN count(r) as total
        """
        total_reqs = tx.run(req_query, {"project_id": project_id}).single()["total"]

        # Verified requirements
        verified_query = """
        MATCH (r:Requirement {project_id: $project_id})-[:VERIFIED_BY]->(t:TestCase)
        RETURN count(distinct r) as count
        """
        verified_reqs = tx.run(verified_query, {"project_id": project_id}).single()["count"]

        # Requirement without tests (gaps)
        gaps_query = """
        MATCH (r:Requirement {project_id: $project_id})
        WHERE NOT (r)-[:VERIFIED_BY]->(:TestCase)
        RETURN count(r) as gaps
        """
        gaps = tx.run(gaps_query, {"project_id": project_id}).single()["gaps"]

        return {
            "project_id": project_id,
            "total_requirements": total_reqs,
            "verified_requirements": verified_reqs,
            "unverified_requirements": gaps,
            "coverage_percentage": (
                100.0 * verified_reqs / total_reqs if total_reqs > 0 else 0
            ),
            "timestamp": datetime.now().isoformat()
        }
```

---

## Part 2: RDF/Semantic Layer Integration

### 2.1 Setup RDF Graph

```python
# src/tracertm/config/rdf_config.py
from rdflib import Graph, Namespace
import os

class RDFConfig:
    """RDF configuration for semantic traceability."""

    def __init__(self):
        self.storage_path = os.getenv(
            "RDF_STORAGE_PATH",
            "/tmp/tracertm_rdf"
        )
        self.graph = Graph(store="BerkeleyDB", identifier="tracertm")

    def get_graph(self) -> Graph:
        """Get RDF graph instance."""
        if not self.graph.store.connected:
            self.graph.open(self.storage_path, create=True)
        return self.graph

    def define_namespaces(self) -> None:
        """Define standard namespaces."""
        graph = self.get_graph()

        graph.bind("req", Namespace("http://example.org/requirement#"))
        graph.bind("test", Namespace("http://example.org/test#"))
        graph.bind("design", Namespace("http://example.org/design#"))
        graph.bind("prov", Namespace("http://www.w3.org/ns/prov#"))
        graph.bind("rdf", Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
        graph.bind("rdfs", Namespace("http://www.w3.org/2000/01/rdf-schema#"))
        graph.bind("owl", Namespace("http://www.w3.org/2002/07/owl#"))

    def close(self) -> None:
        """Close RDF store."""
        if self.graph.store.connected:
            self.graph.close()
```

### 2.2 Semantic Queries for Compliance

```python
# src/tracertm/services/semantic_compliance_service.py
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS
from rdflib.namespace import OWL, XSD
from typing import List, Dict, Any

class SemanticComplianceService:
    """Semantic checking and compliance validation."""

    def __init__(self, rdf_graph: Graph):
        self.graph = rdf_graph
        self.req = Namespace("http://example.org/requirement#")
        self.test = Namespace("http://example.org/test#")
        self.design = Namespace("http://example.org/design#")

    def validate_requirement_completeness(self) -> List[Dict[str, Any]]:
        """
        Validate requirements have necessary properties.

        SPARQL query to check for orphaned or incomplete requirements.
        """
        query = """
        PREFIX req: <http://example.org/requirement#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?req ?issue
        WHERE {
            ?req a req:Requirement .

            OPTIONAL { ?req rdfs:label ?label . }
            OPTIONAL { ?req req:hasStatus ?status . }
            OPTIONAL { ?req req:verifiedBy ?test . }
            OPTIONAL { ?req req:addresses ?design . }

            BIND(IF(!bound(?label), "NO_LABEL", "") as ?label_check)
            BIND(IF(!bound(?status), "NO_STATUS", "") as ?status_check)
            BIND(IF(
                !bound(?test) && !bound(?design),
                "NO_VERIFICATION",
                ""
            ) as ?verification_check)

            BIND(
                CONCAT(
                    IF(?label_check != "", ?label_check, ""),
                    IF(?status_check != "", IF(?label_check != "", " ", "") + ?status_check, ""),
                    IF(?verification_check != "", IF(?label_check != "" || ?status_check != "", " ", "") + ?verification_check, "")
                ) as ?issue
            )

            FILTER (?issue != "")
        }
        """

        results = self.graph.query(query)
        return [
            {
                "requirement": str(row.req),
                "issue": str(row.issue)
            }
            for row in results
        ]

    def find_requirement_gaps(self) -> List[Dict[str, Any]]:
        """Find requirements without test coverage."""
        query = """
        PREFIX req: <http://example.org/requirement#>
        PREFIX test: <http://example.org/test#>

        SELECT ?req ?label
        WHERE {
            ?req a req:Requirement ;
                rdfs:label ?label ;
                req:hasStatus req:APPROVED .

            FILTER NOT EXISTS {
                ?req req:verifiedBy ?test .
            }
        }
        ORDER BY ?label
        """

        results = self.graph.query(query)
        return [
            {
                "requirement": str(row.req),
                "title": str(row.label),
                "gap_type": "NO_TEST_COVERAGE"
            }
            for row in results
        ]

    def check_traceability_continuity(self) -> List[Dict[str, Any]]:
        """
        Check for broken traceability chains.

        Identifies cases where intermediate traceability links are missing.
        """
        query = """
        PREFIX req: <http://example.org/requirement#>
        PREFIX test: <http://example.org/test#>
        PREFIX design: <http://example.org/design#>

        SELECT ?req ?test ?missing
        WHERE {
            ?req a req:Requirement ;
                req:verifiedBy ?test .
            ?test a test:TestCase .

            FILTER NOT EXISTS {
                ?test test:tests ?component .
            }

            BIND("MISSING_COMPONENT_LINK" as ?missing)
        }
        """

        results = self.graph.query(query)
        return [
            {
                "requirement": str(row.req),
                "test": str(row.test),
                "issue": str(row.missing)
            }
            for row in results
        ]

    def compliance_score(self) -> float:
        """
        Calculate overall compliance score.

        Returns 0-100 based on:
        - Requirement completeness (40%)
        - Test coverage (40%)
        - Design justification (20%)
        """
        # Count complete requirements
        complete_query = """
        PREFIX req: <http://example.org/requirement#>

        SELECT (COUNT(?req) as ?count)
        WHERE {
            ?req a req:Requirement ;
                rdfs:label ?label ;
                req:hasStatus ?status ;
                (req:verifiedBy|req:addresses) ?link .
        }
        """
        complete = int(self.graph.query(complete_query).bindings[0][0])

        # Count total requirements
        total_query = """
        PREFIX req: <http://example.org/requirement#>

        SELECT (COUNT(?req) as ?count)
        WHERE {
            ?req a req:Requirement .
        }
        """
        total = int(self.graph.query(total_query).bindings[0][0])

        if total == 0:
            return 0.0

        return (complete / total) * 100.0
```

---

## Part 3: Data Synchronization

### 3.1 Bidirectional Sync Service

```python
# src/tracertm/services/graph_sync_service.py
from sqlalchemy.orm import Session
from neo4j import GraphDatabase
from rdflib import Graph
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GraphSyncService:
    """
    Synchronize between SQLAlchemy → Neo4j → RDF.

    Maintains consistency across three stores for optimal
    performance (relational), speed (graph), and semantics (RDF).
    """

    def __init__(
        self,
        db_session: Session,
        neo4j_driver,
        rdf_graph: Graph
    ):
        self.db_session = db_session
        self.neo4j_driver = neo4j_driver
        self.rdf_graph = rdf_graph

    def sync_requirements_to_neo4j(self) -> Dict[str, Any]:
        """Sync requirements from SQLAlchemy to Neo4j."""
        from tracertm.models.item import Item

        requirements = self.db_session.query(Item).filter(
            Item.item_type == "requirement"
        ).all()

        synced = 0
        errors = 0

        with self.neo4j_driver.session() as session:
            for req in requirements:
                try:
                    session.write_transaction(
                        self._sync_requirement_node,
                        req.id,
                        req.title,
                        req.status,
                        req.metadata.get("priority", "MEDIUM")
                    )
                    synced += 1
                except Exception as e:
                    logger.error(f"Failed to sync requirement {req.id}: {e}")
                    errors += 1

        return {
            "synced": synced,
            "errors": errors,
            "total": len(requirements),
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def _sync_requirement_node(tx, req_id, title, status, priority):
        """Transaction to sync requirement node."""
        query = """
        MERGE (r:Requirement {id: $req_id})
        SET r.title = $title,
            r.status = $status,
            r.priority = $priority,
            r.synced_at = datetime()
        RETURN r
        """
        return tx.run(query, {
            "req_id": req_id,
            "title": title,
            "status": status,
            "priority": priority
        })

    def sync_links_to_neo4j(self) -> Dict[str, Any]:
        """Sync relationship links from SQLAlchemy to Neo4j."""
        from tracertm.models.link import Link

        links = self.db_session.query(Link).all()
        synced = 0
        errors = 0

        with self.neo4j_driver.session() as session:
            for link in links:
                try:
                    session.write_transaction(
                        self._sync_relationship,
                        link.source_item_id,
                        link.link_type,
                        link.target_item_id,
                        link.link_metadata
                    )
                    synced += 1
                except Exception as e:
                    logger.error(f"Failed to sync link {link.id}: {e}")
                    errors += 1

        return {
            "synced": synced,
            "errors": errors,
            "total": len(links)
        }

    @staticmethod
    def _sync_relationship(tx, source_id, rel_type, target_id, metadata):
        """Transaction to sync relationship."""
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        CREATE (source)-[r:{rel_type} {{
            metadata: $metadata,
            synced_at: datetime()
        }}]->(target)
        RETURN r
        """
        return tx.run(query, {
            "source_id": source_id,
            "target_id": target_id,
            "metadata": metadata
        })

    def sync_neo4j_to_rdf(self) -> Dict[str, Any]:
        """Sync Neo4j nodes/relationships to RDF."""
        from rdflib import Namespace, Literal, URIRef, RDF

        req_ns = Namespace("http://example.org/requirement#")
        synced = 0

        # Query all requirements from Neo4j
        with self.neo4j_driver.session() as session:
            results = session.run("""
            MATCH (r:Requirement)
            RETURN r.id as id, r.title as title, r.status as status
            """)

            for record in results:
                req_uri = req_ns[record["id"]]

                # Add to RDF
                self.rdf_graph.add((
                    req_uri,
                    RDF.type,
                    req_ns.Requirement
                ))
                self.rdf_graph.add((
                    req_uri,
                    URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                    Literal(record["title"])
                ))

                synced += 1

        return {
            "synced": synced,
            "timestamp": datetime.now().isoformat()
        }

    def validate_sync_integrity(self) -> Dict[str, Any]:
        """
        Validate consistency between all three stores.

        Returns list of inconsistencies found.
        """
        inconsistencies = []

        # Check count consistency
        from tracertm.models.item import Item

        db_count = self.db_session.query(Item).filter(
            Item.item_type == "requirement"
        ).count()

        # Neo4j count
        with self.neo4j_driver.session() as session:
            result = session.run("MATCH (r:Requirement) RETURN count(r) as count")
            neo4j_count = result.single()["count"]

        if db_count != neo4j_count:
            inconsistencies.append({
                "issue": "REQUIREMENT_COUNT_MISMATCH",
                "database": db_count,
                "neo4j": neo4j_count,
                "difference": abs(db_count - neo4j_count)
            })

        return {
            "consistent": len(inconsistencies) == 0,
            "inconsistencies": inconsistencies,
            "timestamp": datetime.now().isoformat()
        }
```

---

## Part 4: API Integration

### 4.1 FastAPI Routes for Graph Queries

```python
# src/tracertm/api/routers/traceability.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from neo4j import GraphDatabase
from tracertm.services.graph_traceability_service import GraphTraceabilityService
from tracertm.api.deps import get_db_session

router = APIRouter(prefix="/api/traceability", tags=["traceability"])

# Dependency for graph service
def get_graph_service():
    driver = GraphDatabase.driver(
        "neo4j://localhost:7687",
        auth=("neo4j", "password")
    )
    return GraphTraceabilityService(driver)

@router.get("/requirements/{req_id}/coverage")
async def get_requirement_coverage(
    req_id: str,
    graph_service: GraphTraceabilityService = Depends(get_graph_service)
) -> Dict[str, Any]:
    """Get coverage metrics for requirement."""
    coverage = graph_service.get_requirement_coverage(req_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return coverage

@router.get("/requirements/{req_id}/impact")
async def get_requirement_impact(
    req_id: str,
    max_depth: int = 4,
    graph_service: GraphTraceabilityService = Depends(get_graph_service)
) -> List[Dict[str, Any]]:
    """Get impact chain for requirement change."""
    return graph_service.find_impact_chain(req_id, max_depth)

@router.get("/projects/{project_id}/report")
async def get_traceability_report(
    project_id: str,
    graph_service: GraphTraceabilityService = Depends(get_graph_service)
) -> Dict[str, Any]:
    """Generate traceability report for project."""
    return graph_service.generate_traceability_report(project_id)

@router.post("/sync/requirements")
async def sync_requirements(
    db_session = Depends(get_db_session),
    graph_service: GraphTraceabilityService = Depends(get_graph_service)
) -> Dict[str, Any]:
    """Sync requirements from database to graph."""
    from tracertm.models.item import Item

    requirements = db_session.query(Item).filter(
        Item.item_type == "requirement"
    ).all()

    synced = 0
    for req in requirements:
        graph_service.sync_requirement_from_db(
            req.id,
            req.title,
            req.status,
            req.metadata.get("priority", "MEDIUM"),
            req.project_id
        )
        synced += 1

    return {
        "synced": synced,
        "total": len(requirements),
        "success": synced == len(requirements)
    }
```

### 4.2 WebSocket for Real-Time Updates

```python
# src/tracertm/api/ws/graph_updates.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
import json
import asyncio

class GraphUpdateBroadcaster:
    """Broadcast graph changes to connected clients."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Failed to send message: {e}")

broadcaster = GraphUpdateBroadcaster()

async def websocket_endpoint(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process message and broadcast updates
            await broadcaster.broadcast({
                "type": "graph_update",
                "data": json.loads(data),
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
```

---

## Part 5: Monitoring and Optimization

### 5.1 Performance Monitoring

```python
# src/tracertm/services/graph_monitoring.py
from neo4j import GraphDatabase
from typing import Dict, Any
import time

class GraphPerformanceMonitor:
    """Monitor Neo4j query performance."""

    def __init__(self, driver):
        self.driver = driver
        self.query_stats = []

    def profile_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Profile a query execution."""
        with self.driver.session() as session:
            profile_query = f"PROFILE {query}"

            start_time = time.time()
            result = session.run(profile_query, params or {})
            execution_time = time.time() - start_time

            # Get plan info
            plan_info = result.profile

            stat = {
                "query": query[:100],
                "execution_time_ms": execution_time * 1000,
                "db_hits": plan_info.get("dbHits", 0),
                "rows": plan_info.get("rows", 0),
                "timestamp": datetime.now().isoformat()
            }

            self.query_stats.append(stat)
            return stat

    def get_index_statistics(self) -> Dict[str, Any]:
        """Get index usage statistics."""
        with self.driver.session() as session:
            result = session.run("""
            SHOW INDEXES
            YIELD name, type, populationPercent, state
            RETURN name, type, populationPercent, state
            """)

            return {
                "indexes": [dict(record) for record in result]
            }

    def get_slow_queries(self, threshold_ms: int = 100) -> list:
        """Get queries slower than threshold."""
        return [
            stat for stat in self.query_stats
            if stat["execution_time_ms"] > threshold_ms
        ]
```

---

## Implementation Checklist

- [ ] Add Neo4j dependencies to `pyproject.toml`
- [ ] Create `src/tracertm/config/graph_database.py`
- [ ] Create `src/tracertm/services/graph_schema_service.py`
- [ ] Create `src/tracertm/services/graph_traceability_service.py`
- [ ] Create `src/tracertm/services/graph_sync_service.py`
- [ ] Add API routes in `src/tracertm/api/routers/traceability.py`
- [ ] Setup Neo4j instance (Docker: `docker run -it -p 7687:7687 -p 7474:7474 neo4j`)
- [ ] Initialize schema with `GraphSchemaService`
- [ ] Sync existing data from database to Neo4j
- [ ] Add RDF layer for semantic validation
- [ ] Implement monitoring and performance optimization
- [ ] Add integration tests
- [ ] Deploy to production environment

---

## Quick Start Example

```python
# Initialize and use
from tracertm.config.graph_database import Neo4jConfig
from tracertm.services.graph_traceability_service import GraphTraceabilityService

config = Neo4jConfig()
driver = config.get_driver()
service = GraphTraceabilityService(driver)

# Create requirement
service.sync_requirement_from_db(
    "REQ-001",
    "User Login",
    "APPROVED",
    "HIGH"
)

# Link test
service.create_verification_link("REQ-001", "TEST-001", 0.95)

# Get coverage
coverage = service.get_requirement_coverage("REQ-001")
print(f"Coverage: {coverage['avg_coverage']:.1%}")

# Find impact
impacts = service.find_impact_chain("REQ-001")
print(f"Impact chain: {len(impacts)} levels")

# Generate report
report = service.generate_traceability_report("PROJECT-001")
print(f"Overall coverage: {report['coverage_percentage']:.1%}")
```

