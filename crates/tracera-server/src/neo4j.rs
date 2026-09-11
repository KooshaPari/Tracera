//! Neo4j Bolt sync client — replicates SWEE graph nodes + trace_links to a Neo4j Aura
//! instance for graph traversal queries Cypher can't easily express over sqlx.
//!
//! Activates when env `NEO4J_URL` is set (bolt+s URL). Falls back to no-op when unset.
//!
//! Driver: `neo4rs` 0.7.x (Bolt 4.2, async, tokio-compatible).

use std::sync::Arc;
use tracing::{debug, info, warn};

use neo4rs::{Graph, Query};

#[derive(Clone)]
pub struct Neo4jClient {
    inner: Arc<Neo4jInner>,
}

enum Neo4jInner {
    Disabled,
    Enabled { graph: Graph },
}

impl Neo4jClient {
    /// Construct from `NEO4J_URL` / `NEO4J_USER` / `NEO4J_PASSWORD` env vars,
    /// or return `None` if any required var is missing or the driver fails
    /// to initialise.  When `None` is returned, sync is a no-op.
    pub async fn from_env() -> Option<Self> {
        let url = match std::env::var("NEO4J_URL").ok().filter(|u| !u.is_empty()) {
            Some(u) => u,
            None => {
                debug!("NEO4J_URL not set; neo4j sync disabled (no-op)");
                return None;
            }
        };
        let user = std::env::var("NEO4J_USER").unwrap_or_else(|_| "neo4j".to_string());
        let pass = match std::env::var("NEO4J_PASSWORD").ok().filter(|p| !p.is_empty()) {
            Some(p) => p,
            None => {
                warn!("NEO4J_URL set but NEO4J_PASSWORD missing; neo4j sync disabled");
                return None;
            }
        };

        // neo4rs 0.7.x: Graph::new(uri, user, password) returns Future<Output=Result<Graph>>
        let url_for_log = url.clone();
        let graph_result = Graph::new(url.clone(), user.clone(), pass.clone()).await;
        match graph_result {
            Ok(graph) => {
                info!("Neo4j Bolt sync enabled (endpoint {})", url_for_log);
                Some(Self { inner: Arc::new(Neo4jInner::Enabled { graph }) })
            }
            Err(e) => {
                warn!("Neo4j driver init failed ({:?}); sync disabled", e);
                None
            }
        }
    }

    pub fn is_enabled(&self) -> bool {
        matches!(*self.inner, Neo4jInner::Enabled { .. })
    }

    /// Sync a SWEE node to Neo4j as `(:SWEE {id, type, label, metadata})`.
    /// Best-effort: logs + ignores errors (the canonical store is sqlx; neo4j is a derived replica).
    pub async fn sync_swee_node(&self, id: i64, node_type: &str, label: &str, metadata_json: &str) {
        if let Neo4jInner::Enabled { graph } = &*self.inner {
            let q_str = "MERGE (n:SWEE {id: $id}) SET n.type = $type, n.label = $label, n.metadata = $metadata";
            let q = Query::new(q_str.to_string())
                .param("id", id)
                .param("type", node_type.to_string())
                .param("label", label.to_string())
                .param("metadata", metadata_json.to_string());
            let result = graph.execute(q).await;
            if let Err(e) = result {
                warn!("Neo4j sync_swee_node failed: {e:?}");
            }
        }
    }

    /// Sync a SWEE edge as `(:SWEE)-[r:EDGE {type, confidence}]->(:SWEE)`.
    pub async fn sync_swee_edge(&self, id: i64, edge_type: &str, source: i64, target: i64, confidence: f64, metadata_json: &str) {
        if let Neo4jInner::Enabled { graph } = &*self.inner {
            let q_str = "MATCH (a:SWEE {id: $src}), (b:SWEE {id: $dst}) MERGE (a)-[r:EDGE {id: $id}]->(b) SET r.type = $type, r.confidence = $conf, r.metadata = $metadata";
            let q = Query::new(q_str.to_string())
                .param("id", id)
                .param("type", edge_type.to_string())
                .param("src", source)
                .param("dst", target)
                .param("conf", confidence)
                .param("metadata", metadata_json.to_string());
            let result = graph.execute(q).await;
            if let Err(e) = result {
                warn!("Neo4j sync_swee_edge failed: {e:?}");
            }
        }
    }
}
