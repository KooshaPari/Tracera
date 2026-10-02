use super::*;
use std::{sync::Arc, time::Instant};

use axum::{
    body::{to_bytes, Body},
    http::Request,
    Router,
};
use chrono::{TimeZone, Utc};
use serde_json::{json, Value};
use sqlx::sqlite::SqlitePoolOptions;
use tower::ServiceExt;

use crate::{
    product::{
        application::ProductApplication, EvidenceReuseDecision, InvalidationEvent,
        PersistedBaseline, PersistedEntity, PersistedEntityRevision, PersistedObservation,
        PersistedProduct, ProductPersistence,
    },
    sqlite_store::SqliteStore,
};

const TOKEN: &str = "product-read-fixture-only";

async fn fixture() -> Router {
    let pool = SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .expect("SQLite fixture");
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .expect("real migrations");
    let store = Arc::new(SqliteStore::new(pool));
    let now = Utc.timestamp_opt(1_759_392_000, 0).unwrap();
    for product_id in ["p-a", "p-b", "health"] {
        store
            .create_product(&PersistedProduct {
                product_id: product_id.into(),
                display_name: product_id.into(),
                created_at: now,
            })
            .await
            .expect("product");
    }
    for (product_id, baseline_id) in [("p-a", "b-a"), ("p-b", "b-b")] {
        let mut members = Vec::new();
        if product_id == "p-b" {
            for suffix in ["1", "2"] {
                let entity_id = format!("entity-{suffix}");
                let revision_id = format!("revision-{suffix}");
                store
                    .create_entity(&PersistedEntity {
                        entity_id: entity_id.clone(),
                        product_id: product_id.into(),
                        local_id: suffix.into(),
                        entity_kind: "capability".into(),
                        created_at: now,
                    })
                    .await
                    .expect("entity");
                store
                    .append_entity_revision(&PersistedEntityRevision {
                        entity_revision_id: revision_id.clone(),
                        entity_id: entity_id.clone(),
                        content_revision: 1,
                        title: suffix.into(),
                        description: String::new(),
                        status: "accepted".into(),
                        metadata: json!({}),
                        created_at: now,
                    })
                    .await
                    .expect("revision");
                members.push((entity_id, revision_id));
            }
        }
        store
            .accept_baseline(
                &PersistedBaseline {
                    baseline_id: baseline_id.into(),
                    product_id: product_id.into(),
                    revision_number: 1,
                    parent_baseline_id: None,
                    accepted_at: now,
                    metadata: json!({}),
                },
                &members,
            )
            .await
            .expect("baseline");
        let observation_id = format!("observation-{product_id}");
        store
            .append_observation(&PersistedObservation {
                observation_id: observation_id.clone(),
                product_id: product_id.into(),
                baseline_id: baseline_id.into(),
                subject_entity_id: None,
                subject_local_id: Some("search".into()),
                candidate_ref: "git:observed".into(),
                configuration: json!({}),
                result: "passed".into(),
                verifier_id: "suite".into(),
                verifier_version: "1".into(),
                recorded_at: now,
                raw_evidence_ref: None,
                metadata: json!({}),
            })
            .await
            .expect("observation");
        store
            .append_reuse_decision(&EvidenceReuseDecision {
                reuse_decision_id: format!("reuse-{product_id}"),
                observation_id,
                target_baseline_id: baseline_id.into(),
                target_candidate_ref: "git:target".into(),
                criterion_ref: "search".into(),
                applicability_state: "current_valid".into(),
                compatibility_certificate_ref: None,
                policy_version: "1".into(),
                reason: "fixture".into(),
                decided_at: now,
            })
            .await
            .expect("reuse decision");
    }
    store
        .append_invalidation(&InvalidationEvent {
            invalidation_id: "inv-1".into(),
            trigger_kind: "dependency_changed".into(),
            trigger_ref: "change-1".into(),
            target_kind: "criterion".into(),
            target_ref: "criterion:a/b".into(),
            prior_state: Some("current_valid".into()),
            new_state: "suspect".into(),
            reason: "fixture".into(),
            occurred_at: now,
        })
        .await
        .expect("invalidation");
    let state = AppState {
        version: "test".into(),
        backend: "sqlite",
        started_at: Instant::now(),
        store: store.clone(),
        product: Arc::new(ProductApplication::new(store)),
        workos_client: tracera_workos::WorkOSClient::default_for_router(),
        cache: None,
        neo4j: None,
        r2: None,
    };
    crate::router::build_router_with_auth(state, Some(Arc::<str>::from(TOKEN)))
}

async fn request(app: &Router, path: &str, authenticated: bool) -> axum::response::Response {
    let mut request = Request::builder().uri(path);
    if authenticated {
        request = request.header("authorization", format!("Bearer {TOKEN}"));
    }
    app.clone()
        .oneshot(request.body(Body::empty()).unwrap())
        .await
        .unwrap()
}

async fn body(response: axum::response::Response) -> Value {
    let bytes = to_bytes(response.into_body(), 64 * 1024).await.unwrap();
    serde_json::from_slice(&bytes).unwrap()
}

#[test]
fn product_query_limits_are_bounded() {
    assert_eq!(bounded_limit(0), 1);
    assert_eq!(bounded_limit(1), 1);
    assert_eq!(bounded_limit(100), 100);
    assert_eq!(bounded_limit(u32::MAX), 1000);
}

#[test]
fn product_persistence_errors_map_truthfully_to_http_status() {
    for (error, expected) in [
        (
            ProductPersistenceError::NotFound("x".into()),
            StatusCode::NOT_FOUND,
        ),
        (
            ProductPersistenceError::Conflict("x".into()),
            StatusCode::CONFLICT,
        ),
        (
            ProductPersistenceError::Invalid("x".into()),
            StatusCode::BAD_REQUEST,
        ),
        (
            ProductPersistenceError::Backend("x".into()),
            StatusCode::INTERNAL_SERVER_ERROR,
        ),
    ] {
        assert_eq!(persistence_error(error).0, expected);
    }
}

#[test]
fn backend_error_details_are_not_sent_to_clients() {
    let (_, Json(body)) = persistence_error(ProductPersistenceError::Backend(
        "postgres://secret@example.invalid/private_database".into(),
    ));
    assert_eq!(body["error"], "persistence_error");
    assert!(!body.to_string().contains("secret"));
    assert!(!body.to_string().contains("private_database"));
}

#[tokio::test]
async fn mounted_product_lookup_requires_bearer() {
    let app = fixture().await;
    assert_eq!(
        request(&app, "/api/v1/products/p-a", false).await.status(),
        StatusCode::UNAUTHORIZED
    );
    let response = request(&app, "/api/v1/products/p-a", true).await;
    assert_eq!(response.status(), StatusCode::OK);
    assert_eq!(body(response).await["product"]["product_id"], "p-a");
}

#[tokio::test]
async fn product_named_health_is_not_a_public_probe() {
    let app = fixture().await;
    assert_eq!(
        request(&app, "/api/v1/products/health", false)
            .await
            .status(),
        StatusCode::UNAUTHORIZED
    );
    let response = request(&app, "/api/v1/products/health", true).await;
    assert_eq!(response.status(), StatusCode::OK);
    assert_eq!(body(response).await["product"]["product_id"], "health");
    assert_eq!(
        request(&app, "/healthz", false).await.status(),
        StatusCode::OK
    );
}

#[tokio::test]
async fn foreign_and_missing_baselines_are_not_successful_empty_lists() {
    let app = fixture().await;
    for baseline in ["b-b", "missing"] {
        for operation in [
            "entities",
            "observations",
            "reuse-decisions?candidate_ref=git%3Atarget",
        ] {
            let path = format!("/api/v1/products/p-a/baselines/{baseline}/{operation}");
            assert_eq!(
                request(&app, &path, true).await.status(),
                StatusCode::NOT_FOUND,
                "{path}"
            );
        }
    }
}

#[tokio::test]
async fn legitimate_empty_baseline_is_successful_and_complete() {
    let app = fixture().await;
    let response = request(&app, "/api/v1/products/p-a/baselines/b-a/entities", true).await;
    assert_eq!(response.status(), StatusCode::OK);
    let value = body(response).await;
    assert_eq!(value["count"], 0);
    assert_eq!(value["page"]["complete"], true);
}

#[tokio::test]
async fn bounded_entity_list_does_not_claim_full_coverage() {
    let app = fixture().await;
    let response = request(
        &app,
        "/api/v1/products/p-b/baselines/b-b/entities?limit=1",
        true,
    )
    .await;
    assert_eq!(response.status(), StatusCode::OK);
    let value = body(response).await;
    assert_eq!(value["count"], 1);
    assert_eq!(value["page"]["complete"], false);
    assert_eq!(value["page"]["completeness"], "unknown_at_limit");
    assert_eq!(value["page"]["pagination_supported"], false);
}

#[tokio::test]
async fn reuse_projection_preserves_product_and_candidate_scope() {
    let app = fixture().await;
    let response = request(
        &app,
        "/api/v1/products/p-a/baselines/b-a/reuse-decisions?candidate_ref=git%3Atarget",
        true,
    )
    .await;
    assert_eq!(response.status(), StatusCode::OK);
    let value = body(response).await;
    assert_eq!(value["count"], 1);
    assert_eq!(
        value["reuse_decisions"][0]["reuse_decision_id"],
        "reuse-p-a"
    );
    let response = request(
        &app,
        "/api/v1/products/p-a/baselines/b-a/reuse-decisions?candidate_ref=git%3Aother",
        true,
    )
    .await;
    assert_eq!(response.status(), StatusCode::OK);
    assert_eq!(body(response).await["count"], 0);
}

#[tokio::test]
async fn invalidation_reference_survives_query_encoding() {
    let app = fixture().await;
    let response = request(
        &app,
        "/api/v1/product-invalidations/criterion?target_ref=criterion%3Aa%2Fb",
        true,
    )
    .await;
    assert_eq!(response.status(), StatusCode::OK);
    let value = body(response).await;
    assert_eq!(value["target_ref"], "criterion:a/b");
    assert_eq!(value["invalidations"][0]["invalidation_id"], "inv-1");
}

#[tokio::test]
async fn missing_query_fields_and_negative_limits_are_rejected() {
    let app = fixture().await;
    for path in [
        "/api/v1/products/p-a/baselines/b-a/reuse-decisions",
        "/api/v1/products/p-a/baselines/b-a/entities?limit=-1",
        "/api/v1/product-invalidations/criterion",
    ] {
        assert_eq!(
            request(&app, path, true).await.status(),
            StatusCode::BAD_REQUEST,
            "{path}"
        );
    }
}
