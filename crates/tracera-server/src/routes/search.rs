//! Unavailable search operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &["/api/v1/projects/{project_id}/search/advanced"];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
