//! JSON snapshots of canonical items and internal artifact trace links only.
//! Store has no batch transaction: failures report partial progress, never success.
use crate::{
    item::{Item, ItemFilter},
    store::{Store, StoreError, TraceLink},
    AppState,
};
use axum::{
    extract::{MatchedPath, Path, Query, State},
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
const FORMAT: &str = "tracera-project-items-v1";
const MAX_ITEMS: i64 = 1000;
type Failure = (StatusCode, Json<Value>);
type Reply = Result<Json<Value>, Failure>;
fn error(status: StatusCode, code: &str) -> Failure {
    (status, Json(json!({"error":code})))
}
fn unsupported(path: &str) -> Failure {
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(json!({"error":"not_implemented","route":path})),
    )
}
fn store_error(e: StoreError, path: &str) -> Failure {
    match e {
        StoreError::UnsupportedOperation(_) => unsupported(path),
        StoreError::Database(_) | StoreError::Conflict(_) => {
            error(StatusCode::INTERNAL_SERVER_ERROR, "snapshot_store_error")
        }
    }
}
#[derive(Serialize, Deserialize)]
#[serde(deny_unknown_fields, rename_all = "camelCase")]
struct Snapshot {
    format: String,
    project_id: String,
    items: Vec<Item>,
    // These are artifact trace links, NOT the unavailable canonical item-link model.
    artifact_trace_links: Vec<TraceLink>,
}
#[derive(Default, Deserialize)]
#[serde(deny_unknown_fields)]
struct Options {
    format: Option<String>,
}
pub(super) fn routes() -> Router<AppState> {
    Router::new()
        .route(
            "/api/v1/projects/{project_id}/export",
            get(export).fallback(unavailable),
        )
        .route(
            "/api/v1/projects/{project_id}/import",
            post(project_import).fallback(unavailable),
        )
        .route("/api/v1/import", post(global_import).fallback(unavailable))
}
async fn unavailable(path: MatchedPath) -> Failure {
    unsupported(path.as_str())
}
async fn export(
    State(state): State<AppState>,
    Path(id): Path<String>,
    path: MatchedPath,
    Query(options): Query<Options>,
) -> Reply {
    if options
        .format
        .as_deref()
        .is_some_and(|f| f != FORMAT && f != "json")
    {
        return Err(unsupported(path.as_str()));
    }
    let page = state
        .store
        .list_items(
            ItemFilter {
                project_id: Some(id.clone()),
                ..Default::default()
            },
            MAX_ITEMS + 1,
            0,
        )
        .await
        .map_err(|e| store_error(e, path.as_str()))?;
    if page.total > MAX_ITEMS || page.items.len() as i64 != page.total {
        return Err(error(
            StatusCode::SERVICE_UNAVAILABLE,
            "snapshot_too_large_or_changed",
        ));
    }
    if page.items.is_empty()
        && state
            .store
            .get_project(id.clone())
            .await
            .map_err(|e| store_error(e, path.as_str()))?
            .is_none()
    {
        return Err(error(StatusCode::NOT_FOUND, "project_not_found"));
    }
    if page.items.is_empty() {
        return Err(unsupported(path.as_str()));
    }
    let ids: BTreeSet<_> = page.items.iter().map(|i| i.id.as_str()).collect();
    let mut links = BTreeMap::new();
    for item in &page.items {
        for link in state
            .store
            .list_trace_links_for_artifact(item.id.clone())
            .await
            .map_err(|e| store_error(e, path.as_str()))?
        {
            if !ids.contains(link.source_id.as_str())
                || !ids.contains(link.target_id.as_str())
                || link.created_at != link.updated_at
            {
                return Err(unsupported(path.as_str()));
            }
            links.insert(link.id.clone(), link);
        }
    }
    Ok(Json(json!(Snapshot {
        format: FORMAT.into(),
        project_id: id,
        items: page.items,
        artifact_trace_links: links.into_values().collect()
    })))
}
async fn project_import(
    State(state): State<AppState>,
    Path(id): Path<String>,
    path: MatchedPath,
    Json(snapshot): Json<Snapshot>,
) -> Reply {
    if id != snapshot.project_id {
        return Err(error(StatusCode::BAD_REQUEST, "project_id_mismatch"));
    }
    restore(state.store.as_ref(), snapshot, path.as_str()).await
}
async fn global_import(
    State(state): State<AppState>,
    path: MatchedPath,
    Json(snapshot): Json<Snapshot>,
) -> Reply {
    restore(state.store.as_ref(), snapshot, path.as_str()).await
}
async fn restore(store: &dyn Store, snapshot: Snapshot, path: &str) -> Reply {
    if snapshot.format != FORMAT {
        return Err(unsupported(path));
    }
    if snapshot.project_id.trim().is_empty()
        || snapshot.items.is_empty()
        || snapshot.items.len() > MAX_ITEMS as usize
    {
        return Err(error(
            StatusCode::BAD_REQUEST,
            "invalid_snapshot_size_or_project",
        ));
    }
    let mut ids = BTreeSet::new();
    for item in &snapshot.items {
        if item.project_id != snapshot.project_id
            || item.id.trim().is_empty()
            || !ids.insert(item.id.clone())
        {
            return Err(error(StatusCode::BAD_REQUEST, "invalid_or_duplicate_item"));
        }
    }
    let mut link_ids = BTreeSet::new();
    for link in &snapshot.artifact_trace_links {
        if link.id.trim().is_empty()
            || !link_ids.insert(&link.id)
            || !ids.contains(&link.source_id)
            || !ids.contains(&link.target_id)
            || !link.confidence.is_finite()
            || !(0.0..=1.0).contains(&link.confidence)
        {
            return Err(error(
                StatusCode::BAD_REQUEST,
                "invalid_or_duplicate_trace_link",
            ));
        }
        if link.created_at != link.updated_at {
            return Err(unsupported(path));
        }
    }
    // Preflight every item before writes. Imports are additive; never overwrite IDs.
    for item in &snapshot.items {
        if store
            .get_item(item.id.clone())
            .await
            .map_err(|e| store_error(e, path))?
            .is_some()
        {
            return Err(error(StatusCode::CONFLICT, "item_id_exists"));
        }
    }
    let mut imported_items = 0;
    let mut imported_links = 0;
    for item in snapshot.items {
        if let Err(e) = store.create_item(item).await {
            return Err(partial(e, path, imported_items, imported_links));
        }
        imported_items += 1;
    }
    for link in snapshot.artifact_trace_links {
        if let Err(e) = store
            .create_trace_link(
                link.id,
                link.source_id,
                link.target_id,
                link.relationship,
                link.confidence,
                link.source,
                link.created_at,
            )
            .await
        {
            return Err(partial(e, path, imported_items, imported_links));
        }
        imported_links += 1;
    }
    Ok(Json(
        json!({"projectId":snapshot.project_id,"importedItems":imported_items,"importedArtifactTraceLinks":imported_links}),
    ))
}
fn partial(e: StoreError, path: &str, items: usize, links: usize) -> Failure {
    if matches!(e, StoreError::UnsupportedOperation(_)) && items == 0 && links == 0 {
        return unsupported(path);
    }
    let (status, Json(mut body)) = store_error(e, path);
    body["importedItems"] = json!(items);
    body["importedArtifactTraceLinks"] = json!(links);
    body["atomic"] = json!(false);
    (status, Json(body))
}
#[cfg(test)]
mod tests {
    use super::*;
    use crate::sqlite_store::SqliteStore;
    use axum::body::{to_bytes, Body};
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
    fn item(id: &str, project: &str) -> Item {
        serde_json::from_value(
            json!({"id":id,"projectId":project,"view":"requirement","type":"requirement",
            "title":"Persisted requirement","status":"open","priority":"high","version":7,
            "createdAt":"2026-10-16T01:00:00Z","updatedAt":"2026-10-16T02:00:00Z",
            "metadata":{"custom":[1,2]},"description":"Preserve extensions"}),
        )
        .unwrap()
    }
    async fn seed(store: &dyn Store) {
        for (id, project) in [("a", "alpha"), ("b", "alpha"), ("c", "beta")] {
            store.create_item(item(id, project)).await.unwrap();
        }
        store
            .create_trace_link(
                "link".into(),
                "a".into(),
                "b".into(),
                "verifies".into(),
                0.75,
                "manual".into(),
                chrono::Utc::now(),
            )
            .await
            .unwrap();
    }
    async fn request(app: Router, method: &str, path: &str, body: Value) -> (StatusCode, Value) {
        let token = crate::middleware::issue_csrf_token().await;
        let response = app
            .oneshot(
                http::Request::builder()
                    .method(method)
                    .uri(path)
                    .header("origin", "http://127.0.0.1:18000")
                    .header("x-csrf-token", token)
                    .header("content-type", "application/json")
                    .body(Body::from(body.to_string()))
                    .unwrap(),
            )
            .await
            .unwrap();
        let status = response.status();
        let bytes = to_bytes(response.into_body(), 10 * 1024 * 1024)
            .await
            .unwrap();
        (
            status,
            serde_json::from_slice(&bytes)
                .unwrap_or_else(|_| json!({"raw":String::from_utf8_lossy(&bytes)})),
        )
    }
    #[tokio::test]
    async fn export_and_both_import_routes_round_trip_sqlite() {
        let (app, source) = fixture().await;
        seed(source.as_ref()).await;
        let (status, snapshot) =
            request(app, "GET", "/api/v1/projects/alpha/export", Value::Null).await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(snapshot["items"].as_array().unwrap().len(), 2);
        assert_eq!(snapshot["items"][0], json!(item("a", "alpha")));
        assert_eq!(snapshot["artifactTraceLinks"].as_array().unwrap().len(), 1);
        for route in ["/api/v1/projects/alpha/import", "/api/v1/import"] {
            let (target, store) = fixture().await;
            let (status, result) = request(target.clone(), "POST", route, snapshot.clone()).await;
            assert_eq!(status, StatusCode::OK, "{result}");
            assert_eq!(result["importedItems"], 2);
            assert_eq!(result["importedArtifactTraceLinks"], 1);
            let (status, restored) = request(
                target.clone(),
                "GET",
                "/api/v1/projects/alpha/export",
                Value::Null,
            )
            .await;
            assert_eq!(status, StatusCode::OK);
            assert_eq!(restored, snapshot);
            assert!(store.get_item("c".into()).await.unwrap().is_none());
            assert_eq!(
                request(target, "POST", route, snapshot.clone()).await.0,
                StatusCode::CONFLICT
            );
        }
    }
    #[tokio::test]
    async fn invalid_imports_do_not_write() {
        let (app, source) = fixture().await;
        seed(source.as_ref()).await;
        let (_, snapshot) = request(app, "GET", "/api/v1/projects/alpha/export", Value::Null).await;
        let (target, store) = fixture().await;
        let mut invalid = snapshot.clone();
        invalid["items"][1]["projectId"] = json!("beta");
        assert_eq!(
            request(target.clone(), "POST", "/api/v1/import", invalid)
                .await
                .0,
            StatusCode::BAD_REQUEST
        );
        let mut duplicate = snapshot.clone();
        duplicate["items"][1]["id"] = json!("a");
        assert_eq!(
            request(target.clone(), "POST", "/api/v1/import", duplicate)
                .await
                .0,
            StatusCode::BAD_REQUEST
        );
        let mut dangling = snapshot.clone();
        dangling["artifactTraceLinks"][0]["target_id"] = json!("absent");
        assert_eq!(
            request(target.clone(), "POST", "/api/v1/import", dangling)
                .await
                .0,
            StatusCode::BAD_REQUEST
        );
        assert_eq!(
            request(
                target.clone(),
                "POST",
                "/api/v1/projects/beta/import",
                snapshot.clone()
            )
            .await
            .0,
            StatusCode::BAD_REQUEST
        );
        let mut unknown = snapshot;
        unknown["ignored"] = json!(true);
        assert_eq!(
            request(target, "POST", "/api/v1/import", unknown).await.0,
            StatusCode::UNPROCESSABLE_ENTITY
        );
        assert!(store.get_item("a".into()).await.unwrap().is_none());
    }
    #[tokio::test]
    async fn unsupported_shapes_return_exact_template_501() {
        let (app, store) = fixture().await;
        seed(store.as_ref()).await;
        let (_, mut snapshot) = request(
            app.clone(),
            "GET",
            "/api/v1/projects/alpha/export",
            Value::Null,
        )
        .await;
        snapshot["format"] = json!("csv");
        for (method, route, template, body) in [
            (
                "GET",
                "/api/v1/projects/alpha/export?format=csv",
                "/api/v1/projects/{project_id}/export",
                Value::Null,
            ),
            (
                "POST",
                "/api/v1/projects/alpha/export",
                "/api/v1/projects/{project_id}/export",
                Value::Null,
            ),
            (
                "POST",
                "/api/v1/projects/alpha/import",
                "/api/v1/projects/{project_id}/import",
                snapshot.clone(),
            ),
            ("POST", "/api/v1/import", "/api/v1/import", snapshot.clone()),
        ] {
            let (status, body) = request(app.clone(), method, route, body).await;
            assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
            assert_eq!(body, json!({"error":"not_implemented","route":template}));
        }
        store
            .create_trace_link(
                "boundary".into(),
                "a".into(),
                "c".into(),
                "relates".into(),
                1.0,
                "manual".into(),
                chrono::Utc::now(),
            )
            .await
            .unwrap();
        let (status, body) =
            request(app, "GET", "/api/v1/projects/alpha/export", Value::Null).await;
        assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
        assert_eq!(
            body,
            json!({"error":"not_implemented","route":"/api/v1/projects/{project_id}/export"})
        );
    }
    #[tokio::test]
    async fn failed_import_reports_actual_partial_writes() {
        let (app, source) = fixture().await;
        seed(source.as_ref()).await;
        let (_, snapshot) = request(app, "GET", "/api/v1/projects/alpha/export", Value::Null).await;
        let (target, store) = fixture().await;
        sqlx::query("CREATE TRIGGER fail_second BEFORE INSERT ON items WHEN NEW.id = 'b' BEGIN SELECT RAISE(ABORT, 'test failure'); END")
            .execute(&store.pool).await.unwrap();
        let (status, body) = request(target, "POST", "/api/v1/import", snapshot).await;
        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
        assert_eq!(body["importedItems"], 1);
        assert_eq!(body["importedArtifactTraceLinks"], 0);
        assert_eq!(body["atomic"], false);
        assert!(store.get_item("a".into()).await.unwrap().is_some());
        assert!(store.get_item("b".into()).await.unwrap().is_none());
    }
    #[tokio::test]
    async fn missing_project_and_store_failures_are_not_empty_success() {
        let (app, store) = fixture().await;
        assert_eq!(
            request(
                app.clone(),
                "GET",
                "/api/v1/projects/missing/export",
                Value::Null
            )
            .await
            .0,
            StatusCode::NOT_FOUND
        );
        store.pool.close().await;
        assert_eq!(
            request(app, "GET", "/api/v1/projects/alpha/export", Value::Null)
                .await
                .0,
            StatusCode::INTERNAL_SERVER_ERROR
        );
    }
}
