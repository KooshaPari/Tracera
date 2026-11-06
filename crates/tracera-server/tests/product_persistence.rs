use chrono::Utc;
use tracera_server::{
    product::{identity::*, observation::*, persistence::*},
    sqlite_store::SqliteStore,
    store::Store,
};

fn batch(product: &str) -> ProductObservationBatch {
    ProductObservationBatch {
        product_id: ProductId::new(product),
        baseline: BaselineRevision(1),
        idempotency_key: "run-1".into(),
        intents: vec![AcceptedIntent {
            id: "storage".into(),
            kind: IntentKind::Capability,
            title: "Storage".into(),
            description: "Survives restart".into(),
            status: IntentStatus::Accepted,
            baseline: BaselineRevision(1),
        }],
        observations: vec![Observation {
            id: "test-1".into(),
            product_id: ProductId::new(product),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Failed,
            source: ObservationSource {
                collector: "cargo-test".into(),
                version: "1".into(),
                causality: None,
                artifact_ref: Some("file:report.xml".into()),
            },
            recorded_at: Utc::now(),
            capability_id: Some("storage".into()),
        }],
    }
}
async fn store(url: &str) -> SqliteStore {
    let pool = tracera_server::db::connect_sqlite(url).await.unwrap();
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .unwrap();
    SqliteStore::new(pool)
}
#[tokio::test]
async fn observations_survive_restart_and_exact_replay() {
    let path =
        std::env::temp_dir().join(format!("tracera-observations-{}.db", uuid::Uuid::new_v4()));
    let url = format!("sqlite:{}?mode=rwc", path.display());
    let first = store(&url).await;
    let input = batch("alpha");
    assert!(
        !first
            .ingest_product_observations(input.clone())
            .await
            .unwrap()
            .replayed
    );
    first.pool.close().await;
    let reopened = store(&url).await;
    assert!(
        reopened
            .ingest_product_observations(input.clone())
            .await
            .unwrap()
            .replayed
    );
    let model = reopened
        .product_observations("alpha".into(), 1)
        .await
        .unwrap()
        .unwrap();
    assert_eq!(model.observations.len(), 1);
    assert_eq!(model.observations[0].source, input.observations[0].source);
    assert!(reopened
        .product_observations("foreign".into(), 1)
        .await
        .unwrap()
        .is_none());
    reopened.pool.close().await;
    std::fs::remove_file(path).unwrap();
}
#[tokio::test]
async fn invalid_batch_and_conflicting_replay_are_atomic() {
    let db = store("sqlite::memory:").await;
    let original = batch("alpha");
    let mut invalid = original.clone();
    invalid
        .observations
        .push(batch("foreign").observations.remove(0));
    assert!(db.ingest_product_observations(invalid).await.is_err());
    assert!(db
        .product_observations("alpha".into(), 1)
        .await
        .unwrap()
        .is_none());
    db.ingest_product_observations(original.clone())
        .await
        .unwrap();
    let mut conflict = original.clone();
    conflict.observations[0].result = ObservationResult::Passed;
    assert!(db.ingest_product_observations(conflict).await.is_err());
    let mut late_conflict = original.clone();
    late_conflict.idempotency_key = "run-2".into();
    let mut new_obs = original.observations[0].clone();
    new_obs.id = "new".into();
    late_conflict.observations.insert(0, new_obs);
    late_conflict.observations[1].result = ObservationResult::Passed;
    assert!(db.ingest_product_observations(late_conflict).await.is_err());
    assert_eq!(
        db.product_observations("alpha".into(), 1)
            .await
            .unwrap()
            .unwrap()
            .observations
            .len(),
        1
    );
    let mut foreign = original;
    foreign.product_id = ProductId::new("beta");
    foreign.observations[0].product_id = ProductId::new("beta");
    db.ingest_product_observations(foreign).await.unwrap();
}

#[tokio::test]
async fn baseline_and_capability_conflicts_preserve_model() {
    let db = store("sqlite::memory:").await;
    let original = batch("alpha");
    db.ingest_product_observations(original.clone())
        .await
        .unwrap();
    let mut changed = original.clone();
    changed.idempotency_key = "changed".into();
    changed.intents[0].description = "changed accepted contract".into();
    assert!(db.ingest_product_observations(changed).await.is_err());
    for status in [IntentStatus::Deferred, IntentStatus::Retired] {
        let mut invalid = batch("beta");
        invalid.intents[0].status = status;
        assert!(db.ingest_product_observations(invalid).await.is_err());
        assert!(db
            .product_observations("beta".into(), 1)
            .await
            .unwrap()
            .is_none());
    }
    let mut unknown = batch("beta");
    unknown.observations[0].capability_id = Some("unknown".into());
    assert!(db.ingest_product_observations(unknown).await.is_err());
    let mut baseline = original.clone();
    baseline.baseline = BaselineRevision(2);
    baseline.intents[0].baseline = BaselineRevision(2);
    baseline.observations[0].baseline = BaselineRevision(2);
    assert!(db.ingest_product_observations(baseline).await.is_err());
    assert!(db
        .product_observations("alpha".into(), 2)
        .await
        .unwrap()
        .is_none());
    assert_eq!(
        db.product_observations("alpha".into(), 1)
            .await
            .unwrap()
            .unwrap()
            .intents,
        original.intents
    );
}
#[tokio::test]
async fn concurrent_exact_replay_is_one_atomic_write() {
    let path = std::env::temp_dir().join(format!("tracera-concurrent-{}.db", uuid::Uuid::new_v4()));
    let url = format!("sqlite:{}?mode=rwc", path.display());
    let db = store(&url).await;
    let input = batch("alpha");
    let (a, b) = tokio::join!(
        db.ingest_product_observations(input.clone()),
        db.ingest_product_observations(input)
    );
    let (a, b) = (a.unwrap(), b.unwrap());
    assert_eq!(a.accepted + b.accepted, 1);
    assert_ne!(a.replayed, b.replayed);
    assert_eq!(
        db.product_observations("alpha".into(), 1)
            .await
            .unwrap()
            .unwrap()
            .observations
            .len(),
        1
    );
    db.pool.close().await;
    std::fs::remove_file(path).unwrap();
}

#[tokio::test]
#[ignore = "requires explicitly isolated TRACERA_Q1_POSTGRES_URL"]
async fn postgres_all_migrations_from_empty_database_ingest_observation() {
    use tracera_server::pg_store::PgStore;
    let url = std::env::var("TRACERA_Q1_POSTGRES_URL").expect("isolated database URL required");
    let pool = tracera_server::db::connect_postgres(&url).await.unwrap();
    let tables: i64 = sqlx::query_scalar(
        "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema')",
    )
    .fetch_one(&pool)
    .await
    .unwrap();
    assert_eq!(
        tables, 0,
        "migration proof requires an empty isolated database"
    );
    let migrations = sqlx::migrate!("./migrations-postgres");
    migrations.run(&pool).await.unwrap();
    let applied: i64 = sqlx::query_scalar("SELECT count(*) FROM _sqlx_migrations WHERE success")
        .fetch_one(&pool)
        .await
        .unwrap();
    assert_eq!(applied as usize, migrations.iter().count());
    let db = PgStore::new(pool);
    let input = batch("fresh-migrations");
    let receipt = db.ingest_product_observations(input.clone()).await.unwrap();
    assert_eq!(receipt.accepted, 1);
    let model = db
        .product_observations("fresh-migrations".into(), 1)
        .await
        .unwrap()
        .unwrap();
    assert_eq!(model.observations.len(), 1);
    assert_eq!(model.observations[0].id, input.observations[0].id);
    db.pool.close().await;
}

#[tokio::test]
#[ignore = "requires explicitly isolated TRACERA_Q1_POSTGRES_URL"]
async fn postgres_atomic_replay_and_restart() {
    use tracera_server::pg_store::PgStore;
    let url = std::env::var("TRACERA_Q1_POSTGRES_URL").expect("isolated database URL required");
    let pool = tracera_server::db::connect_postgres(&url).await.unwrap();
    sqlx::migrate!("./migrations-postgres")
        .run(&pool)
        .await
        .unwrap();
    let db = PgStore::new(pool);
    let input = batch(&format!("pg-{}", uuid::Uuid::new_v4()));
    let product = input.product_id.as_str().to_owned();
    let (a, b) = tokio::join!(
        db.ingest_product_observations(input.clone()),
        db.ingest_product_observations(input.clone())
    );
    let (a, b) = (a.unwrap(), b.unwrap());
    assert_eq!(a.accepted + b.accepted, 1);
    assert_ne!(a.replayed, b.replayed);
    let mut conflict = input.clone();
    conflict.idempotency_key = "second".into();
    let mut new = input.observations[0].clone();
    new.id = "new".into();
    conflict.observations.insert(0, new);
    conflict.observations[1].result = ObservationResult::Passed;
    assert!(db.ingest_product_observations(conflict).await.is_err());
    db.pool.close().await;
    let reopened = PgStore::new(tracera_server::db::connect_postgres(&url).await.unwrap());
    let model = reopened
        .product_observations(product, 1)
        .await
        .unwrap()
        .unwrap();
    assert_eq!(model.observations.len(), 1);
    assert_eq!(model.observations[0].result, ObservationResult::Failed);
    assert!(
        reopened
            .ingest_product_observations(input)
            .await
            .unwrap()
            .replayed
    );
    assert!(reopened
        .product_observations("foreign".into(), 1)
        .await
        .unwrap()
        .is_none());
    let first = batch(&format!("pg-race-{}", uuid::Uuid::new_v4()));
    let mut second = first.clone();
    second.baseline = BaselineRevision(2);
    second.intents[0].baseline = BaselineRevision(2);
    second.observations[0].baseline = BaselineRevision(2);
    let (a, b) = tokio::join!(
        reopened.ingest_product_observations(first),
        reopened.ingest_product_observations(second)
    );
    assert!(matches!(
        (a, b),
        (Ok(_), Err(tracera_server::store::StoreError::Conflict(_)))
            | (Err(tracera_server::store::StoreError::Conflict(_)), Ok(_))
    ));
    reopened.pool.close().await;
}

#[tokio::test]
async fn canonical_intent_order_and_observation_limit() {
    let db = store("sqlite::memory:").await;
    let mut input = batch("alpha");
    let mut other = input.intents[0].clone();
    other.id = "another".into();
    input.intents.push(other);
    db.ingest_product_observations(input.clone()).await.unwrap();
    input.intents.reverse();
    assert!(
        db.ingest_product_observations(input.clone())
            .await
            .unwrap()
            .replayed
    );
    for run in 0..10 {
        let mut chunk = input.clone();
        chunk.idempotency_key = format!("chunk-{run}");
        chunk.observations = (0..500)
            .map(|n| {
                let mut observation = input.observations[0].clone();
                observation.id = format!("obs-{run}-{n}");
                observation
            })
            .collect();
        if run < 9 {
            db.ingest_product_observations(chunk).await.unwrap();
        } else {
            assert!(db.ingest_product_observations(chunk).await.is_err());
            assert_eq!(
                db.product_observations("alpha".into(), 1)
                    .await
                    .unwrap()
                    .unwrap()
                    .observations
                    .len(),
                4501
            );
        }
    }
}

#[tokio::test]
async fn q1_source_without_causality_preserves_serialization_and_replay() {
    let db = store("sqlite::memory:").await;
    let old_payload = serde_json::json!({"collector":"cargo-test","version":"1","artifact_ref":"file:report.xml"});
    let source: ObservationSource = serde_json::from_value(old_payload.clone()).unwrap();
    assert!(source.causality.is_none());
    assert_eq!(serde_json::to_value(&source).unwrap(), old_payload);
    let mut input = batch("legacy");
    input.observations[0].source = source;
    db.ingest_product_observations(input.clone()).await.unwrap();
    assert!(
        db.ingest_product_observations(input)
            .await
            .unwrap()
            .replayed
    );
}

#[tokio::test]
async fn actual_q1_stored_payload_replays_without_causality_rewrite() {
    let db = store("sqlite::memory:").await;
    let rows: serde_json::Value =
        serde_json::from_str(include_str!("../testdata/q1-legacy-observation-rows.json")).unwrap();
    let input: ProductObservationBatch =
        serde_json::from_str(rows["batch"].as_str().unwrap()).unwrap();
    let product = input.product_id.as_str();
    sqlx::query(
        "INSERT INTO product_observation_baselines(product_id,baseline,intents) VALUES(?,?,?)",
    )
    .bind(product)
    .bind(1i64)
    .bind(rows["intents"].as_str().unwrap())
    .execute(&db.pool)
    .await
    .unwrap();
    sqlx::query("INSERT INTO product_observations(product_id,observation_id,baseline,capability_id,payload) VALUES(?,?,?,?,?)").bind(product).bind(&input.observations[0].id).bind(1i64).bind(&input.observations[0].capability_id).bind(rows["observation"].as_str().unwrap()).execute(&db.pool).await.unwrap();
    sqlx::query("INSERT INTO product_observation_batches(product_id,baseline,batch_key,payload) VALUES(?,?,?,?)").bind(product).bind(1i64).bind(&input.idempotency_key).bind(rows["batch"].as_str().unwrap()).execute(&db.pool).await.unwrap();
    assert!(
        db.ingest_product_observations(input)
            .await
            .unwrap()
            .replayed
    );
}
