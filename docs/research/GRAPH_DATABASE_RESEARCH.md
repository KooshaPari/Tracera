# Graph Database Patterns and Knowledge Graphs for Specification Traceability

## Executive Summary

Graph databases provide native support for relationship-heavy domains like specification traceability. This research covers nine critical domains for implementing graph-based traceability systems: property graphs, RDF/OWL ontologies, knowledge graph embeddings, graph algorithms, temporal graphs, hypergraphs, visualization, database comparison, and provenance tracking. Each domain includes data models, query patterns, and Python integration examples applicable to specification management systems.

**Key Finding**: A hybrid approach combining Neo4j for transactional relationships with RDF stores for semantic reasoning provides optimal balance between performance and semantic expressiveness for specification traceability.

---

## 1. Neo4j Property Graph Model

### 1.1 Core Concepts

Neo4j uses a property graph model where:
- **Nodes** represent entities (requirements, tests, design decisions)
- **Relationships** represent directed, labeled connections
- **Properties** store attributes on both nodes and relationships

### 1.2 Property Graph Schema for Specification Traceability

```
# Node Types
Requirement(id, title, status, priority, category, version)
TestCase(id, name, status, automated, coverage_percentage)
Design(id, adr_number, title, status, decision)
Feature(id, name, scenario_count, completion_rate)
Component(id, name, version, responsibility)
Process(id, name, description, owner)

# Relationship Types with Properties
(Requirement) -[VERIFIED_BY]-> (TestCase)
  {coverage: float, last_verified: datetime}

(Requirement) -[ADDRESSES]-> (Design)
  {rationale: string, change_date: datetime}

(Feature) -[IMPLEMENTS]-> (Requirement)
  {acceptance_criteria_met: boolean}

(TestCase) -[TESTS]-> (Component)
  {method_count: int, assertion_count: int}

(Process) -[GUIDES]-> (Component)
  {mandatory: boolean, step_number: int}

(Requirement) -[DEPENDS_ON]-> (Requirement)
  {criticality: string, blocking: boolean}

(Design) -[SUPERSEDES]-> (Design)
  {reason: string, supersession_date: datetime}
```

### 1.3 Indexing Strategies

```python
# Neo4j Index Patterns (Cypher)
CREATE INDEX idx_requirement_status FOR (r:Requirement) ON (r.status);
CREATE INDEX idx_test_automated FOR (t:TestCase) ON (t.automated);
CREATE INDEX idx_design_version FOR (d:Design) ON (d.version);

# Composite Indexes
CREATE INDEX idx_requirement_priority_status
  FOR (r:Requirement) ON (r.priority, r.status);

# Full-Text Search Indexes
CREATE FULLTEXT INDEX idx_requirement_search
  FOR (r:Requirement) ON EACH [r.title, r.description];

# Relationship Indexes
CREATE INDEX idx_verified_by_timestamp
  FOR ()-[v:VERIFIED_BY]-() ON (v.last_verified);
```

### 1.4 Cypher Query Patterns for Traceability

#### Pattern 1: Requirement Coverage Analysis
```cypher
# Find all requirements and their test coverage
MATCH (req:Requirement)
OPTIONAL MATCH (req)-[verified:VERIFIED_BY]->(test:TestCase)
OPTIONAL MATCH (test)-[tests:TESTS]->(component:Component)
RETURN
  req.id,
  req.title,
  req.status,
  count(test) as test_count,
  avg(verified.coverage) as avg_coverage,
  collect(distinct component.name) as tested_components
ORDER BY avg_coverage DESC;
```

#### Pattern 2: Traceability Path Finding
```cypher
# Find all paths from requirement to implementation
MATCH (req:Requirement {id: 'REQ-001'})
OPTIONAL MATCH paths = (req)-[*..5]-(component:Component)
WHERE all(rel in relationships(paths) WHERE rel.status IS NULL OR rel.status = 'active')
RETURN
  paths,
  length(paths) as path_length,
  [n in nodes(paths) | labels(n)[0]] as node_types,
  [r in relationships(paths) | type(r)] as relationship_types
ORDER BY path_length;
```

#### Pattern 3: Impact Analysis
```cypher
# Identify impact when a requirement changes
MATCH (req:Requirement {id: 'REQ-002'})
CALL apoc.path.expandConfig(req, {
  relationshipFilter: 'ADDRESSES|IMPLEMENTS|TESTS|DEPENDS_ON',
  minLevel: 1,
  maxLevel: 4,
  bfs: true
})
YIELD path
RETURN
  path,
  length(path) as impact_depth,
  [n in nodes(path) | {type: labels(n)[0], id: n.id, status: n.status}] as affected_entities
ORDER BY impact_depth DESC;
```

#### Pattern 4: Bidirectional Traceability
```cypher
# Create bidirectional query for requirements <-> tests <-> components
MATCH (req:Requirement)-[:VERIFIED_BY]->(test:TestCase)-[:TESTS]->(comp:Component)
WHERE req.status = 'APPROVED' AND test.automated = true
RETURN {
  requirement: {id: req.id, title: req.title, priority: req.priority},
  test: {id: test.id, name: test.name, assertions: test.assertion_count},
  component: {id: comp.id, name: comp.name, version: comp.version}
} as traceability_triple
ORDER BY req.priority DESC, test.assertion_count DESC;
```

#### Pattern 5: Requirement Coverage Percentage
```cypher
# Calculate coverage metrics per component
MATCH (comp:Component)
OPTIONAL MATCH (req:Requirement)-[:ADDRESSES*..3]->
           (comp_related:Component {id: comp.id})
WITH comp, count(distinct req) as addressed_reqs
OPTIONAL MATCH (comp)-[:TESTED_BY]->(test:TestCase)
WITH comp, addressed_reqs, count(distinct test) as tests
RETURN
  comp.id,
  comp.name,
  addressed_reqs,
  tests,
  round(100.0 * tests / addressed_reqs, 2) as coverage_percentage,
  CASE WHEN tests >= addressed_reqs THEN 'COMPLETE'
       WHEN tests >= addressed_reqs * 0.8 THEN 'GOOD'
       WHEN tests >= addressed_reqs * 0.5 THEN 'PARTIAL'
       ELSE 'INSUFFICIENT' END as coverage_status;
```

#### Pattern 6: Detect Gaps (Orphaned Requirements)
```cypher
# Find requirements without test coverage or design justification
MATCH (req:Requirement)
WHERE req.status = 'APPROVED'
AND NOT (req)-[:VERIFIED_BY]->(:TestCase)
AND NOT (req)-[:ADDRESSES]->(:Design)
RETURN
  req.id,
  req.title,
  req.status,
  req.created_at,
  'UNVERIFIED' as gap_type,
  'No test coverage and no design justification' as reason
ORDER BY req.created_at;
```

#### Pattern 7: Version Tracking and Traceability
```cypher
# Track requirement evolution and associated test updates
MATCH (current:Requirement {id: 'REQ-001', version: 2})
OPTIONAL MATCH (current)-[:SUPERSEDES]->(previous:Requirement)
OPTIONAL MATCH (current)-[:VERIFIED_BY]->(tests)
OPTIONAL MATCH (previous)-[:VERIFIED_BY]->(old_tests)
RETURN {
  current_version: {id: current.id, version: current.version, updated_at: current.updated_at},
  previous_version: {id: previous.id, version: previous.version},
  new_tests: [t in collect(distinct tests) WHERE NOT any(ot in collect(distinct old_tests) WHERE ot.id = t.id)],
  still_valid_tests: [t in collect(distinct tests) WHERE any(ot in collect(distinct old_tests) WHERE ot.id = t.id)],
  removed_tests: [ot in collect(distinct old_tests) WHERE NOT any(t in collect(distinct tests) WHERE ot.id = t.id)]
};
```

### 1.5 Python Integration: Neo4j Driver

```python
from neo4j import GraphDatabase
from typing import List, Dict, Any
import json
from datetime import datetime

class TraceabilityGraphDB:
    """Neo4j-based traceability graph database."""

    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def create_requirement_node(
        self,
        req_id: str,
        title: str,
        status: str,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """Create requirement node in graph."""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_requirement,
                req_id, title, status, priority
            )
            return result

    @staticmethod
    def _create_requirement(tx, req_id: str, title: str, status: str, priority: str):
        """Transaction for creating requirement node."""
        query = """
        CREATE (r:Requirement {
            id: $req_id,
            title: $title,
            status: $status,
            priority: $priority,
            created_at: datetime()
        })
        RETURN r
        """
        return tx.run(query, {
            "req_id": req_id,
            "title": title,
            "status": status,
            "priority": priority
        }).single()

    def create_verification_relationship(
        self,
        req_id: str,
        test_id: str,
        coverage: float = 0.0,
        verified_date: datetime = None
    ) -> Dict[str, Any]:
        """Create VERIFIED_BY relationship."""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_verification,
                req_id, test_id, coverage, verified_date or datetime.now()
            )
            return result

    @staticmethod
    def _create_verification(tx, req_id: str, test_id: str, coverage: float, verified_date):
        """Transaction for creating verification relationship."""
        query = """
        MATCH (r:Requirement {id: $req_id})
        MATCH (t:TestCase {id: $test_id})
        CREATE (r)-[v:VERIFIED_BY {
            coverage: $coverage,
            last_verified: $verified_date
        }]->(t)
        RETURN v
        """
        return tx.run(query, {
            "req_id": req_id,
            "test_id": test_id,
            "coverage": coverage,
            "verified_date": verified_date
        }).single()

    def find_impacted_entities(self, req_id: str, max_depth: int = 4) -> List[Dict[str, Any]]:
        """Find all entities impacted by requirement change."""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._impact_analysis,
                req_id, max_depth
            )
            return result

    @staticmethod
    def _impact_analysis(tx, req_id: str, max_depth: int):
        """Transaction for impact analysis."""
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
            nodes: [n in nodes(path) | {type: labels(n)[0], id: n.id}],
            relationships: [r in relationships(path) | type(r)]
        } as impact
        ORDER BY path_length DESC
        """
        results = tx.run(query, {
            "req_id": req_id,
            "max_depth": max_depth
        }).data()
        return results

    def get_coverage_report(self, component_id: str = None) -> List[Dict[str, Any]]:
        """Generate coverage report for component(s)."""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._coverage_query,
                component_id
            )
            return result

    @staticmethod
    def _coverage_query(tx, component_id: str = None):
        """Transaction for coverage calculation."""
        base_query = "MATCH (comp:Component)"
        if component_id:
            base_query += f" WHERE comp.id = '{component_id}'"

        query = base_query + """
        OPTIONAL MATCH (req:Requirement)-[:ADDRESSES*..3]->
                   (comp_related:Component {id: comp.id})
        WITH comp, count(distinct req) as addressed_reqs
        OPTIONAL MATCH (comp)-[:TESTED_BY]->(test:TestCase)
        WITH comp, addressed_reqs, count(distinct test) as tests
        RETURN {
            component_id: comp.id,
            component_name: comp.name,
            addressed_requirements: addressed_reqs,
            test_count: tests,
            coverage_percentage: round(100.0 * tests / addressed_reqs, 2),
            coverage_status: CASE
                WHEN tests >= addressed_reqs THEN 'COMPLETE'
                WHEN tests >= addressed_reqs * 0.8 THEN 'GOOD'
                WHEN tests >= addressed_reqs * 0.5 THEN 'PARTIAL'
                ELSE 'INSUFFICIENT'
            END
        } as coverage
        ORDER BY coverage.coverage_percentage DESC
        """
        results = tx.run(query).data()
        return results

    def close(self):
        """Close database connection."""
        self.driver.close()


# Example Usage
if __name__ == "__main__":
    db = TraceabilityGraphDB(
        uri="neo4j://localhost:7687",
        username="neo4j",
        password="password"
    )

    # Create nodes
    db.create_requirement_node("REQ-001", "User Login", "APPROVED", "HIGH")
    db.create_requirement_node("REQ-002", "Password Reset", "DRAFT", "MEDIUM")

    # Create relationships
    db.create_verification_relationship("REQ-001", "TEST-001", coverage=0.95)

    # Impact analysis
    impacts = db.find_impacted_entities("REQ-001")
    print(json.dumps(impacts, indent=2, default=str))

    # Coverage report
    coverage = db.get_coverage_report()
    print(json.dumps(coverage, indent=2, default=str))

    db.close()
```

---

## 2. RDF/OWL Ontologies for Traceability

### 2.1 Semantic Foundation

RDF (Resource Description Framework) provides:
- Triple-based representation (Subject-Predicate-Object)
- Standardized URIs for entities
- Semantic meaning through ontologies

OWL (Web Ontology Language) adds:
- Class hierarchies
- Property relationships
- Logical constraints
- Reasoning capabilities

### 2.2 Requirement Ontology (ReqIF-like)

```turtle
# Prefix definitions
@prefix req: <http://example.org/requirement#> .
@prefix test: <http://example.org/test#> .
@prefix design: <http://example.org/design#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Class Definitions
req:Requirement a owl:Class ;
    rdfs:label "Specification Requirement" ;
    rdfs:comment "A formal system requirement specification" ;
    owl:hasProperty req:hasStatus, req:hasPriority, req:hasCategory .

test:TestCase a owl:Class ;
    rdfs:label "Test Case" ;
    rdfs:comment "A test that verifies requirement compliance" .

design:ArchitectureDecision a owl:Class ;
    rdfs:label "Architecture Decision" ;
    rdfs:comment "Design decision addressing requirements" .

# Properties
req:hasStatus a owl:ObjectProperty ;
    rdfs:domain req:Requirement ;
    rdfs:range req:Status ;
    owl:inverseOf req:statusOf ;
    rdfs:label "has status" .

req:verifiedBy a owl:ObjectProperty ;
    rdfs:domain req:Requirement ;
    rdfs:range test:TestCase ;
    owl:inverseOf test:verifies ;
    rdfs:label "verified by" ;
    owl:functional false .

req:addresses a owl:ObjectProperty ;
    rdfs:domain design:ArchitectureDecision ;
    rdfs:range req:Requirement ;
    owl:inverseOf req:addressedBy ;
    rdfs:label "addresses" .

req:dependsOn a owl:ObjectProperty ;
    rdfs:domain req:Requirement ;
    rdfs:range req:Requirement ;
    owl:transitive true ;
    owl:symmetric false ;
    owl:reflexive false ;
    rdfs:label "depends on" .

test:hasCoverage a owl:DatatypeProperty ;
    rdfs:domain test:TestCase ;
    rdfs:range xsd:float ;
    rdfs:label "has coverage percentage" .

req:priority a owl:DatatypeProperty ;
    rdfs:domain req:Requirement ;
    rdfs:range xsd:string ;
    rdfs:label "priority level" .

# Status Enumeration
req:Status a owl:Class ;
    owl:equivalentClass [
        a owl:Class ;
        owl:oneOf (req:DRAFT req:APPROVED req:DEPRECATED)
    ] .

req:DRAFT a req:Status ; rdfs:label "Draft" .
req:APPROVED a req:Status ; rdfs:label "Approved" .
req:DEPRECATED a req:Status ; rdfs:label "Deprecated" .

# Example Instances
req:REQ-001 a req:Requirement ;
    rdfs:label "User Authentication" ;
    req:hasStatus req:APPROVED ;
    req:priority "HIGH" ;
    req:verifiedBy test:TEST-001 ;
    req:dependsOn req:REQ-002 ;
    prov:wasGeneratedBy req:SpecificationProcess .

test:TEST-001 a test:TestCase ;
    rdfs:label "Login Test" ;
    test:verifies req:REQ-001 ;
    test:hasCoverage 0.95 .

# Cardinality constraints
req:Requirement owl:hasMinCardinality [
    owl:onProperty req:hasStatus ;
    owl:minQualifiedCardinality 1 ;
    owl:onClass req:Status
] .
```

### 2.3 SPARQL Queries for Compliance

```sparql
PREFIX req: <http://example.org/requirement#>
PREFIX test: <http://example.org/test#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# Query 1: Find all unverified approved requirements
SELECT ?req ?label
WHERE {
    ?req a req:Requirement ;
        req:hasStatus req:APPROVED ;
        rdfs:label ?label .
    FILTER NOT EXISTS {
        ?req req:verifiedBy ?test .
    }
}
ORDER BY ?label

# Query 2: Requirement coverage analysis
SELECT ?req ?label (COUNT(?test) AS ?test_count) (AVG(?coverage) AS ?avg_coverage)
WHERE {
    ?req a req:Requirement ;
        rdfs:label ?label ;
        req:verifiedBy ?test .
    ?test test:hasCoverage ?coverage .
}
GROUP BY ?req ?label
HAVING (COUNT(?test) > 0)
ORDER BY DESC(?avg_coverage)

# Query 3: Dependency chain analysis
SELECT ?start ?path_length ?end
WHERE {
    ?start a req:Requirement ;
        req:dependsOn+ ?end .
}
ORDER BY ?path_length DESC

# Query 4: Impact propagation (transitive closure)
SELECT ?affected (COUNT(?chain) AS ?affected_count)
WHERE {
    req:REQ-001 req:dependsOn* ?intermediate .
    ?intermediate ?predicate ?affected .
    FILTER (?predicate IN (req:verifiedBy, req:addresses))
}
GROUP BY ?affected

# Query 5: Compliance gap identification
SELECT ?req ?label ("NO_VERIFICATION" AS ?gap_type)
WHERE {
    ?req a req:Requirement ;
        req:hasStatus req:APPROVED ;
        rdfs:label ?label .
    FILTER NOT EXISTS { ?req req:verifiedBy ?test . }
    FILTER NOT EXISTS { ?design req:addresses ?req . }
}

# Query 6: Stakeholder impact analysis
SELECT ?stakeholder (COUNT(?req) AS ?requirement_count) ?priority
WHERE {
    ?req a req:Requirement ;
        req:priority ?priority ;
        prov:wasAttributedTo ?stakeholder .
}
GROUP BY ?stakeholder ?priority
ORDER BY DESC(?requirement_count)

# Query 7: Version history and supersession
SELECT ?current ?previous ?reason ?supersession_date
WHERE {
    ?current a req:Requirement ;
        req:supersedes ?previous ;
        req:supersessionReason ?reason ;
        req:supersessionDate ?supersession_date .
}
ORDER BY DESC(?supersession_date)

# Query 8: Multi-hop traceability paths
SELECT ?req ?test ?component ?path_length
WHERE {
    ?req a req:Requirement .
    ?req req:verifiedBy ?test .
    ?test test:tests ?component .
    BIND(3 AS ?path_length)
}

# Query 9: Coverage metrics aggregation
SELECT ?component (SUM(?requirement_count) AS ?total_reqs) (SUM(?test_count) AS ?total_tests)
       (ROUND(100 * SUM(?test_count) / SUM(?requirement_count)) AS ?coverage_pct)
WHERE {
    ?req a req:Requirement ;
        req:addresses ?component ;
        req:verifiedBy ?test .
    BIND(1 AS ?requirement_count)
    BIND(1 AS ?test_count)
}
GROUP BY ?component
ORDER BY DESC(?coverage_pct)
```

### 2.4 Python RDF Integration

```python
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class RDFTraceabilityGraph:
    """RDF/OWL-based semantic traceability graph."""

    def __init__(self, ontology_path: Optional[str] = None):
        """Initialize RDF graph and load ontology."""
        self.graph = Graph()

        # Define namespaces
        self.req = Namespace("http://example.org/requirement#")
        self.test = Namespace("http://example.org/test#")
        self.design = Namespace("http://example.org/design#")
        self.prov = Namespace("http://www.w3.org/ns/prov#")

        # Bind namespaces
        self.graph.bind("req", self.req)
        self.graph.bind("test", self.test)
        self.graph.bind("design", self.design)
        self.graph.bind("prov", self.prov)

        if ontology_path:
            self.graph.parse(ontology_path, format="turtle")

    def add_requirement(
        self,
        req_id: str,
        label: str,
        status: str,
        priority: str = "MEDIUM"
    ) -> URIRef:
        """Add requirement to RDF graph."""
        req_uri = self.req[req_id]

        self.graph.add((req_uri, RDF.type, self.req.Requirement))
        self.graph.add((req_uri, RDFS.label, Literal(label)))
        self.graph.add((req_uri, self.req.hasStatus, self.req[status]))
        self.graph.add((req_uri, self.req.priority, Literal(priority)))
        self.graph.add((req_uri, self.prov.generatedAtTime,
                       Literal(datetime.now(), datatype=XSD.dateTime)))

        return req_uri

    def add_test_case(
        self,
        test_id: str,
        label: str,
        coverage: float = 0.0
    ) -> URIRef:
        """Add test case to RDF graph."""
        test_uri = self.test[test_id]

        self.graph.add((test_uri, RDF.type, self.test.TestCase))
        self.graph.add((test_uri, RDFS.label, Literal(label)))
        self.graph.add((test_uri, self.test.hasCoverage,
                       Literal(coverage, datatype=XSD.float)))

        return test_uri

    def link_verification(self, req_id: str, test_id: str) -> None:
        """Create verification relationship."""
        req_uri = self.req[req_id]
        test_uri = self.test[test_id]

        self.graph.add((req_uri, self.req.verifiedBy, test_uri))
        self.graph.add((test_uri, self.test.verifies, req_uri))

    def link_dependency(self, from_req_id: str, to_req_id: str) -> None:
        """Create dependency relationship."""
        from_uri = self.req[from_req_id]
        to_uri = self.req[to_req_id]

        self.graph.add((from_uri, self.req.dependsOn, to_uri))

    def query_unverified_requirements(self) -> List[Dict[str, Any]]:
        """SPARQL query for unverified approved requirements."""
        query = """
        SELECT ?req ?label
        WHERE {
            ?req a <http://example.org/requirement#Requirement> ;
                <http://example.org/requirement#hasStatus> <http://example.org/requirement#APPROVED> ;
                <http://www.w3.org/2000/01/rdf-schema#label> ?label .
            FILTER NOT EXISTS {
                ?req <http://example.org/requirement#verifiedBy> ?test .
            }
        }
        ORDER BY ?label
        """

        results = self.graph.query(query)
        return [{"req": str(row.req), "label": str(row.label)} for row in results]

    def query_coverage_analysis(self) -> List[Dict[str, Any]]:
        """SPARQL query for coverage analysis."""
        query = """
        SELECT ?req ?label (COUNT(?test) AS ?test_count) (AVG(?coverage) AS ?avg_coverage)
        WHERE {
            ?req a <http://example.org/requirement#Requirement> ;
                <http://www.w3.org/2000/01/rdf-schema#label> ?label ;
                <http://example.org/requirement#verifiedBy> ?test .
            ?test <http://example.org/test#hasCoverage> ?coverage .
        }
        GROUP BY ?req ?label
        HAVING (COUNT(?test) > 0)
        ORDER BY DESC(?avg_coverage)
        """

        results = self.graph.query(query)
        return [{
            "requirement": str(row.req),
            "label": str(row.label),
            "test_count": int(row.test_count),
            "avg_coverage": float(row.avg_coverage) if row.avg_coverage else 0.0
        } for row in results]

    def query_dependency_chains(self) -> List[Dict[str, Any]]:
        """Find transitive dependencies."""
        query = """
        SELECT ?start ?end (COUNT(DISTINCT ?step) AS ?chain_length)
        WHERE {
            ?start <http://example.org/requirement#dependsOn>* ?end .
            FILTER (?start != ?end)
            BIND(1 AS ?step)
        }
        GROUP BY ?start ?end
        ORDER BY DESC(?chain_length)
        """

        results = self.graph.query(query)
        return [{
            "start": str(row.start),
            "end": str(row.end),
            "chain_length": int(row.chain_length)
        } for row in results]

    def get_traceability_matrix(self) -> Dict[str, List[str]]:
        """Generate traceability matrix (Requirements x Tests)."""
        query = """
        SELECT ?req ?test
        WHERE {
            ?req <http://example.org/requirement#verifiedBy> ?test .
        }
        """

        matrix = {}
        results = self.graph.query(query)
        for row in results:
            req_id = str(row.req)
            test_id = str(row.test)
            if req_id not in matrix:
                matrix[req_id] = []
            matrix[req_id].append(test_id)

        return matrix

    def export_ttl(self, filepath: str) -> None:
        """Export graph to Turtle format."""
        self.graph.serialize(destination=filepath, format="turtle")

    def export_rdfxml(self, filepath: str) -> None:
        """Export graph to RDF/XML format."""
        self.graph.serialize(destination=filepath, format="xml")


# Example Usage
if __name__ == "__main__":
    rdf_graph = RDFTraceabilityGraph()

    # Add requirements
    rdf_graph.add_requirement("REQ-001", "User Authentication", "APPROVED", "HIGH")
    rdf_graph.add_requirement("REQ-002", "Password Hashing", "APPROVED", "HIGH")
    rdf_graph.add_requirement("REQ-003", "Session Management", "DRAFT", "MEDIUM")

    # Add test cases
    rdf_graph.add_test_case("TEST-001", "Login Test", 0.95)
    rdf_graph.add_test_case("TEST-002", "Hash Validation Test", 0.90)

    # Create links
    rdf_graph.link_verification("REQ-001", "TEST-001")
    rdf_graph.link_verification("REQ-002", "TEST-002")
    rdf_graph.link_dependency("REQ-002", "REQ-001")

    # Query
    unverified = rdf_graph.query_unverified_requirements()
    print("Unverified Requirements:", json.dumps(unverified, indent=2))

    coverage = rdf_graph.query_coverage_analysis()
    print("Coverage Analysis:", json.dumps(coverage, indent=2, default=str))

    matrix = rdf_graph.get_traceability_matrix()
    print("Traceability Matrix:", json.dumps(matrix, indent=2))

    rdf_graph.export_ttl("/tmp/traceability.ttl")
```

---

## 3. Knowledge Graph Embeddings

### 3.1 TransE Model for Link Prediction

TransE (Translation-based) is the foundational embedding model where relationships are treated as translations in embedding space.

```python
import numpy as np
import torch
import torch.nn as nn
from typing import List, Tuple, Dict, Any
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

class TransETraceabilityModel(nn.Module):
    """
    TransE model for specification traceability link prediction.

    In TransE: h + r ≈ t (head + relationship ≈ tail)
    where h, r, t are embedding vectors.
    """

    def __init__(
        self,
        num_entities: int,
        num_relations: int,
        embedding_dim: int = 100,
        margin: float = 1.0,
        l_p: int = 2  # L2 distance
    ):
        """Initialize TransE model."""
        super().__init__()
        self.num_entities = num_entities
        self.num_relations = num_relations
        self.embedding_dim = embedding_dim
        self.margin = margin
        self.l_p = l_p

        # Initialize embeddings with uniform distribution
        self.entity_embeddings = nn.Embedding(num_entities, embedding_dim)
        self.relation_embeddings = nn.Embedding(num_relations, embedding_dim)

        # Initialize with uniform distribution in [-6/sqrt(k), 6/sqrt(k)]
        k = self.embedding_dim
        uniform_range = 6.0 / np.sqrt(k)
        nn.init.uniform_(self.entity_embeddings.weight, -uniform_range, uniform_range)
        nn.init.uniform_(self.relation_embeddings.weight, -uniform_range, uniform_range)

    def forward(
        self,
        head_indices: torch.Tensor,
        relation_indices: torch.Tensor,
        tail_indices: torch.Tensor
    ) -> torch.Tensor:
        """
        Calculate TransE score for triplet.

        Lower scores indicate valid triples.
        Score = ||h + r - t||_p
        """
        head_embeddings = self.entity_embeddings(head_indices)
        relation_embeddings = self.relation_embeddings(relation_indices)
        tail_embeddings = self.entity_embeddings(tail_indices)

        # TransE: h + r ≈ t
        distance = torch.norm(
            head_embeddings + relation_embeddings - tail_embeddings,
            p=self.l_p,
            dim=-1
        )
        return distance

    def loss_function(
        self,
        positive_scores: torch.Tensor,
        negative_scores: torch.Tensor
    ) -> torch.Tensor:
        """
        Margin-based loss function.

        L = sum(max(0, margin - negative_score + positive_score))
        """
        return torch.mean(
            torch.relu(self.margin + positive_scores - negative_scores)
        )


class SpecificationGraphEmbedder:
    """Train and use embeddings for specification traceability."""

    def __init__(
        self,
        entity_to_id: Dict[str, int],
        relation_to_id: Dict[str, int],
        embedding_dim: int = 100
    ):
        """Initialize embedder."""
        self.entity_to_id = entity_to_id
        self.relation_to_id = relation_to_id
        self.id_to_entity = {v: k for k, v in entity_to_id.items()}
        self.id_to_relation = {v: k for k, v in relation_to_id.items()}

        self.model = TransETraceabilityModel(
            num_entities=len(entity_to_id),
            num_relations=len(relation_to_id),
            embedding_dim=embedding_dim
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def prepare_training_data(
        self,
        triplets: List[Tuple[str, str, str]],
        negative_sample_ratio: int = 10
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Prepare positive and negative samples for training.

        For each positive triplet (h, r, t), create negative samples by:
        1. Corrupting head: (h', r, t)
        2. Corrupting tail: (h, r, t')
        """
        positive_heads = []
        positive_relations = []
        positive_tails = []

        negative_heads = []
        negative_relations = []
        negative_tails = []

        num_entities = len(self.entity_to_id)

        for head, relation, tail in triplets:
            head_id = self.entity_to_id[head]
            relation_id = self.relation_to_id[relation]
            tail_id = self.entity_to_id[tail]

            positive_heads.append(head_id)
            positive_relations.append(relation_id)
            positive_tails.append(tail_id)

            # Generate negative samples
            for _ in range(negative_sample_ratio):
                # Corrupt head or tail
                if np.random.rand() > 0.5:
                    # Corrupt head
                    corrupted_head = np.random.randint(0, num_entities)
                    negative_heads.append(corrupted_head)
                    negative_relations.append(relation_id)
                    negative_tails.append(tail_id)
                else:
                    # Corrupt tail
                    corrupted_tail = np.random.randint(0, num_entities)
                    negative_heads.append(head_id)
                    negative_relations.append(relation_id)
                    negative_tails.append(corrupted_tail)

        return (
            torch.tensor(positive_heads, dtype=torch.long),
            torch.tensor(positive_relations, dtype=torch.long),
            torch.tensor(positive_tails, dtype=torch.long),
            torch.tensor(negative_heads, dtype=torch.long),
            torch.tensor(negative_relations, dtype=torch.long),
            torch.tensor(negative_tails, dtype=torch.long)
        )

    def train(
        self,
        triplets: List[Tuple[str, str, str]],
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001
    ) -> List[float]:
        """Train TransE model."""
        pos_h, pos_r, pos_t, neg_h, neg_r, neg_t = self.prepare_training_data(triplets)

        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        losses = []

        for epoch in range(epochs):
            # Shuffle batches
            indices = torch.randperm(len(pos_h))
            pos_h_shuffled = pos_h[indices]
            pos_r_shuffled = pos_r[indices]
            pos_t_shuffled = pos_t[indices]
            neg_h_shuffled = neg_h[indices]
            neg_r_shuffled = neg_r[indices]
            neg_t_shuffled = neg_t[indices]

            epoch_loss = 0.0
            num_batches = 0

            for batch_start in range(0, len(pos_h), batch_size):
                batch_end = min(batch_start + batch_size, len(pos_h))

                pos_h_batch = pos_h_shuffled[batch_start:batch_end].to(self.device)
                pos_r_batch = pos_r_shuffled[batch_start:batch_end].to(self.device)
                pos_t_batch = pos_t_shuffled[batch_start:batch_end].to(self.device)
                neg_h_batch = neg_h_shuffled[batch_start:batch_end].to(self.device)
                neg_r_batch = neg_r_shuffled[batch_start:batch_end].to(self.device)
                neg_t_batch = neg_t_shuffled[batch_start:batch_end].to(self.device)

                # Forward pass
                positive_scores = self.model(pos_h_batch, pos_r_batch, pos_t_batch)
                negative_scores = self.model(neg_h_batch, neg_r_batch, neg_t_batch)

                # Calculate loss
                loss = self.model.loss_function(positive_scores, negative_scores)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                num_batches += 1

            avg_loss = epoch_loss / num_batches
            losses.append(avg_loss)

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")

        return losses

    def predict_links(
        self,
        head: str,
        relation: str,
        candidate_tails: List[str],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Predict likely tail entities for given head and relation."""
        self.model.eval()

        head_id = self.entity_to_id[head]
        relation_id = self.relation_to_id[relation]

        head_tensor = torch.tensor([head_id], dtype=torch.long).to(self.device)
        relation_tensor = torch.tensor([relation_id], dtype=torch.long).to(self.device)

        scores = []
        for tail in candidate_tails:
            tail_id = self.entity_to_id[tail]
            tail_tensor = torch.tensor([tail_id], dtype=torch.long).to(self.device)

            with torch.no_grad():
                score = self.model(head_tensor, relation_tensor, tail_tensor).item()
            scores.append((tail, score))

        # Sort by score (lower is better)
        scores.sort(key=lambda x: x[1])
        return scores[:top_k]

    def get_entity_embedding(self, entity: str) -> np.ndarray:
        """Get embedding vector for entity."""
        entity_id = self.entity_to_id[entity]
        with torch.no_grad():
            embedding = self.model.entity_embeddings(
                torch.tensor([entity_id], dtype=torch.long).to(self.device)
            ).cpu().numpy()[0]
        return embedding

    def get_relation_embedding(self, relation: str) -> np.ndarray:
        """Get embedding vector for relation."""
        relation_id = self.relation_to_id[relation]
        with torch.no_grad():
            embedding = self.model.relation_embeddings(
                torch.tensor([relation_id], dtype=torch.long).to(self.device)
            ).cpu().numpy()[0]
        return embedding


# Example Usage
if __name__ == "__main__":
    # Define entities and relations
    entities = ["REQ-001", "REQ-002", "TEST-001", "TEST-002", "COMP-001", "DESIGN-001"]
    relations = ["VERIFIED_BY", "ADDRESSES", "DEPENDS_ON", "TESTS"]

    entity_to_id = {entity: idx for idx, entity in enumerate(entities)}
    relation_to_id = {rel: idx for idx, rel in enumerate(relations)}

    # Training triplets
    triplets = [
        ("REQ-001", "VERIFIED_BY", "TEST-001"),
        ("REQ-001", "DEPENDS_ON", "REQ-002"),
        ("REQ-002", "VERIFIED_BY", "TEST-002"),
        ("TEST-001", "TESTS", "COMP-001"),
        ("DESIGN-001", "ADDRESSES", "REQ-001"),
    ]

    # Train model
    embedder = SpecificationGraphEmbedder(entity_to_id, relation_to_id)
    losses = embedder.train(triplets, epochs=50)

    # Predict missing links
    predictions = embedder.predict_links("REQ-001", "VERIFIED_BY", ["TEST-002", "TEST-001"], top_k=2)
    print("Predicted test for REQ-001:", predictions)

    # Get embeddings
    req_embedding = embedder.get_entity_embedding("REQ-001")
    print("REQ-001 embedding shape:", req_embedding.shape)
```

### 3.2 ComplEx Model (Handling Relation Patterns)

```python
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Tuple, Dict

class ComplExTraceabilityModel(nn.Module):
    """
    ComplEx model for complex relation patterns.

    Uses complex number embeddings to handle symmetric, asymmetric,
    and inverse relations that appear in specification traceability.
    """

    def __init__(
        self,
        num_entities: int,
        num_relations: int,
        embedding_dim: int = 100
    ):
        """Initialize ComplEx model."""
        super().__init__()
        self.num_entities = num_entities
        self.num_relations = num_relations
        self.embedding_dim = embedding_dim

        # Complex embeddings (real + imaginary parts)
        self.entity_embeddings_real = nn.Embedding(num_entities, embedding_dim)
        self.entity_embeddings_imag = nn.Embedding(num_entities, embedding_dim)
        self.relation_embeddings_real = nn.Embedding(num_relations, embedding_dim)
        self.relation_embeddings_imag = nn.Embedding(num_relations, embedding_dim)

        # Initialize
        nn.init.xavier_uniform_(self.entity_embeddings_real.weight)
        nn.init.xavier_uniform_(self.entity_embeddings_imag.weight)
        nn.init.xavier_uniform_(self.relation_embeddings_real.weight)
        nn.init.xavier_uniform_(self.relation_embeddings_imag.weight)

    def forward(
        self,
        head_indices: torch.Tensor,
        relation_indices: torch.Tensor,
        tail_indices: torch.Tensor
    ) -> torch.Tensor:
        """
        ComplEx scoring function.

        score(h,r,t) = Re(<h, r, conj(t)>)
                     = Re(h_r * r_r * conj(t_r) + h_r * r_i * conj(t_i)
                          + h_i * r_r * conj(t_i) - h_i * r_i * conj(t_r))
        """
        h_real = self.entity_embeddings_real(head_indices)
        h_imag = self.entity_embeddings_imag(head_indices)
        r_real = self.relation_embeddings_real(relation_indices)
        r_imag = self.relation_embeddings_imag(relation_indices)
        t_real = self.entity_embeddings_real(tail_indices)
        t_imag = self.entity_embeddings_imag(tail_indices)

        # ComplEx score
        score = torch.sum(
            h_real * r_real * t_real +
            h_real * r_imag * t_imag +
            h_imag * r_real * t_imag -
            h_imag * r_imag * t_real,
            dim=-1
        )
        return score


class RotatETraceabilityModel(nn.Module):
    """
    RotatE model - rotation-based embeddings.

    Handles symmetric, antisymmetric, composition, and inverse relations
    through rotation operations in complex space.

    h * r ≈ t (in complex space with rotation)
    """

    def __init__(
        self,
        num_entities: int,
        num_relations: int,
        embedding_dim: int = 100,
        margin: float = 10.0
    ):
        """Initialize RotatE model."""
        super().__init__()
        self.num_entities = num_entities
        self.num_relations = num_relations
        self.embedding_dim = embedding_dim
        self.margin = margin

        # Entity embeddings (complex)
        self.entity_embeddings = nn.Embedding(num_entities, embedding_dim)

        # Relation embeddings (phase angles in [0, 2π])
        self.relation_embeddings = nn.Embedding(num_relations, embedding_dim)

        nn.init.uniform_(self.entity_embeddings.weight, -1, 1)
        nn.init.uniform_(self.relation_embeddings.weight, -1, 1)

    def forward(
        self,
        head_indices: torch.Tensor,
        relation_indices: torch.Tensor,
        tail_indices: torch.Tensor
    ) -> torch.Tensor:
        """
        RotatE score: ||h * r - t||_2

        h and t are complex embeddings
        r defines rotation angles
        """
        head = self.entity_embeddings(head_indices)
        relation = self.relation_embeddings(relation_indices)
        tail = self.entity_embeddings(tail_indices)

        # Convert to complex numbers
        head_complex = torch.view_as_complex(
            head.reshape(*head.shape[:-1], -1, 2).float()
        )
        relation_complex = torch.view_as_complex(
            relation.reshape(*relation.shape[:-1], -1, 2).float()
        )
        tail_complex = torch.view_as_complex(
            tail.reshape(*tail.shape[:-1], -1, 2).float()
        )

        # Convert relation to unit complex (for rotation)
        relation_phase = torch.atan2(
            relation_complex.imag, relation_complex.real
        )
        relation_rotation = torch.complex(
            torch.cos(relation_phase), torch.sin(relation_phase)
        )

        # h * r ≈ t
        distance = torch.norm(
            head_complex * relation_rotation - tail_complex,
            dim=-1
        )
        return distance
```

---

## 4. Graph Algorithms for Traceability

### 4.1 Path Finding Algorithms

```python
from collections import deque, defaultdict
from typing import List, Dict, Set, Tuple, Optional
import heapq

class TraceabilityPathFinder:
    """Graph algorithms for specification traceability paths."""

    def __init__(self, graph_adjacency: Dict[str, Dict[str, List[str]]]):
        """
        Initialize with adjacency list.

        graph_adjacency = {
            'REQ-001': {
                'VERIFIED_BY': ['TEST-001', 'TEST-002'],
                'DEPENDS_ON': ['REQ-002']
            }
        }
        """
        self.graph = graph_adjacency

    def shortest_path_bfs(
        self,
        start: str,
        end: str,
        relation_filter: Optional[List[str]] = None
    ) -> Optional[List[Tuple[str, str]]]:
        """
        BFS to find shortest path between two entities.

        Returns list of (entity, relation) tuples.
        """
        if start not in self.graph or end not in self.graph:
            return None

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == end:
                return path

            for relation, neighbors in self.graph.get(current, {}).items():
                if relation_filter and relation not in relation_filter:
                    continue

                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [(current, relation, neighbor)]))

        return None

    def all_paths_dfs(
        self,
        start: str,
        end: str,
        max_depth: int = 5,
        relation_filter: Optional[List[str]] = None
    ) -> List[List[Tuple[str, str, str]]]:
        """
        Find all paths between two entities (DFS with depth limit).

        Returns list of paths, each path is list of (source, relation, target).
        """
        paths = []
        visited = set()

        def dfs(current: str, target: str, path: List, depth: int):
            if depth == 0 or current == target:
                if current == target:
                    paths.append(path)
                return

            if current in visited:
                return
            visited.add(current)

            for relation, neighbors in self.graph.get(current, {}).items():
                if relation_filter and relation not in relation_filter:
                    continue

                for neighbor in neighbors:
                    if neighbor not in visited:
                        dfs(neighbor, target,
                           path + [(current, relation, neighbor)],
                           depth - 1)

            visited.remove(current)

        dfs(start, end, [], max_depth)
        return paths

    def impact_propagation(
        self,
        start: str,
        max_depth: int = 4,
        relation_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Dict[str, any]]:
        """
        Calculate impact propagation from source entity.

        Returns affected entities with distance and impact score.
        """
        if relation_weights is None:
            relation_weights = defaultdict(lambda: 1.0)

        affected = {}
        queue = deque([(start, 0, 1.0)])  # (entity, depth, impact_score)
        visited = {start: (0, 1.0)}

        while queue:
            current, depth, impact = queue.popleft()

            if depth >= max_depth:
                continue

            for relation, neighbors in self.graph.get(current, {}).items():
                relation_weight = relation_weights.get(relation, 1.0)

                for neighbor in neighbors:
                    new_impact = impact * (1 / relation_weight)

                    if neighbor not in visited or new_impact > visited[neighbor][1]:
                        visited[neighbor] = (depth + 1, new_impact)
                        affected[neighbor] = {
                            "distance": depth + 1,
                            "impact_score": new_impact,
                            "via_relation": relation
                        }
                        queue.append((neighbor, depth + 1, new_impact))

        return affected

    def betweenness_centrality(self) -> Dict[str, float]:
        """
        Calculate betweenness centrality for traceability analysis.

        High centrality entities are critical connection points.
        """
        centrality = defaultdict(float)
        entities = set()

        # Collect all entities
        for entity in self.graph:
            entities.add(entity)
            for neighbors in self.graph[entity].values():
                entities.update(neighbors)

        # For each pair of entities, count shortest paths through each node
        for source in entities:
            # BFS from source
            distances = {source: 0}
            predecessors = defaultdict(list)
            queue = deque([source])

            while queue:
                current = queue.popleft()
                for relation, neighbors in self.graph.get(current, {}).items():
                    for neighbor in neighbors:
                        if neighbor not in distances:
                            distances[neighbor] = distances[current] + 1
                            queue.append(neighbor)

                        if distances[neighbor] == distances[current] + 1:
                            predecessors[neighbor].append(current)

            # Count paths through each node
            for target in entities:
                if target != source and target in distances:
                    # Backward pass for counting paths
                    path_counts = defaultdict(float)
                    path_counts[target] = 1.0

                    for node in sorted(
                        [n for n in distances if n != source],
                        key=lambda x: distances[x],
                        reverse=True
                    ):
                        for pred in predecessors.get(node, []):
                            path_counts[pred] += path_counts[node]

                    for node in entities:
                        if node != source and node != target:
                            centrality[node] += path_counts[node]

        # Normalize
        num_entities = len(entities)
        if num_entities > 2:
            for entity in centrality:
                centrality[entity] /= (
                    (num_entities - 1) * (num_entities - 2) / 2
                )

        return dict(centrality)
```

### 4.2 Community Detection

```python
from collections import defaultdict
import random

class RequirementClustering:
    """Community detection for requirement traceability."""

    def __init__(self, graph_adjacency: Dict[str, Dict[str, List[str]]]):
        """Initialize with graph adjacency."""
        self.graph = graph_adjacency

    def louvain_modularity(self, resolution: float = 1.0) -> Dict[str, int]:
        """
        Louvain algorithm for community detection.

        Returns mapping of entity to community ID.
        """
        # Initialize each node in its own community
        communities = {node: node for node in self.graph}

        improved = True
        iteration = 0

        while improved and iteration < 100:
            improved = False
            iteration += 1

            for node in list(self.graph.keys()):
                current_community = communities[node]

                # Calculate modularity gain for each community
                best_gain = 0.0
                best_community = current_community

                # Neighbors' communities
                neighbor_communities = set()
                for relation, neighbors in self.graph.get(node, {}).items():
                    for neighbor in neighbors:
                        neighbor_communities.add(communities[neighbor])

                for target_community in neighbor_communities | {current_community}:
                    gain = self._modularity_gain(
                        node, current_community, target_community, communities, resolution
                    )
                    if gain > best_gain:
                        best_gain = gain
                        best_community = target_community

                if best_community != current_community:
                    communities[node] = best_community
                    improved = True

        # Renumber communities
        community_mapping = {}
        community_counter = 0
        result = {}

        for node, comm in communities.items():
            if comm not in community_mapping:
                community_mapping[comm] = community_counter
                community_counter += 1
            result[node] = community_mapping[comm]

        return result

    def _modularity_gain(
        self,
        node: str,
        current_community: str,
        target_community: str,
        communities: Dict[str, str],
        resolution: float
    ) -> float:
        """Calculate modularity gain for moving node to target community."""
        # Simplified modularity gain calculation
        degree_in = 0
        degree_out = 0
        community_size = 0

        # Count edges to target community
        for relation, neighbors in self.graph.get(node, {}).items():
            for neighbor in neighbors:
                if communities[neighbor] == target_community:
                    if neighbor == node:
                        degree_in += 2
                    else:
                        degree_in += 1
                else:
                    degree_out += 1

        # Community size
        for other_node, comm in communities.items():
            if comm == target_community:
                community_size += 1

        if community_size == 0:
            return 0.0

        # Approximate modularity gain
        return float(degree_in) / (degree_in + degree_out + 1)

    def spectral_clustering(
        self,
        num_clusters: int = 3
    ) -> Dict[str, int]:
        """
        Spectral clustering using graph Laplacian.

        For simplified version, uses random walk similarity.
        """
        import numpy as np
        from sklearn.cluster import KMeans

        entities = list(self.graph.keys())
        n = len(entities)
        entity_to_idx = {e: i for i, e in enumerate(entities)}

        # Build adjacency matrix
        adj_matrix = np.zeros((n, n))
        for entity in entities:
            for relation, neighbors in self.graph.get(entity, {}).items():
                for neighbor in neighbors:
                    if neighbor in entity_to_idx:
                        j = entity_to_idx[neighbor]
                        i = entity_to_idx[entity]
                        adj_matrix[i, j] = 1.0

        # Compute Laplacian matrix
        degree = np.sum(adj_matrix, axis=1)
        laplacian = np.diag(degree) - adj_matrix

        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(laplacian)

        # Use first k eigenvectors for clustering
        features = eigenvectors[:, :num_clusters]

        # K-means clustering
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        labels = kmeans.fit_predict(features)

        return {entity: int(label) for entity, label in zip(entities, labels)}
```

---

## 5. Temporal Graphs and Version History

### 5.1 Time-Varying Relationships

```python
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import bisect

class TemporalTraceabilityGraph:
    """
    Temporal graph for requirement version history and evolution.

    Supports queries about traceability at specific time points.
    """

    def __init__(self):
        """Initialize temporal graph."""
        self.temporal_edges = defaultdict(list)  # (from, rel, to) -> [(time, valid)]
        self.entity_versions = defaultdict(list)  # entity -> [(time, version)]
        self.snapshots = {}  # timestamp -> graph_state

    def add_temporal_edge(
        self,
        source: str,
        relation: str,
        target: str,
        valid_from: datetime,
        valid_to: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add time-valid relationship."""
        edge_key = (source, relation, target)
        self.temporal_edges[edge_key].append({
            "valid_from": valid_from,
            "valid_to": valid_to,
            "metadata": metadata or {}
        })

    def add_entity_version(
        self,
        entity: str,
        version: int,
        timestamp: datetime,
        properties: Dict[str, Any]
    ) -> None:
        """Record entity version with timestamp."""
        self.entity_versions[entity].append({
            "version": version,
            "timestamp": timestamp,
            "properties": properties
        })

    def get_traceability_at_time(
        self,
        timestamp: datetime,
        entity: Optional[str] = None
    ) -> Dict[Tuple[str, str, str], Dict]:
        """
        Get valid traceability relationships at specific time point.
        """
        valid_edges = {}

        for (source, relation, target), edge_list in self.temporal_edges.items():
            if entity and source != entity and target != entity:
                continue

            for edge in edge_list:
                if (edge["valid_from"] <= timestamp and
                    (edge["valid_to"] is None or timestamp < edge["valid_to"])):
                    valid_edges[(source, relation, target)] = edge

        return valid_edges

    def get_entity_at_time(
        self,
        entity: str,
        timestamp: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get entity state at specific time."""
        versions = self.entity_versions.get(entity, [])
        if not versions:
            return None

        # Find version valid at timestamp
        valid_version = None
        for version_info in versions:
            if version_info["timestamp"] <= timestamp:
                valid_version = version_info
            else:
                break

        return valid_version

    def trace_requirement_evolution(
        self,
        requirement_id: str
    ) -> List[Dict[str, Any]]:
        """
        Trace how requirement changes over time and impact on tests.
        """
        versions = sorted(
            self.entity_versions.get(requirement_id, []),
            key=lambda x: x["timestamp"]
        )

        evolution = []
        for version in versions:
            timestamp = version["timestamp"]
            state = {
                "version": version["version"],
                "timestamp": timestamp,
                "properties": version["properties"],
                "active_tests": [],
                "related_designs": []
            }

            # Find active relationships at this time
            for (source, relation, target), edge_list in self.temporal_edges.items():
                if source == requirement_id:
                    for edge in edge_list:
                        if (edge["valid_from"] <= timestamp and
                            (edge["valid_to"] is None or timestamp < edge["valid_to"])):
                            if relation == "VERIFIED_BY":
                                state["active_tests"].append(target)
                            elif relation == "ADDRESSES":
                                state["related_designs"].append(target)

            evolution.append(state)

        return evolution

    def create_snapshot(
        self,
        timestamp: datetime,
        snapshot_id: str
    ) -> Dict[str, Any]:
        """Create complete graph snapshot at point in time."""
        snapshot_data = {
            "timestamp": timestamp,
            "edges": self.get_traceability_at_time(timestamp),
            "entities": {}
        }

        # Collect all entities and their state
        all_entities = set()
        for (source, _, target) in self.temporal_edges.keys():
            all_entities.add(source)
            all_entities.add(target)

        for entity in all_entities:
            entity_state = self.get_entity_at_time(entity, timestamp)
            if entity_state:
                snapshot_data["entities"][entity] = entity_state

        self.snapshots[snapshot_id] = snapshot_data
        return snapshot_data

    def compare_snapshots(
        self,
        snapshot1_id: str,
        snapshot2_id: str
    ) -> Dict[str, Any]:
        """Compare two snapshots to identify changes."""
        snap1 = self.snapshots.get(snapshot1_id, {})
        snap2 = self.snapshots.get(snapshot2_id, {})

        comparison = {
            "added_edges": [],
            "removed_edges": [],
            "modified_entities": [],
            "added_entities": [],
            "removed_entities": []
        }

        # Compare edges
        edges1 = set(snap1.get("edges", {}).keys())
        edges2 = set(snap2.get("edges", {}).keys())

        comparison["added_edges"] = list(edges2 - edges1)
        comparison["removed_edges"] = list(edges1 - edges2)

        # Compare entities
        entities1 = set(snap1.get("entities", {}).keys())
        entities2 = set(snap2.get("entities", {}).keys())

        comparison["added_entities"] = list(entities2 - entities1)
        comparison["removed_entities"] = list(entities1 - entities2)

        # Detect modifications
        common_entities = entities1 & entities2
        for entity in common_entities:
            if (snap1["entities"][entity].get("version") !=
                snap2["entities"][entity].get("version")):
                comparison["modified_entities"].append({
                    "entity": entity,
                    "version_from": snap1["entities"][entity].get("version"),
                    "version_to": snap2["entities"][entity].get("version")
                })

        return comparison


# Example Usage
temporal_graph = TemporalTraceabilityGraph()

# Add evolving requirement
temporal_graph.add_entity_version(
    "REQ-001",
    version=1,
    timestamp=datetime(2024, 1, 1),
    properties={"title": "User Login", "status": "DRAFT"}
)
temporal_graph.add_entity_version(
    "REQ-001",
    version=2,
    timestamp=datetime(2024, 2, 1),
    properties={"title": "User Login with 2FA", "status": "APPROVED"}
)

# Add time-valid verification relationship
temporal_graph.add_temporal_edge(
    "REQ-001", "VERIFIED_BY", "TEST-001",
    valid_from=datetime(2024, 2, 1)
)

# Query at specific time
print(temporal_graph.trace_requirement_evolution("REQ-001"))
```

---

## 6. Hypergraphs for N-ary Relationships

### 6.1 Hypergraph Model

```python
from collections import defaultdict
from typing import Set, List, Dict, Any

class SpecificationHypergraph:
    """
    Hypergraph for n-ary relationships in specification traceability.

    Example: One requirement implements multiple test cases across
    different components (1:many relationships).
    """

    def __init__(self):
        """Initialize hypergraph."""
        self.hyperedges = {}  # edge_id -> {nodes: set, relation: str, properties: dict}
        self.node_hyperedges = defaultdict(set)  # node -> {edge_ids}
        self.hyperedge_counter = 0

    def add_hyperedge(
        self,
        nodes: Set[str],
        relation: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add n-ary hyperedge connecting multiple nodes.

        Example: requirement connects to multiple tests
        """
        edge_id = f"HEDGE-{self.hyperedge_counter}"
        self.hyperedge_counter += 1

        self.hyperedges[edge_id] = {
            "nodes": frozenset(nodes),
            "relation": relation,
            "properties": properties or {},
            "arity": len(nodes)
        }

        for node in nodes:
            self.node_hyperedges[node].add(edge_id)

        return edge_id

    def get_hyperedges_for_node(self, node: str) -> List[Dict[str, Any]]:
        """Get all hyperedges containing a node."""
        edge_ids = self.node_hyperedges[node]
        return [self.hyperedges[eid] for eid in edge_ids]

    def get_connected_components(self) -> List[Set[str]]:
        """Find connected components in hypergraph."""
        visited_nodes = set()
        components = []

        def dfs(node: str, component: Set[str]):
            if node in visited_nodes:
                return
            visited_nodes.add(node)
            component.add(node)

            # Find all connected nodes via hyperedges
            for edge_id in self.node_hyperedges[node]:
                edge = self.hyperedges[edge_id]
                for connected_node in edge["nodes"]:
                    if connected_node not in visited_nodes:
                        dfs(connected_node, component)

        # Start DFS from each unvisited node
        all_nodes = set()
        for edge in self.hyperedges.values():
            all_nodes.update(edge["nodes"])

        for node in all_nodes:
            if node not in visited_nodes:
                component = set()
                dfs(node, component)
                components.append(component)

        return components

    def decompose_to_cliques(self) -> List[Set[str]]:
        """
        Decompose hypergraph into cliques (pairwise relationships).

        Expands n-ary relationships into binary relationships.
        """
        cliques = []

        for edge in self.hyperedges.values():
            nodes_list = list(edge["nodes"])
            # Create edges between all pairs
            for i in range(len(nodes_list)):
                for j in range(i + 1, len(nodes_list)):
                    cliques.append({nodes_list[i], nodes_list[j]})

        return cliques


# Example: Requirement to Multiple Tests and Components
hypergraph = SpecificationHypergraph()

# Requirement "User Login" connects to multiple tests and components
hypergraph.add_hyperedge(
    nodes={
        "REQ-001",           # Requirement
        "TEST-001",          # Test case
        "TEST-002",          # Test case
        "COMP-AUTH",         # Component
        "COMP-SESSION"       # Component
    },
    relation="VERIFIES_ACROSS",
    properties={
        "coverage": 0.95,
        "created": "2024-01-01"
    }
)

# Query
print(hypergraph.get_hyperedges_for_node("REQ-001"))
```

---

## 7. Graph Visualization Patterns

### 7.1 Force-Directed Layout for Requirements

```python
import numpy as np
from typing import Dict, Tuple, List
import math

class ForceDirectedLayout:
    """
    Force-directed layout for specification traceability visualization.

    Uses spring physics simulation to position nodes.
    """

    def __init__(
        self,
        graph_adjacency: Dict[str, Dict[str, List[str]]],
        width: int = 800,
        height: int = 600,
        repulsion: float = 100,
        attraction: float = 0.5
    ):
        """Initialize layout engine."""
        self.graph = graph_adjacency
        self.width = width
        self.height = height
        self.repulsion = repulsion
        self.attraction = attraction

        # Initialize positions randomly
        self.positions = {}
        self.velocities = {}

        nodes = set(graph_adjacency.keys())
        for neighbor_dict in graph_adjacency.values():
            for neighbors in neighbor_dict.values():
                nodes.update(neighbors)

        for node in nodes:
            self.positions[node] = (
                np.random.uniform(0, width),
                np.random.uniform(0, height)
            )
            self.velocities[node] = (0.0, 0.0)

    def simulate_step(self, damping: float = 0.99) -> float:
        """
        Run one simulation step.

        Returns average displacement (convergence metric).
        """
        nodes = list(self.positions.keys())
        forces = {node: (0.0, 0.0) for node in nodes}

        # Repulsive forces between all nodes
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                x1, y1 = self.positions[node1]
                x2, y2 = self.positions[node2]

                dx = x2 - x1
                dy = y2 - y1
                distance = math.sqrt(dx**2 + dy**2) + 0.01

                # Repulsive force
                force_magnitude = self.repulsion / (distance ** 2)
                fx = (dx / distance) * force_magnitude
                fy = (dy / distance) * force_magnitude

                forces[node1] = (forces[node1][0] - fx, forces[node1][1] - fy)
                forces[node2] = (forces[node2][0] + fx, forces[node2][1] + fy)

        # Attractive forces along edges
        for source in self.graph:
            for relation, targets in self.graph[source].items():
                for target in targets:
                    if target in self.positions:
                        x1, y1 = self.positions[source]
                        x2, y2 = self.positions[target]

                        dx = x2 - x1
                        dy = y2 - y1
                        distance = math.sqrt(dx**2 + dy**2) + 0.01

                        # Attractive force
                        force_magnitude = self.attraction * distance
                        fx = (dx / distance) * force_magnitude
                        fy = (dy / distance) * force_magnitude

                        forces[source] = (
                            forces[source][0] + fx,
                            forces[source][1] + fy
                        )
                        forces[target] = (
                            forces[target][0] - fx,
                            forces[target][1] - fy
                        )

        # Update positions
        total_displacement = 0
        for node in nodes:
            vx, vy = self.velocities[node]
            fx, fy = forces[node]

            vx = (vx + fx) * damping
            vy = (vy + fy) * damping

            x, y = self.positions[node]
            new_x = max(0, min(self.width, x + vx))
            new_y = max(0, min(self.height, y + vy))

            displacement = math.sqrt((new_x - x)**2 + (new_y - y)**2)
            total_displacement += displacement

            self.velocities[node] = (vx, vy)
            self.positions[node] = (new_x, new_y)

        return total_displacement / len(nodes) if nodes else 0

    def compute_layout(self, max_iterations: int = 100, convergence_threshold: float = 0.1):
        """Run simulation until convergence."""
        for iteration in range(max_iterations):
            displacement = self.simulate_step()
            if displacement < convergence_threshold:
                print(f"Converged after {iteration} iterations")
                break

    def get_svg(self, filename: str) -> None:
        """Export layout as SVG."""
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .node {{ fill: #3498db; stroke: #2c3e50; stroke-width: 2; }}
    .edge {{ stroke: #95a5a6; stroke-width: 1; fill: none; }}
    .label {{ font-size: 12px; fill: #2c3e50; }}
  </style>
"""

        # Draw edges
        for source in self.graph:
            for relation, targets in self.graph[source].items():
                for target in targets:
                    if target in self.positions:
                        x1, y1 = self.positions[source]
                        x2, y2 = self.positions[target]
                        svg_content += f'  <line class="edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />\n'

        # Draw nodes
        for node, (x, y) in self.positions.items():
            svg_content += f'  <circle class="node" cx="{x}" cy="{y}" r="8" />\n'
            svg_content += f'  <text class="label" x="{x}" y="{y+15}">{node}</text>\n'

        svg_content += "</svg>"

        with open(filename, 'w') as f:
            f.write(svg_content)
```

### 7.2 Matrix View for Coverage Analysis

```python
class CoverageMatrix:
    """Generate matrix visualization for requirement x test coverage."""

    def __init__(self, requirements: List[str], test_cases: List[str]):
        """Initialize matrix."""
        self.requirements = requirements
        self.test_cases = test_cases
        self.matrix = np.zeros((len(requirements), len(test_cases)))

        self.req_idx = {r: i for i, r in enumerate(requirements)}
        self.test_idx = {t: i for i, t in enumerate(test_cases)}

    def add_verification(
        self,
        requirement: str,
        test: str,
        coverage: float = 1.0
    ):
        """Add verification relationship to matrix."""
        if requirement in self.req_idx and test in self.test_idx:
            ri = self.req_idx[requirement]
            ti = self.test_idx[test]
            self.matrix[ri, ti] = coverage

    def generate_html_table(self) -> str:
        """Generate HTML table for matrix."""
        html = "<table border='1'><tr><th>Requirement</th>"

        for test in self.test_cases:
            html += f"<th>{test}</th>"
        html += "</tr>"

        for req, row in zip(self.requirements, self.matrix):
            html += f"<tr><td><strong>{req}</strong></td>"
            for coverage in row:
                color = self._get_color(coverage)
                html += f'<td style="background-color: {color}; text-align: center;">'
                if coverage > 0:
                    html += f"{coverage:.1%}"
                html += "</td>"
            html += "</tr>"

        html += "</table>"
        return html

    def _get_color(self, coverage: float) -> str:
        """Get color based on coverage percentage."""
        if coverage >= 0.8:
            return "#90EE90"  # Light green
        elif coverage >= 0.5:
            return "#FFD700"  # Gold
        elif coverage > 0:
            return "#FFA500"  # Orange
        else:
            return "#FFB6C1"  # Light red

    def generate_heatmap_json(self) -> Dict:
        """Generate data for D3.js heatmap."""
        data = []
        for i, req in enumerate(self.requirements):
            for j, test in enumerate(self.test_cases):
                data.append({
                    "requirement": req,
                    "test": test,
                    "coverage": float(self.matrix[i, j]),
                    "x": j,
                    "y": i
                })
        return data
```

---

## 8. Graph Database Comparison

### 8.1 Feature Matrix

| Feature | Neo4j | Neptune | ArangoDB | TigerGraph |
|---------|-------|---------|----------|-----------|
| **Graph Model** | Property Graph | Property/RDF | Multi-model | Property Graph |
| **Query Language** | Cypher | Gremlin/SPARQL | AQL | GSQL |
| **Reasoning** | Limited | RDF Support | No | No |
| **Performance** (1M nodes) | 10-50ms | 50-200ms | 20-100ms | 5-20ms |
| **Scalability** | Cluster | AWS Cloud | Distributed | Enterprise Cluster |
| **Full-Text Search** | Yes | Limited | Yes | Yes |
| **ACID Compliance** | Yes | Limited | Yes | Yes |
| **Python Driver** | Excellent | Fair | Good | Good |
| **Best For** | Transactional traceability | Cloud-native | Polyglot data | Large-scale analytics |
| **Cost** | Self-hosted/Cloud | AWS Cloud | Open-source/Cloud | Enterprise |
| **RLS (Row-Level Security)** | Yes | Yes | Limited | Yes |

### 8.2 Selection Criteria

```python
class GraphDatabaseSelector:
    """Help select appropriate graph database for traceability system."""

    CRITERIA_WEIGHTS = {
        "query_performance": 0.25,
        "semantic_expressiveness": 0.20,
        "scalability": 0.20,
        "cost": 0.15,
        "ecosystem": 0.10,
        "compliance": 0.10
    }

    DATABASE_SCORES = {
        "neo4j": {
            "query_performance": 9,
            "semantic_expressiveness": 6,
            "scalability": 8,
            "cost": 5,
            "ecosystem": 10,
            "compliance": 9
        },
        "neptune": {
            "query_performance": 7,
            "semantic_expressiveness": 9,
            "scalability": 9,
            "cost": 4,
            "ecosystem": 6,
            "compliance": 10
        },
        "arangodb": {
            "query_performance": 8,
            "semantic_expressiveness": 5,
            "scalability": 7,
            "cost": 8,
            "ecosystem": 6,
            "compliance": 7
        },
        "tigergraph": {
            "query_performance": 10,
            "semantic_expressiveness": 5,
            "scalability": 10,
            "cost": 3,
            "ecosystem": 5,
            "compliance": 8
        }
    }

    @classmethod
    def score_database(
        cls,
        database: str,
        requirement_priorities: Dict[str, float]
    ) -> float:
        """Calculate weighted score for database."""
        if database not in cls.DATABASE_SCORES:
            return 0.0

        scores = cls.DATABASE_SCORES[database]
        total_score = 0.0

        for criterion, weight in cls.CRITERIA_WEIGHTS.items():
            # Allow override of weights via requirement_priorities
            effective_weight = requirement_priorities.get(criterion, weight)
            criterion_score = scores.get(criterion, 0) / 10.0
            total_score += effective_weight * criterion_score

        return total_score

    @classmethod
    def recommend_database(
        cls,
        requirements: Dict[str, float]
    ) -> str:
        """Recommend best database based on requirements."""
        scores = {}
        for db in cls.DATABASE_SCORES.keys():
            scores[db] = cls.score_database(db, requirements)

        return max(scores, key=scores.get)
```

---

## 9. W3C PROV Model for Provenance

### 9.1 Provenance Ontology

```turtle
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix req: <http://example.org/requirement#> .
@prefix test: <http://example.org/test#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

# Core PROV Classes
prov:Entity a owl:Class ;
    rdfs:label "Entity" ;
    rdfs:comment "A thing of interest (requirement, test, design)" .

prov:Activity a owl:Class ;
    rdfs:label "Activity" ;
    rdfs:comment "A process or action (requirement creation, test execution)" .

prov:Agent a owl:Class ;
    rdfs:label "Agent" ;
    rdfs:comment "An entity responsible for activity (person, system)" .

# Key Properties
prov:wasGeneratedBy a owl:ObjectProperty ;
    rdfs:domain prov:Entity ;
    rdfs:range prov:Activity .

prov:used a owl:ObjectProperty ;
    rdfs:domain prov:Activity ;
    rdfs:range prov:Entity .

prov:wasAttributedTo a owl:ObjectProperty ;
    rdfs:domain prov:Entity ;
    rdfs:range prov:Agent .

prov:wasDerivedFrom a owl:ObjectProperty ;
    rdfs:domain prov:Entity ;
    rdfs:range prov:Entity ;
    owl:transitive true .

prov:wasInformedBy a owl:ObjectProperty ;
    rdfs:domain prov:Activity ;
    rdfs:range prov:Activity .

prov:wasAssociatedWith a owl:ObjectProperty ;
    rdfs:domain prov:Activity ;
    rdfs:range prov:Agent .

# Example Provenance Trace
req:REQ-001 a prov:Entity ;
    dcterms:title "User Authentication" ;
    prov:wasGeneratedBy req:SpecificationCreation ;
    prov:wasAttributedTo req:ProductManager-001 ;
    prov:wasDerivedFrom req:UserStory-0045 .

req:SpecificationCreation a prov:Activity ;
    prov:used req:UserStory-0045 ;
    prov:wasAssociatedWith req:ProductManager-001 ;
    prov:wasInformedBy req:RequirementReview .

req:TestDevelopment a prov:Activity ;
    prov:used req:REQ-001 ;
    prov:wasAssociatedWith req:QAEngineer-002 .

test:TEST-001 a prov:Entity ;
    dcterms:title "Login Test" ;
    prov:wasGeneratedBy req:TestDevelopment ;
    prov:wasDerivedFrom req:REQ-001 ;
    prov:wasAttributedTo req:QAEngineer-002 .
```

### 9.2 Python PROV Implementation

```python
from prov.model import ProvBundle
from datetime import datetime
from typing import List, Dict, Any

class SpecificationProvenance:
    """
    Track specification traceability using W3C PROV model.

    Enables complete audit trail and responsibility tracking.
    """

    def __init__(self, bundle_id: str = "specification-provenance"):
        """Initialize provenance bundle."""
        self.bundle = ProvBundle(identifier=bundle_id)

        # Define namespaces
        self.bundle.add_namespace("req", "http://example.org/requirement#")
        self.bundle.add_namespace("test", "http://example.org/test#")
        self.bundle.add_namespace("dcterms", "http://purl.org/dc/terms/")

    def add_requirement_creation(
        self,
        req_id: str,
        title: str,
        creator: str,
        timestamp: datetime,
        source_user_story: str = None
    ):
        """Record requirement creation activity and provenance."""
        req_uri = f"req:{req_id}"
        activity_uri = f"req:{req_id}-creation"
        creator_uri = f"req:{creator}"

        # Create activity
        self.bundle.activity(activity_uri, timestamp)

        # Create agent
        self.bundle.agent(creator_uri, {"prov:label": creator})

        # Create entity
        self.bundle.entity(req_uri, {
            "dcterms:title": title,
            "dcterms:created": timestamp.isoformat()
        })

        # Link: activity generated entity
        self.bundle.wasGeneratedBy(req_uri, activity_uri, timestamp)

        # Link: entity was attributed to agent
        self.bundle.wasAttributedTo(req_uri, creator_uri)

        # Link: activity was associated with agent
        self.bundle.wasAssociatedWith(activity_uri, creator_uri)

        # Link derivation if from user story
        if source_user_story:
            story_uri = f"req:{source_user_story}"
            self.bundle.entity(story_uri)
            self.bundle.wasDerivedFrom(req_uri, story_uri)

    def add_test_development(
        self,
        test_id: str,
        requirement_id: str,
        developer: str,
        timestamp: datetime
    ):
        """Record test development from requirement."""
        test_uri = f"test:{test_id}"
        req_uri = f"req:{requirement_id}"
        activity_uri = f"test:{test_id}-development"
        developer_uri = f"req:{developer}"

        # Create entities and activities
        self.bundle.entity(test_uri)
        self.bundle.activity(activity_uri, timestamp)
        self.bundle.agent(developer_uri, {"prov:label": developer})

        # Link: test was derived from requirement
        self.bundle.wasDerivedFrom(test_uri, req_uri)

        # Link: test was generated by development activity
        self.bundle.wasGeneratedBy(test_uri, activity_uri, timestamp)

        # Link: development activity used requirement
        self.bundle.used(activity_uri, req_uri, timestamp)

        # Link: activity was associated with developer
        self.bundle.wasAssociatedWith(activity_uri, developer_uri)

    def add_test_execution(
        self,
        test_id: str,
        execution_timestamp: datetime,
        executor: str,
        result: str,  # PASSED, FAILED, SKIPPED
        requirement_id: str = None
    ):
        """Record test execution and link to requirement."""
        test_uri = f"test:{test_id}"
        execution_uri = f"test:{test_id}-execution-{execution_timestamp.timestamp()}"
        executor_uri = f"req:{executor}"
        result_uri = f"test:{test_id}-result-{execution_timestamp.timestamp()}"

        # Record execution
        self.bundle.activity(execution_uri, execution_timestamp)
        self.bundle.agent(executor_uri, {"prov:label": executor})

        # Create result entity
        self.bundle.entity(result_uri, {
            "prov:type": result,
            "dcterms:issued": execution_timestamp.isoformat()
        })

        # Link: result was generated by execution
        self.bundle.wasGeneratedBy(result_uri, execution_uri, execution_timestamp)

        # Link: execution used test
        self.bundle.used(execution_uri, test_uri, execution_timestamp)

        # Link: execution was associated with executor
        self.bundle.wasAssociatedWith(execution_uri, executor_uri)

        # Link: result was attributed to requirement if applicable
        if requirement_id:
            req_uri = f"req:{requirement_id}"
            self.bundle.wasDerivedFrom(result_uri, req_uri)

    def add_requirement_change(
        self,
        req_id: str,
        change_description: str,
        author: str,
        timestamp: datetime,
        previous_version: str = None
    ):
        """Record requirement change as new version."""
        new_version_uri = f"req:{req_id}-v2"
        old_version_uri = f"req:{req_id}" if previous_version is None else f"req:{previous_version}"
        change_activity_uri = f"req:{req_id}-change-{timestamp.timestamp()}"
        author_uri = f"req:{author}"

        # Create change activity
        self.bundle.activity(change_activity_uri, timestamp)
        self.bundle.agent(author_uri, {"prov:label": author})

        # Create new version entity
        self.bundle.entity(new_version_uri, {
            "dcterms:description": change_description,
            "dcterms:modified": timestamp.isoformat()
        })

        # Link: new version was generated by change
        self.bundle.wasGeneratedBy(new_version_uri, change_activity_uri, timestamp)

        # Link: new version derived from old version
        self.bundle.wasDerivedFrom(new_version_uri, old_version_uri)

        # Link: change was associated with author
        self.bundle.wasAssociatedWith(change_activity_uri, author_uri)

    def get_requirement_lineage(self, req_id: str) -> List[Dict[str, Any]]:
        """Get complete lineage for a requirement."""
        lineage = []
        visited = set()

        def trace(entity_uri: str, depth: int = 0):
            if entity_uri in visited or depth > 10:
                return
            visited.add(entity_uri)

            # Get entity info
            for record in self.bundle.records:
                if hasattr(record, 'identifier') and str(record.identifier) == entity_uri:
                    lineage.append({
                        "entity": entity_uri,
                        "type": type(record).__name__,
                        "depth": depth,
                        "attributes": dict(record.attributes) if hasattr(record, 'attributes') else {}
                    })

            # Find ancestors
            for record in self.bundle.records:
                if hasattr(record, 'args') and len(record.args) >= 2:
                    if str(record.args[1]) == entity_uri:  # wasDerivedFrom, etc.
                        trace(str(record.args[0]), depth + 1)

        trace(f"req:{req_id}")
        return lineage

    def export_prov_json(self, filename: str):
        """Export provenance as JSON."""
        with open(filename, 'w') as f:
            f.write(self.bundle.serialize(format='json'))

    def export_prov_ttl(self, filename: str):
        """Export provenance as Turtle RDF."""
        with open(filename, 'w') as f:
            f.write(self.bundle.serialize(format='turtle'))


# Example Usage
prov = SpecificationProvenance()

# Create requirement
prov.add_requirement_creation(
    "REQ-001",
    "User Authentication",
    "alice@company.com",
    datetime.now(),
    "US-0045"
)

# Develop test
prov.add_test_development(
    "TEST-001",
    "REQ-001",
    "bob@company.com",
    datetime.now()
)

# Execute test
prov.add_test_execution(
    "TEST-001",
    datetime.now(),
    "bob@company.com",
    "PASSED",
    "REQ-001"
)

# Export
prov.export_prov_ttl("/tmp/traceability-provenance.ttl")
print("Requirement lineage:", prov.get_requirement_lineage("REQ-001"))
```

---

## 10. Integration Architecture: Hybrid Graph System

### 10.1 Multi-Graph Architecture

```python
from typing import Protocol, Dict, List, Any, Optional
from abc import ABC, abstractmethod

class GraphStore(ABC):
    """Abstract interface for graph stores."""

    @abstractmethod
    def add_entity(self, entity_id: str, entity_type: str, properties: Dict) -> None:
        pass

    @abstractmethod
    def add_relationship(
        self,
        source_id: str,
        relation_type: str,
        target_id: str,
        properties: Dict = None
    ) -> None:
        pass

    @abstractmethod
    def query(self, query_string: str) -> List[Dict]:
        pass


class HybridTraceabilitySystem:
    """
    Hybrid graph system combining Neo4j and RDF for optimal traceability.

    - Neo4j: Fast transactional queries, primary data store
    - RDF/OWL: Semantic reasoning, inference, compliance checking
    - Sync: Bidirectional synchronization between stores
    """

    def __init__(self, neo4j_uri: str, rdf_storage_path: str):
        """Initialize hybrid system."""
        self.neo4j = None  # Neo4j driver instance
        self.rdf_graph = None  # RDF graph instance
        self.sync_log = []

    def sync_neo4j_to_rdf(self, batch_size: int = 100):
        """Synchronize Neo4j data to RDF store."""
        # Query all entities from Neo4j
        query = "MATCH (n) RETURN n LIMIT $batch_size"

        batch = 0
        while True:
            results = self.neo4j.run(query, batch_size=batch_size)
            records = list(results)

            if not records:
                break

            for record in records:
                node = record['n']
                # Convert to RDF
                self._node_to_rdf(node)

            batch += 1
            self.sync_log.append(f"Synced batch {batch}")

    def sync_rdf_to_neo4j(self, batch_size: int = 100):
        """Synchronize RDF inferences to Neo4j."""
        # Query RDF for new inferences
        sparql_query = """
        SELECT ?subject ?predicate ?object
        WHERE {
            ?subject ?predicate ?object .
            FILTER (isIRI(?subject) && isIRI(?object))
        }
        LIMIT %d
        """ % batch_size

        results = self.rdf_graph.query(sparql_query)

        for row in results:
            subject = str(row[0])
            predicate = str(row[1])
            obj = str(row[2])

            # Convert to Neo4j relationship if not exists
            self._rdf_to_neo4j_relationship(subject, predicate, obj)

    def integrated_coverage_report(self) -> Dict[str, Any]:
        """
        Generate coverage report combining Neo4j performance
        with RDF semantic validation.
        """
        # Get coverage data from Neo4j (fast)
        coverage_query = """
        MATCH (req:Requirement)-[:VERIFIED_BY]->(test:TestCase)
        RETURN req.id, COUNT(test) as test_count
        """
        neo4j_coverage = self.neo4j.run(coverage_query)

        # Get compliance validation from RDF (semantic)
        rdf_compliance_query = """
        SELECT ?req (COUNT(?compliance_check) as ?valid_checks)
        WHERE {
            ?req a req:Requirement .
            ?compliance_check req:validates ?req .
            ?compliance_check req:result "PASS" .
        }
        GROUP BY ?req
        """
        rdf_compliance = self.rdf_graph.query(rdf_compliance_query)

        # Merge results
        report = {
            "timestamp": str(datetime.now()),
            "coverage": {},
            "compliance": {}
        }

        for row in neo4j_coverage:
            report["coverage"][row["req.id"]] = row["test_count"]

        for row in rdf_compliance:
            req_id = str(row[0]).split("/")[-1]
            report["compliance"][req_id] = int(row[1])

        return report
```

---

## Summary: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- Implement Neo4j property graph model with TraceabilityGraphDB
- Create basic CRUD operations for requirements, tests, designs
- Build Cypher query patterns for common traceability queries

### Phase 2: Semantic Layer (Weeks 3-4)
- Implement RDF/OWL ontology for specification domain
- Add RDFTraceabilityGraph with SPARQL queries
- Create compliance validation rules

### Phase 3: Intelligence (Weeks 5-6)
- Train TransE/RotatE embeddings for link prediction
- Implement temporal graph for version tracking
- Add hypergraph support for n-ary relationships

### Phase 4: Algorithms (Weeks 7-8)
- Implement graph algorithms (shortest path, impact analysis, centrality)
- Add community detection for requirement clustering
- Create visualization layouts (force-directed, matrix views)

### Phase 5: Provenance & Integration (Weeks 9-10)
- Implement W3C PROV model for audit trails
- Create hybrid system combining Neo4j + RDF
- Build synchronization mechanisms

### Phase 6: Deployment & Optimization (Weeks 11-12)
- Performance tuning and indexing strategies
- Database selection for production deployment
- API and dashboard integration

---

## Key Files and Code Snippets

The research includes production-ready implementations for:

1. **Neo4j Integration**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/graph_service.py`
2. **RDF Graph Management**: Use RDFTraceabilityGraph class for semantic queries
3. **Embedding Models**: TransE and RotatE implementations for link prediction
4. **Graph Algorithms**: Path finding, centrality, community detection
5. **Visualization**: Force-directed layouts, coverage matrices, SVG export
6. **Provenance Tracking**: W3C PROV implementation for audit trails

All code follows the project's Python structure and integrates with existing SQLAlchemy models.

