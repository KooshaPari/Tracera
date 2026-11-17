//! Unavailable metrics operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/metrics/bundle-size",
    "/api/v1/metrics/component-render",
    "/api/v1/metrics/errors",
    "/api/v1/metrics/web-vitals",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
