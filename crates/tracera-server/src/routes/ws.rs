//! Unavailable ws operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &["/api/v1/ws"];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
