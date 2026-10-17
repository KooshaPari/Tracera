//! Canonical items persisted through Store; no synthetic SWEE projections.
//! Queries use SQL pagination and a two-second store budget. Mutations and
//! equivalence navigation remain typed 501 until their semantics exist.
use crate::{item::ItemFilter, store::StoreResult, AppState};
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::Deserialize;
use serde_json::{json, Value};
use std::{future::Future, time::Duration};

type Reply = Result<Json<Value>, (StatusCode, Json<Value>)>;
fn error(status: StatusCode, code: &str) -> (StatusCode, Json<Value>) {
    (status, Json(json!({"error":code})))
}
#[derive(Default, Deserialize)]
#[serde(deny_unknown_fields)]
pub(super) struct Params {
    limit: Option<i64>,
    offset: Option<i64>,
    project_id: Option<String>,
    status: Option<String>,
    view: Option<String>,
    priority: Option<String>,
}
impl Params {
    fn validate(&self) -> Result<(i64, i64), (StatusCode, Json<Value>)> {
        let limit = self.limit.unwrap_or(50);
        let offset = self.offset.unwrap_or(0);
        if !(1..=100).contains(&limit) {
            return Err(error(StatusCode::BAD_REQUEST, "limit_must_be_1_to_100"));
        }
        if offset < 0 {
            return Err(error(StatusCode::BAD_REQUEST, "offset_must_be_nonnegative"));
        }
        // Bound expensive deep-offset scans independently of response size.
        if offset > 100_000 {
            return Err(error(
                StatusCode::SERVICE_UNAVAILABLE,
                "items_query_over_budget",
            ));
        }
        Ok((limit, offset))
    }
    fn filter(self) -> ItemFilter {
        ItemFilter {
            project_id: self.project_id,
            status: self.status,
            view: self.view,
            priority: self.priority,
        }
    }
}
async fn bounded<T>(
    future: impl Future<Output = StoreResult<T>>,
) -> Result<T, (StatusCode, Json<Value>)> {
    tokio::time::timeout(Duration::from_secs(2), future)
        .await
        .map_err(|_| error(StatusCode::SERVICE_UNAVAILABLE, "items_query_over_budget"))?
        .map_err(|_| error(StatusCode::INTERNAL_SERVER_ERROR, "items_store_error"))
}
pub(super) async fn list(State(state): State<AppState>, Query(p): Query<Params>) -> Reply {
    listing(&state, p).await
}
async fn listing(state: &AppState, p: Params) -> Reply {
    let (limit, offset) = p.validate()?;
    let page = bounded(state.store.list_items(p.filter(), limit, offset)).await?;
    Ok(Json(
        json!({"items":page.items, "total":page.total, "limit":limit,
        "offset":offset, "has_more":offset.saturating_add(page.items.len() as i64) < page.total,
        "store":"items"}),
    ))
}
pub(super) async fn get(State(state): State<AppState>, Path(id): Path<String>) -> Reply {
    let item = bounded(state.store.get_item(id))
        .await?
        .ok_or_else(|| error(StatusCode::NOT_FOUND, "item_not_found"))?;
    Ok(Json(json!(item)))
}
pub(super) async fn project_list(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Query(mut p): Query<Params>,
) -> Reply {
    p.validate()?;
    if p.project_id.as_ref().is_some_and(|query| query != &id) {
        return Err(error(StatusCode::BAD_REQUEST, "project_id_mismatch"));
    }
    let project = bounded(state.store.get_project(id.clone())).await?;
    if project.is_none() {
        let existing = bounded(state.store.list_items(
            ItemFilter {
                project_id: Some(id.clone()),
                ..Default::default()
            },
            1,
            0,
        ))
        .await?;
        if existing.total == 0 {
            return Err(error(StatusCode::NOT_FOUND, "project_not_found"));
        }
    }
    p.project_id = Some(id);
    listing(&state, p).await
}

#[cfg(test)]
#[path = "items_tests.rs"]
mod tests;

// W9 unavailable routes (generated).
pub(super) const W9_ROUTES: &[&str] = &[
    "/api/v1/items/stream",
    "/items/{param2}/pivot",
    "/items/{param2}/pivot-targets",
];
pub(super) fn w9_routes() -> axum::Router<AppState> {
    super::w9_routes::unavailable_routes(W9_ROUTES)
}
