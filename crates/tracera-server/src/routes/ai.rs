//! Unavailable ai operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &["/api/v1/ai/analyze", "/api/v1/ai/stream-chat"];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
