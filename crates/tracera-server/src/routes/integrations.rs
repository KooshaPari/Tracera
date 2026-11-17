//! Unavailable integrations operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/integrations/conflicts",
    "/api/v1/integrations/conflicts/{param5}/resolve",
    "/api/v1/integrations/credentials",
    "/api/v1/integrations/credentials/{param5}",
    "/api/v1/integrations/credentials/{param5}/validate",
    "/api/v1/integrations/github/app/install-url",
    "/api/v1/integrations/github/app/installations",
    "/api/v1/integrations/github/app/installations/{param7}",
    "/api/v1/integrations/github/app/installations/{param7}/link",
    "/api/v1/integrations/github/projects",
    "/api/v1/integrations/github/repos",
    "/api/v1/integrations/github/repos/{param6}/{param7}/issues",
    "/api/v1/integrations/linear/projects",
    "/api/v1/integrations/linear/teams",
    "/api/v1/integrations/linear/teams/{param6}/issues",
    "/api/v1/integrations/mappings",
    "/api/v1/integrations/mappings/{param5}",
    "/api/v1/integrations/oauth/callback",
    "/api/v1/integrations/oauth/start",
    "/api/v1/integrations/stats",
    "/api/v1/integrations/sync/queue",
    "/api/v1/integrations/sync/status",
    "/api/v1/integrations/sync/trigger",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
