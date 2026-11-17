//! Unavailable projects operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/projects/{param2}/concepts",
    "/projects/{param2}/equivalences",
    "/projects/{param2}/equivalences/detect",
    "/projects/{param2}/journeys",
    "/projects/{param2}/journeys/detect",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
