use super::*;
use crate::{sqlite_store::SqliteStore, store::Store};
use axum::{
    body::{to_bytes, Body},
    Router,
};
use std::{sync::Arc, time::Instant};
use tower::ServiceExt;
async fn fixture() -> (Router, Arc<SqliteStore>, Vec<String>) {
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
    let mut ids = Vec::new();
    for name in ["root", "middle", "leaf", "isolated"] {
        ids.push(
            store
                .create_swee_node(
                    "artifact".into(),
                    name.into(),
                    json!({}),
                    chrono::Utc::now(),
                )
                .await
                .unwrap(),
        );
    }
    for (from, to) in [(0, 1), (1, 2)] {
        store
            .create_swee_edge(
                "depends_on".into(),
                ids[from].clone(),
                ids[to].clone(),
                1.0,
                "manual".into(),
                json!({}),
                chrono::Utc::now(),
            )
            .await
            .unwrap();
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
        frontend: crate::FrontendState::Ok,
        frontend_dist: std::path::PathBuf::new(),
    };
    let app = crate::router::build_router(state);
    (app, store, ids)
}
async fn request(app: Router, uri: &str) -> (StatusCode, Value) {
    let response = app
        .oneshot(
            http::Request::builder()
                .uri(format!("/api/v1/graph{uri}"))
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let body = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    (status, serde_json::from_slice(&body).unwrap())
}
#[tokio::test]
async fn graph_routes_read_sqlite_data() {
    let (app, _, ids) = fixture().await;
    for (route, count) in [
        ("/full".to_owned(), 6),
        ("/orphans".to_owned(), 1),
        ("/topo-sort".to_owned(), 4),
        (format!("/path?source={}&target={}", ids[0], ids[2]), 3),
        (format!("/ancestors/{}", ids[2]), 2),
        (format!("/descendants/{}", ids[0]), 2),
        (format!("/dependencies/{}", ids[0]), 1),
        ("/cycles".to_owned(), 0),
    ] {
        let (status, body) = request(app.clone(), &route).await;
        assert_eq!(status, StatusCode::OK, "{route}: {body}");
        assert_eq!(body["total"], count, "{route}");
    }
    let (_, orphan) = request(app.clone(), "/orphans").await;
    assert_eq!(orphan["items"][0]["id"], ids[3]);
    let (_, path) = request(app, &format!("/path?source={}&target={}", ids[0], ids[2])).await;
    assert_eq!(
        path["items"]
            .as_array()
            .unwrap()
            .iter()
            .map(|n| n["id"].as_str().unwrap())
            .collect::<Vec<_>>(),
        ids.iter().take(3).map(String::as_str).collect::<Vec<_>>()
    );
}
#[tokio::test]
async fn cycles_and_topology_detect_persisted_cycle() {
    let (app, store, ids) = fixture().await;
    store
        .create_swee_edge(
            "depends_on".into(),
            ids[2].clone(),
            ids[0].clone(),
            1.0,
            "manual".into(),
            json!({}),
            chrono::Utc::now(),
        )
        .await
        .unwrap();
    let (status, cycles) = request(app.clone(), "/cycles").await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(cycles["total"], 1);
    assert_eq!(cycles["items"][0]["node_ids"], json!(&ids[..3]));
    let (status, body) = request(app, "/topo-sort").await;
    assert_eq!(status, StatusCode::CONFLICT);
    assert_eq!(body["error"], "graph_contains_cycle");
}
#[tokio::test]
async fn pagination_and_negative_controls() {
    let (app, _, ids) = fixture().await;
    let (_, body) = request(app.clone(), "/full?limit=2&offset=2").await;
    assert_eq!(body["items"].as_array().unwrap().len(), 2);
    assert_eq!(body["total"], 6);
    assert_eq!(body["has_more"], true);
    for uri in ["/full?limit=101", "/cycles?limit=0", "/path"] {
        assert_eq!(request(app.clone(), uri).await.0, StatusCode::BAD_REQUEST);
    }
    for uri in [
        "/ancestors/missing".into(),
        format!("/path?source={}&target={}", ids[2], ids[0]),
    ] {
        assert_eq!(request(app.clone(), &uri).await.0, StatusCode::NOT_FOUND);
    }
    for uri in ["/paths", "/impact/1", "/traverse/1"] {
        let (status, body) = request(app.clone(), uri).await;
        assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
        assert_eq!(body["error"], "not_implemented");
    }
}
#[tokio::test]
async fn empty_graph_self_loop_and_store_failure() {
    let (app, store, ids) = fixture().await;
    store
        .create_swee_edge(
            "depends_on".into(),
            ids[3].clone(),
            ids[3].clone(),
            1.0,
            "manual".into(),
            json!({}),
            chrono::Utc::now(),
        )
        .await
        .unwrap();
    let (_, body) = request(app.clone(), "/cycles").await;
    assert_eq!(body["items"][0]["node_ids"], json!([ids[3]]));
    assert_eq!(
        request(app.clone(), "/topo-sort").await.0,
        StatusCode::CONFLICT
    );
    sqlx::query("DELETE FROM swee_edges")
        .execute(&store.pool)
        .await
        .unwrap();
    sqlx::query("DELETE FROM swee_nodes")
        .execute(&store.pool)
        .await
        .unwrap();
    for route in ["/full", "/cycles", "/orphans", "/topo-sort"] {
        let (status, body) = request(app.clone(), route).await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(body["total"], 0);
    }
    let (_, body) = request(app.clone(), "/full?limit=100&offset=18446744073709551615").await;
    assert_eq!(body["has_more"], false);
    sqlx::raw_sql("PRAGMA foreign_keys=OFF; INSERT INTO swee_edges(source_id,target_id,type) VALUES(999,998,'depends_on');").execute(&store.pool).await.unwrap();
    assert_eq!(
        request(app.clone(), "/cycles").await.0,
        StatusCode::CONFLICT
    );
    sqlx::query("DELETE FROM swee_edges")
        .execute(&store.pool)
        .await
        .unwrap();
    sqlx::query("WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x<501) INSERT INTO swee_nodes(type,name) SELECT 'artifact','bulk' FROM n").execute(&store.pool).await.unwrap();
    let (status, body) = request(app.clone(), "/cycles").await;
    assert_eq!(status, StatusCode::SERVICE_UNAVAILABLE);
    assert_eq!(body["error"], "cycle_query_graph_too_large");
    sqlx::query("DROP TABLE swee_edges")
        .execute(&store.pool)
        .await
        .unwrap();
    let (status, body) = request(app, "/cycles").await;
    assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
    assert_eq!(body["error"], "graph_store_error");
}
