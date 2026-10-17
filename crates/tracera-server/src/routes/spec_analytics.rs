//! Unavailable spec-analytics operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/spec-analytics/analyze",
    "/api/v1/spec-analytics/batch-analyze",
    "/api/v1/spec-analytics/ears-patterns",
    "/api/v1/spec-analytics/validate-iso29148",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
