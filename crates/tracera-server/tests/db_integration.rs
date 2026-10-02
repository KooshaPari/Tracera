//! Hermetic DB-layer integration tests — SWEE graph + Evidence + Sprint
//! against an in-memory SQLite store with the real migrations applied.
//!
//! These exercise the `Store` trait directly (no HTTP layer), which is the
//! ground-truth persistence path every API/MCP handler funnels through.

use chrono::{TimeZone, Utc};
use serde_json::{json, Value};
use sqlx::{
    sqlite::{SqliteConnectOptions, SqlitePoolOptions},
    SqlitePool,
};

use tracera_server::product::{
    DependencyAuthority, DependencyEdge, EvidenceReuseDecision, InvalidationEvent,
    PersistedBaseline, PersistedEntity, PersistedEntityRevision, PersistedObservation,
    PersistedProduct, ProductPersistence, execute_dependency_invalidation,
};
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
async fn persistence_backed_invalidation_preserves_partial_continuation_and_event_count() {
    let store = mem_store().await;
    let edges = vec![
        DependencyEdge {
            dependency: "schema".into(),
            dependent: "criterion-a".into(),
            authority: DependencyAuthority::Accepted,
            revision: "r1".into(),
            active: true,
        },
        DependencyEdge {
            dependency: "criterion-a".into(),
            dependent: "criterion-b".into(),
            authority: DependencyAuthority::Accepted,
            revision: "r1".into(),
            active: true,
        },
    ];

    let result = execute_dependency_invalidation(
        &store,
        &["schema".into()],
        &edges,
        "r1",
        2,
        "change:bounded",
        "criterion",
    )
    .await
    .expect("execute bounded invalidation");

    assert!(!result.plan.propagation.complete);
    assert_eq!(result.plan.propagation.affected, vec!["schema", "criterion-a"]);
    assert_eq!(result.plan.propagation.continuation, vec!["criterion-b"]);
    assert_eq!(result.persisted_events, 1);

    let persisted = ProductPersistence::list_invalidations(
        &store,
        "criterion",
        "criterion-a",
        10,
    )
    .await
    .expect("list persisted invalidations");
    assert_eq!(persisted.len(), 1);
    assert_eq!(persisted[0].trigger_ref, "change:bounded");

    let not_yet_visited = ProductPersistence::list_invalidations(
        &store,
        "criterion",
        "criterion-b",
        10,
    )
    .await
    .expect("list continuation target invalidations");
    assert!(
        not_yet_visited.is_empty(),
        "continuation target must not be falsely persisted as already invalidated"
    );
}

#[tokio::test]
async fn product_persistence_port_roundtrip_preserves_history_and_invalidation() {
    let store = mem_store().await;
    let t = now();

    let product = PersistedProduct {
        product_id: "port-product".into(),
        display_name: "Port Product".into(),
        created_at: t,
    };
    ProductPersistence::create_product(&store, &product)
        .await
        .expect("create product");
    let got = ProductPersistence::get_product(&store, "port-product")
        .await
        .expect("get product")
        .expect("product exists");
    assert_eq!(got, product);

    let entity = PersistedEntity {
        entity_id: "port-entity-search".into(),
        product_id: product.product_id.clone(),
        local_id: "search".into(),
        entity_kind: "capability".into(),
        created_at: t,
    };
    ProductPersistence::create_entity(&store, &entity)
        .await
        .expect("create entity");

    let revision = PersistedEntityRevision {
        entity_revision_id: "port-entity-search-r1".into(),
        entity_id: entity.entity_id.clone(),
        content_revision: 1,
        title: "Search".into(),
        description: "Accepted search capability".into(),
        status: "accepted".into(),
        metadata: json!({"source":"test"}),
        created_at: t,
    };
    ProductPersistence::append_entity_revision(&store, &revision)
        .await
        .expect("append revision");

    let baseline = PersistedBaseline {
        baseline_id: "port-b1".into(),
        product_id: product.product_id.clone(),
        revision_number: 1,
        parent_baseline_id: None,
        accepted_at: t,
        metadata: json!({"stage":"test"}),
    };
    ProductPersistence::accept_baseline(
        &store,
        &baseline,
        &[(
            entity.entity_id.clone(),
            revision.entity_revision_id.clone(),
        )],
    )
    .await
    .expect("accept baseline");

    let members = ProductPersistence::list_baseline_entities(
        &store,
        &product.product_id,
        &baseline.baseline_id,
        10,
    )
    .await
    .expect("list members");
    assert_eq!(members, vec![revision.clone()]);

    let observation = PersistedObservation {
        observation_id: "port-o1".into(),
        product_id: product.product_id.clone(),
        baseline_id: baseline.baseline_id.clone(),
        subject_entity_id: Some(entity.entity_id.clone()),
        subject_local_id: Some(entity.local_id.clone()),
        candidate_ref: "git:abc".into(),
        configuration: json!({"platform":"test"}),
        result: "passed".into(),
        verifier_id: "suite".into(),
        verifier_version: "1".into(),
        recorded_at: t,
        raw_evidence_ref: Some("artifact:test".into()),
        metadata: json!({}),
    };
    ProductPersistence::append_observation(&store, &observation)
        .await
        .expect("append observation");

    let observations = ProductPersistence::list_observations(
        &store,
        &product.product_id,
        &baseline.baseline_id,
        Some("search"),
        10,
    )
    .await
    .expect("list observations");
    assert_eq!(observations, vec![observation.clone()]);

    let reuse = EvidenceReuseDecision {
        reuse_decision_id: "port-r1".into(),
        observation_id: observation.observation_id.clone(),
        target_baseline_id: baseline.baseline_id.clone(),
        target_candidate_ref: "git:def".into(),
        criterion_ref: "search-compatible".into(),
        applicability_state: "current_valid".into(),
        compatibility_certificate_ref: Some("cert:1".into()),
        policy_version: "reuse-v1".into(),
        reason: "compatible".into(),
        decided_at: t,
    };
    ProductPersistence::append_reuse_decision(&store, &reuse)
        .await
        .expect("append reuse");

    let invalidation = InvalidationEvent {
        invalidation_id: "port-i1".into(),
        trigger_kind: "certificate_revoked".into(),
        trigger_ref: "cert:1".into(),
        target_kind: "reuse_decision".into(),
        target_ref: reuse.reuse_decision_id.clone(),
        prior_state: Some("current_valid".into()),
        new_state: "suspect".into(),
        reason: "certificate revoked".into(),
        occurred_at: t,
    };
    ProductPersistence::append_invalidation(&store, &invalidation)
        .await
        .expect("append invalidation");

    let invalidations = ProductPersistence::list_invalidations(
        &store,
        "reuse_decision",
        &reuse.reuse_decision_id,
        10,
    )
    .await
    .expect("list invalidations");
    assert_eq!(invalidations, vec![invalidation]);

    let observations_after = ProductPersistence::list_observations(
        &store,
        &product.product_id,
        &baseline.baseline_id,
        Some("search"),
        10,
    )
    .await
    .expect("list observations after invalidation");
    assert_eq!(
        observations_after,
        vec![observation],
        "invalidation must not delete historical observation"
    );
}

#[tokio::test]
async fn product_persistence_rejects_cross_product_baseline_membership_atomically() {
    let store = mem_store().await;
    let t = now();

    for product_id in ["product-a", "product-b"] {
        ProductPersistence::create_product(
            &store,
            &PersistedProduct {
                product_id: product_id.into(),
                display_name: product_id.into(),
                created_at: t,
            },
        )
        .await
        .expect("create product");
    }

    let foreign_entity = PersistedEntity {
        entity_id: "entity-b-search".into(),
        product_id: "product-b".into(),
        local_id: "search".into(),
        entity_kind: "capability".into(),
        created_at: t,
    };
    ProductPersistence::create_entity(&store, &foreign_entity)
        .await
        .expect("create foreign entity");
    let foreign_revision = PersistedEntityRevision {
        entity_revision_id: "entity-b-search-r1".into(),
        entity_id: foreign_entity.entity_id.clone(),
        content_revision: 1,
        title: "Foreign search".into(),
        description: String::new(),
        status: "accepted".into(),
        metadata: json!({}),
        created_at: t,
    };
    ProductPersistence::append_entity_revision(&store, &foreign_revision)
        .await
        .expect("create foreign revision");

    let baseline = PersistedBaseline {
        baseline_id: "a-bad".into(),
        product_id: "product-a".into(),
        revision_number: 1,
        parent_baseline_id: None,
        accepted_at: t,
        metadata: json!({}),
    };
    let err = ProductPersistence::accept_baseline(
        &store,
        &baseline,
        &[(
            foreign_entity.entity_id.clone(),
            foreign_revision.entity_revision_id.clone(),
        )],
    )
    .await
    .expect_err("cross-product membership must fail");
    assert!(
        matches!(
            err,
            tracera_server::product::ProductPersistenceError::Invalid(_)
        ),
        "expected invalid membership error, got {err:?}"
    );

    let persisted = ProductPersistence::get_baseline(&store, "product-a", "a-bad")
        .await
        .expect("query baseline");
    assert!(
        persisted.is_none(),
        "failed membership validation must roll back baseline creation"
    );
}

#[tokio::test]
async fn product_persistence_rejects_cross_product_evidence_reuse() {
    let store = mem_store().await;
    let t = now();

    for product_id in ["reuse-a", "reuse-b"] {
        ProductPersistence::create_product(
            &store,
            &PersistedProduct {
                product_id: product_id.into(),
                display_name: product_id.into(),
                created_at: t,
            },
        )
        .await
        .expect("create product");
    }

    let baseline_a = PersistedBaseline {
        baseline_id: "reuse-a-b1".into(),
        product_id: "reuse-a".into(),
        revision_number: 1,
        parent_baseline_id: None,
        accepted_at: t,
        metadata: json!({}),
    };
    let baseline_b = PersistedBaseline {
        baseline_id: "reuse-b-b1".into(),
        product_id: "reuse-b".into(),
        revision_number: 1,
        parent_baseline_id: None,
        accepted_at: t,
        metadata: json!({}),
    };
    ProductPersistence::accept_baseline(&store, &baseline_a, &[])
        .await
        .expect("accept baseline a");
    ProductPersistence::accept_baseline(&store, &baseline_b, &[])
        .await
        .expect("accept baseline b");

    let observation = PersistedObservation {
        observation_id: "reuse-a-o1".into(),
        product_id: "reuse-a".into(),
        baseline_id: baseline_a.baseline_id.clone(),
        subject_entity_id: None,
        subject_local_id: Some("search".into()),
        candidate_ref: "git:a".into(),
        configuration: json!({}),
        result: "passed".into(),
        verifier_id: "suite".into(),
        verifier_version: "1".into(),
        recorded_at: t,
        raw_evidence_ref: None,
        metadata: json!({}),
    };
    ProductPersistence::append_observation(&store, &observation)
        .await
        .expect("append observation");

    let decision = EvidenceReuseDecision {
        reuse_decision_id: "reuse-cross-product".into(),
        observation_id: observation.observation_id.clone(),
        target_baseline_id: baseline_b.baseline_id.clone(),
        target_candidate_ref: "git:b".into(),
        criterion_ref: "search-compatible".into(),
        applicability_state: "current_valid".into(),
        compatibility_certificate_ref: Some("cert:cross".into()),
        policy_version: "reuse-v1".into(),
        reason: "must be rejected".into(),
        decided_at: t,
    };

    let err = ProductPersistence::append_reuse_decision(&store, &decision)
        .await
        .expect_err("cross-product reuse must fail");
    assert!(matches!(
        err,
        tracera_server::product::ProductPersistenceError::Invalid(_)
    ));

    let leaked: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM evidence_reuse_decisions_v1 WHERE reuse_decision_id='reuse-cross-product'",
    )
    .fetch_one(&store.pool)
    .await
    .expect("count rejected reuse");
    assert_eq!(leaked, 0, "rejected reuse decision must not be persisted");
}

#[tokio::test]
async fn invalidation_batch_is_atomic_on_conflicting_replay() {
    let store = mem_store().await;
    let t = now();

    let existing = InvalidationEvent {
        invalidation_id: "batch-i2".into(),
        trigger_kind: "dependency_changed".into(),
        trigger_ref: "change:1".into(),
        target_kind: "criterion".into(),
        target_ref: "c2".into(),
        prior_state: Some("current_valid".into()),
        new_state: "suspect".into(),
        reason: "existing".into(),
        occurred_at: t,
    };
    ProductPersistence::append_invalidation(&store, &existing)
        .await
        .expect("seed existing invalidation");

    let first = InvalidationEvent {
        invalidation_id: "batch-i1".into(),
        trigger_kind: "dependency_changed".into(),
        trigger_ref: "change:1".into(),
        target_kind: "criterion".into(),
        target_ref: "c1".into(),
        prior_state: Some("current_valid".into()),
        new_state: "suspect".into(),
        reason: "new".into(),
        occurred_at: t,
    };
    let conflicting = InvalidationEvent {
        reason: "different immutable content".into(),
        ..existing.clone()
    };

    let err = ProductPersistence::append_invalidations(&store, &[first.clone(), conflicting])
        .await
        .expect_err("divergent replay must fail the whole batch");
    assert!(matches!(
        err,
        tracera_server::product::ProductPersistenceError::Conflict(_)
    ));

    let first_count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM invalidation_events_v1 WHERE invalidation_id='batch-i1'",
    )
    .fetch_one(&store.pool)
    .await
    .expect("count rolled-back event");
    assert_eq!(
        first_count, 0,
        "earlier batch events must roll back when a later event conflicts"
    );
}

#[tokio::test]
async fn invalidation_batch_exact_replay_is_idempotent() {
    let store = mem_store().await;
    let t = now();
    let events = vec![
        InvalidationEvent {
            invalidation_id: "retry-i1".into(),
            trigger_kind: "dependency_changed".into(),
            trigger_ref: "change:retry".into(),
            target_kind: "criterion".into(),
            target_ref: "c1".into(),
            prior_state: Some("current_valid".into()),
            new_state: "suspect".into(),
            reason: "retry-safe".into(),
            occurred_at: t,
        },
        InvalidationEvent {
            invalidation_id: "retry-i2".into(),
            trigger_kind: "dependency_changed".into(),
            trigger_ref: "change:retry".into(),
            target_kind: "criterion".into(),
            target_ref: "c2".into(),
            prior_state: Some("current_valid".into()),
            new_state: "suspect".into(),
            reason: "retry-safe".into(),
            occurred_at: t,
        },
    ];

    ProductPersistence::append_invalidations(&store, &events)
        .await
        .expect("first batch");
    ProductPersistence::append_invalidations(&store, &events)
        .await
        .expect("exact replay");

    let count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM invalidation_events_v1 WHERE trigger_ref='change:retry'",
    )
    .fetch_one(&store.pool)
    .await
    .expect("count replay rows");
    assert_eq!(
        count, 2,
        "exact retry must not duplicate invalidation history"
    );
}

#[tokio::test]
async fn product_persistence_rejects_cross_product_parent_and_observation_scope() {
    let store = mem_store().await;
    let t = now();

    for product_id in ["scope-a", "scope-b"] {
        ProductPersistence::create_product(
            &store,
            &PersistedProduct {
                product_id: product_id.into(),
                display_name: product_id.into(),
                created_at: t,
            },
        )
        .await
        .expect("create product");
    }

    let b_parent = PersistedBaseline {
        baseline_id: "scope-b-parent".into(),
        product_id: "scope-b".into(),
        revision_number: 1,
        parent_baseline_id: None,
        accepted_at: t,
        metadata: json!({}),
    };
    ProductPersistence::accept_baseline(&store, &b_parent, &[])
        .await
        .expect("accept b parent");

    let a_bad_child = PersistedBaseline {
        baseline_id: "scope-a-child".into(),
        product_id: "scope-a".into(),
        revision_number: 1,
        parent_baseline_id: Some(b_parent.baseline_id.clone()),
        accepted_at: t,
        metadata: json!({}),
    };
    let err = ProductPersistence::accept_baseline(&store, &a_bad_child, &[])
        .await
        .expect_err("cross-product parent must fail");
    assert!(matches!(
        err,
        tracera_server::product::ProductPersistenceError::Invalid(_)
    ));
    assert!(
        ProductPersistence::get_baseline(&store, "scope-a", "scope-a-child")
            .await
            .expect("query child")
            .is_none(),
        "failed parent validation must not persist child baseline"
    );

    let a_baseline = PersistedBaseline {
        baseline_id: "scope-a-b1".into(),
        product_id: "scope-a".into(),
        revision_number: 2,
        parent_baseline_id: None,
        accepted_at: t,
        metadata: json!({}),
    };
    ProductPersistence::accept_baseline(&store, &a_baseline, &[])
        .await
        .expect("accept a baseline");

    let b_entity = PersistedEntity {
        entity_id: "scope-b-entity".into(),
        product_id: "scope-b".into(),
        local_id: "foreign".into(),
        entity_kind: "capability".into(),
        created_at: t,
    };
    ProductPersistence::create_entity(&store, &b_entity)
        .await
        .expect("create b entity");

    let bad_observation = PersistedObservation {
        observation_id: "scope-o-bad".into(),
        product_id: "scope-a".into(),
        baseline_id: a_baseline.baseline_id.clone(),
        subject_entity_id: Some(b_entity.entity_id.clone()),
        subject_local_id: Some(b_entity.local_id.clone()),
        candidate_ref: "git:bad".into(),
        configuration: json!({}),
        result: "passed".into(),
        verifier_id: "suite".into(),
        verifier_version: "1".into(),
        recorded_at: t,
        raw_evidence_ref: None,
        metadata: json!({}),
    };
    let err = ProductPersistence::append_observation(&store, &bad_observation)
        .await
        .expect_err("cross-product subject must fail");
    assert!(matches!(
        err,
        tracera_server::product::ProductPersistenceError::Invalid(_)
    ));

    let leaked: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM product_observations_v1 WHERE observation_id='scope-o-bad'",
    )
    .fetch_one(&store.pool)
    .await
    .expect("count bad observation");
    assert_eq!(leaked, 0, "invalid observation must not be persisted");
}

#[tokio::test]
async fn product_persistence_rejects_entity_for_unknown_product() {
    let store = mem_store().await;
    let err = ProductPersistence::create_entity(
        &store,
        &PersistedEntity {
            entity_id: "orphan-entity".into(),
            product_id: "missing-product".into(),
            local_id: "orphan".into(),
            entity_kind: "capability".into(),
            created_at: now(),
        },
    )
    .await
    .expect_err("canonical port must reject orphan product entities");
    assert!(matches!(
        err,
        tracera_server::product::ProductPersistenceError::Invalid(_)
    ));

    let count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM product_entities_v1 WHERE entity_id='orphan-entity'",
    )
    .fetch_one(&store.pool)
    .await
    .expect("count orphan entity");
    assert_eq!(count, 0);
}

#[tokio::test]
async fn product_v1_schema_supports_scoped_ids_and_immutable_baselines() {
    let store = mem_store().await;
    let pool = &store.pool;

    // Two products may use the same human/local identity.
    for (entity_id, product_id) in [
        ("entity-a-search", "product-a"),
        ("entity-b-search", "product-b"),
    ] {
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
                ('a-b2','product-a',2,'a-b1',?1,'{}')",
    )
    .bind(now().to_rfc3339())
    .execute(pool)
    .await
    .expect("insert baselines");

    sqlx::query(
        "INSERT INTO baseline_entity_membership_v1 (baseline_id, entity_id, entity_revision_id)
         VALUES ('a-b1','entity-a-search','a-search-r1'),
                ('a-b2','entity-a-search','a-search-r2')",
    )
    .execute(pool)
    .await
    .expect("insert baseline membership");

    let b1_title: String = sqlx::query_scalar(
        "SELECT r.title
         FROM baseline_entity_membership_v1 m
         JOIN product_entity_revisions_v1 r ON r.entity_revision_id=m.entity_revision_id
         WHERE m.baseline_id='a-b1' AND m.entity_id='entity-a-search'",
    )
    .fetch_one(pool)
    .await
    .expect("read baseline 1");
    let b2_title: String = sqlx::query_scalar(
        "SELECT r.title
         FROM baseline_entity_membership_v1 m
         JOIN product_entity_revisions_v1 r ON r.entity_revision_id=m.entity_revision_id
         WHERE m.baseline_id='a-b2' AND m.entity_id='entity-a-search'",
    )
    .fetch_one(pool)
    .await
    .expect("read baseline 2");

    assert_eq!(b1_title, "Search v1");
    assert_eq!(b2_title, "Search v2");

    let scoped_count: i64 =
        sqlx::query_scalar("SELECT COUNT(*) FROM product_entities_v1 WHERE local_id='search'")
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
         VALUES ('a-b1','product-a',1,?1,'{}')",
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
                 'test-suite','1',?1,'{}')",
    )
    .bind(now().to_rfc3339())
    .execute(pool)
    .await
    .expect("observation");

    let before: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM product_observations_v1 WHERE observation_id='obs-1'",
    )
    .fetch_one(pool)
    .await
    .unwrap();
    assert_eq!(before, 1);

    // Later invalidation/reuse state must be represented separately; the
    // original observation row remains historically queryable.
    let result: String = sqlx::query_scalar(
        "SELECT result FROM product_observations_v1 WHERE observation_id='obs-1'",
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

    let observation_result: String =
        sqlx::query_scalar("SELECT result FROM product_observations_v1 WHERE observation_id='o1'")
            .fetch_one(pool)
            .await
            .unwrap();
    assert_eq!(observation_result, "passed");

    let new_state:String=sqlx::query_scalar("SELECT new_state FROM invalidation_events_v1 WHERE target_kind='reuse_decision' AND target_ref='r1' ORDER BY occurred_at DESC,invalidation_id DESC LIMIT 1").fetch_one(pool).await.unwrap();
    assert_eq!(new_state, "suspect");

    let reuse_count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM evidence_reuse_decisions_v1 WHERE reuse_decision_id='r1'",
    )
    .fetch_one(pool)
    .await
    .unwrap();
    assert_eq!(reuse_count, 1);
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
        let revision: i64 = sqlx::query_scalar(
            "SELECT revision_number FROM product_baselines_v1 WHERE baseline_id='restart-b1'",
        )
        .fetch_one(pool)
        .await
        .unwrap();
        let result: String = sqlx::query_scalar(
            "SELECT result FROM product_observations_v1 WHERE observation_id='restart-o1'",
        )
        .fetch_one(pool)
        .await
        .unwrap();
        assert_eq!(revision, 1);
        assert_eq!(result, "passed");
    }
    let _ = std::fs::remove_file(path);
}
