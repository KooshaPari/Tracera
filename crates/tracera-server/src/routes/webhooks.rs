//! Unavailable webhooks operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/webhooks/stats",
    "/api/v1/webhooks",
    "/api/v1/webhooks/{id}",
    "/api/v1/webhooks/{id}/logs",
    "/api/v1/webhooks/{id}/regenerate-secret",
    "/api/v1/webhooks/{id}/status",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
