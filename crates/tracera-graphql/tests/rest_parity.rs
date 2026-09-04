//! Top-level integration tests for the GraphQL gateway.
//!
//! These exercise the schema end-to-end against an in-memory store so we
//! can verify REST parity without spinning up Postgres / SQLite.

use std::collections::HashMap;
use std::sync::Arc;

use async_graphql::{EmptySubscription, Schema};
use chrono::Utc;
use serde_json::{json, Value as JsonValue};
use tokio::sync::Mutex;
use uuid::Uuid;

use tracera_graphql::resolvers::edge::{
    EdgeCreateInput, EdgeKind, EdgeListFilter, GraphEdge, NodeRef, PersistedTraceLink, TraceDirection,
};
use tracera_graphql::resolvers::node::{GraphNode, NodeKind, NodeListFilter};
use tracera_graphql::{
    build_schema, GraphContext, GraphEventBus, GraphStore, MutationRoot, QueryRoot,
};

// ---------------------------------------------------------------------------
// Shared in-memory store
// ---------------------------------------------------------------------------

#[derive(Default)]
pub struct MemStore {
    pub nodes: Mutex<Vec<GraphNode>>,
    pub edges: Mutex<Vec<GraphEdge>>,
    pub trace_links: Mutex<Vec<PersistedTraceLink>>,
}

#[async_trait::async_trait]
impl GraphStore for MemStore {
    async fn create_node(
        &self,
        node_type: NodeKind,
        label: String,
        metadata: JsonValue,
    ) -> Result<String, String> {
        let now = Utc::now();
        let id = format!("n-{}", Uuid::new_v4());
        self.nodes.lock().await.push(GraphNode {
            id: id.clone(),
            node_type,
            label,
            metadata,
            created_at: now,
            updated_at: now,
        });
        Ok(id)
    }

    async fn get_node(&self, id: &str) -> Result<Option<GraphNode>, String> {
        Ok(self.nodes.lock().await.iter().find(|n| n.id == id).cloned())
    }

    async fn list_nodes(&self, filter: &NodeListFilter) -> Result<Vec<GraphNode>, String> {
        let limit = filter.validated_limit() as usize;
        let guard = self.nodes.lock().await;
        let mut out: Vec<GraphNode> = guard
            .iter()
            .filter(|n| filter.node_type.map(|k| k == n.node_type).unwrap_or(true))
            .cloned()
            .collect();
        out.truncate(limit);
        Ok(out)
    }

    async fn create_edge(&self, input: &EdgeCreateInput) -> Result<String, String> {
        let now = Utc::now();
        let id = format!("e-{}", Uuid::new_v4());
        self.edges.lock().await.push(GraphEdge {
            id: id.clone(),
            edge_type: input.edge_type,
            source_id: input.source_id.clone(),
            target_id: input.target_id.clone(),
            confidence: input.confidence.unwrap_or(1.0),
            source: input.source.clone().unwrap_or_else(|| "manual".into()),
            metadata: input.metadata.clone(),
            created_at: now,
            updated_at: now,
        });
        Ok(id)
    }

    async fn get_edge(&self, id: &str) -> Result<Option<GraphEdge>, String> {
        Ok(self.edges.lock().await.iter().find(|e| e.id == id).cloned())
    }

    async fn list_edges(&self, filter: &EdgeListFilter) -> Result<Vec<GraphEdge>, String> {
        let limit = filter.validated_limit() as usize;
        let guard = self.edges.lock().await;
        let mut out: Vec<GraphEdge> = guard
            .iter()
            .filter(|e| filter.edge_type.map(|k| k == e.edge_type).unwrap_or(true))
            .filter(|e| {
                filter
                    .source_id
                    .as_ref()
                    .map(|s| &e.source_id == s)
                    .unwrap_or(true)
            })
            .cloned()
            .collect();
        out.truncate(limit);
        Ok(out)
    }

    async fn list_neighbor_node_refs(
        &self,
        id: &str,
        direction: TraceDirection,
    ) -> Result<Vec<NodeRef>, String> {
        let nodes = self.nodes.lock().await;
        let by_id: HashMap<String, NodeRef> = nodes
            .iter()
            .map(|n| {
                (
                    n.id.clone(),
                    NodeRef {
                        id: n.id.clone(),
                        node_type: n.node_type,
                        label: n.label.clone(),
                    },
                )
            })
            .collect();
        drop(nodes);
        let edges = self.edges.lock().await;
        let mut out = Vec::new();
        for edge in edges.iter() {
            match direction {
                TraceDirection::Forward if edge.source_id == id => {
                    if let Some(r) = by_id.get(&edge.target_id) {
                        out.push(r.clone());
                    }
                }
                TraceDirection::Reverse if edge.target_id == id => {
                    if let Some(r) = by_id.get(&edge.source_id) {
                        out.push(r.clone());
                    }
                }
                _ => {}
            }
        }
        Ok(out)
    }

    async fn create_trace_link(
        &self,
        id: String,
        source_id: String,
        target_id: String,
        relationship: String,
    ) -> Result<PersistedTraceLink, String> {
        let now = Utc::now();
        let link = PersistedTraceLink {
            id: id.clone(),
            source_id: source_id.clone(),
            target_id: target_id.clone(),
            relationship: relationship.clone(),
            confidence: 1.0,
            source: "api".into(),
            direction: "forward".into(),
            created_at: now,
            updated_at: now,
        };
        self.trace_links.lock().await.push(link.clone());
        Ok(link)
    }

    async fn list_trace_links_for_artifact(
        &self,
        artifact_id: String,
    ) -> Result<Vec<PersistedTraceLink>, String> {
        let guard = self.trace_links.lock().await;
        let mut out: Vec<PersistedTraceLink> = guard
            .iter()
            .filter(|l| l.source_id == artifact_id || l.target_id == artifact_id)
            .cloned()
            .map(|mut l| {
                l.direction = if l.source_id == artifact_id {
                    "forward".into()
                } else {
                    "reverse".into()
                };
                l
            })
            .collect();
        out.sort_by(|a, b| a.id.cmp(&b.id));
        Ok(out)
    }
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

fn ctx() -> (GraphContext, Arc<MemStore>) {
    let store = Arc::new(MemStore::default());
    let ctx = GraphContext::new(store.clone(), GraphEventBus::default());
    (ctx, store)
}

// ---------------------------------------------------------------------------
// SDL — make sure the public REST surface is exposed
// ---------------------------------------------------------------------------

#[test]
fn sdl_includes_every_rest_endpoint() {
    let (ctx, _) = ctx();
    let schema = build_schema(ctx);
    let sdl = schema.sdl();

    // Every GraphQL field name that mirrors a REST endpoint must be present.
    let must_have = [
        "healthz",
        "apiVersion",
        "node(",
        "nodes(",
        "edge(",
        "edges(",
        "incidentLinks(",
        "graphNeighbors(",
        "createNode(",
        "createEdge(",
        "createTraceLink(",
        "coverageMatrix(",
        "impact(",
        "blastRadius(",
        "traceNeighbors(",
        "specCheck(",
        "graphEvents(",
        "emitDomainEvent(",
    ];

    for needle in must_have {
        assert!(
            sdl.contains(needle),
            "SDL missing REST-mirrored field `{needle}`:\n{sdl}"
        );
    }

    // Both node-kind and edge-kind enums must be declared.
    assert!(sdl.contains("enum NodeKind"));
    assert!(sdl.contains("enum EdgeKind"));
    assert!(sdl.contains("enum TraceDirection"));

    // The subscription must mention the event types.
    assert!(sdl.contains("NodeCreated"));
    assert!(sdl.contains("EdgeCreated"));
    assert!(sdl.contains("DomainEvent"));
}

#[test]
fn schema_compiles_with_empty_subscription() {
    // Useful for federation / introspection tests.
    let _schema: Schema<QueryRoot, MutationRoot, EmptySubscription> =
        Schema::build(QueryRoot, MutationRoot, EmptySubscription).finish();
}

// ---------------------------------------------------------------------------
// REST parity: same inputs produce same JSON for stateless endpoints
// ---------------------------------------------------------------------------

#[tokio::test]
async fn rest_parity_coverage_matrix() {
    // Same body the REST `POST /api/v1/coverage-matrix` would receive.
    let (ctx, _) = ctx();
    let schema = build_schema(ctx);
    let q = r#"
        query {
          coverageMatrix(input: {
            links: [
              { sourceId: "S1", targetId: "T1", relationship: "implements", confidence: 1.0 }
              { sourceId: "S1", targetId: "T1", relationship: "tests",    confidence: 1.0 }
              { sourceId: "S2", targetId: "T2", relationship: "implements", confidence: 1.0 }
            ]
            staleAfterDays: 30
          }) {
            linkCount cellCount staleLinks
            cells { sourceId targetId coverage }
          }
        }
    "#;
    let res = schema.execute(q).await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);
    let v: JsonValue = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
    assert_eq!(v["coverageMatrix"]["linkCount"], 3);
    assert_eq!(v["coverageMatrix"]["cellCount"], 2);
    assert_eq!(v["coverageMatrix"]["staleLinks"], 0);
    let cells = v["coverageMatrix"]["cells"].as_array().unwrap();
    assert_eq!(cells.len(), 2);
    assert_eq!(cells[0]["sourceId"], "S1");
    assert_eq!(cells[0]["targetId"], "T1");
    assert_eq!(cells[0]["coverage"], "covered");
}

#[tokio::test]
async fn rest_parity_impact_matches_rest_handler_numbers() {
    let (ctx, _) = ctx();
    let schema = build_schema(ctx);
    let q = r#"
        query {
          impact(input: {
            links: [
              { sourceId: "a", targetId: "b", relationship: "depends_on", confidence: 1.0 }
              { sourceId: "b", targetId: "c", relationship: "depends_on", confidence: 1.0 }
              { sourceId: "a", targetId: "c", relationship: "conflicts_with", confidence: 1.0 }
            ]
            changedArtifactIds: ["a", "b"]
            maxDepth: 5
          }) {
            seeds
            totalScore
            truncated
            maxDepthSeen
            conflicts { sourceId targetId relationship }
          }
        }
    "#;
    let res = schema.execute(q).await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);
    let v: JsonValue = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
    let r = &v["impact"];
    assert_eq!(r["seeds"], json!(["a", "b"]));
    assert_eq!(r["truncated"], false);
    // 3 conflicts relationships exist but only one is "conflicts_with" → exactly 1.
    assert_eq!(r["conflicts"].as_array().unwrap().len(), 1);
    assert_eq!(r["conflicts"][0]["sourceId"], "a");
}

#[tokio::test]
async fn rest_parity_blast_radius() {
    let (ctx, _) = ctx();
    let schema = build_schema(ctx);
    let q = r#"
        query {
          blastRadius(input: {
            links: [
              { sourceId: "a", targetId: "b", relationship: "calls", confidence: 1.0 }
              { sourceId: "b", targetId: "c", relationship: "calls", confidence: 1.0 }
              { sourceId: "c", targetId: "d", relationship: "calls", confidence: 1.0 }
            ]
            changedArtifactIds: ["a"]
          }) {
            total seeds
            blastRadius { artifactId distance }
          }
        }
    "#;
    let res = schema.execute(q).await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);
    let v: JsonValue = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
    assert_eq!(v["blastRadius"]["total"], 4); // a, b, c, d
    let by_id: HashMap<String, u64> = v["blastRadius"]["blastRadius"]
        .as_array()
        .unwrap()
        .iter()
        .map(|n| {
            (
                n["artifactId"].as_str().unwrap().to_string(),
                n["distance"].as_u64().unwrap(),
            )
        })
        .collect();
    assert_eq!(by_id["a"], 0);
    assert_eq!(by_id["d"], 3);
}

#[tokio::test]
async fn create_node_and_query_round_trip() {
    let (ctx, store) = ctx();
    let schema = build_schema(ctx);

    // Mutate
    let m = r#"
        mutation {
          createNode(input: { nodeType: requirement, label: "REQ-1", metadata: {"x":1} }) {
            id label nodeType
          }
        }
    "#;
    let res = schema.execute(m).await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);
    let v: JsonValue = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
    let id = v["createNode"]["id"].as_str().unwrap().to_string();

    // Query
    let q = format!(
        r#"{{ node(id: "{id}") {{ id label nodeType }} }}"#
    );
    let res = schema.execute(&q).await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);
    let v: JsonValue = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
    assert_eq!(v["node"]["label"], "REQ-1");
    assert_eq!(v["node"]["nodeType"], "REQUIREMENT");

    // Underlying store should agree.
    assert_eq!(store.nodes.lock().await.len(), 1);
}

#[tokio::test]
async fn incident_links_returned_for_artifact() {
    let (ctx, _) = ctx();
    let schema = build_schema(ctx);

    // Seed two trace links incident to "A".
    schema
        .execute(
            r#"mutation {
                createTraceLink(input: { sourceId: "A", targetId: "B", relationship: "implements" }) { id }
            }"#,
        )
        .await;
    schema
        .execute(
            r#"mutation {
                createTraceLink(input: { sourceId: "C", targetId: "A", relationship: "covers" }) { id }
            }"#,
        )
        .await;

    let res = schema
        .execute(r#"{ incidentLinks(artifactId: "A") { id sourceId targetId direction relationship } }"#)
        .await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);
    let v: JsonValue = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
    let links = v["incidentLinks"].as_array().unwrap();
    assert_eq!(links.len(), 2);
    let directions: Vec<&str> = links
        .iter()
        .map(|l| l["direction"].as_str().unwrap())
        .collect();
    assert!(directions.contains(&"forward"));
    assert!(directions.contains(&"reverse"));
}

#[tokio::test]
async fn graph_events_subscription_publishes_on_mutation() {
    let store = Arc::new(MemStore::default());
    let bus = GraphEventBus::default();
    let mut rx = bus.subscribe();
    let ctx = GraphContext::new(store, bus);
    let schema = build_schema(ctx);
    let res = schema
        .execute(
            r#"mutation {
                createNode(input: { nodeType: requirement, label: "live" }) { id }
            }"#,
        )
        .await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);

    let evt = tokio::time::timeout(std::time::Duration::from_secs(1), rx.recv())
        .await
        .expect("must not time out")
        .expect("event must be published");
    use tracera_graphql::events::GraphEvent;
    match evt {
        GraphEvent::NodeCreated(n) => {
            assert_eq!(n.label, "live");
            assert_eq!(n.node_type, NodeKind::Requirement);
        }
        other => panic!("expected NodeCreated, got {other:?}"),
    }
}

#[tokio::test]
async fn spec_check_pass_and_fail_paths() {
    let (ctx, _) = ctx();
    let schema = build_schema(ctx);

    let fail_q = r#"
        query {
          specCheck(input: {
            specs: [
              { specId: "S1", acceptanceCriteria: [], evidenceLinks: ["e"], status: "draft" }
            ]
            traces: []
          }) {
            status specCount
            violations { code message }
          }
        }
    "#;
    let res = schema.execute(fail_q).await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);
    let v: JsonValue = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
    assert_eq!(v["specCheck"]["status"], "fail");
    let codes: Vec<&str> = v["specCheck"]["violations"]
        .as_array()
        .unwrap()
        .iter()
        .map(|x| x["code"].as_str().unwrap())
        .collect();
    assert!(codes.contains(&"not_approved"));
    assert!(codes.contains(&"missing_acceptance"));

    let pass_q = r#"
        query {
          specCheck(input: {
            specs: [
              { specId: "S1", acceptanceCriteria: ["a"], evidenceLinks: ["e"], status: "approved" }
            ]
            traces: [
              { specId: "S1", targetId: "src", kind: "implementation" }
              { specId: "S1", targetId: "tst", kind: "test" }
            ]
          }) {
            status violations { code }
          }
        }
    "#;
    let res = schema.execute(pass_q).await;
    assert!(res.errors.is_empty(), "{:#?}", res.errors);
    let v: JsonValue = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
    assert_eq!(v["specCheck"]["status"], "pass");
    assert_eq!(v["specCheck"]["violations"].as_array().unwrap().len(), 0);
}
