//! GraphQL schema: Query, Mutation, and Subscription roots.
//!
//! The Query / Mutation roots are split into two strategy layers:
//!
//! 1. **Pure / stateless** — coverage matrix, impact, blast radius, trace
//!    neighbours, and spec-check. These are wired directly to the helpers in
//!    `resolvers::subgraph` because they take caller-supplied links and
//!    return derived data; they never touch storage.
//!
//! 2. **Stateful** — anything that touches a node, edge, or trace-link row.
//!    These are wired through the [`GraphContext`] so the binary can plug
//!    in either an in-memory mock store or the production
//!    `tracera_server::Store` trait without changing this file.
//!
//! The [`GraphEventBus`] is shared via [`GraphContext`] so the
//! `graph_events` subscription works out of the box.

use async_graphql::{Context, Object, Schema, Subscription, ID};
use chrono::Utc;
use futures_util::stream::Stream;
use serde_json::Value as JsonValue;
use std::sync::Arc;
use tokio::sync::broadcast;
use tokio_stream::{wrappers::BroadcastStream, StreamExt};
use tracing::warn;
use uuid::Uuid;

use crate::events::{
    DomainEvent, EdgeCreatedEvent, EdgeUpdatedEvent, GraphEvent, GraphEventFilter,
    NodeCreatedEvent, NodeUpdatedEvent,
};
use crate::resolvers::edge::{
    EdgeCreateInput, EdgeListFilter, GraphEdge, PersistedTraceLink, TraceDirection,
    TraceLinkCreateInput, TraceNeighbors,
};
use crate::resolvers::node::{GraphNode, NodeCreateInput, NodeKind, NodeListFilter, NodeRef};
use crate::resolvers::subgraph::{
    build_blast_radius, build_coverage_matrix, build_impact, build_neighbors, build_spec_check,
    BlastRadiusInput, BlastRadiusReport, CoverageMatrix, CoverageMatrixInput, GovernanceReport,
    ImpactInput, ImpactReport, MAX_COVERAGE_LINKS, SpecCheckInput, TraceNeighborsInput,
};

// ===========================================================================
// Storage abstraction
// ===========================================================================

/// Minimal storage contract the schema needs from a backing store.
///
/// Both the production `tracera-server` `Store` trait and the in-memory
/// test store implement this. The gateway stays decoupled from the server
/// crate so it can be built / deployed independently.
#[async_graphql::async_trait]
pub trait GraphStore: Send + Sync + 'static {
    // --- SWEE node CRUD ---
    async fn create_node(
        &self,
        node_type: NodeKind,
        label: String,
        metadata: JsonValue,
    ) -> Result<String, String>;

    async fn get_node(&self, id: &str) -> Result<Option<GraphNode>, String>;

    async fn list_nodes(&self, filter: &NodeListFilter) -> Result<Vec<GraphNode>, String>;

    // --- SWEE edge CRUD ---
    async fn create_edge(&self, input: &EdgeCreateInput) -> Result<String, String>;

    async fn get_edge(&self, id: &str) -> Result<Option<GraphEdge>, String>;

    async fn list_edges(&self, filter: &EdgeListFilter) -> Result<Vec<GraphEdge>, String>;

    async fn list_neighbor_node_refs(
        &self,
        id: &str,
        direction: TraceDirection,
    ) -> Result<Vec<NodeRef>, String>;

    // --- Legacy trace-link ---
    async fn create_trace_link(
        &self,
        id: String,
        source_id: String,
        target_id: String,
        relationship: String,
    ) -> Result<PersistedTraceLink, String>;

    async fn list_trace_links_for_artifact(
        &self,
        artifact_id: String,
    ) -> Result<Vec<PersistedTraceLink>, String>;
}

/// Shared application context — passed to every resolver via [`Context`].
#[derive(Clone)]
pub struct GraphContext {
    pub store: Arc<dyn GraphStore>,
    pub bus: GraphEventBus,
}

impl GraphContext {
    pub fn new(store: Arc<dyn GraphStore>, bus: GraphEventBus) -> Self {
        Self { store, bus }
    }
}

// ===========================================================================
// Query root
// ===========================================================================

pub struct QueryRoot;

#[Object]
impl QueryRoot {
    /// API version — mirrors `GET /healthz`.
    async fn api_version(&self) -> &'static str {
        env!("CARGO_PKG_VERSION")
    }

    /// Service health check — mirrors `GET /healthz`.
    async fn healthz(&self) -> &'static str {
        "ok"
    }

    // --- Node queries ---

    /// Fetch a single SWEE node by id (`GET /api/v1/graph/nodes/{id}`).
    async fn node(&self, ctx: &Context<'_>, id: ID) -> Result<Option<GraphNode>, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        app.store.get_node(&id.to_string()).await
    }

    /// List SWEE nodes (`GET /api/v1/graph/nodes`).
    async fn nodes(
        &self,
        ctx: &Context<'_>,
        #[graphql(default)] filter: NodeListFilter,
    ) -> Result<Vec<GraphNode>, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        app.store.list_nodes(&filter).await
    }

    // --- Edge queries ---

    /// Fetch a single SWEE edge by id.
    async fn edge(&self, ctx: &Context<'_>, id: ID) -> Result<Option<GraphEdge>, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        app.store.get_edge(&id.to_string()).await
    }

    /// List SWEE edges (`GET /api/v1/graph/edges`).
    async fn edges(
        &self,
        ctx: &Context<'_>,
        #[graphql(default)] filter: EdgeListFilter,
    ) -> Result<Vec<GraphEdge>, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        app.store.list_edges(&filter).await
    }

    // --- Persisted trace-link queries ---

    /// `GET /api/v1/trace/{artifact_id}/links`.
    async fn incident_links(
        &self,
        ctx: &Context<'_>,
        artifact_id: String,
    ) -> Result<Vec<PersistedTraceLink>, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        app.store.list_trace_links_for_artifact(artifact_id).await
    }

    // --- Subgraph queries (stateless, pure functions of caller input) ---

    /// `POST /api/v1/coverage-matrix`.
    async fn coverage_matrix(
        &self,
        input: CoverageMatrixInput,
    ) -> Result<CoverageMatrix, String> {
        if input.links.len() > MAX_COVERAGE_LINKS {
            return Err(format!(
                "coverage matrix exceeds link limit ({MAX_COVERAGE_LINKS}); use a paged export"
            ));
        }
        Ok(build_coverage_matrix(&input))
    }

    /// `POST /api/v1/impact`.
    async fn impact(&self, input: ImpactInput) -> Result<ImpactReport, String> {
        Ok(build_impact(&input))
    }

    /// `POST /api/v1/blast-radius`.
    async fn blast_radius(&self, input: BlastRadiusInput) -> Result<BlastRadiusReport, String> {
        Ok(build_blast_radius(&input))
    }

    /// `POST /api/v1/trace/{forward|reverse}/{id}`.
    async fn trace_neighbors(
        &self,
        artifact_id: String,
        direction: TraceDirection,
        input: TraceNeighborsInput,
    ) -> Result<TraceNeighbors, String> {
        Ok(build_neighbors(&artifact_id, direction, &input))
    }

    /// `POST /api/v1/governance/spec-check`.
    async fn spec_check(&self, input: SpecCheckInput) -> Result<GovernanceReport, String> {
        Ok(build_spec_check(&input))
    }

    /// Live subscriber count — handy for ops dashboards.
    async fn graph_event_subscribers(&self, ctx: &Context<'_>) -> usize {
        ctx.data::<GraphContext>()
            .map(|c| c.bus.subscriber_count())
            .unwrap_or(0)
    }

    /// Direct node-neighbour read for a single artifact.
    async fn graph_neighbors(
        &self,
        ctx: &Context<'_>,
        id: ID,
        direction: TraceDirection,
    ) -> Result<Vec<NodeRef>, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        app.store.list_neighbor_node_refs(&id.to_string(), direction).await
    }
}

// ===========================================================================
// Mutation root
// ===========================================================================

pub struct MutationRoot;

#[Object]
impl MutationRoot {
    /// Create a SWEE node (`POST /api/v1/graph/nodes`).
    async fn create_node(
        &self,
        ctx: &Context<'_>,
        input: NodeCreateInput,
    ) -> Result<GraphNode, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        let id = app
            .store
            .create_node(input.node_type, input.label.clone(), input.metadata.clone())
            .await?;
        let now = Utc::now();
        let node = GraphNode {
            id,
            node_type: input.node_type,
            label: input.label,
            metadata: input.metadata,
            created_at: now,
            updated_at: now,
        };
        app.bus.publish_node_created(node.node_type, node.label.clone(), node.metadata.clone());
        Ok(node)
    }

    /// Create a SWEE edge (`POST /api/v1/graph/edges`).
    async fn create_edge(
        &self,
        ctx: &Context<'_>,
        input: EdgeCreateInput,
    ) -> Result<GraphEdge, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        let id = app.store.create_edge(&input).await?;
        let now = Utc::now();
        let edge = GraphEdge {
            id: id.clone(),
            edge_type: input.edge_type,
            source_id: input.source_id.clone(),
            target_id: input.target_id.clone(),
            confidence: input.confidence.unwrap_or(1.0),
            source: input.source.clone().unwrap_or_else(|| "manual".into()),
            metadata: input.metadata.clone(),
            created_at: now,
            updated_at: now,
        };
        app.bus.publish_edge_created(
            edge.edge_type,
            edge.source_id.clone(),
            edge.target_id.clone(),
            edge.confidence,
        );
        Ok(edge)
    }

    /// Create a persisted trace-link (`POST /api/v1/trace`).
    async fn create_trace_link(
        &self,
        ctx: &Context<'_>,
        input: TraceLinkCreateInput,
    ) -> Result<PersistedTraceLink, String> {
        let app = ctx.data::<GraphContext>().map_err(|e| e.to_string())?;
        let id = format!("tl-{}", Uuid::new_v4());
        app.store
            .create_trace_link(id, input.source_id, input.target_id, input.relationship)
            .await
    }

    /// Convenience helper to publish a domain event for testing / federation.
    async fn emit_domain_event(
        &self,
        ctx: &Context<'_>,
        event_type: String,
        source: String,
        payload: JsonValue,
    ) -> bool {
        let app = match ctx.data::<GraphContext>() {
            Ok(c) => c,
            Err(e) => {
                warn!("emit_domain_event failed: {e}");
                return false;
            }
        };
        app.bus.publish_domain(event_type, source, payload, Utc::now());
        true
    }
}

// ===========================================================================
// Subscription root
// ===========================================================================

pub struct SubscriptionRoot;

#[Subscription]
impl SubscriptionRoot {
    /// Live stream of graph mutations and domain events.
    ///
    /// Subscribers receive:
    ///  - `NODE_CREATED` / `NODE_UPDATED`     (mutation-side)
    ///  - `EDGE_CREATED` / `EDGE_UPDATED`     (mutation-side)
    ///  - `DOMAIN_EVENT`                      (ingest pipeline, fed via
    ///                                         `MutationRoot::emit_domain_event`
    ///                                         or directly by the binary).
    ///
    /// Optional filter narrows the stream to a single node kind, edge kind,
    /// or domain event type.
    async fn graph_events(
        &self,
        ctx: &Context<'_>,
        #[graphql(default)] filter: GraphEventFilter,
    ) -> impl Stream<Item = GraphEvent> + Send + 'static {
        let app = match ctx.data::<GraphContext>() {
            Ok(c) => c.clone(),
            Err(e) => {
                warn!("graph_events subscription failed to acquire context: {e}");
                // Return an empty stream rather than crashing the executor.
                let (_tx, rx) = broadcast::channel::<GraphEvent>(1);
                return BroadcastStream::new(rx).filter_map(|r| r.ok()).boxed();
            }
        };

        let rx: broadcast::Receiver<GraphEvent> = app.bus.subscribe();
        BroadcastStream::new(rx)
            .filter_map(|r| r.ok())
            .filter(move |evt| filter_matches(evt, &filter))
            .boxed()
    }
}

fn filter_matches(event: &GraphEvent, filter: &GraphEventFilter) -> bool {
    if filter.node_type.is_none() && filter.edge_type.is_none() && filter.domain_event_type.is_none()
    {
        return true;
    }
    match event {
        GraphEvent::NodeCreated(NodeCreatedEvent { node_type, .. })
        | GraphEvent::NodeUpdated(NodeUpdatedEvent { node_type, .. }) => {
            filter.node_type.map(|k| k == *node_type).unwrap_or(true)
        }
        GraphEvent::EdgeCreated(EdgeCreatedEvent { edge_type, .. })
        | GraphEvent::EdgeUpdated(EdgeUpdatedEvent { edge_type, .. }) => {
            filter.edge_type.map(|k| k == *edge_type).unwrap_or(true)
        }
        GraphEvent::DomainEvent(DomainEvent { event_type, .. }) => filter
            .domain_event_type
            .as_ref()
            .map(|want| want == event_type)
            .unwrap_or(true),
    }
}

// ===========================================================================
// Schema build
// ===========================================================================

/// Concrete schema type — preferred for binary use (better error messages
/// than the boxed trait object).
pub type TraceraSchema = Schema<QueryRoot, MutationRoot, SubscriptionRoot>;

/// Build the production schema bound to a [`GraphContext`].
pub fn build_schema(ctx: GraphContext) -> TraceraSchema {
    Schema::build(QueryRoot, MutationRoot, SubscriptionRoot)
        .data(ctx)
        .finish()
}

// ===========================================================================
// Tests
// ===========================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use crate::resolvers::edge::TraceDirection;
    use async_graphql::EmptySubscription;
    use std::collections::HashMap;

    // ---- In-memory store used by tests ---------------------------------

    #[derive(Default)]
    struct MemStore {
        nodes: tokio::sync::Mutex<Vec<GraphNode>>,
        edges: tokio::sync::Mutex<Vec<GraphEdge>>,
        trace_links: tokio::sync::Mutex<Vec<PersistedTraceLink>>,
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
            let mut guard = self.nodes.lock().await;
            guard.push(GraphNode {
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
            Ok(self
                .nodes
                .lock()
                .await
                .iter()
                .find(|n| n.id == id)
                .cloned())
        }

        async fn list_nodes(&self, filter: &NodeListFilter) -> Result<Vec<GraphNode>, String> {
            let limit = filter.validated_limit() as usize;
            let guard = self.nodes.lock().await;
            let mut out: Vec<GraphNode> = guard
                .iter()
                .filter(|n| filter.node_type.map(|k| k == n.node_type).unwrap_or(true))
                .filter(|n| {
                    filter
                        .label_contains
                        .as_ref()
                        .map(|q| n.label.to_lowercase().contains(&q.to_lowercase()))
                        .unwrap_or(true)
                })
                .cloned()
                .collect();
            out.truncate(limit);
            Ok(out)
        }

        async fn create_edge(&self, input: &EdgeCreateInput) -> Result<String, String> {
            let now = Utc::now();
            let id = format!("e-{}", Uuid::new_v4());
            let edge = GraphEdge {
                id: id.clone(),
                edge_type: input.edge_type,
                source_id: input.source_id.clone(),
                target_id: input.target_id.clone(),
                confidence: input.confidence.unwrap_or(1.0),
                source: input.source.clone().unwrap_or_else(|| "manual".into()),
                metadata: input.metadata.clone(),
                created_at: now,
                updated_at: now,
            };
            self.edges.lock().await.push(edge);
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
                .filter(|e| {
                    filter
                        .target_id
                        .as_ref()
                        .map(|t| &e.target_id == t)
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
            let edges = self.edges.lock().await;
            let mut by_id: HashMap<String, NodeRef> = HashMap::new();
            let nodes = self.nodes.lock().await;
            for n in nodes.iter() {
                by_id.insert(
                    n.id.clone(),
                    NodeRef {
                        id: n.id.clone(),
                        node_type: n.node_type,
                        label: n.label.clone(),
                    },
                );
            }
            let mut out: Vec<NodeRef> = Vec::new();
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
            // Stable order to keep tests deterministic.
            out.sort_by(|a, b| a.id.cmp(&b.id));
            Ok(out)
        }
    }

    fn ctx_with(store: Arc<dyn GraphStore>, bus: GraphEventBus) -> GraphContext {
        GraphContext::new(store, bus)
    }

    #[tokio::test]
    async fn schema_builds_and_executes_a_query() {
        let store = Arc::new(MemStore::default());
        let schema = build_schema(ctx_with(store.clone(), GraphEventBus::default()));
        let res = schema
            .execute("{ healthz apiVersion graphEventSubscribers }")
            .await;
        assert!(res.errors.is_empty(), "unexpected errors: {:#?}", res.errors);
        let body = res.data.into_json().expect("must serialise");
        assert_eq!(body["healthz"], "ok");
        assert_eq!(
            body["apiVersion"],
            env!("CARGO_PKG_VERSION"),
            "version must come from CARGO_PKG_VERSION"
        );
        assert_eq!(body["graphEventSubscribers"], 0);
    }

    #[tokio::test]
    async fn coverage_matrix_query_returns_cells() {
        let store = Arc::new(MemStore::default());
        let schema = build_schema(ctx_with(store.clone(), GraphEventBus::default()));
        let q = r#"
            query {
              coverageMatrix(input: {
                links: [
                  { sourceId: "r-1", targetId: "src-a", relationship: "implements", confidence: 1.0 }
                  { sourceId: "r-1", targetId: "src-a", relationship: "tests", confidence: 1.0 }
                ]
              }) {
                linkCount cellCount cells { sourceId targetId coverage }
              }
            }
        "#;
        let res = schema.execute(q).await;
        assert!(res.errors.is_empty(), "{:#?}", res.errors);
        let v: serde_json::Value = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
        assert_eq!(v["coverageMatrix"]["linkCount"], 2);
        assert_eq!(v["coverageMatrix"]["cellCount"], 1);
        assert_eq!(v["coverageMatrix"]["cells"][0]["coverage"], "covered");
    }

    #[tokio::test]
    async fn impact_query_returns_depth_decay() {
        let store = Arc::new(MemStore::default());
        let schema = build_schema(ctx_with(store, GraphEventBus::default()));
        let q = r#"
            query {
              impact(input: {
                links: [
                  { sourceId: "a", targetId: "b", relationship: "depends_on", confidence: 1.0 }
                  { sourceId: "b", targetId: "c", relationship: "depends_on", confidence: 1.0 }
                ]
                changedArtifactIds: ["a"]
                maxDepth: 5
              }) {
                affected { artifactId depth score }
                totalScore
                truncated
                maxDepthSeen
              }
            }
        "#;
        let res = schema.execute(q).await;
        assert!(res.errors.is_empty(), "{:#?}", res.errors);
        let v: serde_json::Value = serde_json::from_str(&res.data.into_json().unwrap()).unwrap();
        let affected = v["impact"]["affected"].as_array().unwrap();
        assert_eq!(affected.len(), 3);
        let by_id: std::collections::HashMap<&str, &serde_json::Value> = affected
            .iter()
            .map(|n| (n["artifactId"].as_str().unwrap(), n))
            .collect();
        assert_eq!(by_id["a"]["depth"], 0);
        assert_eq!(by_id["b"]["depth"], 1);
        assert_eq!(by_id["c"]["depth"], 2);
        assert!(by_id["c"]["score"].as_f64().unwrap() < by_id["b"]["score"].as_f64().unwrap());
        assert_eq!(v["impact"]["truncated"], false);
    }

    #[tokio::test]
    async fn create_node_mutation_publishes_event() {
        let store = Arc::new(MemStore::default());
        let bus = GraphEventBus::default();
        let mut rx = bus.subscribe();
        let schema = build_schema(ctx_with(store.clone(), bus));
        let q = r#"
            mutation {
              createNode(input: { nodeType: requirement, label: "R-1" }) {
                id nodeType label
              }
            }
        "#;
        let res = schema.execute(q).await;
        assert!(res.errors.is_empty(), "{:#?}", res.errors);
        let evt = rx.recv().await.expect("event must be published");
        match evt {
            GraphEvent::NodeCreated(NodeCreatedEvent { node_type, label, .. }) => {
                assert_eq!(node_type, NodeKind::Requirement);
                assert_eq!(label, "R-1");
            }
            other => panic!("expected NodeCreated, got {other:?}"),
        }
    }

    #[tokio::test]
    async fn coverage_matrix_rejects_oversized_input() {
        let store = Arc::new(MemStore::default());
        let schema = build_schema(ctx_with(store, GraphEventBus::default()));
        let mut links = String::new();
        for i in 0..(MAX_COVERAGE_LINKS + 1) {
            if i > 0 {
                links.push(',');
            }
            links.push_str(&format!(
                "{{ sourceId: \"s{i}\", targetId: \"t{i}\", relationship: \"implements\", confidence: 1.0 }}"
            ));
        }
        let q = format!(
            r#"{{ coverageMatrix(input: {{ links: [{links}] }} ) {{ linkCount }} }}"#
        );
        let res = schema.execute(&q).await;
        assert!(
            !res.errors.is_empty(),
            "expected an error for oversized coverage matrix"
        );
    }

    #[test]
    fn ensure_empty_subscription_compiles() {
        // Compile-only check: confirms we can build the same schema with an
        // `EmptySubscription` for federation / testing.
        let _: Schema<QueryRoot, MutationRoot, EmptySubscription> =
            Schema::build(QueryRoot, MutationRoot, EmptySubscription).finish();
    }
}
