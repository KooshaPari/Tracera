use axum::{
    extract::DefaultBodyLimit,
    routing::{any, get, post}, Router,
};
use http::{header, HeaderValue, Method};
use std::collections::HashSet;

use crate::handlers::{
    dashboard::{dashboard_summary, get_project, list_projects, list_teams, org_metrics},
    evidence::{create_evidence, list_evidence},
    governance::{blast_radius, confidence, coverage_matrix, impact, spec_check},
    ingest_api::{ingest_agileplus, ingest_github, ingest_jira},
    problems::{create_problem, list_problems},
    sprints::{create_sprint, list_sprints},
    stories::{create_story, create_trace_link, list_stories, list_stories_api},
};
use crate::handlers::{governance, swee};
use crate::middleware::{CANONICAL_BROWSER_ORIGIN, csrf_protection};
use crate::AppState;

const MAX_REQUEST_BODY_BYTES: usize = 10 * 1024 * 1024;

/// Stub handler for Tier-2 endpoints not yet implemented.
async fn not_implemented() -> impl axum::response::IntoResponse {
    (
        axum::http::StatusCode::NOT_IMPLEMENTED,
        axum::Json(serde_json::json!({"error": "not_implemented", "message": "ADR-SERVER-001"})),
    )
}

#[allow(dead_code)]
pub(crate) fn build_router(state: AppState) -> Router {
    build_router_with_auth(state, None)
}

/// Browser origins permitted to call this server's API cross-origin.
pub(crate) fn cors_allowed_origins() -> tower_http::cors::AllowOrigin {
    let mut origins: Vec<HeaderValue> = Vec::new();
    if let Some(raw) = std::env::var("TRACERA_ALLOWED_ORIGINS")
        .ok()
        .filter(|s| !s.trim().is_empty())
    {
        for part in raw.split(',') {
            let o = part.trim();
            if !o.is_empty() {
                if let Ok(hv) = HeaderValue::try_from(o) {
                    origins.push(hv);
                }
            }
        }
    } else {
        let mut set = HashSet::new();
        for o in [
            CANONICAL_BROWSER_ORIGIN,
            "https://tracera-kappa.vercel.app",
            "https://tracera.pheno.studio",
            "https://api.tracera.pheno.studio",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ] {
            if set.insert(o) {
                if let Ok(hv) = HeaderValue::try_from(o) {
                    origins.push(hv);
                }
            }
        }
    }
    tower_http::cors::AllowOrigin::list(origins)
}

/// Build the `/auth/workos/*` sub-router.
fn build_workos_router<S>(client: tracera_workos::WorkOSClient) -> axum::Router<S>
where
    S: Clone + Send + Sync + 'static,
{
    if tracera_workos::WorkOSConfig::from_env().is_ok() {
        tracing::info!("WorkOS integration enabled");
        return tracera_workos::router::router_with_state::<S>(client);
    }
    fallback_inert_workos_router::<S>()
}

/// Inert `/auth/workos/*` router used when WorkOS env vars are not configured.
fn fallback_inert_workos_router<S>() -> axum::Router<S>
where
    S: Clone + Send + Sync + 'static,
{
    use axum::response::IntoResponse;
    async fn not_configured() -> impl IntoResponse {
        (
            axum::http::StatusCode::SERVICE_UNAVAILABLE,
            axum::Json(serde_json::json!({
                "error": "workos_not_configured",
                "message":
                    "set WORKOS_API_KEY, WORKOS_CLIENT_ID, WORKOS_WEBHOOK_SECRET, \
                     WORKOS_REDIRECT_URI to enable the WorkOS auth surface",
            })),
        )
    }
    axum::Router::new().fallback(not_configured)
}

pub(crate) fn build_router_with_auth(state: AppState, auth_token: crate::auth::AuthToken) -> Router {
    let workos_router = build_workos_router::<AppState>(state.workos_client.clone());
    Router::new()
        .route("/healthz", get(crate::health::healthz))
        .route("/health", get(crate::health::health))
        .route("/readyz", get(crate::health::readyz))
        .route("/ready", get(crate::health::ready))
        .route("/metrics", get(crate::prom_metrics_handler))
        .route("/api/v1/coverage-matrix", post(coverage_matrix))
        .route("/api/v1/health", get(crate::health::health))
        .route("/api/v1/csrf-token", get(crate::csrf_token))
        .route("/api/v1/impact", post(impact))
        .route("/api/v1/confidence", post(confidence))
        .route("/api/v1/blast-radius", post(blast_radius))
        .route("/api/v1/governance/spec-check", post(spec_check))
        .route(
            "/api/v1/trace/forward/{artifact_id}",
            post(governance::trace_forward),
        )
        .route(
            "/api/v1/trace/reverse/{artifact_id}",
            post(governance::trace_reverse),
        )
        .route(
            "/api/v1/trace/{artifact_id}/links",
            get(governance::list_persisted_trace_links),
        )
        .route("/evidence", get(list_evidence).post(create_evidence))
        .route("/evidence/health", get(crate::health::health))
        .route("/ingest/github", post(ingest_github))
        .route("/ingest/jira", post(ingest_jira))
        .route("/ingest/agileplus", post(ingest_agileplus))
        .route("/sdlc-pm/health", get(crate::health::health))
        .route("/sdlc-pm/sprints", get(list_sprints).post(create_sprint))
        .route("/sdlc-pm/stories", get(list_stories))
        .route("/api/v1/stories", get(list_stories_api).post(create_story))
        .route("/api/v1/trace", post(create_trace_link))
        .route(
            "/api/v1/projects",
            get(list_projects).post(crate::handlers::projects::create_project_stub),
        )
        .route("/api/v1/dashboard/summary", get(dashboard_summary))
        .route(
            "/api/v1/projects/{project_id}",
            get(get_project)
                .put(crate::handlers::projects::update_project_stub)
                .delete(crate::handlers::projects::delete_project_stub),
        )
        .route("/problems", get(list_problems).post(create_problem))
        .route("/problems/health", get(crate::health::health))
        .route("/org-intel/health", get(crate::health::health))
        .route("/org-intel/teams", get(list_teams))
        .route("/org-intel/metrics", get(org_metrics))
        // Items
        .route("/api/v1/items", any(not_implemented))
        .route("/api/v1/items/summary", any(not_implemented))
        .route("/api/v1/items/bulk-update", any(not_implemented))
        .route("/api/v1/items/{id}", any(not_implemented))
        .route(
            "/api/v1/items/{item_id}/pivot-targets",
            any(not_implemented),
        )
        .route("/api/v1/items/{item_id}/pivot", any(not_implemented))
        // Links
        .route("/api/v1/links", any(not_implemented))
        .route("/api/v1/links/{id}", any(not_implemented))
        .route("/api/v1/links/grouped", any(not_implemented))
        .route("/api/v1/projects/{project_id}/links", any(not_implemented))
        // Graph
        .route("/api/v1/graph/ancestors/{id}", any(not_implemented))
        .route("/api/v1/graph/descendants/{id}", any(not_implemented))
        .route("/api/v1/graph/impact/{id}", any(not_implemented))
        .route("/api/v1/graph/dependencies/{id}", any(not_implemented))
        .route("/api/v1/graph/traverse/{id}", any(not_implemented))
        .route("/api/v1/graph/path", any(not_implemented))
        .route("/api/v1/graph/paths", any(not_implemented))
        .route("/api/v1/graph/full", any(not_implemented))
        .route("/api/v1/graph/cycles", any(not_implemented))
        .route("/api/v1/graph/topo-sort", any(not_implemented))
        .route("/api/v1/graph/orphans", any(not_implemented))
        .route("/api/v1/graph/analysis/centrality", any(not_implemented))
        .route("/api/v1/graph/analysis/coverage", any(not_implemented))
        .route("/api/v1/graph/analysis/cycles", any(not_implemented))
        .route("/api/v1/graph/analysis/dependencies", any(not_implemented))
        .route("/api/v1/graph/analysis/dependents", any(not_implemented))
        .route("/api/v1/graph/analysis/impact", any(not_implemented))
        .route("/api/v1/graph/analysis/metrics", any(not_implemented))
        .route(
            "/api/v1/graph/analysis/shortest-path",
            any(not_implemented),
        )
        .route(
            "/api/v1/graph/cache/invalidate",
            any(not_implemented),
        )
        // Search
        .route("/api/v1/search", any(not_implemented))
        .route("/api/v1/search/suggest", any(not_implemented))
        .route("/api/v1/search/index/{id}", any(not_implemented))
        .route("/api/v1/search/batch-index", any(not_implemented))
        .route("/api/v1/search/reindex", any(not_implemented))
        .route("/api/v1/search/stats", any(not_implemented))
        .route("/api/v1/search/health", any(not_implemented))
        // Projects extended
        .route(
            "/api/v1/projects/{project_id}/export",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/import",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/versions/compare",
            any(not_implemented),
        )
        .route("/api/v1/import", any(not_implemented))
        // Auth
        .route("/api/v1/auth/login", any(not_implemented))
        .route("/api/v1/auth/logout", any(not_implemented))
        .route("/api/v1/auth/refresh", any(not_implemented))
        .route("/api/v1/auth/verify", any(not_implemented))
        .route("/api/v1/auth/me", get(crate::auth_me))
        // WorkOS
        .nest("/auth/workos", workos_router)
        // Equivalences
        .route("/api/v1/equivalences", any(not_implemented))
        .route("/api/v1/equivalences/{id}", any(not_implemented))
        .route("/api/v1/equivalences/confirm", any(not_implemented))
        .route("/api/v1/equivalences/reject", any(not_implemented))
        .route("/api/v1/equivalences/batch", any(not_implemented))
        .route(
            "/api/v1/projects/{project_id}/equivalences",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/equivalences/{id}",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/equivalences/canonical",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/equivalences/projections",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/equivalences/detect",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/equivalences/batch",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/equivalences/stats",
            any(not_implemented),
        )
        // Journeys
        .route("/api/v1/journeys", any(not_implemented))
        .route("/api/v1/journeys/{id}", any(not_implemented))
        .route("/api/v1/journeys/{id}/steps", any(not_implemented))
        .route(
            "/api/v1/journeys/{id}/steps/{step_id}",
            any(not_implemented),
        )
        .route("/api/v1/journeys/{id}/detect", any(not_implemented))
        .route("/api/v1/journeys/{id}/visualize", any(not_implemented))
        .route(
            "/api/v1/projects/{project_id}/journeys",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/journeys/{id}",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/journeys/{id}/steps",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/journeys/{id}/steps/{step_id}",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/journeys/{id}/detect",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/journeys/{id}/visualize",
            any(not_implemented),
        )
        // Component library
        .route("/api/v1/libraries", any(not_implemented))
        .route("/api/v1/libraries/{id}", any(not_implemented))
        .route(
            "/api/v1/libraries/{id}/components",
            any(not_implemented),
        )
        .route(
            "/api/v1/libraries/{id}/tokens",
            any(not_implemented),
        )
        .route("/api/v1/components", any(not_implemented))
        .route("/api/v1/components/{id}", any(not_implemented))
        .route(
            "/api/v1/components/{id}/usage",
            any(not_implemented),
        )
        .route("/api/v1/tokens", any(not_implemented))
        // Codex / Docs / AI
        .route(
            "/api/v1/projects/{project_id}/codex/auth-status",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/codex/sessions",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/codex/sessions/{session_id}",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/docs/generate",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/ai/summarize",
            any(not_implemented),
        )
        .route(
            "/api/v1/projects/{project_id}/ai/classify",
            any(not_implemented),
        )
        // SWEe Graph
        .route(
            "/api/v1/swee/nodes",
            post(swee::create_swee_node_handler).get(swee::list_swee_nodes_handler),
        )
        .route(
            "/api/v1/swee/nodes/{id}",
            get(swee::get_swee_node_handler),
        )
        .route(
            "/api/v1/swee/edges",
            post(swee::create_swee_edge_handler).get(swee::list_swee_edges_handler),
        )
        .route(
            "/api/v1/swee/nodes/{id}/neighbors",
            get(swee::get_swee_neighbors_handler),
        )
        // SWEE backward-compatible aliases
        .route(
            "/sw/nodes",
            post(swee::create_swee_node_handler).get(swee::list_swee_nodes_handler),
        )
        .route("/sw/nodes/{id}", get(swee::get_swee_node_handler))
        .route(
            "/sw/edges",
            post(swee::create_swee_edge_handler).get(swee::list_swee_edges_handler),
        )
        .route(
            "/sw/nodes/{id}/neighbors",
            get(swee::get_swee_neighbors_handler),
        )
        .layer(axum::middleware::from_fn_with_state(
            auth_token,
            crate::auth::require_bearer,
        ))
        .layer(DefaultBodyLimit::max(MAX_REQUEST_BODY_BYTES))
        .layer(tower_http::set_header::SetResponseHeaderLayer::if_not_present(
            header::X_CONTENT_TYPE_OPTIONS,
            HeaderValue::from_static("nosniff"),
        ))
        .layer(tower_http::set_header::SetResponseHeaderLayer::if_not_present(
            header::X_FRAME_OPTIONS,
            HeaderValue::from_static("DENY"),
        ))
        .layer(tower_http::set_header::SetResponseHeaderLayer::if_not_present(
            header::REFERRER_POLICY,
            HeaderValue::from_static("no-referrer"),
        ))
        .layer(tower_http::set_header::SetResponseHeaderLayer::if_not_present(
            header::CACHE_CONTROL,
            HeaderValue::from_static("no-store"),
        ))
        .layer(axum::middleware::from_fn(csrf_protection))
        .layer(
            tower_http::cors::CorsLayer::new()
                .allow_origin(HeaderValue::from_static(CANONICAL_BROWSER_ORIGIN))
                .allow_methods([
                    Method::GET,
                    Method::POST,
                    Method::PUT,
                    Method::PATCH,
                    Method::DELETE,
                    Method::OPTIONS,
                ])
                .allow_headers([
                    header::AUTHORIZATION,
                    header::CONTENT_TYPE,
                    http::HeaderName::from_static("x-csrf-token"),
                ])
                .allow_credentials(true)
                .allow_origin(cors_allowed_origins()),
        )
        .with_state(state)
}
