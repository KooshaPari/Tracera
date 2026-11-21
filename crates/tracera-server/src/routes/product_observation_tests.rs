use super::*;
use axum::body::{to_bytes, Body};
use std::{sync::Arc, time::Instant};
use tower::ServiceExt;
static PRODUCT_ENV: tokio::sync::Mutex<()> = tokio::sync::Mutex::const_new(());
struct AllowlistGuard {
    previous: Option<std::ffi::OsString>,
    _lock: tokio::sync::MutexGuard<'static, ()>,
}
impl Drop for AllowlistGuard {
    fn drop(&mut self) {
        match self.previous.take() {
            Some(value) => std::env::set_var("TRACERA_PRODUCT_IDS", value),
            None => std::env::remove_var("TRACERA_PRODUCT_IDS"),
        }
    }
}
async fn fixture() -> (
    Router,
    Arc<crate::sqlite_store::SqliteStore>,
    AllowlistGuard,
) {
    fixture_auth(None).await
}
async fn fixture_auth(
    auth: crate::auth::AuthToken,
) -> (
    Router,
    Arc<crate::sqlite_store::SqliteStore>,
    AllowlistGuard,
) {
    let lock = PRODUCT_ENV.lock().await;
    let guard = AllowlistGuard {
        previous: std::env::var_os("TRACERA_PRODUCT_IDS"),
        _lock: lock,
    };
    std::env::set_var("TRACERA_PRODUCT_IDS", " alpha, other ");
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
        frontend: crate::FrontendState::Ok,
        frontend_dist: std::path::PathBuf::new(),
    };
    (
        crate::router::build_router_with_auth(state, auth),
        store,
        guard,
    )
}
fn payload() -> Value {
    json!({"product_id":"alpha","baseline":1,"idempotency_key":"run-1", "intents":[{"id":"storage","kind":"Capability","title":"Storage","description":"durability","status":"Accepted","baseline":1}],"observations":[{"id":"obs-1","product_id":"alpha","baseline":1,"kind":"TestResult","result":"Failed","source":{"collector":"cargo-test","version":"1","artifact_ref":"file:report.xml"},"recorded_at":"2026-10-16T00:00:00Z","capability_id":"storage"}]})
}
async fn call(app: Router, method: &str, uri: &str, body: Value) -> (StatusCode, Value) {
    request(app, method, uri, body, true).await
}
async fn request(
    app: Router,
    method: &str,
    uri: &str,
    body: Value,
    authenticated: bool,
) -> (StatusCode, Value) {
    let token = crate::middleware::issue_csrf_token().await;
    let response = app
        .oneshot(
            axum::http::Request::builder()
                .method(method)
                .uri(uri)
                .header(
                    "authorization",
                    if authenticated {
                        "Bearer test-only-token"
                    } else {
                        "Bearer invalid"
                    },
                )
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
// ---------------------------------------------------------------------------
// `/findings` assessment wiring (slice 2.4)
// ---------------------------------------------------------------------------

const OBSERVATIONS_URI: &str = "/api/v1/products/alpha/baselines/1/observations";
const FINDINGS_URI: &str = "/api/v1/products/alpha/baselines/1/findings";

/// RFC 3339 timestamp that is inside the 24h freshness window.
fn fresh_at() -> String {
    chrono::Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Secs, true)
}

fn capability(id: &str) -> Value {
    json!({
        "id": id,
        "kind": "Capability",
        "title": id,
        "description": "",
        "status": "Accepted",
        "baseline": 1,
    })
}

fn observation(id: &str, capability_id: &str, result: &str, recorded_at: &str) -> Value {
    json!({
        "id": id,
        "product_id": "alpha",
        "baseline": 1,
        "kind": "TestResult",
        "result": result,
        "source": {"collector": "cargo-test", "version": "1", "artifact_ref": null},
        "recorded_at": recorded_at,
        "capability_id": capability_id,
    })
}

async fn post_batch(app: &Router, batch: Value) {
    let (status, body) = call(app.clone(), "POST", OBSERVATIONS_URI, batch).await;
    assert_eq!(status, StatusCode::OK, "ingest rejected: {body}");
}

async fn get_findings(app: &Router) -> Value {
    let (status, body) = call(app.clone(), "GET", FINDINGS_URI, Value::Null).await;
    assert_eq!(status, StatusCode::OK, "findings failed: {body}");
    body
}

fn assessment_finding<'a>(body: &'a Value, capability_id: &str) -> &'a Value {
    body["assessment"]["findings"]
        .as_array()
        .expect("assessment.findings must be an array")
        .iter()
        .find(|finding| finding["capability_id"] == json!(capability_id))
        .unwrap_or_else(|| panic!("no assessment finding for '{capability_id}'"))
}

fn explanation(finding: &Value) -> &str {
    finding["explanation"]
        .as_str()
        .expect("explanation must be a string")
}

#[tokio::test]
async fn mounted_ingest_read_detect_and_foreign_scope() {
    let (app, _, _guard) = fixture().await;
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
        StatusCode::FORBIDDEN
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
    let (app, store, _guard) = fixture().await;
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
    let (app, _, _guard) = fixture().await;
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
    let (app, _, _guard) = fixture_auth(Some(Arc::from("test-only-token"))).await;
    let uri = "/api/v1/products/alpha/baselines/1/observations";
    for method in ["GET", "POST"] {
        assert_eq!(
            request(app.clone(), method, uri, payload(), false).await.0,
            StatusCode::UNAUTHORIZED
        );
    }
    assert_eq!(
        request(
            app.clone(),
            "POST",
            "/api/v1/products/alpha/baselines/1/benchmark-observations",
            payload(),
            false
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
    let (app, _, _guard) = fixture().await;
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
            "/api/v1/products/other/baselines/1/benchmark-observations",
            input
        )
        .await
        .0,
        StatusCode::UNPROCESSABLE_ENTITY
    );
}

#[tokio::test]
async fn product_allowlist_denies_every_foreign_route_with_valid_bearer() {
    let (app, _, _guard) = fixture_auth(Some(Arc::from("test-only-token"))).await;
    assert_eq!(
        call(
            app.clone(),
            "POST",
            "/api/v1/products/alpha/baselines/1/observations",
            payload()
        )
        .await
        .0,
        StatusCode::OK
    );
    assert_eq!(
        call(
            app.clone(),
            "GET",
            "/api/v1/products/alpha/baselines/1/observations",
            Value::Null
        )
        .await
        .0,
        StatusCode::OK
    );
    for (method, endpoint) in [
        ("GET", "observations"),
        ("POST", "observations"),
        ("GET", "findings"),
        ("POST", "benchmark-observations"),
    ] {
        let (status, body) = call(
            app.clone(),
            method,
            &format!("/api/v1/products/beta/baselines/1/{endpoint}"),
            json!({}),
        )
        .await;
        assert_eq!(status, StatusCode::FORBIDDEN, "{method} {endpoint}");
        assert_eq!(body, json!({"error":"product_access_denied"}));
    }
}
#[tokio::test]
async fn unset_and_empty_product_allowlist_deny_every_route() {
    let (app, _, _guard) = fixture_auth(Some(Arc::from("test-only-token"))).await;
    for allowlist in [None, Some(""), Some(" , ")] {
        match allowlist {
            None => std::env::remove_var("TRACERA_PRODUCT_IDS"),
            Some(value) => std::env::set_var("TRACERA_PRODUCT_IDS", value),
        }
        for (method, endpoint) in [
            ("GET", "observations"),
            ("POST", "observations"),
            ("GET", "findings"),
            ("POST", "benchmark-observations"),
        ] {
            let (status, body) = call(
                app.clone(),
                method,
                &format!("/api/v1/products/alpha/baselines/1/{endpoint}"),
                json!({}),
            )
            .await;
            assert_eq!(
                status,
                StatusCode::FORBIDDEN,
                "{allowlist:?} {method} {endpoint}"
            );
            assert_eq!(body, json!({"error":"product_access_denied"}));
        }
    }
}

// ---------------------------------------------------------------------------
// Assessment wiring: every status must be reachable and explained.
// ---------------------------------------------------------------------------

#[tokio::test]
async fn findings_explain_fresh_failure_as_violation() {
    let (app, _, _guard) = fixture().await;
    post_batch(
        &app,
        json!({
            "product_id": "alpha",
            "baseline": 1,
            "idempotency_key": "fresh-failure",
            "intents": [capability("storage")],
            "observations": [observation("obs-1", "storage", "Failed", &fresh_at())],
        }),
    )
    .await;

    let body = get_findings(&app).await;
    assert_eq!(body["status"], "Violated");
    // Detector report keeps its previous shape at the top level.
    assert_eq!(body["products_scanned"], 1);
    assert!(body["findings"].is_array());

    let storage = assessment_finding(&body, "storage");
    assert_eq!(storage["status"], "Violated");
    assert_eq!(storage["severity"], "High");
    assert_eq!(storage["observation_ids"], json!(["obs-1"]));
    assert!(
        explanation(storage).contains("failed observations"),
        "{}",
        explanation(storage)
    );
    assert!(explanation(storage).contains("obs-1"));
}

#[tokio::test]
async fn findings_distinguish_contradiction_from_missing_evidence() {
    let (app, _, _guard) = fixture().await;
    post_batch(
        &app,
        json!({
            "product_id": "alpha",
            "baseline": 1,
            "idempotency_key": "contradiction",
            "intents": [capability("storage"), capability("cache")],
            "observations": [
                observation("obs-pass", "storage", "Passed", &fresh_at()),
                observation("obs-fail", "storage", "Failed", &fresh_at()),
            ],
        }),
    )
    .await;

    let body = get_findings(&app).await;
    assert_eq!(body["status"], "Inconclusive");

    let storage = assessment_finding(&body, "storage");
    assert_eq!(storage["status"], "Inconclusive");
    assert!(
        explanation(storage).contains("conflicting"),
        "{}",
        explanation(storage)
    );

    let cache = assessment_finding(&body, "cache");
    assert_eq!(cache["status"], "Unknown");
    assert!(
        explanation(cache).contains("No observations found"),
        "{}",
        explanation(cache)
    );
    assert_eq!(cache["observation_ids"], json!([]));
    // The contradiction detector still reports the same conflict.
    assert!(body["findings"]
        .as_array()
        .expect("findings must be an array")
        .iter()
        .any(|finding| finding["kind"] == "Contradiction"));
}

#[tokio::test]
async fn findings_distinguish_stale_from_missing_and_satisfied() {
    let (app, _, _guard) = fixture().await;
    post_batch(
        &app,
        json!({
            "product_id": "alpha",
            "baseline": 1,
            "idempotency_key": "stale-evidence",
            "intents": [
                capability("storage"),
                capability("cache"),
                capability("search"),
            ],
            "observations": [
                observation("obs-old", "storage", "Passed", "2026-01-01T00:00:00Z"),
                observation("obs-new", "search", "Passed", &fresh_at()),
            ],
        }),
    )
    .await;

    let body = get_findings(&app).await;
    let storage = assessment_finding(&body, "storage");
    assert_eq!(storage["status"], "Stale");
    assert!(
        explanation(storage).contains("older than the freshness threshold"),
        "{}",
        explanation(storage)
    );
    assert_eq!(assessment_finding(&body, "cache")["status"], "Unknown");
    assert_eq!(assessment_finding(&body, "search")["status"], "Satisfied");
    // Worst status wins for the product verdict.
    assert_eq!(body["status"], "Stale");
}

#[tokio::test]
async fn findings_report_satisfied_when_all_evidence_passes() {
    let (app, _, _guard) = fixture().await;
    post_batch(
        &app,
        json!({
            "product_id": "alpha",
            "baseline": 1,
            "idempotency_key": "satisfied",
            "intents": [capability("storage")],
            "observations": [observation("obs-1", "storage", "Passed", &fresh_at())],
        }),
    )
    .await;

    let body = get_findings(&app).await;
    assert_eq!(body["status"], "Satisfied");
    let storage = assessment_finding(&body, "storage");
    assert_eq!(storage["status"], "Satisfied");
    assert_eq!(storage["severity"], "Info");
    assert!(
        explanation(storage).contains("passing observation"),
        "{}",
        explanation(storage)
    );
}

#[tokio::test]
async fn findings_report_unknown_result_separately_from_missing_evidence() {
    let (app, _, _guard) = fixture().await;
    post_batch(
        &app,
        json!({
            "product_id": "alpha",
            "baseline": 1,
            "idempotency_key": "unknown-result",
            "intents": [capability("storage"), capability("cache")],
            "observations": [observation("obs-1", "storage", "Unknown", &fresh_at())],
        }),
    )
    .await;

    let body = get_findings(&app).await;
    assert_eq!(body["status"], "Unknown");

    let storage = assessment_finding(&body, "storage");
    assert_eq!(storage["status"], "Unknown");
    assert!(
        explanation(storage).contains("incomplete evidence"),
        "{}",
        explanation(storage)
    );
    assert_eq!(storage["observation_ids"], json!(["obs-1"]));

    let cache = assessment_finding(&body, "cache");
    assert_eq!(cache["status"], "Unknown");
    assert!(
        explanation(cache).contains("No observations found"),
        "{}",
        explanation(cache)
    );
    assert_ne!(explanation(storage), explanation(cache));
}
