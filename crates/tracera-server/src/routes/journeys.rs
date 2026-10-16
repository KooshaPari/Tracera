//! Read persisted journey Items through Store. No client-derived journeys or steps.
//! The canonical Item document is preserved; name aliases title for journey clients.
//! Steps require explicit persisted steps; absence means unavailable, never empty success.
use crate::{
    item::{Item, ItemFilter},
    store::{StoreError, StoreResult},
    AppState,
};
use axum::{
    extract::{MatchedPath, Path, Query, State},
    http::StatusCode,
    routing::{any, get},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{collections::HashMap, future::Future, time::Duration};
type Failure = (StatusCode, Json<Value>);
type Reply = Result<Json<Value>, Failure>;
fn error(status: StatusCode, code: &str) -> Failure {
    (status, Json(json!({"error":code})))
}
#[derive(Serialize)]
struct Unavailable {
    error: &'static str,
    route: String,
}
async fn unavailable(path: MatchedPath) -> (StatusCode, Json<Unavailable>) {
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(Unavailable {
            error: "not_implemented",
            route: path.as_str().into(),
        }),
    )
}
fn unsupported(path: &MatchedPath) -> Failure {
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(json!({"error":"not_implemented", "route":path.as_str()})),
    )
}
async fn read<T>(work: impl Future<Output = StoreResult<T>>) -> Result<T, Failure> {
    tokio::time::timeout(Duration::from_secs(2), work)
        .await
        .map_err(|_| {
            error(
                StatusCode::SERVICE_UNAVAILABLE,
                "journeys_query_over_budget",
            )
        })?
        .map_err(|e| match e {
            StoreError::UnsupportedOperation(_) => {
                error(StatusCode::NOT_IMPLEMENTED, "not_implemented")
            }
            StoreError::Database(_) => {
                error(StatusCode::INTERNAL_SERVER_ERROR, "journeys_store_error")
            }
        })
}
#[derive(Default, Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    project_id: Option<String>,
    #[serde(rename = "type")]
    kind: Option<String>,
}
fn is_journey(i: &Item) -> bool {
    i.item_type.eq_ignore_ascii_case("journey")
}
fn document(i: &Item) -> Value {
    let mut value = serde_json::to_value(i).expect("Item serializes");
    value["name"] = i
        .extra
        .get("name")
        .cloned()
        .unwrap_or_else(|| json!(i.title));
    value
}
async fn listing(
    State(state): State<AppState>,
    Path(ids): Path<HashMap<String, String>>,
    Query(p): Query<Params>,
    path: MatchedPath,
) -> Reply {
    let project = ids
        .get("project_id")
        .cloned()
        .or_else(|| p.project_id.clone());
    if ids
        .get("project_id")
        .zip(p.project_id.as_ref())
        .is_some_and(|(a, b)| a != b)
    {
        return Err(error(StatusCode::BAD_REQUEST, "project_id_mismatch"));
    }
    let filter = ItemFilter {
        project_id: project.clone(),
        ..Default::default()
    };
    let work = async {
        let mut items = Vec::new();
        let mut offset = 0;
        loop {
            let page = state.store.list_items(filter.clone(), 100, offset).await?;
            if page.total > 100_000 {
                return Err(StoreError::Database("query budget exceeded".into()));
            }
            let count = page.items.len();
            offset += count as i64;
            items.extend(page.items);
            if offset >= page.total {
                break;
            }
            if count == 0 {
                return Err(StoreError::Database("incomplete journey read".into()));
            }
        }
        if items.is_empty() {
            if let Some(project) = project {
                if state.store.get_project(project).await?.is_none() {
                    return Ok(None);
                }
            }
        }
        Ok(Some(items))
    };
    let all = read(work)
        .await
        .map_err(|e| {
            if e.0 == StatusCode::NOT_IMPLEMENTED {
                unsupported(&path)
            } else {
                e
            }
        })?
        .ok_or_else(|| error(StatusCode::NOT_FOUND, "project_not_found"))?;
    let journeys: Vec<_> = all
        .iter()
        .filter(|i| is_journey(i))
        .filter(|i| {
            p.kind
                .as_ref()
                .is_none_or(|kind| i.extra.get("journeyType").and_then(Value::as_str) == Some(kind))
        })
        .map(document)
        .collect();
    Ok(Json(json!(journeys)))
}
async fn detail(
    State(state): State<AppState>,
    Path(ids): Path<HashMap<String, String>>,
    path: MatchedPath,
) -> Reply {
    let id = ids.get("id").expect("journey route has id");
    let item = read(state.store.get_item(id.clone()))
        .await
        .map_err(|e| {
            if e.0 == StatusCode::NOT_IMPLEMENTED {
                unsupported(&path)
            } else {
                e
            }
        })?
        .filter(is_journey)
        .filter(|i| ids.get("project_id").is_none_or(|p| p == &i.project_id))
        .ok_or_else(|| error(StatusCode::NOT_FOUND, "journey_not_found"))?;
    if !path.as_str().contains("/steps") {
        return Ok(Json(document(&item)));
    }
    let steps = item
        .extra
        .get("steps")
        .and_then(Value::as_array)
        .ok_or_else(|| unsupported(&path))?;
    // Explicit empty arrays are known-empty. Missing/invalid observations never become [].
    if steps.iter().any(|s| {
        s.get("itemId").and_then(Value::as_str).is_none()
            || s.get("order").and_then(Value::as_u64).is_none()
    }) {
        return Err(unsupported(&path));
    }
    let mut steps = steps.clone();
    steps.sort_by_key(|s| s["order"].as_u64());
    if let Some(step) = ids.get("step_id") {
        return steps
            .into_iter()
            .find(|s| s["itemId"].as_str() == Some(step))
            .map(Json)
            .ok_or_else(|| error(StatusCode::NOT_FOUND, "journey_step_not_found"));
    }
    Ok(Json(json!(steps)))
}
pub(super) fn routes() -> Router<AppState> {
    let mut router = Router::new();
    for prefix in ["/api/v1", "/api/v1/projects/{project_id}"] {
        router = router.route(
            &format!("{prefix}/journeys"),
            get(listing).fallback(unavailable),
        );
        for suffix in ["/{id}", "/{id}/steps", "/{id}/steps/{step_id}"] {
            router = router.route(
                &format!("{prefix}/journeys{suffix}"),
                get(detail).fallback(unavailable),
            );
        }
        for suffix in ["/{id}/detect", "/{id}/visualize"] {
            router = router.route(&format!("{prefix}/journeys{suffix}"), any(unavailable));
        }
    }
    router
}
#[cfg(test)]
mod tests {
    use super::*;
    use crate::{sqlite_store::SqliteStore, store::Store};
    use axum::{
        body::{to_bytes, Body},
        http::Request,
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
        for (id, project, kind) in [
            ("j", "P", "journey"),
            ("other", "OTHER", "journey"),
            ("wrong", "P", "requirement"),
            ("missing-steps", "P", "journey"),
        ] {
            let mut item:Item=serde_json::from_value(json!({"id":id,"projectId":project,"type":kind,
                "view":"journey","title":"Stored journey","status":"active","priority":"high","version":1,
                "createdAt":"2026-10-16","updatedAt":"2026-10-16","journeyType":"user"})).unwrap();
            if id == "j" {
                item.extra.insert("steps".into(),json!((0..124).rev().map(|n|json!({"itemId":format!("step-{n}"),"order":n,"description":"Persisted step"})).collect::<Vec<_>>()));
            }
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
    async fn request(app: Router, method: &str, uri: &str) -> (StatusCode, Value) {
        let token = crate::middleware::issue_csrf_token().await;
        let r = app
            .oneshot(
                Request::builder()
                    .method(method)
                    .uri(uri)
                    .header("origin", "http://127.0.0.1:18000")
                    .header("x-csrf-token", token)
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        let status = r.status();
        let bytes = to_bytes(r.into_body(), 1024 * 1024).await.unwrap();
        let body = serde_json::from_slice(&bytes)
            .unwrap_or_else(|_| json!({"raw": String::from_utf8_lossy(&bytes)}));
        (status, body)
    }
    #[tokio::test]
    async fn reads_all_persisted_steps_and_scopes_every_alias() {
        let (app, store) = fixture().await;
        for prefix in ["/api/v1", "/api/v1/projects/P"] {
            let (status, body) = request(
                app.clone(),
                "GET",
                &format!("{prefix}/journeys?project_id=P&type=user"),
            )
            .await;
            assert_eq!(status, StatusCode::OK, "{body}");
            assert_eq!(body.as_array().unwrap().len(), 2);
            assert!(body
                .as_array()
                .unwrap()
                .iter()
                .all(|j| j["projectId"] == "P"));
            let (status, body) = request(app.clone(), "GET", &format!("{prefix}/journeys/j")).await;
            assert_eq!(status, StatusCode::OK);
            assert_eq!(
                body,
                document(&store.get_item("j".into()).await.unwrap().unwrap())
            );
            let (status, body) =
                request(app.clone(), "GET", &format!("{prefix}/journeys/j/steps")).await;
            assert_eq!(status, StatusCode::OK);
            assert_eq!(body.as_array().unwrap().len(), 124);
            assert_eq!(body[0]["itemId"], "step-0");
            assert_eq!(body[123]["order"], 123);
            let (status, body) = request(
                app.clone(),
                "GET",
                &format!("{prefix}/journeys/j/steps/step-123"),
            )
            .await;
            assert_eq!(status, StatusCode::OK);
            assert_eq!(body["description"], "Persisted step");
        }
        assert_eq!(
            request(app.clone(), "GET", "/api/v1/journeys")
                .await
                .1
                .as_array()
                .unwrap()
                .len(),
            3
        );
        for uri in [
            "/api/v1/journeys/wrong",
            "/api/v1/journeys/absent",
            "/api/v1/projects/OTHER/journeys/j",
            "/api/v1/projects/OTHER/journeys/j/steps",
            "/api/v1/journeys/j/steps/absent",
            "/api/v1/projects/absent/journeys",
        ] {
            assert_eq!(
                request(app.clone(), "GET", uri).await.0,
                StatusCode::NOT_FOUND,
                "{uri}"
            );
        }
        for uri in [
            "/api/v1/journeys?unknown=x",
            "/api/v1/projects/P/journeys?project_id=OTHER",
        ] {
            assert_eq!(
                request(app.clone(), "GET", uri).await.0,
                StatusCode::BAD_REQUEST
            );
        }
    }
    #[tokio::test]
    async fn every_unavailable_operation_has_exact_template_contract() {
        let (app, _) = fixture().await;
        for prefix in ["/api/v1", "/api/v1/projects/{project_id}"] {
            for (suffix, method) in [
                ("", "POST"),
                ("/{id}", "PATCH"),
                ("/{id}", "DELETE"),
                ("/{id}", "PUT"),
                ("/{id}/steps", "POST"),
                ("/{id}/steps/{step_id}", "PUT"),
                ("/{id}/detect", "POST"),
                ("/{id}/visualize", "GET"),
            ] {
                let template = format!("{prefix}/journeys{suffix}");
                let uri = template
                    .replace("{project_id}", "P")
                    .replace("{id}", "j")
                    .replace("{step_id}", "step-0");
                let (status, body) = request(app.clone(), method, &uri).await;
                assert_eq!(status, StatusCode::NOT_IMPLEMENTED, "{uri}: {body}");
                assert_eq!(body, json!({"error":"not_implemented","route":template}));
            }
            for suffix in ["/{id}/steps", "/{id}/steps/{step_id}"] {
                let template = format!("{prefix}/journeys{suffix}");
                let uri = template
                    .replace("{project_id}", "P")
                    .replace("{id}", "missing-steps")
                    .replace("{step_id}", "x");
                let (status, body) = request(app.clone(), "GET", &uri).await;
                assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
                assert_eq!(body, json!({"error":"not_implemented","route":template}));
            }
        }
    }
    #[tokio::test]
    async fn persistence_failures_never_report_empty_success() {
        let (app, store) = fixture().await;
        let conn = store.pool.acquire().await.unwrap();
        assert_eq!(
            request(app.clone(), "GET", "/api/v1/journeys").await.0,
            StatusCode::SERVICE_UNAVAILABLE
        );
        drop(conn);
        store.pool.close().await;
        for uri in [
            "/api/v1/journeys",
            "/api/v1/journeys/j",
            "/api/v1/journeys/j/steps",
            "/api/v1/projects/P/journeys",
        ] {
            let (status, body) = request(app.clone(), "GET", uri).await;
            assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
            assert_eq!(body["error"], "journeys_store_error");
        }
    }
    #[tokio::test]
    async fn pagination_reads_journeys_beyond_the_first_store_page() {
        let (app, store) = fixture().await;
        let original = store.get_item("j".into()).await.unwrap().unwrap();
        for n in 0..105 {
            let mut item = original.clone();
            item.id = format!("a-{n:03}");
            item.item_type = "requirement".into();
            store.create_item(item).await.unwrap();
        }
        let (status, body) = request(app, "GET", "/api/v1/projects/P/journeys").await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(body.as_array().unwrap().len(), 2);
    }
    #[tokio::test]
    async fn explicit_empty_steps_and_malformed_steps_are_distinct() {
        let (app, store) = fixture().await;
        let original = store.get_item("j".into()).await.unwrap().unwrap();
        for (id, steps) in [
            ("empty", json!([])),
            ("invalid", json!([{"itemId":"x"}])),
            ("wrong-order", json!([{"itemId":"x","order":-1}])),
        ] {
            let mut item = original.clone();
            item.id = id.into();
            item.extra.insert("steps".into(), steps);
            store.create_item(item).await.unwrap();
        }
        let (status, body) = request(app.clone(), "GET", "/api/v1/journeys/empty/steps").await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(body, json!([]));
        for id in ["invalid", "wrong-order"] {
            let (status, body) =
                request(app.clone(), "GET", &format!("/api/v1/journeys/{id}/steps")).await;
            assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
            assert_eq!(
                body,
                json!({"error":"not_implemented","route":"/api/v1/journeys/{id}/steps"})
            );
        }
    }
}
