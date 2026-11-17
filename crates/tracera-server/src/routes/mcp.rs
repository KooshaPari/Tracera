//! Unavailable mcp operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &["/api/v1/mcp/config"];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
