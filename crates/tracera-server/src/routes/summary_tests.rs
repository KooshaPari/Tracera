use crate::{sqlite_store::SqliteStore, AppState};
use axum::{
    body::{to_bytes, Body},
    http::{Request, StatusCode},
    Router,
};
use serde_json::{json, Value};
use std::{sync::Arc, time::Instant};
use tower::ServiceExt;
async fn fixture(projects: usize, alpha_count: usize) -> Router {
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .unwrap();
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .unwrap();
    for index in 0..(alpha_count + projects - 1) {
        let project = if index < alpha_count {
            "alpha".to_string()
        } else {
            format!("project-{index}")
        };
        sqlx::query("INSERT INTO problems (id,project_id,problem_number,title,status,created_at,updated_at) VALUES (?1,?2,?1,'Stored problem',?3,'2026-10-16T00:00:00Z','2026-10-16T00:00:00Z')")
            .bind(format!("problem-{index}")).bind(project)
            .bind(if index == 0 { "closed" } else { "open" }).execute(&pool).await.unwrap();
    }
    sqlx::query("INSERT INTO problems (id,project_id,problem_number,title,created_at,updated_at,deleted_at) VALUES ('deleted','alpha','deleted','Deleted','2026-10-16T00:00:00Z','2026-10-16T00:00:00Z','2026-10-16T00:00:00Z')")
        .execute(&pool).await.unwrap();
    crate::router::build_router(AppState {
        store: Arc::new(SqliteStore::new(pool)),
        version: "test".into(),
        backend: "sqlite",
        started_at: Instant::now(),
        workos_client: tracera_workos::WorkOSClient::default_for_router(),
        cache: None,
        neo4j: None,
        r2: None,
    })
}
async fn request(app: Router, path: &str) -> (StatusCode, Value) {
    let response = app
        .oneshot(Request::builder().uri(path).body(Body::empty()).unwrap())
        .await
        .unwrap();
    let status = response.status();
    assert!(response.headers()["content-type"]
        .to_str()
        .unwrap()
        .starts_with("application/json"));
    let body = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    (status, serde_json::from_slice(&body).unwrap())
}
#[tokio::test]
async fn links_have_exact_501_template_contracts() {
    let app = fixture(1, 1).await;
    for (path, template) in [
        ("/api/v1/links", "/api/v1/links"),
        ("/api/v1/links/real-id?limit=10", "/api/v1/links/{id}"),
        (
            "/api/v1/projects/alpha/links",
            "/api/v1/projects/{project_id}/links",
        ),
    ] {
        let (status, body) = request(app.clone(), path).await;
        assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
        assert_eq!(body, json!({"error":"not_implemented","route":template}));
    }
}
#[tokio::test]
async fn summaries_and_project_list_agree_on_533_persisted_records() {
    let app = fixture(1, 533).await;
    let (status, project) = request(app.clone(), "/api/v1/projects/alpha/summary").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(project["totalCount"], 533);
    assert_eq!(project["completedCount"], 1);
    assert_eq!(project["statusCounts"]["open"], 532);
    let (status, dashboard) = request(app.clone(), "/api/v1/dashboard/summary").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(dashboard["totalItemCount"], 533);
    assert_eq!(dashboard["perProject"]["alpha"], project);
    let (status, listing) = request(app.clone(), "/api/v1/projects").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(listing["items"][0]["problem_count"], project["totalCount"]);
    assert_eq!(
        request(app, "/api/v1/projects/missing/summary").await.0,
        StatusCode::NOT_FOUND
    );
}
#[tokio::test]
async fn dashboard_does_not_truncate_after_500_projects() {
    let app = fixture(501, 1).await;
    let (status, dashboard) = request(app, "/api/v1/dashboard/summary").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(dashboard["projectCount"], 501);
    assert_eq!(dashboard["totalItemCount"], 501);
    assert_eq!(dashboard["perProject"].as_object().unwrap().len(), 501);
}

#[tokio::test]
async fn unavailable_store_is_an_error_instead_of_a_zero_summary() {
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .unwrap();
    let app = crate::router::build_router(AppState {
        store: Arc::new(SqliteStore::new(pool)),
        version: "test".into(),
        backend: "sqlite",
        started_at: Instant::now(),
        workos_client: tracera_workos::WorkOSClient::default_for_router(),
        cache: None,
        neo4j: None,
        r2: None,
    });
    for route in [
        "/api/v1/dashboard/summary",
        "/api/v1/projects/alpha/summary",
    ] {
        let (status, body) = request(app.clone(), route).await;
        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
        assert_eq!(body, json!({"error":"project_summary_failed"}));
    }
}
