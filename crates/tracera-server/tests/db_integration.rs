//! Hermetic DB-layer integration tests — SWEE graph + Evidence + Sprint
//! against an in-memory SQLite store with the real migrations applied.
//!
//! These exercise the `Store` trait directly (no HTTP layer), which is the
//! ground-truth persistence path every API/MCP handler funnels through.

use chrono::{TimeZone, Utc};
use serde_json::{json, Value};
use sqlx::{sqlite::{SqliteConnectOptions, SqlitePoolOptions}, SqlitePool};

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

async fn file_store(path: &std::path::Path) -> SqliteStore {
    let options = SqliteConnectOptions::new()
        .filename(path)
        .create_if_missing(true);
    let pool = SqlitePoolOptions::new()
        .max_connections(1)
        .connect_with(options)
        .await
        .expect("open file-backed sqlite");
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


#[tokio::test]
async fn product_v1_schema_supports_scoped_ids_and_immutable_baselines() {
    let store = mem_store().await;
    let pool = &store.pool;

    // Two products may use the same human/local identity.
    for (entity_id, product_id) in [("entity-a-search", "product-a"), ("entity-b-search", "product-b")] {
        sqlx::query(
            "INSERT INTO product_entities_v1 (entity_id, product_id, local_id, entity_kind, created_at)
             VALUES (?1, ?2, 'search', 'capability', ?3)"
        )
        .bind(entity_id)
        .bind(product_id)
        .bind(now().to_rfc3339())
        .execute(pool)
        .await
        .expect("insert product-scoped entity");
    }

    sqlx::query(
        "INSERT INTO product_entity_revisions_v1
         (entity_revision_id, entity_id, content_revision, title, description, status, metadata, created_at)
         VALUES ('a-search-r1','entity-a-search',1,'Search v1','','accepted','{}',?1),
                ('a-search-r2','entity-a-search',2,'Search v2','','accepted','{}',?1)"
    )
    .bind(now().to_rfc3339())
    .execute(pool)
    .await
    .expect("insert entity revisions");

    sqlx::query(
        "INSERT INTO product_baselines_v1
         (baseline_id, product_id, revision_number, parent_baseline_id, accepted_at, metadata)
         VALUES ('a-b1','product-a',1,NULL,?1,'{}'),
                ('a-b2','product-a',2,'a-b1',?1,'{}')"
    )
    .bind(now().to_rfc3339())
    .execute(pool)
    .await
    .expect("insert baselines");

    sqlx::query(
        "INSERT INTO baseline_entity_membership_v1 (baseline_id, entity_id, entity_revision_id)
         VALUES ('a-b1','entity-a-search','a-search-r1'),
                ('a-b2','entity-a-search','a-search-r2')"
    )
    .execute(pool)
    .await
    .expect("insert baseline membership");

    let b1_title: String = sqlx::query_scalar(
        "SELECT r.title
         FROM baseline_entity_membership_v1 m
         JOIN product_entity_revisions_v1 r ON r.entity_revision_id=m.entity_revision_id
         WHERE m.baseline_id='a-b1' AND m.entity_id='entity-a-search'"
    )
    .fetch_one(pool)
    .await
    .expect("read baseline 1");
    let b2_title: String = sqlx::query_scalar(
        "SELECT r.title
         FROM baseline_entity_membership_v1 m
         JOIN product_entity_revisions_v1 r ON r.entity_revision_id=m.entity_revision_id
         WHERE m.baseline_id='a-b2' AND m.entity_id='entity-a-search'"
    )
    .fetch_one(pool)
    .await
    .expect("read baseline 2");

    assert_eq!(b1_title, "Search v1");
    assert_eq!(b2_title, "Search v2");

    let scoped_count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM product_entities_v1 WHERE local_id='search'"
    )
    .fetch_one(pool)
    .await
    .expect("count scoped identities");
    assert_eq!(scoped_count, 2);
}

#[tokio::test]
async fn product_v1_observation_is_append_only_history_across_invalidation() {
    let store = mem_store().await;
    let pool = &store.pool;

    sqlx::query(
        "INSERT INTO product_baselines_v1
         (baseline_id, product_id, revision_number, accepted_at, metadata)
         VALUES ('a-b1','product-a',1,?1,'{}')"
    )
    .bind(now().to_rfc3339())
    .execute(pool)
    .await
    .expect("baseline");

    sqlx::query(
        "INSERT INTO product_observations_v1
         (observation_id, product_id, baseline_id, subject_local_id, candidate_ref,
          configuration, result, verifier_id, verifier_version, recorded_at, metadata)
         VALUES ('obs-1','product-a','a-b1','search','git:abc','{}','passed',
                 'test-suite','1',?1,'{}')"
    )
    .bind(now().to_rfc3339())
    .execute(pool)
    .await
    .expect("observation");

    let before: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM product_observations_v1 WHERE observation_id='obs-1'"
    )
    .fetch_one(pool)
    .await
    .unwrap();
    assert_eq!(before, 1);

    // Later invalidation/reuse state must be represented separately; the
    // original observation row remains historically queryable.
    let result: String = sqlx::query_scalar(
        "SELECT result FROM product_observations_v1 WHERE observation_id='obs-1'"
    )
    .fetch_one(pool)
    .await
    .unwrap();
    assert_eq!(result, "passed");
}


#[tokio::test]
async fn product_v1_revocation_invalidates_reuse_not_observation_history() {
    let store = mem_store().await;
    let pool = &store.pool;
    let t = now().to_rfc3339();

    sqlx::query("INSERT INTO product_baselines_v1 (baseline_id,product_id,revision_number,accepted_at,metadata) VALUES ('b1','p',1,?1,'{}'),('b2','p',2,?1,'{}')")
        .bind(&t).execute(pool).await.unwrap();
    sqlx::query("INSERT INTO product_observations_v1 (observation_id,product_id,baseline_id,subject_local_id,candidate_ref,configuration,result,verifier_id,verifier_version,recorded_at,metadata) VALUES ('o1','p','b1','search','git:abc','{}','passed','suite','1',?1,'{}')")
        .bind(&t).execute(pool).await.unwrap();
    sqlx::query("INSERT INTO evidence_reuse_decisions_v1 (reuse_decision_id,observation_id,target_baseline_id,target_candidate_ref,criterion_ref,applicability_state,compatibility_certificate_ref,policy_version,reason,decided_at) VALUES ('r1','o1','b2','git:def','search-compatible','current_valid','cert:c1','reuse-v1','compatible',?1)")
        .bind(&t).execute(pool).await.unwrap();
    sqlx::query("INSERT INTO invalidation_events_v1 (invalidation_id,trigger_kind,trigger_ref,target_kind,target_ref,prior_state,new_state,reason,occurred_at) VALUES ('i1','certificate_revoked','cert:c1','reuse_decision','r1','current_valid','suspect','certificate revoked',?1)")
        .bind(&t).execute(pool).await.unwrap();

    let observation_result:String=sqlx::query_scalar("SELECT result FROM product_observations_v1 WHERE observation_id='o1'").fetch_one(pool).await.unwrap();
    assert_eq!(observation_result,"passed");

    let new_state:String=sqlx::query_scalar("SELECT new_state FROM invalidation_events_v1 WHERE target_kind='reuse_decision' AND target_ref='r1' ORDER BY occurred_at DESC,invalidation_id DESC LIMIT 1").fetch_one(pool).await.unwrap();
    assert_eq!(new_state,"suspect");

    let reuse_count:i64=sqlx::query_scalar("SELECT COUNT(*) FROM evidence_reuse_decisions_v1 WHERE reuse_decision_id='r1'").fetch_one(pool).await.unwrap();
    assert_eq!(reuse_count,1);
}


#[tokio::test]
async fn product_v1_file_restart_preserves_baseline_and_observation_history() {
    let path = std::env::temp_dir().join(format!("tracera-product-v1-{}.db", uuid::Uuid::new_v4()));
    {
        let store = file_store(&path).await;
        let pool = &store.pool;
        let t = now().to_rfc3339();
        sqlx::query("INSERT INTO product_baselines_v1 (baseline_id,product_id,revision_number,accepted_at,metadata) VALUES ('restart-b1','restart-product',1,?1,'{}')")
            .bind(&t).execute(pool).await.unwrap();
        sqlx::query("INSERT INTO product_observations_v1 (observation_id,product_id,baseline_id,subject_local_id,candidate_ref,configuration,result,verifier_id,verifier_version,recorded_at,metadata) VALUES ('restart-o1','restart-product','restart-b1','search','git:restart','{}','passed','suite','1',?1,'{}')")
            .bind(&t).execute(pool).await.unwrap();
    }
    {
        let store = file_store(&path).await;
        let pool = &store.pool;
        let revision:i64=sqlx::query_scalar("SELECT revision_number FROM product_baselines_v1 WHERE baseline_id='restart-b1'").fetch_one(pool).await.unwrap();
        let result:String=sqlx::query_scalar("SELECT result FROM product_observations_v1 WHERE observation_id='restart-o1'").fetch_one(pool).await.unwrap();
        assert_eq!(revision,1);
        assert_eq!(result,"passed");
    }
    let _ = std::fs::remove_file(path);
}
