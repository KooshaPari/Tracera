use super::*;
use axum::body::{to_bytes, Body};
use std::{sync::Arc, time::Instant};
use tower::ServiceExt;
async fn fixture() -> (Router, Arc<crate::sqlite_store::SqliteStore>) {
    fixture_auth(None).await
}
async fn fixture_auth(
    auth: crate::auth::AuthToken,
) -> (Router, Arc<crate::sqlite_store::SqliteStore>) {
    let pool = crate::db::connect_sqlite("sqlite::memory:").await.unwrap();
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .unwrap();
    let store = Arc::new(crate::sqlite_store::SqliteStore::new(pool));
    let state = AppState {
        store: store.clone(),
        version: "test".into(),
        backend: "sqlite",
        started_at: Instant::now(),
        workos_client: tracera_workos::WorkOSClient::default_for_router(),
        cache: None,
        neo4j: None,
        r2: None,
    };
    (crate::router::build_router_with_auth(state, auth), store)
}
fn payload() -> Value {
    json!({"product_id":"alpha","baseline":1,"idempotency_key":"run-1", "intents":[{"id":"storage","kind":"Capability","title":"Storage","description":"durability","status":"Accepted","baseline":1}],"observations":[{"id":"obs-1","product_id":"alpha","baseline":1,"kind":"TestResult","result":"Failed","source":{"collector":"cargo-test","version":"1","artifact_ref":"file:report.xml"},"recorded_at":"2026-10-16T00:00:00Z","capability_id":"storage"}]})
}
async fn call(app: Router, method: &str, uri: &str, body: Value) -> (StatusCode, Value) {
    let token = crate::middleware::issue_csrf_token().await;
    let response = app
        .oneshot(
            axum::http::Request::builder()
                .method(method)
                .uri(uri)
                .header("content-type", "application/json")
                .header("origin", "http://127.0.0.1:18000")
                .header("x-csrf-token", token)
                .body(Body::from(body.to_string()))
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let bytes = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    (
        status,
        serde_json::from_slice(&bytes).unwrap_or(Value::Null),
    )
}
#[tokio::test]
async fn mounted_ingest_read_detect_and_foreign_scope() {
    let (app, _) = fixture().await;
    let uri = "/api/v1/products/alpha/baselines/1/observations";
    let (status, receipt) = call(app.clone(), "POST", uri, payload()).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(receipt["accepted"], 1);
    let (status, model) = call(app.clone(), "GET", uri, Value::Null).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(model["observations"][0]["capability_id"], "storage");
    let (status, finding) = call(
        app.clone(),
        "GET",
        "/api/v1/products/alpha/baselines/1/findings",
        Value::Null,
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(finding["products_scanned"], 1);
    assert_eq!(finding["findings"][0]["product_id"], "alpha");
    assert_eq!(
        call(
            app.clone(),
            "GET",
            "/api/v1/products/beta/baselines/1/observations",
            Value::Null
        )
        .await
        .0,
        StatusCode::NOT_FOUND
    );
    assert!(call(
        app,
        "POST",
        "/api/v1/products/beta/baselines/1/observations",
        payload()
    )
    .await
    .0
    .is_client_error());
}
#[tokio::test]
async fn unavailable_database_fails_closed() {
    let (app, store) = fixture().await;
    store.pool.close().await;
    assert!(call(
        app,
        "GET",
        "/api/v1/products/alpha/baselines/1/observations",
        Value::Null
    )
    .await
    .0
    .is_server_error());
}

#[tokio::test]
async fn immutable_replay_conflict_is_409_and_invalid_is_422() {
    let (app, _) = fixture().await;
    let uri = "/api/v1/products/alpha/baselines/1/observations";
    assert_eq!(
        call(app.clone(), "POST", uri, payload()).await.0,
        StatusCode::OK
    );
    let mut conflicting = payload();
    conflicting["observations"][0]["result"] = json!("Passed");
    assert_eq!(
        call(app.clone(), "POST", uri, conflicting).await.0,
        StatusCode::CONFLICT
    );
    let mut invalid = payload();
    invalid["observations"][0]["capability_id"] = json!("foreign");
    assert_eq!(
        call(app, "POST", uri, invalid).await.0,
        StatusCode::UNPROCESSABLE_ENTITY
    );
}
#[tokio::test]
async fn mounted_routes_retain_authentication_and_body_limit() {
    let (app, _) = fixture_auth(Some(Arc::from("test-only-token"))).await;
    let uri = "/api/v1/products/alpha/baselines/1/observations";
    for method in ["GET", "POST"] {
        assert_eq!(
            call(app.clone(), method, uri, payload()).await.0,
            StatusCode::UNAUTHORIZED
        );
    }
    assert_eq!(
        call(
            app.clone(),
            "POST",
            "/api/v1/products/alpha/baselines/1/benchmark-observations",
            payload()
        )
        .await
        .0,
        StatusCode::UNAUTHORIZED
    );
    let response = app
        .clone()
        .oneshot(
            axum::http::Request::builder()
                .uri(uri)
                .header("authorization", "Bearer test-only-token")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::NOT_FOUND);
    let token = crate::middleware::issue_csrf_token().await;
    let response = app
        .oneshot(
            axum::http::Request::builder()
                .method("POST")
                .uri(uri)
                .header("authorization", "Bearer test-only-token")
                .header("origin", "http://127.0.0.1:18000")
                .header("x-csrf-token", token)
                .header("content-type", "application/json")
                .body(Body::from(" ".repeat(10 * 1024 * 1024 + 1)))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::PAYLOAD_TOO_LARGE);
}

#[tokio::test]
async fn benchmark_adapter_mounts_preserves_causality_and_rejects_conflicts() {
    let (app, _) = fixture().await;
    let envelope: Value =
        serde_json::from_str(include_str!("../../testdata/helios-benchmark-run.json")).unwrap();
    let source = payload();
    let input = json!({"product_id":"alpha","baseline":1,"capability_id":"storage","intents":source["intents"],"recorded_at":"2026-10-16T00:00:00Z","envelope":envelope});
    let uri = "/api/v1/products/alpha/baselines/1/benchmark-observations";
    assert_eq!(
        call(app.clone(), "POST", uri, input.clone()).await.0,
        StatusCode::OK
    );
    assert_eq!(
        call(app.clone(), "POST", uri, input.clone()).await.1["replayed"],
        true
    );
    // Exercise alternate wire object order, not a pre-normalized Value payload.
    fn reversed(value: &Value) -> String {
        match value {
            Value::Object(fields) => format!(
                "{{{}}}",
                fields
                    .iter()
                    .rev()
                    .map(|(key, value)| format!(
                        "{}:{}",
                        serde_json::to_string(key).unwrap(),
                        reversed(value)
                    ))
                    .collect::<Vec<_>>()
                    .join(",")
            ),
            Value::Array(values) => format!(
                "[{}]",
                values.iter().map(reversed).collect::<Vec<_>>().join(",")
            ),
            _ => value.to_string(),
        }
    }
    let token = crate::middleware::issue_csrf_token().await;
    let reordered = app
        .clone()
        .oneshot(
            axum::http::Request::builder()
                .method("POST")
                .uri(uri)
                .header("content-type", "application/json")
                .header("origin", "http://127.0.0.1:18000")
                .header("x-csrf-token", token)
                .body(Body::from(reversed(&input)))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(reordered.status(), StatusCode::OK);
    let reordered: Value =
        serde_json::from_slice(&to_bytes(reordered.into_body(), 4096).await.unwrap()).unwrap();
    assert_eq!(reordered["replayed"], true);
    let model = call(
        app.clone(),
        "GET",
        "/api/v1/products/alpha/baselines/1/observations",
        Value::Null,
    )
    .await
    .1;
    assert_eq!(
        model["observations"][0]["source"]["causality"]["session_id"],
        input["envelope"]["session_id"]
    );
    assert_eq!(
        model["observations"][0]["source"]["causality"]["replay_hash"],
        input["envelope"]["result"]["replay_hash"]
    );
    let mut changed_provenance = input.clone();
    changed_provenance["envelope"]["subject"] = json!({"repo":"changed-source"});
    assert_eq!(
        call(app.clone(), "POST", uri, changed_provenance).await.0,
        StatusCode::CONFLICT
    );
    let mut conflict = input.clone();
    conflict["envelope"]["result"]["status"] = json!("failed");
    assert_eq!(
        call(app.clone(), "POST", uri, conflict).await.0,
        StatusCode::CONFLICT
    );
    for (field, value) in [
        ("schema_version", json!("2.0.0")),
        ("tenant_id", json!("bad tenant")),
    ] {
        let mut invalid = input.clone();
        invalid["envelope"][field] = value;
        assert_eq!(
            call(app.clone(), "POST", uri, invalid).await.0,
            StatusCode::UNPROCESSABLE_ENTITY
        );
    }
    let mut invalid_capability = input.clone();
    invalid_capability["capability_id"] = json!("missing");
    assert_eq!(
        call(app.clone(), "POST", uri, invalid_capability).await.0,
        StatusCode::UNPROCESSABLE_ENTITY
    );
    let mut future = input.clone();
    future["recorded_at"] = json!("2999-01-01T00:00:00Z");
    assert_eq!(
        call(app.clone(), "POST", uri, future).await.0,
        StatusCode::UNPROCESSABLE_ENTITY
    );
    let mut invalid = input.clone();
    invalid["envelope"]["session_id"] = json!("invalid");
    assert_eq!(
        call(app.clone(), "POST", uri, invalid).await.0,
        StatusCode::UNPROCESSABLE_ENTITY
    );
    assert_eq!(
        call(
            app,
            "POST",
            "/api/v1/products/beta/baselines/1/benchmark-observations",
            input
        )
        .await
        .0,
        StatusCode::UNPROCESSABLE_ENTITY
    );
}
