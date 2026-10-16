//! Unavailable journeys operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/journeys/detect",
    "/journeys",
    "/journeys/call-chains",
    "/journeys/data-paths",
    "/journeys/detect",
    "/journeys/stats",
    "/journeys/user-flows",
    "/journeys/{param2}",
    "/journeys/{param2}/steps",
    "/journeys/{param2}/steps/{id}",
    "/journeys/{param2}/visualization",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
