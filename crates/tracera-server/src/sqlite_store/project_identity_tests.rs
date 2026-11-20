//! Canonical project discovery tests backed by real SQLite migrations.
use super::*;
use crate::{sqlite_store::SqliteStore, store::ListParams};
use serde_json::{json, Value};

async fn store() -> SqliteStore {
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .unwrap();
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .unwrap();
    SqliteStore::new(pool)
}

fn payload(product: &str) -> Value {
    json!({
        "product_id": product,
        "baseline": 1,
        "idempotency_key": "identity-run",
        "intents": [{"id":"storage","kind":"Capability","title":"Storage","description":"durability","status":"Accepted","baseline":1}],
        "observations": [{
            "id":"obs-1","product_id":product,"baseline":1,"kind":"TestResult","result":"Failed",
            "source":{"collector":"cargo-test","version":"1","artifact_ref":"file:report.xml"},
            "recorded_at":"2026-10-16T00:00:00Z","capability_id":"storage"
        }]
    })
}

#[tokio::test]
async fn product_with_observations_is_discovered_without_a_problem_row() {
    let store = store().await;
    assert_eq!(
        sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM problems")
            .fetch_one(&store.pool)
            .await
            .unwrap(),
        0
    );
    let receipt = store
        .ingest_product_observations(serde_json::from_value(payload("product-alpha")).unwrap())
        .await
        .unwrap();
    assert_eq!(receipt.accepted, 1);

    let listed = store
        .list_projects(ListParams {
            page: 1,
            page_size: 50,
        })
        .await
        .unwrap();
    let found = listed.iter().find(|project| project.id == "product-alpha");
    assert!(found.is_some(), "product missing from normal listing");
    assert_eq!(found.unwrap().problem_count, 0);
    assert_eq!(found.unwrap().metadata["kind"], "product");

    let detail = store
        .get_project("product-alpha".to_owned())
        .await
        .unwrap()
        .expect("product should be discoverable by id");
    assert_eq!(detail.id, "product-alpha");
    assert_eq!(detail.problem_count, 0);
    assert_eq!(store.count_projects().await.unwrap(), 1);
}

#[tokio::test]
async fn empty_store_discovery_is_empty_and_creates_no_placeholder() {
    let store = store().await;
    let listed = store
        .list_projects(ListParams {
            page: 1,
            page_size: 50,
        })
        .await
        .unwrap();
    assert!(listed.is_empty());
    assert_eq!(store.count_projects().await.unwrap(), 0);
    assert!(store
        .get_project("product-alpha".to_owned())
        .await
        .unwrap()
        .is_none());
    assert_eq!(
        sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM projects")
            .fetch_one(&store.pool)
            .await
            .unwrap(),
        0
    );
}

#[tokio::test]
async fn product_baseline_and_observations_resolve_to_one_project_scope() {
    let store = store().await;
    store
        .ingest_product_observations(serde_json::from_value(payload("product-beta")).unwrap())
        .await
        .unwrap();

    let baseline_scope: String = sqlx::query_scalar(
        "SELECT project_id FROM project_scopes WHERE source_kind = 'product_baseline' LIMIT 1",
    )
    .fetch_one(&store.pool)
    .await
    .unwrap();
    let observation_scope: String = sqlx::query_scalar(
        "SELECT project_id FROM project_scopes WHERE source_kind = 'product_observation' LIMIT 1",
    )
    .fetch_one(&store.pool)
    .await
    .unwrap();
    assert_eq!(baseline_scope, "product-beta");
    assert_eq!(observation_scope, "product-beta");

    let source_id: String = sqlx::query_scalar(
        "SELECT source_id FROM project_scopes WHERE project_id = 'product-beta' LIMIT 1",
    )
    .fetch_one(&store.pool)
    .await
    .unwrap();
    assert_eq!(source_id, "product-beta:1");
    assert_eq!(
        store
            .get_project(baseline_scope)
            .await
            .unwrap()
            .map(|item| item.id),
        Some("product-beta".to_owned())
    );
}
