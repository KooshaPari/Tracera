use super::*;
use crate::{item::Item, sqlite_store::SqliteStore, store::Store};
use axum::{
    body::{to_bytes, Body},
    http, Router,
};
use serde_json::json;
use std::{sync::Arc, time::Instant};
use tower::ServiceExt;

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
    let store = Arc::new(SqliteStore::new(pool.clone()));
    for (id, project, item_type) in [
        ("req-a", "alpha", "requirement"),
        ("req-b", "alpha", "requirement"),
        ("feat-a", "alpha", "feature"),
        ("other", "beta", "requirement"),
    ] {
        let item: Item = serde_json::from_value(json!({
            "id":id,"projectId":project,"status":"todo","view":item_type,
            "priority":"high","type":item_type,"title":id,"version":1,
            "description":"fixture item","createdAt":"2026-11-20T00:00:00Z","updatedAt":"2026-11-20T00:00:00Z",
            "canonicalId":format!("canonical-{id}"),"metadata":{},"dimensions":{}
        }))
        .unwrap();
        store.create_item(item).await.unwrap();
    }
    store
        .create_trace_link(
            "link-1".into(),
            "req-a".into(),
            "feat-a".into(),
            "implements".into(),
            0.9,
            "manual".into(),
            chrono::Utc::now(),
        )
        .await
        .unwrap();
    store
        .create_trace_link(
            "link-outside".into(),
            "req-b".into(),
            "other".into(),
            "implements".into(),
            0.9,
            "manual".into(),
            chrono::Utc::now(),
        )
        .await
        .unwrap();
    sqlx::query("INSERT OR IGNORE INTO projects (id,name,description,metadata,created_at,updated_at) VALUES ('empty','empty',NULL,'{}','2026-11-20T00:00:00Z','2026-11-20T00:00:00Z')")
        .execute(&pool)
        .await
        .unwrap();

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

async fn get(app: Router, path: &str) -> (StatusCode, Value) {
    let token = crate::middleware::issue_csrf_token().await;
    let response = app
        .oneshot(
            http::Request::builder()
                .uri(path)
                .header("origin", "http://127.0.0.1:18000")
                .header("x-csrf-token", token)
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let content_type = response
        .headers()
        .get("content-type")
        .and_then(|value| value.to_str().ok())
        .unwrap_or("")
        .to_string();
    let bytes = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    let body = if content_type.starts_with("application/json") {
        serde_json::from_slice(&bytes).unwrap_or(json!({"message":String::from_utf8_lossy(&bytes)}))
    } else {
        json!({"text":String::from_utf8_lossy(&bytes)})
    };
    (status, body)
}

async fn post(app: Router, path: &str) -> (StatusCode, Value) {
    let token = crate::middleware::issue_csrf_token().await;
    let response = app
        .oneshot(
            http::Request::builder()
                .method("POST")
                .uri(path)
                .header("origin", "http://127.0.0.1:18000")
                .header("x-csrf-token", token)
                .header("content-type", "application/json")
                .body(Body::from(
                    json!({"viewport":{"minX":0,"minY":0,"maxX":100,"maxY":100},"zoom":1,"bufferPx":500})
                        .to_string(),
                ))
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let bytes = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    (status, serde_json::from_slice(&bytes).unwrap())
}

#[tokio::test]
async fn scoped_graph_and_matrix_share_the_same_persisted_ids() {
    let (app, _) = fixture().await;
    let (status, graphs) = get(app.clone(), "/api/v1/projects/alpha/graphs").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(graphs["graphs"][0]["id"], "alpha");
    assert_eq!(graphs["graphs"][0]["graphType"], "traceability");

    let (status, graph) = get(app.clone(), "/api/v1/projects/alpha/graph?graph_id=alpha").await;
    assert_eq!(status, StatusCode::OK);
    let (_, matrix) = get(app.clone(), "/api/v1/projects/alpha/matrix").await;
    assert_eq!(graph["nodes"], matrix["items"]);
    assert_eq!(graph["links"], matrix["links"]);
    assert_eq!(graph["nodes"].as_array().unwrap().len(), 3);
    assert_eq!(graph["links"].as_array().unwrap().len(), 1);
    assert_eq!(graph["links"][0]["id"], "link-1");
    assert_eq!(matrix["coverage"]["total"], 2);
    assert_eq!(matrix["coverage"]["traced"], 1);
    assert_eq!(matrix["coverage"]["percentage"], 50.0);
}

#[tokio::test]
async fn viewport_and_export_are_real_views_of_the_same_rows() {
    let (app, _) = fixture().await;
    let (status, viewport) = post(app.clone(), "/api/v1/projects/alpha/graph/viewport").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(viewport["totalCount"], 3);
    assert_eq!(viewport["edges"].as_array().unwrap().len(), 1);
    assert_eq!(viewport["nodes"][0]["data"]["id"], "feat-a");
    assert!(viewport["nodes"]
        .as_array()
        .unwrap()
        .iter()
        .any(|node| node["data"]["id"] == viewport["links"][0]["sourceId"]));

    let (status, csv) = get(
        app.clone(),
        "/api/v1/projects/alpha/matrix/export?format=csv",
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert!(csv["text"]
        .as_str()
        .unwrap()
        .contains("link-1,alpha,req-a,feat-a,implements"));
    let (status, json_export) = get(
        app.clone(),
        "/api/v1/projects/alpha/matrix/export?format=json",
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(json_export["coverage"]["traced"], 1);
    let (status, _) = get(
        app.clone(),
        "/api/v1/projects/alpha/matrix/export?format=xlsx",
    )
    .await;
    assert_eq!(status, StatusCode::BAD_REQUEST);
}

#[tokio::test]
async fn unknown_projects_are_404_and_known_empty_projects_are_empty() {
    let (app, _) = fixture().await;
    for path in [
        "/api/v1/projects/unknown/graphs",
        "/api/v1/projects/unknown/graph",
        "/api/v1/projects/unknown/matrix",
        "/api/v1/projects/unknown/matrix/export?format=csv",
    ] {
        let (status, body) = get(app.clone(), path).await;
        assert_eq!(status, StatusCode::NOT_FOUND, "{path}: {body}");
        assert_eq!(body["error"], "project_not_found");
    }
    let (status, matrix) = get(app.clone(), "/api/v1/projects/empty/matrix").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(matrix["items"], json!([]));
    assert_eq!(matrix["links"], json!([]));
    assert_eq!(matrix["coverage"]["total"], 0);
    assert_eq!(matrix["coverage"]["percentage"], 0.0);
    let (status, graphs) = get(app, "/api/v1/projects/empty/graphs").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(graphs["graphs"][0]["id"], "empty");
}

#[tokio::test]
async fn unrelated_graph_stubs_and_remaining_501s_are_unchanged() {
    let (app, _) = fixture().await;
    let (status, body) = get(app.clone(), "/api/v1/projects/alpha/coverage/matrix").await;
    assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
    assert_eq!(body["error"], "not_implemented");
    let (status, _) = get(app, "/api/v1/graph/analysis/coverage").await;
    assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
}
