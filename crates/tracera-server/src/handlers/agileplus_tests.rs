//! Contract tests for SPEC-009 AgilePlus ingestion (issue #1164).
//!
//! Every test that depends on the ingest token holds `ENV_LOCK`, because the
//! token is process-wide configuration and these tests mutate it.

// The guard is deliberately held across awaits: it serialises process-wide env
// mutation, so releasing it early would reintroduce the race it exists to stop.
#![allow(clippy::await_holding_lock)]

use super::*;
use crate::sqlite_store::SqliteStore;
use crate::store::Store;
use axum::body::{to_bytes, Body};
use axum::Router;
use serde_json::json;
use std::sync::{Arc, Mutex};
use std::time::Instant;
use tower::ServiceExt;

static ENV_LOCK: Mutex<()> = Mutex::new(());
const TEST_TOKEN: &str = "test-agileplus-token";

fn with_token() -> std::sync::MutexGuard<'static, ()> {
    let guard = ENV_LOCK
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner());
    std::env::set_var(AGILEPLUS_TOKEN_ENV, TEST_TOKEN);
    guard
}

async fn fixture() -> (Router, Arc<SqliteStore>) {
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .unwrap();
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .unwrap();
    let store = Arc::new(SqliteStore::new(pool));
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
    (crate::router::build_router(state), store)
}

struct Reply {
    status: StatusCode,
    location: Option<String>,
    body: Value,
}

async fn post(app: Router, path: &str, headers: &[(&str, String)], body: Value) -> Reply {
    let token = crate::middleware::issue_csrf_token().await;
    let mut builder = http::Request::builder()
        .method("POST")
        .uri(path)
        .header("origin", "http://127.0.0.1:18000")
        .header("x-csrf-token", token)
        .header("content-type", "application/json");
    for (name, value) in headers {
        builder = builder.header(*name, value.clone());
    }
    let response = app
        .oneshot(builder.body(Body::from(body.to_string())).unwrap())
        .await
        .unwrap();
    let status = response.status();
    let location = response
        .headers()
        .get(http::header::LOCATION)
        .and_then(|value| value.to_str().ok())
        .map(str::to_string);
    let bytes = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    Reply {
        status,
        location,
        body: serde_json::from_slice(&bytes).unwrap_or(Value::Null),
    }
}

fn auth_headers(key: &str) -> Vec<(&'static str, String)> {
    vec![
        (AGILEPLUS_TOKEN_HEADER, TEST_TOKEN.to_string()),
        (IDEMPOTENCY_HEADER, key.to_string()),
    ]
}

async fn send(app: Router, body: Value) -> Reply {
    let key = uuid::Uuid::new_v4().to_string();
    post(app, "/api/v1/ingest/agileplus", &auth_headers(&key), body).await
}

fn envelope(source: &str, entities: Vec<Value>, trace_links: Vec<Value>) -> Value {
    json!({
        "source": source,
        "version": "2026-08-30",
        "entities": entities,
        "trace_links": trace_links,
    })
}

fn entity(entity_type: &str, id: &str, status: &str, revision: i64) -> Value {
    json!({
        "type": entity_type,
        "agileplus_id": id,
        "title": format!("{entity_type} {id}"),
        "body": {"sections": []},
        "metadata": {
            "version": revision,
            "status": status,
            "author": "governance-bot",
            "decided_at": "2026-08-30T14:30:00Z",
            "created_at": "2026-08-30T10:00:00Z",
            "updated_at": "2026-08-30T14:30:00Z",
        },
    })
}

fn full_envelope(revision: i64) -> Value {
    envelope(
        "agileplus",
        vec![
            entity("spec", "AP-SPEC-0042", "approved", revision),
            entity("work_item", "AP-WI-1087", "done", revision),
            entity("governance_decision", "AP-GOV-0007", "approved", revision),
            entity("research_doc", "AP-RD-0011", "published", revision),
        ],
        vec![
            json!({"source_id": "AP-SPEC-0042", "target_id": "AP-WI-1087", "relation": "specifies", "confidence": 1.0}),
            json!({"source_id": "AP-SPEC-0042", "target_id": "AP-ABSENT-1", "relation": "specifies"}),
        ],
    )
}

#[tokio::test]
async fn agcord_and_agileplus_paths_are_distinct() {
    let (app, store) = fixture().await;
    let _guard = with_token();

    // AgCord items on the explicit path still ingest exactly as before.
    let agcord = post(
        app.clone(),
        "/ingest/agcord",
        &[],
        json!({"items": [{"id": "a-1", "name": "Agent One", "status": "active"}]}),
    )
    .await;
    assert_eq!(agcord.status, StatusCode::OK, "{:?}", agcord.body);
    assert_eq!(agcord.body["requirements_created"], 1);

    // The legacy path is a redirect, not an ingestion success.
    let legacy = post(
        app.clone(),
        "/ingest/agileplus",
        &[],
        json!({"items": [{"id": "a-2", "name": "Agent Two"}]}),
    )
    .await;
    assert_eq!(legacy.status, StatusCode::PERMANENT_REDIRECT);
    assert_eq!(legacy.location.as_deref(), Some("/ingest/agcord"));
    assert_eq!(legacy.body["error"], "agcord_ingest_moved");
    assert_eq!(store.list_stories().await.unwrap().len(), 1);

    // A governance envelope on the legacy path is refused, never reinterpreted.
    let wrong_path = post(app.clone(), "/ingest/agileplus", &[], full_envelope(1)).await;
    assert_eq!(wrong_path.status, StatusCode::BAD_REQUEST);
    assert_eq!(wrong_path.body["error"], "agileplus_wrong_path");
    assert_eq!(store.list_stories().await.unwrap().len(), 1);

    // The SPEC-009 path accepts only the governance envelope.
    let accepted = post(
        app,
        "/api/v1/ingest/agileplus",
        &auth_headers(&uuid::Uuid::new_v4().to_string()),
        full_envelope(1),
    )
    .await;
    assert_eq!(accepted.status, StatusCode::OK, "{:?}", accepted.body);
    assert_eq!(accepted.body["status"], "accepted");
}

#[tokio::test]
async fn unauthenticated_requests_fail_closed() {
    let (app, store) = fixture().await;
    let _guard = with_token();

    let missing = post(
        app.clone(),
        "/api/v1/ingest/agileplus",
        &[],
        full_envelope(1),
    )
    .await;
    assert_eq!(missing.status, StatusCode::UNAUTHORIZED);
    assert_eq!(missing.body["error"], "agileplus_unauthorized");

    let wrong = post(
        app.clone(),
        "/api/v1/ingest/agileplus",
        &[
            (AGILEPLUS_TOKEN_HEADER, "not-the-token".to_string()),
            (IDEMPOTENCY_HEADER, uuid::Uuid::new_v4().to_string()),
        ],
        full_envelope(1),
    )
    .await;
    assert_eq!(wrong.status, StatusCode::UNAUTHORIZED);
    assert_eq!(store.list_stories().await.unwrap().len(), 0);

    // Without server-side configuration the endpoint refuses to ingest at all.
    std::env::remove_var(AGILEPLUS_TOKEN_ENV);
    let unconfigured = post(app, "/api/v1/ingest/agileplus", &[], full_envelope(1)).await;
    assert_eq!(unconfigured.status, StatusCode::SERVICE_UNAVAILABLE);
    assert_eq!(
        unconfigured.body["error"],
        "agileplus_ingest_not_configured"
    );
    std::env::set_var(AGILEPLUS_TOKEN_ENV, TEST_TOKEN);
}

#[tokio::test]
async fn missing_or_non_v4_idempotency_key_is_rejected() {
    let (app, store) = fixture().await;
    let _guard = with_token();

    let missing = post(
        app.clone(),
        "/api/v1/ingest/agileplus",
        &[(AGILEPLUS_TOKEN_HEADER, TEST_TOKEN.to_string())],
        full_envelope(1),
    )
    .await;
    assert_eq!(missing.status, StatusCode::BAD_REQUEST);
    assert_eq!(missing.body["error"], "agileplus_missing_idempotency_key");

    let not_v4 = post(
        app,
        "/api/v1/ingest/agileplus",
        &[
            (AGILEPLUS_TOKEN_HEADER, TEST_TOKEN.to_string()),
            (
                IDEMPOTENCY_HEADER,
                "6ba7b810-9dad-11d1-80b4-00c04fd430c8".to_string(),
            ),
        ],
        full_envelope(1),
    )
    .await;
    assert_eq!(not_v4.status, StatusCode::BAD_REQUEST);
    assert_eq!(store.list_swee_nodes(None).await.unwrap().len(), 0);
}

#[tokio::test]
async fn wrong_producer_and_bad_entities_are_rejected() {
    let (app, store) = fixture().await;
    let _guard = with_token();

    let wrong_source = send(
        app.clone(),
        envelope(
            "agcord",
            vec![entity("spec", "AP-SPEC-1", "approved", 1)],
            vec![],
        ),
    )
    .await;
    assert_eq!(wrong_source.status, StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(wrong_source.body["error"], "agileplus_wrong_producer");

    let wrong_version = send(
        app.clone(),
        json!({
            "source": "agileplus", "version": "2099-01-01",
            "entities": [entity("spec", "AP-SPEC-1", "approved", 1)],
        }),
    )
    .await;
    assert_eq!(wrong_version.status, StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(wrong_version.body["error"], "agileplus_unsupported_version");

    let empty = send(app.clone(), envelope("agileplus", vec![], vec![])).await;
    assert_eq!(empty.status, StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(empty.body["error"], "agileplus_empty_entities");

    let unknown_type = send(
        app.clone(),
        envelope(
            "agileplus",
            vec![entity("epic", "AP-EPIC-1", "open", 1)],
            vec![],
        ),
    )
    .await;
    assert_eq!(unknown_type.status, StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(unknown_type.body["error"], "agileplus_invalid_entity_type");

    let mut no_revision = entity("spec", "AP-SPEC-2", "approved", 1);
    no_revision["metadata"]
        .as_object_mut()
        .unwrap()
        .remove("version");
    let missing_revision = send(
        app.clone(),
        envelope("agileplus", vec![no_revision], vec![]),
    )
    .await;
    assert_eq!(missing_revision.status, StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(missing_revision.body["error"], "agileplus_missing_revision");

    let bad_confidence = send(app.clone(), envelope(
        "agileplus",
        vec![entity("spec", "AP-SPEC-3", "approved", 1)],
        vec![json!({"source_id": "AP-SPEC-3", "target_id": "AP-SPEC-3", "relation": "specifies", "confidence": 1.5})],
    ))
    .await;
    assert_eq!(bad_confidence.status, StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(bad_confidence.body["error"], "agileplus_invalid_confidence");

    assert_eq!(store.list_swee_nodes(None).await.unwrap().len(), 0);
}

#[tokio::test]
async fn forged_approvals_and_verification_claims_are_rejected() {
    let (app, store) = fixture().await;
    let _guard = with_token();

    let mut forged = entity("governance_decision", "AP-GOV-1", "approved", 1);
    forged["metadata"].as_object_mut().unwrap().remove("author");
    let forged_reply = send(app.clone(), envelope("agileplus", vec![forged], vec![])).await;
    assert_eq!(forged_reply.status, StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(forged_reply.body["error"], "agileplus_forged_approval");

    let mut claimed = entity("work_item", "AP-WI-1", "done", 1);
    claimed["metadata"]["verified"] = json!(true);
    let claimed_reply = send(app.clone(), envelope("agileplus", vec![claimed], vec![])).await;
    assert_eq!(claimed_reply.status, StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(claimed_reply.body["error"], "agileplus_unaccepted_claim");

    assert_eq!(store.list_swee_nodes(None).await.unwrap().len(), 0);
}

#[tokio::test]
async fn replayed_and_conflicting_idempotency_keys_are_rejected() {
    let (app, store) = fixture().await;
    let _guard = with_token();
    let key = uuid::Uuid::new_v4().to_string();

    let first = post(
        app.clone(),
        "/api/v1/ingest/agileplus",
        &auth_headers(&key),
        full_envelope(1),
    )
    .await;
    assert_eq!(first.status, StatusCode::OK, "{:?}", first.body);

    let identical = post(
        app.clone(),
        "/api/v1/ingest/agileplus",
        &auth_headers(&key),
        full_envelope(1),
    )
    .await;
    assert_eq!(identical.status, StatusCode::CONFLICT);
    assert_eq!(
        identical.body["error"],
        "agileplus_idempotency_key_consumed"
    );
    assert_eq!(identical.body["identical_replay"], true);
    assert_eq!(identical.body["conflicting_replay"], false);

    let conflicting = post(
        app.clone(),
        "/api/v1/ingest/agileplus",
        &auth_headers(&key),
        full_envelope(2),
    )
    .await;
    assert_eq!(conflicting.status, StatusCode::CONFLICT);
    assert_eq!(conflicting.body["identical_replay"], false);
    assert_eq!(conflicting.body["conflicting_replay"], true);

    // Neither replay created a second node set.
    assert_eq!(
        store
            .list_swee_nodes(Some("specification".into()))
            .await
            .unwrap()
            .len(),
        1
    );
}

#[tokio::test]
async fn stale_and_duplicate_revisions_are_rejected() {
    let (app, store) = fixture().await;
    let _guard = with_token();
    let governance = |revision: i64| {
        envelope(
            "agileplus",
            vec![entity("spec", "AP-SPEC-9", "approved", revision)],
            vec![],
        )
    };

    assert_eq!(
        send(app.clone(), governance(3)).await.status,
        StatusCode::OK
    );
    let stale = send(app.clone(), governance(2)).await;
    assert_eq!(stale.status, StatusCode::CONFLICT);
    assert_eq!(stale.body["error"], "agileplus_stale_revision");
    let duplicate = send(app.clone(), governance(3)).await;
    assert_eq!(duplicate.status, StatusCode::CONFLICT);
    assert_eq!(duplicate.body["error"], "agileplus_stale_revision");
    assert_eq!(
        store
            .list_swee_nodes(Some("specification".into()))
            .await
            .unwrap()
            .len(),
        1
    );
}

#[tokio::test]
async fn accepted_ingestion_maps_and_persists_without_verifying_capabilities() {
    let (app, store) = fixture().await;
    let _guard = with_token();

    let reply = post(
        app,
        "/api/v1/ingest/agileplus",
        &auth_headers(&uuid::Uuid::new_v4().to_string()),
        full_envelope(1),
    )
    .await;
    assert_eq!(reply.status, StatusCode::OK, "{:?}", reply.body);
    assert_eq!(reply.body["entities_accepted"], 4);
    assert_eq!(reply.body["trace_links_created"], 1);
    assert_eq!(
        reply.body["trace_links_unresolved"][0]["reason"],
        "endpoint_not_in_this_request"
    );
    assert_eq!(reply.body["product_capabilities_verified"], 0);
    assert_eq!(reply.body["ownership"]["governance"], "agileplus");
    assert_eq!(
        reply.body["ownership"]["product_state_and_evidence"],
        "tracera"
    );

    for (node_type, expected) in [
        ("specification", 1),
        ("story", 1),
        ("change_request", 1),
        ("evidence", 1),
    ] {
        let nodes = store.list_swee_nodes(Some(node_type.into())).await.unwrap();
        assert_eq!(nodes.len(), expected, "{node_type}");
        assert_eq!(nodes[0]["metadata"]["source"], "agileplus");
        assert_eq!(nodes[0]["metadata"]["capability_verified"], false);
    }

    // WorkPackage Done is governance evidence, not Tracera verification.
    let stories = store.list_swee_nodes(Some("story".into())).await.unwrap();
    assert_eq!(stories[0]["metadata"]["status"], "done");
    assert_eq!(stories[0]["metadata"]["capability_verified"], false);

    let edges = store.list_swee_edges(None).await.unwrap();
    assert_eq!(edges.len(), 1);
    assert_eq!(edges[0]["edge_type"], "specifies");
    assert_eq!(edges[0]["metadata"]["agileplus_target_id"], "AP-WI-1087");
}

#[test]
fn fingerprint_is_stable_and_distinguishes_content() {
    let first = json!({"b": 1, "a": 2});
    let reordered = json!({"a": 2, "b": 1});
    let different = json!({"a": 2, "b": 3});
    assert_eq!(fingerprint(&first), fingerprint(&reordered));
    assert_ne!(fingerprint(&first), fingerprint(&different));
    assert!(constant_time_equal(b"t", b"t"));
    assert!(!constant_time_equal(b"t", b"T"));
}
