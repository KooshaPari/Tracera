//! Unavailable qa operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/qa/metrics/coverage",
    "/api/v1/qa/metrics/defect-density",
    "/api/v1/qa/metrics/execution-history",
    "/api/v1/qa/metrics/flaky-tests",
    "/api/v1/qa/metrics/pass-rate",
    "/api/v1/qa/metrics/summary",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
