use super::*;
use axum::{
    body::{to_bytes, Body},
    http::{Request, StatusCode},
};
use serde_json::{json, Value};
use std::{sync::Arc, time::Instant};
use tower::ServiceExt;

async fn fixture() -> Router {
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .unwrap();
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .unwrap();
    let state = AppState {
        store: Arc::new(crate::sqlite_store::SqliteStore::new(pool)),
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
    crate::router::build_router(state)
}

#[tokio::test]
async fn every_remaining_route_has_a_typed_501_for_all_operation_methods() {
    // Use the integrated router: duplicate/wildcard registration panics and
    // static-vs-parameter precedence bugs must fail this test too.
    let app = fixture().await;
    let parameter = regex::Regex::new(r"\{[^}]+\}").unwrap();
    let token = crate::middleware::issue_csrf_token().await;
    let templates = templates();
    assert!(
        templates.len() > 200,
        "remaining cohort unexpectedly shrank"
    );
    for template in templates {
        let path = parameter.replace_all(template, "probe-id");
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE"] {
            let response = app
                .clone()
                .oneshot(
                    Request::builder()
                        .method(method)
                        .uri(format!("{path}?private=not-in-response"))
                        .header("origin", "http://127.0.0.1:18000")
                        .header("x-csrf-token", &token)
                        .body(Body::empty())
                        .unwrap(),
                )
                .await
                .unwrap();
            assert_eq!(
                response.status(),
                StatusCode::NOT_IMPLEMENTED,
                "{method} {template}"
            );
            let body: Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(
                body,
                json!({"error":"not_implemented", "route":template}),
                "{method} {template}"
            );
        }
    }
}

#[tokio::test]
async fn unknown_routes_stay_404() {
    let response = fixture()
        .await
        .oneshot(
            Request::builder()
                .uri("/api/v1/unknown-family/probe")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn existing_project_mutations_never_claim_an_unpersisted_write() {
    let app = fixture().await;
    let token = crate::middleware::issue_csrf_token().await;
    for (method, path, template) in [
        ("POST", "/api/v1/projects", "/api/v1/projects"),
        (
            "PUT",
            "/api/v1/projects/probe-id",
            "/api/v1/projects/{project_id}",
        ),
        (
            "DELETE",
            "/api/v1/projects/probe-id",
            "/api/v1/projects/{project_id}",
        ),
        ("GET", "/org-intel/metrics", "/org-intel/metrics"),
    ] {
        let response = app
            .clone()
            .oneshot(
                Request::builder()
                    .method(method)
                    .uri(path)
                    .header("origin", "http://127.0.0.1:18000")
                    .header("x-csrf-token", &token)
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(
            response.status(),
            StatusCode::NOT_IMPLEMENTED,
            "{method} {path}"
        );
        let body: Value =
            serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap()).unwrap();
        assert_eq!(body, json!({"error":"not_implemented", "route":template}));
    }
}
