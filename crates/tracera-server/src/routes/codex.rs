//! Unavailable codex operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/codex/interactions",
    "/api/v1/projects/{project_id}/codex/review-image",
    "/api/v1/projects/{project_id}/codex/review-video",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
