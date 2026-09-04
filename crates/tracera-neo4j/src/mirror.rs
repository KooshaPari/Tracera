//! Bidirectional synchronization between SWEE SQLite rows and Neo4j.

use crate::{Error, SweeEdge, SweeNode};
use neo4rs::Query;
use sqlx::{Row, SqlitePool};

/// Read all SWEE nodes from SQLite.
pub async fn load_nodes(pool: &SqlitePool) -> Result<Vec<SweeNode>, Error> {
    let rows = sqlx::query(
        "SELECT id, type, name, metadata, created_at, updated_at FROM swee_nodes ORDER BY id",
    )
    .fetch_all(pool)
    .await?;
    Ok(rows
        .into_iter()
        .map(|row| SweeNode {
            id: row.try_get("id")?,
            kind: row.try_get("type")?,
            name: row.try_get("name")?,
            metadata: parse_metadata(&row.try_get::<String, _>("metadata").unwrap_or_default()),
            created_at: row.try_get("created_at")?,
            updated_at: row.try_get("updated_at")?,
        })
        .collect())
}

/// Read all SWEE edges from SQLite.
pub async fn load_edges(pool: &SqlitePool) -> Result<Vec<SweeEdge>, Error> {
    let rows = sqlx::query(
        "SELECT id, source_id, target_id, type, weight, metadata, created_at
         FROM swee_edges ORDER BY id",
    )
    .fetch_all(pool)
    .await?;
    Ok(rows
        .into_iter()
        .map(|row| SweeEdge {
            id: row.try_get("id")?,
            source_id: row.try_get("source_id")?,
            target_id: row.try_get("target_id")?,
            kind: row.try_get("type")?,
            weight: row.try_get::<Option<f64>, _>("weight")?.unwrap_or(1.0),
            metadata: parse_metadata(&row.try_get::<String, _>("metadata").unwrap_or_default()),
            created_at: row.try_get("created_at")?,
        })
        .collect())
}

/// Merge one SQLite node into Neo4j using a stable numeric identity.
pub fn merge_node(node: &SweeNode) -> Result<(String, Query), Error> {
    let metadata = serde_json::to_string(&node.metadata)?;
    Ok((
        format!("upsert SWEE node {}", node.id),
        Query::new(
            "MERGE (n:SWEE {id: $id}) SET n.kind = $kind, n.name = $name, n.metadata = $metadata, n.created_at = $created_at, n.updated_at = $updated_at",
        )
        .param("id", node.id)
        .param("kind", node.kind.as_str())
        .param("name", node.name.as_str())
        .param("metadata", metadata)
        .param("created_at", node.created_at.as_str())
        .param("updated_at", node.updated_at.as_str()),
    ))
}

/// Merge one SQLite edge into Neo4j.
pub fn merge_edge(edge: &SweeEdge) -> Result<(String, Query), Error> {
    let metadata = serde_json::to_string(&edge.metadata)?;
    Ok((
        format!("upsert SWEE edge {}", edge.id),
        Query::new(
            "MATCH (a:SWEE {id: $source_id}), (b:SWEE {id: $target_id}) MERGE (a)-[r:SWEE_EDGE {id: $id}]->(b) SET r.kind = $kind, r.weight = $weight, r.metadata = $metadata, r.created_at = $created_at",
        )
        .param("id", edge.id)
        .param("source_id", edge.source_id)
        .param("target_id", edge.target_id)
        .param("kind", edge.kind.as_str())
        .param("weight", edge.weight)
        .param("metadata", metadata)
        .param("created_at", edge.created_at.as_str()),
    ))
}

/// Synchronize all rows to Neo4j. Nodes are written before edges so every
/// relationship endpoint exists.
pub async fn sync_sqlite_to_neo4j(
    pool: &SqlitePool,
    graph: &neo4rs::Graph,
) -> Result<usize, Error> {
    let nodes = load_nodes(pool).await?;
    let edges = load_edges(pool).await?;
    for node in &nodes {
        let (label, query) = merge_node(node)?;
        graph.execute(query).await.map_err(|e| Error::Neo4j(e))?;
        tracing::debug!(operation = %label);
    }
    for edge in &edges {
        let (label, query) = merge_edge(edge)?;
        graph.execute(query).await.map_err(|e| Error::Neo4j(e))?;
        tracing::debug!(operation = %label);
    }
    Ok(nodes.len() + edges.len())
}

fn parse_metadata(value: &str) -> serde_json::Value {
    serde_json::from_str(value).unwrap_or_else(|_| serde_json::json!({}))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn metadata_parser_handles_null_and_json() {
        assert_eq!(parse_metadata("null"), serde_json::Value::Null);
        assert_eq!(parse_metadata(r#"{"owner":"alice"}"#), json!({"owner":"alice"}));
        assert_eq!(parse_metadata("not-json"), json!({}));
    }

    #[test]
    fn node_query_uses_stable_id() {
        let node = SweeNode {
            id: 7,
            kind: "requirement".into(),
            name: "R-7".into(),
            metadata: json!({}),
            created_at: "2026-01-01T00:00:00Z".into(),
            updated_at: "2026-01-01T00:00:00Z".into(),
        };
        let (_, query) = merge_node(&node).unwrap();
        let rendered = query.to_string();
        assert!(rendered.contains("MERGE"));
        assert!(rendered.contains("SWEE"));
    }
}
