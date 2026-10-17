//! Unavailable notifications operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/notifications",
    "/api/v1/notifications/read-all",
    "/api/v1/notifications/stream",
    "/api/v1/notifications/{id}",
    "/api/v1/notifications/{id}/read",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
