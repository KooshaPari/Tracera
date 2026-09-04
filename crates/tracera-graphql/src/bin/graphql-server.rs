//! GraphQL gateway binary — `tracera-graphql`.
//!
//! Defaults to loopback bind on `:8081` so it can run alongside the REST
//! server (`tracera-server` on `:8080`) without port collisions. Set the
//! `TRACERA_GRAPHQL_BIND_ADDR` env var to override.
//!
//! Endpoints:
//!   - `POST /graphql`     — single-shot queries / mutations
//!   - `GET  /graphql`     — GraphiQL playground (development)
//!   - `GET  /ws`          — graphql-ws subscription transport
//!   - `GET  /graphql/schema` — SDL dump
//!   - `GET  /healthz`     — service health (REST parity)
//!   - `GET  /readyz`      — readiness probe (REST parity)
//!
//! The default in-memory store keeps the binary deployable as a standalone
//! dev/demo without depending on `tracera-server`. A production deployment
//! would replace `MemStore` with an adapter over the real `Store` trait.

use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;

use async_graphql::http::{playground_source, GraphQLPlaygroundConfig};
use async_graphql_axum::{GraphQLRequest, GraphQLResponse, GraphQLSubscription};
use axum::{
    extract::State,
    http::{header, HeaderValue, StatusCode},
    response::{IntoResponse, Response},
    routing::{get, post},
    Router,
};
use chrono::Utc;
use serde_json::{json, Value as JsonValue};
use tokio::sync::Mutex;
use tower_http::{
    cors::CorsLayer,
    set_header::SetResponseHeaderLayer,
};
use tracing::{info, warn};
use tracing_subscriber::EnvFilter;
use uuid::Uuid;

use tracera_graphql::resolvers::edge::{
    EdgeCreateInput, EdgeKind, EdgeListFilter, GraphEdge, NodeRef, PersistedTraceLink, TraceDirection,
};
use tracera_graphql::resolvers::node::{GraphNode, NodeCreateInput, NodeKind, NodeListFilter};
use tracera_graphql::{
    build_schema, GraphContext, GraphEventBus, GraphStore, TraceraSchema,
};

const BIND_ENV: &str = "TRACERA_GRAPHQL_BIND_ADDR";
const DEFAULT_BIND: &str = "127.0.0.1:8081";

// ---------------------------------------------------------------------------
// In-memory store — kept here (rather than in lib.rs) so production builds
// can swap in a real backend without forcing the gateway library to depend
// on it.
// ---------------------------------------------------------------------------

#[derive(Default)]
struct MemStore {
    nodes: Mutex<Vec<GraphNode>>,
    edges: Mutex<Vec<GraphEdge>>,
    trace_links: Mutex<Vec<PersistedTraceLink>>,
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
        out.sort_by(|a, b| a.id.cmp(&b.id));
        Ok(out)
    }
}

// ---------------------------------------------------------------------------
// HTTP handlers
// ---------------------------------------------------------------------------

#[derive(Clone)]
struct AppState {
    schema: TraceraSchema,
}

async fn graphql_post(
    State(state): State<AppState>,
    req: GraphQLRequest,
) -> GraphQLResponse {
    state.schema.execute(req.into_inner()).await.into()
}

async fn graphql_ws(
    State(state): State<AppState>,
    protocol: axum::extract::WebSocketUpgrade,
) -> Response {
    protocol
        .protocols(["graphql-transport-ws", "graphql-ws"])
        .on_upgrade(move |socket| {
            let schema = state.schema.clone();
            async move {
                GraphQLSubscription::new(schema)
                    .on_connection_init(|_value| async move { Ok(Default::default()) })
                    .serve(socket)
                    .await
                    .unwrap_or_else(|e| warn!("subscription error: {e}"));
            }
        })
}

async fn graphql_get() -> Response {
    // GraphiQL playground — handy for development.
    let html = playground_source(GraphQLPlaygroundConfig::new("/graphql"));
    ([(header::CONTENT_TYPE, HeaderValue::from_static("text/html; charset=utf-8"))], html)
        .into_response()
}

async fn graphql_schema(State(state): State<AppState>) -> Response {
    let sdl = state.schema.sdl();
    (
        [(
            header::CONTENT_TYPE,
            HeaderValue::from_static("text/plain; charset=utf-8"),
        )],
        sdl,
    )
        .into_response()
}

async fn healthz() -> Response {
    (StatusCode::OK, Json(json!({ "status": "ok" }))).into_response()
}

async fn readyz() -> Response {
    (StatusCode::OK, Json(json!({ "ready": true }))).into_response()
}

use axum::Json;

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::from_default_env()
                .add_directive("tracera_graphql=info".parse().unwrap())
                .add_directive("graphql_server=info".parse().unwrap()),
        )
        .init();

    let store: Arc<dyn GraphStore> = Arc::new(MemStore::default());
    let bus = GraphEventBus::default();
    let ctx = GraphContext::new(store, bus);
    let schema = build_schema(ctx);

    let app = Router::new()
        .route("/graphql", post(graphql_post).get(graphql_get))
        .route("/ws", get(graphql_ws))
        .route("/graphql/schema", get(graphql_schema))
        .route("/healthz", get(healthz))
        .route("/readyz", get(readyz))
        .with_state(AppState { schema })
        // Same security headers the REST server sets.
        .layer(SetResponseHeaderLayer::if_not_present(
            header::X_CONTENT_TYPE_OPTIONS,
            HeaderValue::from_static("nosniff"),
        ))
        .layer(SetResponseHeaderLayer::if_not_present(
            header::X_FRAME_OPTIONS,
            HeaderValue::from_static("DENY"),
        ))
        .layer(SetResponseHeaderLayer::if_not_present(
            header::REFERRER_POLICY,
            HeaderValue::from_static("no-referrer"),
        ))
        .layer(SetResponseHeaderLayer::if_not_present(
            header::CACHE_CONTROL,
            HeaderValue::from_static("no-store"),
        ))
        .layer(
            CorsLayer::new()
                .allow_origin(HeaderValue::from_static("http://127.0.0.1:8080"))
                .allow_methods([
                    axum::http::Method::GET,
                    axum::http::Method::POST,
                    axum::http::Method::OPTIONS,
                ])
                .allow_headers([header::AUTHORIZATION, header::CONTENT_TYPE])
                .allow_credentials(true),
        );

    let addr: SocketAddr = std::env::var(BIND_ENV)
        .unwrap_or_else(|_| DEFAULT_BIND.to_string())
        .parse()
        .expect("TRACERA_GRAPHQL_BIND_ADDR must be a valid socket address");

    if !addr.ip().is_loopback() {
        warn!(
            "tracera-graphql binding to non-loopback address {addr}; \
             set up a reverse proxy with TLS and authentication before exposing publicly"
        );
    }

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .unwrap_or_else(|e| {
            eprintln!("FATAL: cannot bind tracera-graphql to {addr}: {e}");
            std::process::exit(1);
        });
    info!("tracera-graphql listening on http://{addr}");
    info!("  GraphQL endpoint: POST http://{addr}/graphql");
    info!("  GraphiQL UI:      GET  http://{addr}/graphql");
    info!("  Subscriptions:    WS   ws://{addr}/ws");
    info!("  SDL dump:         GET  http://{addr}/graphql/schema");
    info!("  Health:           GET  http://{addr}/healthz");

    if let Err(e) = axum::serve(listener, app).await {
        eprintln!("FATAL: tracera-graphql stopped unexpectedly: {e}");
        std::process::exit(1);
    }
}
