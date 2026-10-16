use super::*;
use crate::{item::Item, sqlite_store::SqliteStore, store::Store};
use axum::{
    body::{to_bytes, Body},
    Router,
};
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
    let store = Arc::new(SqliteStore::new(pool));
    for (id, project, status, view, priority) in [
        ("a", "alpha", "todo", "requirement", "high"),
        ("b", "beta", "done", "test", "low"),
        ("c", "alpha", "done", "test", "high"),
    ] {
        let item: Item = serde_json::from_value(json!({"id":id, "projectId":project,
            "status":status, "view":view, "priority":priority, "type":"requirement",
            "title":format!("Persisted {id}"), "description":"real description",
            "version":3, "createdAt":"2026-10-16T00:00:00Z", "updatedAt":"2026-10-16T00:00:00Z",
            "canonicalId":"concept-1", "metadata":{"source":"fixture"},
            "dimensions":{"security":true}}))
        .unwrap();
        store.create_item(item).await.unwrap();
    }
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
    (crate::router::build_router(state), store)
}
async fn request(app: Router, method: &str, path: &str) -> (StatusCode, Value) {
    let token = crate::middleware::issue_csrf_token().await;
    let response = app
        .oneshot(
            http::Request::builder()
                .method(method)
                .header("origin", "http://127.0.0.1:18000")
                .header("x-csrf-token", token)
                .uri(path)
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let body = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    (
        status,
        serde_json::from_slice(&body)
            .unwrap_or_else(|_| json!({"message":String::from_utf8_lossy(&body)})),
    )
}
#[tokio::test]
async fn list_and_detail_preserve_real_item_contract() {
    let (app, store) = fixture().await;
    let (status, body) = request(app.clone(), "GET", "/api/v1/items").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["total"], 3);
    assert_eq!(body["limit"], 50);
    assert_eq!(body["offset"], 0);
    assert_eq!(body["has_more"], false);
    let expected =
        serde_json::to_value(store.get_item("a".into()).await.unwrap().unwrap()).unwrap();
    let (status, detail) = request(app, "GET", "/api/v1/items/a").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(detail, expected);
    assert_eq!(body["items"][0], expected);
    assert_eq!(detail["dimensions"]["security"], true);
    assert!(detail.get("project_id").is_none());
}
#[tokio::test]
async fn filters_are_exact_and_project_scoped_routes_agree() {
    let (app, _) = fixture().await;
    for route in [
        "/api/v1/items?project_id=alpha",
        "/api/v1/projects/alpha/items",
    ] {
        let (status, body) = request(app.clone(), "GET", route).await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(body["total"], 2);
        assert!(body["items"]
            .as_array()
            .unwrap()
            .iter()
            .all(|i| i["projectId"] == "alpha"));
    }
    for query in ["status=done", "view=test", "priority=high"] {
        let (_, body) = request(app.clone(), "GET", &format!("/api/v1/items?{query}")).await;
        assert_eq!(body["total"], 2);
    }
    let (_, body) = request(
        app.clone(),
        "GET",
        "/api/v1/items?project_id=alpha&status=done&view=test&priority=high",
    )
    .await;
    assert_eq!(body["total"], 1);
    assert_eq!(body["items"][0]["id"], "c");
    let (_, body) = request(
        app.clone(),
        "GET",
        "/api/v1/items?project_id=alpha%27%20OR%201%3D1--",
    )
    .await;
    assert_eq!(body["total"], 0);
    let (_, body) = request(app, "GET", "/api/v1/projects/alpha/items?status=absent").await;
    assert_eq!(body["total"], 0);
}
#[tokio::test]
async fn pagination_boundaries_are_complete() {
    let (app, _) = fixture().await;
    let (_, first) = request(app.clone(), "GET", "/api/v1/items?limit=1").await;
    assert_eq!(first["items"][0]["id"], "a");
    assert_eq!(first["total"], 3);
    assert_eq!(first["has_more"], true);
    let (_, second) = request(app.clone(), "GET", "/api/v1/items?limit=1&offset=1").await;
    assert_eq!(second["items"][0]["id"], "b");
    let (_, last) = request(app.clone(), "GET", "/api/v1/items?limit=1&offset=2").await;
    assert_eq!(last["items"][0]["id"], "c");
    assert_eq!(last["has_more"], false);
    for offset in [3, 100000] {
        let (_, body) = request(
            app.clone(),
            "GET",
            &format!("/api/v1/items?limit=100&offset={offset}"),
        )
        .await;
        assert_eq!(body["total"], 3);
        assert_eq!(body["items"], json!([]));
        assert_eq!(body["has_more"], false);
    }
}
#[tokio::test]
async fn invalid_queries_and_missing_records_are_honest() {
    let (app, _) = fixture().await;
    for query in [
        "limit=0",
        "limit=101",
        "limit=-1",
        "offset=-1",
        "unknown=true",
        "offset=overflow",
    ] {
        assert_eq!(
            request(app.clone(), "GET", &format!("/api/v1/items?{query}"))
                .await
                .0,
            StatusCode::BAD_REQUEST
        );
    }
    for (route, code) in [
        ("/api/v1/items/missing", "item_not_found"),
        ("/api/v1/projects/missing/items", "project_not_found"),
    ] {
        let (status, body) = request(app.clone(), "GET", route).await;
        assert_eq!(status, StatusCode::NOT_FOUND);
        assert_eq!(body["error"], code);
    }
    let (status, body) = request(app.clone(), "GET", "/api/v1/items?offset=100001").await;
    assert_eq!(status, StatusCode::SERVICE_UNAVAILABLE);
    assert_eq!(body["error"], "items_query_over_budget");
    let (status, body) = request(app, "GET", "/api/v1/projects/alpha/items?project_id=beta").await;
    assert_eq!(status, StatusCode::BAD_REQUEST);
    assert_eq!(body["error"], "project_id_mismatch");
}
#[tokio::test]
async fn unimplemented_semantics_return_typed_route_labelled_501() {
    let (app, _) = fixture().await;
    for (method, path) in [
        ("GET", "/api/v1/pivot-targets"),
        ("GET", "/api/v1/items/a/pivot-targets"),
        ("POST", "/api/v1/items/a/pivot"),
        ("GET", "/api/v1/items/a/pivot"),
        ("POST", "/api/v1/items"),
        ("PUT", "/api/v1/items/a"),
        ("DELETE", "/api/v1/items/a"),
        ("POST", "/api/v1/projects/alpha/items"),
        ("GET", "/api/v1/items/summary"),
        ("POST", "/api/v1/items/bulk-update"),
    ] {
        let (status, body) = request(app.clone(), method, path).await;
        assert_eq!(
            status,
            StatusCode::NOT_IMPLEMENTED,
            "{method} {path}: {body}"
        );
        assert_eq!(
            body,
            json!({"error":"not_implemented", "route":path, "since":"2026-10-16"})
        );
    }
}
#[tokio::test]
async fn store_failures_do_not_become_empty_success() {
    let (app, store) = fixture().await;
    store.pool.close().await;
    for route in [
        "/api/v1/items",
        "/api/v1/items/a",
        "/api/v1/projects/alpha/items",
    ] {
        let (status, body) = request(app.clone(), "GET", route).await;
        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
        assert_eq!(body["error"], "items_store_error");
    }
}
#[tokio::test]
async fn exhausted_store_budget_returns_503() {
    let (app, store) = fixture().await;
    let _connection = store.pool.acquire().await.unwrap();
    let (status, body) = request(app, "GET", "/api/v1/items").await;
    assert_eq!(status, StatusCode::SERVICE_UNAVAILABLE);
    assert_eq!(body["error"], "items_query_over_budget");
}
#[tokio::test]
async fn empty_store_is_distinct_from_failure() {
    let (app, store) = fixture().await;
    sqlx::query("DELETE FROM items")
        .execute(&store.pool)
        .await
        .unwrap();
    let (status, body) = request(app, "GET", "/api/v1/items").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["total"], 0);
    assert_eq!(body["items"], json!([]));
    assert_eq!(body["has_more"], false);
}
#[tokio::test]
async fn known_problem_project_can_have_no_items() {
    let (app, store) = fixture().await;
    store
        .create_problem(
            "problem-1".into(),
            "empty-project".into(),
            "PRB-1".into(),
            "Persisted project identity".into(),
            None,
            "open".into(),
            None,
            None,
            None,
            None,
            "low".into(),
            "low".into(),
            "low".into(),
            false,
            false,
            false,
            false,
            None,
            None,
            None,
            None,
            chrono::Utc::now(),
        )
        .await
        .unwrap();
    let (status, body) = request(app, "GET", "/api/v1/projects/empty-project/items").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["total"], 0);
    assert_eq!(body["items"], json!([]));
    assert_eq!(body["has_more"], false);
}
