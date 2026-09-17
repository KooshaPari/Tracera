//! Hermetic DB-layer integration tests — SWEE graph + Evidence + Sprint
//! against an in-memory SQLite store with the real migrations applied.
//!
//! These exercise the `Store` trait directly (no HTTP layer), which is the
//! ground-truth persistence path every API/MCP handler funnels through.

use chrono::{TimeZone, Utc};
use serde_json::{json, Value};
use sqlx::{sqlite::SqlitePoolOptions, SqlitePool};

use tracera_server::sqlite_store::SqliteStore;
use tracera_server::store::Store;

async fn mem_store() -> SqliteStore {
    // Single connection so an in-memory DB is shared across migrate + queries.
    let pool: SqlitePool = SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .expect("open in-memory sqlite");
    // Apply the real migration DDL (same files the server uses).
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .expect("apply sqlite migrations");
    SqliteStore::new(pool)
}

fn now() -> chrono::DateTime<Utc> {
    Utc.timestamp_opt(1_752_000_000, 0).unwrap()
}

#[tokio::test]
async fn swee_node_roundtrip() {
    let store = mem_store().await;
    let id = store
        .create_swee_node(
            "requirement".into(),
            "REQ-001".into(),
            json!({"owner":"alice"}),
            now(),
        )
        .await
        .expect("create node");
    assert!(!id.is_empty());

    let nodes = store.list_swee_nodes(None).await.expect("list nodes");
    assert_eq!(nodes.len(), 1);
    assert_eq!(nodes[0]["node_type"], "requirement");
    assert_eq!(nodes[0]["label"], "REQ-001");

    let got = store.get_swee_node(id.clone()).await.expect("get node");
    assert!(got.is_some());
    assert_eq!(got.unwrap()["label"], "REQ-001");
}

#[tokio::test]
async fn swee_edge_roundtrip_and_neighbors() {
    let store = mem_store().await;
    let a = store
        .create_swee_node("requirement".into(), "REQ-001".into(), Value::Null, now())
        .await
        .expect("node a");
    let b = store
        .create_swee_node("source_file".into(), "auth.rs".into(), Value::Null, now())
        .await
        .expect("node b");

    let eid = store
        .create_swee_edge(
            "implements".into(),
            a.clone(),
            b.clone(),
            1.0,
            "test".into(),
            Value::Null,
            now(),
        )
        .await
        .expect("create edge");
    assert!(!eid.is_empty());

    let edges = store.list_swee_edges(None).await.expect("list edges");
    assert_eq!(edges.len(), 1);
    assert_eq!(edges[0]["edge_type"], "implements");

    let neighbors = store
        .get_swee_neighbors(a, "forward".into())
        .await
        .expect("neighbors");
    assert_eq!(neighbors.len(), 1);
}

#[tokio::test]
async fn evidence_roundtrip() {
    let store = mem_store().await;
    store
        .create_evidence(
            "evt-1".into(),
            "art-1".into(),
            "unit_test".into(),
            "crates/tracera-server/src/store.rs".into(),
            json!({"result": "pass"}),
            now(),
        )
        .await
        .expect("create evidence");

    let items = store.list_evidence().await.expect("list evidence");
    assert_eq!(items.len(), 1);
    assert_eq!(items[0].id, "evt-1");
    assert_eq!(items[0].kind, "unit_test");
}

#[tokio::test]
async fn sprint_roundtrip() {
    let store = mem_store().await;
    store
        .create_sprint(
            "sp-1".into(),
            "Sprint 1".into(),
            "Ship SWEE CRUD".into(),
            Utc.timestamp_opt(1_750_000_000, 0).unwrap(),
            Utc.timestamp_opt(1_760_000_000, 0).unwrap(),
            now(),
        )
        .await
        .expect("create sprint");

    let sprints = store.list_sprints().await.expect("list sprints");
    assert_eq!(sprints.len(), 1);
    assert_eq!(sprints[0].name, "Sprint 1");
}
