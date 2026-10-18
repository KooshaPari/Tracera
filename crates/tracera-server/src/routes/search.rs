//! Title substring search over persisted items, with explicit unavailable index APIs.
//! SQLite LIKE folds ASCII case only. Results use stable item-id order, not relevance.
use crate::{item::ItemPage, store::StoreError, AppState};
use axum::{
    extract::{MatchedPath, Query, State},
    http::StatusCode,
    routing::{any, get},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::time::Duration;

type Reply = Result<Json<Value>, (StatusCode, Json<Value>)>;

pub(super) fn router() -> Router<AppState> {
    Router::new()
        .route(
            "/api/v1/search",
            get(search_get).post(search_post).fallback(unsupported),
        )
        .route("/api/v1/search/suggest", get(suggest).fallback(unsupported))
        .route("/api/v1/search/index/{id}", any(unsupported))
        .route("/api/v1/search/batch-index", any(unsupported))
        .route("/api/v1/search/reindex", any(unsupported))
        .route("/api/v1/search/stats", any(unsupported))
        .route("/api/v1/search/health", any(unsupported))
}

#[derive(Serialize)]
struct Unavailable {
    error: &'static str,
    route: String,
}
async fn unsupported(path: MatchedPath) -> (StatusCode, Json<Unavailable>) {
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(Unavailable {
            error: "not_implemented",
            route: path.as_str().to_owned(),
        }),
    )
}

fn error(status: StatusCode, code: &str) -> (StatusCode, Json<Value>) {
    (status, Json(json!({"error":code})))
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct SearchParams {
    q: String,
    page: Option<i64>,
    per_page: Option<i64>,
    #[serde(rename = "projectId", alias = "project_id")]
    project_id: Option<String>,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct SuggestParams {
    q: String,
    limit: Option<i64>,
}
async fn query(
    state: &AppState,
    q: String,
    project: Option<String>,
    limit: i64,
    offset: i64,
    route: &str,
) -> Result<ItemPage, (StatusCode, Json<Value>)> {
    let q = q.trim();
    if q.is_empty() || q.len() > 256 || !(1..=100).contains(&limit) || offset < 0 {
        return Err(error(StatusCode::BAD_REQUEST, "invalid_search_parameters"));
    }
    if offset > 100_000 {
        return Err(error(
            StatusCode::SERVICE_UNAVAILABLE,
            "search_query_over_budget",
        ));
    }
    tokio::time::timeout(
        Duration::from_secs(2),
        state.store.search_items(q.into(), project, limit, offset),
    )
    .await
    .map_err(|_| error(StatusCode::SERVICE_UNAVAILABLE, "search_query_over_budget"))?
    .map_err(|e| match e {
        StoreError::UnsupportedOperation(_) => (
            StatusCode::NOT_IMPLEMENTED,
            Json(json!({"error":"not_implemented","route":route})),
        ),
        StoreError::Database(_) => error(StatusCode::INTERNAL_SERVER_ERROR, "search_store_error"),
    })
}
async fn search_get(State(state): State<AppState>, Query(params): Query<SearchParams>) -> Reply {
    search(&state, params).await
}
async fn search_post(State(state): State<AppState>, Json(params): Json<SearchParams>) -> Reply {
    search(&state, params).await
}
async fn search(state: &AppState, params: SearchParams) -> Reply {
    let page = params.page.unwrap_or(1);
    let size = params.per_page.unwrap_or(50);
    if page < 1 || !(1..=100).contains(&size) {
        return Err(error(StatusCode::BAD_REQUEST, "invalid_search_parameters"));
    }
    let offset = (page - 1)
        .checked_mul(size)
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "invalid_search_parameters"))?;
    let result = query(
        state,
        params.q,
        params.project_id,
        size,
        offset,
        "/api/v1/search",
    )
    .await?;
    Ok(Json(
        json!({"items":result.items,"total":result.total,"page":page,
        "pageSize":size,"hasMore":offset + size < result.total}),
    ))
}
async fn suggest(State(state): State<AppState>, Query(params): Query<SuggestParams>) -> Reply {
    let result = query(
        &state,
        params.q,
        None,
        params.limit.unwrap_or(10),
        0,
        "/api/v1/search/suggest",
    )
    .await?;
    let mut titles = Vec::new();
    for item in result.items {
        if !titles.contains(&item.title) {
            titles.push(item.title);
        }
    }
    Ok(Json(json!(titles)))
}

pub(crate) const ROUTES: &[&str] = &["/api/v1/projects/{project_id}/search/advanced"];


pub(crate) fn w9_routes() -> Router<AppState> {
    Router::new().route(ROUTES[0], any(crate::not_implemented::not_implemented))
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::{item::Item, sqlite_store::SqliteStore, store::Store};
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
        for (id, project, title) in [
            ("a", "alpha", "Persisted Search"),
            ("b", "beta", "Search another project"),
            ("c", "alpha", "100%_literal!"),
            ("d", "alpha", "Unrelated title"),
        ] {
            let item: Item = serde_json::from_value(json!({"id":id,"projectId":project,
                "title":title,"view":"requirement","type":"requirement","status":"todo",
                "priority":"high","version":1,"createdAt":"2026-10-16T00:00:00Z",
                "updatedAt":"2026-10-16T00:00:00Z","description":"search description only"}))
            .unwrap();
            store.create_item(item).await.unwrap();
        }
        let app = crate::router::build_router(AppState {
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
        });
        (app, store)
    }
    async fn request(app: Router, method: &str, path: &str, body: Value) -> (StatusCode, Value) {
        let token = crate::middleware::issue_csrf_token().await;
        let response = app
            .oneshot(
                Request::builder()
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
        if status != StatusCode::BAD_REQUEST {
            assert!(response.headers()["content-type"]
                .to_str()
                .unwrap()
                .starts_with("application/json"));
        }
        let bytes = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
        (
            status,
            serde_json::from_slice(&bytes).unwrap_or(Value::Null),
        )
    }
    #[tokio::test]
    async fn get_and_post_search_use_persisted_titles_and_pagination() {
        let (app, store) = fixture().await;
        let (status, first) = request(
            app.clone(),
            "GET",
            "/api/v1/search?q=SEARCH&per_page=1",
            Value::Null,
        )
        .await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(first["total"], 2);
        assert_eq!(first["page"], 1);
        assert_eq!(first["pageSize"], 1);
        assert_eq!(first["hasMore"], true);
        assert_eq!(
            first["items"][0],
            serde_json::to_value(store.get_item("a".into()).await.unwrap().unwrap()).unwrap()
        );
        let (status, second) = request(
            app.clone(),
            "POST",
            "/api/v1/search",
            json!({"q":"search","page":2,"per_page":1}),
        )
        .await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(second["items"][0]["id"], "b");
        assert_eq!(second["hasMore"], false);
        let (_, scoped) = request(
            app.clone(),
            "GET",
            "/api/v1/search?q=search&projectId=alpha",
            Value::Null,
        )
        .await;
        assert_eq!(scoped["total"], 1);
        assert_eq!(scoped["items"][0]["id"], "a");
        let (_, absent) = request(app, "GET", "/api/v1/search?q=description", Value::Null).await;
        assert_eq!(absent["total"], 0);
        assert_eq!(absent["items"], json!([]));
    }
    #[tokio::test]
    async fn suggestions_are_persisted_titles_with_a_bound() {
        let (app, _) = fixture().await;
        let (status, body) = request(
            app.clone(),
            "GET",
            "/api/v1/search/suggest?q=sEaRcH&limit=1",
            Value::Null,
        )
        .await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(body, json!(["Persisted Search"]));
        let (status, body) =
            request(app, "GET", "/api/v1/search/suggest?q=absent", Value::Null).await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(body, json!([]));
    }
    #[tokio::test]
    async fn wildcards_and_sql_input_are_literal() {
        let (app, _) = fixture().await;
        for q in ["%25", "_", "%21", "100%25_literal%21"] {
            let (status, body) = request(
                app.clone(),
                "GET",
                &format!("/api/v1/search?q={q}"),
                Value::Null,
            )
            .await;
            assert_eq!(status, StatusCode::OK);
            assert_eq!(body["total"], 1);
            assert_eq!(body["items"][0]["id"], "c");
        }
        let (_, body) = request(app, "POST", "/api/v1/search", json!({"q":"' OR 1=1 --"})).await;
        assert_eq!(body["total"], 0);
    }
    #[tokio::test]
    async fn all_five_unavailable_routes_return_exact_template_501() {
        let (app, _) = fixture().await;
        for (method, path, template) in [
            (
                "POST",
                "/api/v1/search/index/secret-id?ignored=1",
                "/api/v1/search/index/{id}",
            ),
            (
                "POST",
                "/api/v1/search/batch-index",
                "/api/v1/search/batch-index",
            ),
            ("POST", "/api/v1/search/reindex", "/api/v1/search/reindex"),
            ("GET", "/api/v1/search/stats", "/api/v1/search/stats"),
            ("GET", "/api/v1/search/health", "/api/v1/search/health"),
        ] {
            let (status, body) = request(app.clone(), method, path, Value::Null).await;
            assert_eq!(status, StatusCode::NOT_IMPLEMENTED, "{path}");
            assert_eq!(body, json!({"error":"not_implemented","route":template}));
        }
    }
    #[tokio::test]
    async fn invalid_parameters_fail_before_querying() {
        let (app, _) = fixture().await;
        for path in [
            "/api/v1/search?q=",
            "/api/v1/search?q=%20",
            "/api/v1/search?q=x&page=0",
            "/api/v1/search?q=x&per_page=101",
            "/api/v1/search?q=x&per_page=0",
            "/api/v1/search?q=x&page=9223372036854775807",
            "/api/v1/search?q=x&unknown=1",
            "/api/v1/search/suggest?q=x&limit=0",
            "/api/v1/search/suggest?q=x&limit=101",
        ] {
            assert_eq!(
                request(app.clone(), "GET", path, Value::Null).await.0,
                StatusCode::BAD_REQUEST,
                "{path}"
            );
        }
        assert_eq!(
            request(
                app,
                "GET",
                "/api/v1/search?q=x&page=100002&per_page=1",
                Value::Null
            )
            .await
            .0,
            StatusCode::SERVICE_UNAVAILABLE
        );
    }
    #[tokio::test]
    async fn failures_and_timeouts_are_not_empty_successes() {
        let (app, store) = fixture().await;
        let connection = store.pool.acquire().await.unwrap();
        let (status, body) =
            request(app.clone(), "GET", "/api/v1/search?q=search", Value::Null).await;
        assert_eq!(status, StatusCode::SERVICE_UNAVAILABLE);
        assert_eq!(body["error"], "search_query_over_budget");
        drop(connection);
        store.pool.close().await;
        for path in ["/api/v1/search?q=search", "/api/v1/search/suggest?q=search"] {
            let (status, body) = request(app.clone(), "GET", path, Value::Null).await;
            assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
            assert_eq!(body, json!({"error":"search_store_error"}));
        }
    }
    #[tokio::test]
    async fn empty_database_and_out_of_range_page_are_real_empty_results() {
        let (app, store) = fixture().await;
        let (status, body) = request(
            app.clone(),
            "GET",
            "/api/v1/search?q=search&page=3&per_page=1",
            Value::Null,
        )
        .await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(body["total"], 2);
        assert_eq!(body["items"], json!([]));
        assert_eq!(body["hasMore"], false);
        sqlx::query("DELETE FROM items")
            .execute(&store.pool)
            .await
            .unwrap();
        let (status, body) = request(app, "GET", "/api/v1/search?q=search", Value::Null).await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(body["total"], 0);
        assert_eq!(body["items"], json!([]));
    }
    #[tokio::test]
    async fn unsupported_backend_fails_closed_without_connecting() {
        let pool = sqlx::postgres::PgPoolOptions::new()
            .connect_lazy("postgres://localhost/unused")
            .unwrap();
        let app = crate::router::build_router(AppState {
            store: Arc::new(crate::pg_store::PgStore::new(pool)),
            version: "test".into(),
            backend: "postgres",
            started_at: Instant::now(),
            workos_client: tracera_workos::WorkOSClient::default_for_router(),
            cache: None,
            neo4j: None,
            r2: None,
            frontend: crate::FrontendState::Ok,
            frontend_dist: std::path::PathBuf::new(),
        });
        for route in ["/api/v1/search", "/api/v1/search/suggest"] {
            let (status, body) = request(
                app.clone(),
                "GET",
                &format!("{route}?q=search"),
                Value::Null,
            )
            .await;
            assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
            assert_eq!(body, json!({"error":"not_implemented","route":route}));
        }
    }
}