//! Neo4j Bolt sync client — replicates SWEE graph nodes + trace_links to a Neo4j Aura
//! instance for graph traversal queries Cypher can't easily express over sqlx.
//!
//! Activates when env `NEO4J_URL` is set (bolt+s URL). Falls back to no-op when unset.
//!
//! Driver: `neo4rs` (Bolt 5.x, async, tokio-compatible).

use std::sync::Arc;
use tracing::{debug, info, warn};

use neo4rs::{Auth, Driver, Query};

#[derive(Clone)]
pub struct Neo4jClient {
    inner: Arc<Neo4jInner>,
}

enum Neo4jInner {
    Disabled,
    Enabled { driver: Driver },
}

impl Neo4jClient {
    pub fn from_env() -> Self {
        let url = std::env::var("NEO4J_URL").ok();
        let user = std::env::var("NEO4J_USER").unwrap_or_else(|_| "neo4j".to_string());
        let pass = std::env::var("NEO4J_PASSWORD").ok();

        let url = match url {
            Some(u) if !u.is_empty() => u,
            _ => {
                debug!("NEO4J_URL not set; neo4j sync disabled (no-op)");
                return Self { inner: Arc::new(Neo4jInner::Disabled) };
            }
        };

        let pass = match pass {
            Some(p) if !p.is_empty() => p,
            _ => {
                warn!("NEO4J_URL set but NEO4J_PASSWORD missing; neo4j sync disabled");
                return Self { inner: Arc::new(Neo4jInner::Disabled) };
            }
        };

        match Driver::new(&url, Auth::Basic(user, pass)) {
            Ok(driver) => {
                info!("Neo4j Bolt sync enabled (endpoint {})", url);
                Self { inner: Arc::new(Neo4jInner::Enabled { driver }) }
            }
            Err(e) => {
                warn!("Neo4j driver init failed ({:?}); sync disabled", e);
                Self { inner: Arc::new(Neo4jInner::Disabled) }
            }
        }
    }

    pub fn is_enabled(&self) -> bool {
        matches!(*self.inner, Neo4jInner::Enabled { .. })
    }

    /// Sync a SWEE node to Neo4j as `(:SWEE {id, type, label, metadata})`.
    /// Best-effort: logs + ignores errors (the canonical store is sqlx; neo4j is a derived replica).
    pub async fn sync_swee_node(&self, id: i64, node_type: &str, label: &str, metadata_json: &str) {
        if let Neo4jInner::Enabled { driver } = &*self.inner {
            let mut session = match driver.session() {
                Ok(s) => s,
                Err(e) => { warn!("Neo4j session error: {e:?}"); return; }
            };
            let q = "MERGE (n:SWEE {id: $id}) SET n.type = $type, n.label = $label, n.metadata = $metadata";
            let id_val = id;
            let q_obj = Query::new(q.to_string())
                .param("id", id_val)
                .param("type", node_type.to_string())
                .param("label", label.to_string())
                .param("metadata", metadata_json.to_string());
            if let Err(e) = session.run(q_obj).await {
                warn!("Neo4j sync_swee_node failed: {e:?}");
            }
        }
    }

    /// Sync a SWEE edge as `(:SWEE)-[r:EDGE {type, confidence}]->(:SWEE)`.
    pub async fn sync_swee_edge(&self, id: i64, edge_type: &str, source: i64, target: i64, confidence: f64, metadata_json: &str) {
        if let Neo4jInner::Enabled { driver } = &*self.inner {
            let mut session = match driver.session() {
                Ok(s) => s,
                Err(e) => { warn!("Neo4j session error: {e:?}"); return; }
            };
            let q = "MATCH (a:SWEE {id: $src}), (b:SWEE {id: $dst}) MERGE (a)-[r:EDGE {id: $id}]->(b) SET r.type = $type, r.confidence = $conf, r.metadata = $metadata";
            let q_obj = Query::new(q.to_string())
                .param("id", id)
                .param("type", edge_type.to_string())
                .param("src", source)
                .param("dst", target)
                .param("conf", confidence)
                .param("metadata", metadata_json.to_string());
            if let Err(e) = session.run(q_obj).await {
                warn!("Neo4j sync_swee_edge failed: {e:?}");
            }
        }
    }
}
