//! Unavailable docs operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &["/api/v1/docs", "/api/v1/docs/search", "/api/v1/docs/{id}"];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
