//! Unavailable events operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &["/api/v1/events", "/api/v1/events/{id}"];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
