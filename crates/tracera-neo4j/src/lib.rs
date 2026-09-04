//! Neo4j synchronization and graph query support for Tracera.
//!
//! The crate keeps the SWEE graph contract independent from a specific Neo4j
//! client version: data types and Cypher statements live in [`mirror`] and
//! [`queries`], while the `sync-worker` binary provides continuous operation.

pub mod mirror;
pub mod queries;

/// Error returned by the Neo4j synchronization surface.
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("SQLite error: {0}")]
    Sqlite(#[from] sqlx::Error),
    #[error("Neo4j error: {0}")]
    Neo4j(#[from] neo4rs::Error),
    #[error("serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("invalid synchronization configuration: {0}")]
    Configuration(String),
    #[error("synchronization I/O error: {0}")]
    Io(#[from] std::io::Error),
}

/// A graph node read from the SWEE SQLite store.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct SweeNode {
    pub id: i64,
    #[serde(alias = "node_type")]
    pub kind: String,
    pub name: String,
    #[serde(default)]
    pub metadata: serde_json::Value,
    pub created_at: String,
    pub updated_at: String,
}

/// A directed graph edge read from the SWEE SQLite store.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct SweeEdge {
    pub id: i64,
    pub source_id: i64,
    pub target_id: i64,
    #[serde(alias = "edge_type")]
    pub kind: String,
    #[serde(default = "default_weight")]
    pub weight: f64,
    #[serde(default)]
    pub metadata: serde_json::Value,
    pub created_at: String,
}

/// A compact Neo4j graph query result.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct GraphRecord {
    pub id: i64,
    pub kind: String,
    pub name: String,
}

const fn default_weight() -> f64 {
    1.0
}
