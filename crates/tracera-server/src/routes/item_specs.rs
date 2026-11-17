//! Unavailable item-specs operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/item-specs/analyze/coverage-gaps",
    "/api/v1/projects/{project_id}/item-specs/analyze/suspect-links",
    "/api/v1/projects/{project_id}/item-specs/defects",
    "/api/v1/projects/{project_id}/item-specs/defects/by-item/{param8}",
    "/api/v1/projects/{project_id}/item-specs/defects/{param7}",
    "/api/v1/projects/{project_id}/item-specs/defects/{param7}/analyze/cvss",
    "/api/v1/projects/{project_id}/item-specs/defects/{param7}/analyze/odc",
    "/api/v1/projects/{project_id}/item-specs/epics",
    "/api/v1/projects/{project_id}/item-specs/epics/by-item/{param8}",
    "/api/v1/projects/{project_id}/item-specs/epics/{param7}",
    "/api/v1/projects/{project_id}/item-specs/requirements",
    "/api/v1/projects/{project_id}/item-specs/requirements/by-item/{param8}",
    "/api/v1/projects/{project_id}/item-specs/requirements/high-risk",
    "/api/v1/projects/{project_id}/item-specs/requirements/unverified",
    "/api/v1/projects/{project_id}/item-specs/requirements/{param7}",
    "/api/v1/projects/{project_id}/item-specs/requirements/{param7}/analyze-impact",
    "/api/v1/projects/{project_id}/item-specs/requirements/{param7}/analyze-quality",
    "/api/v1/projects/{project_id}/item-specs/requirements/{param7}/analyze/ears",
    "/api/v1/projects/{project_id}/item-specs/requirements/{param7}/analyze/quality",
    "/api/v1/projects/{project_id}/item-specs/requirements/{param7}/verify",
    "/api/v1/projects/{project_id}/item-specs/tasks",
    "/api/v1/projects/{project_id}/item-specs/tasks/by-item/{param8}",
    "/api/v1/projects/{project_id}/item-specs/tasks/{param7}",
    "/api/v1/projects/{project_id}/item-specs/tests",
    "/api/v1/projects/{project_id}/item-specs/tests/by-item/{param8}",
    "/api/v1/projects/{project_id}/item-specs/tests/flaky",
    "/api/v1/projects/{project_id}/item-specs/tests/health-report",
    "/api/v1/projects/{project_id}/item-specs/tests/quarantined",
    "/api/v1/projects/{project_id}/item-specs/tests/{param7}",
    "/api/v1/projects/{project_id}/item-specs/tests/{param7}/analyze/flakiness",
    "/api/v1/projects/{project_id}/item-specs/tests/{param7}/quarantine",
    "/api/v1/projects/{project_id}/item-specs/tests/{param7}/record-run",
    "/api/v1/projects/{project_id}/item-specs/tests/{param7}/unquarantine",
    "/api/v1/projects/{project_id}/item-specs/user-stories",
    "/api/v1/projects/{project_id}/item-specs/user-stories/by-item/{param8}",
    "/api/v1/projects/{project_id}/item-specs/user-stories/{param7}",
    "/api/v1/projects/{project_id}/item-specs/{param6}/{param7}/analyze/impact",
    "/api/v1/projects/{project_id}/item-specs/{param6}/{param7}/analyze/similarity",
    "/api/v1/projects/{project_id}/item-specs/{param6}/{param7}/content-address",
    "/api/v1/projects/{project_id}/item-specs/{param6}/{param7}/merkle-proof",
    "/api/v1/projects/{project_id}/item-specs/{param6}/{param7}/prioritization",
    "/api/v1/projects/{project_id}/item-specs/{param6}/{param7}/verify-baseline",
    "/api/v1/projects/{project_id}/item-specs/{param6}/{param7}/version-chain",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
