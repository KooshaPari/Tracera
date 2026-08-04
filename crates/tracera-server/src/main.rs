mod db;
mod auth;
mod health;
mod ingest;
mod pg_store;
#[cfg(feature = "phenodag-queue")]
mod queue;
mod sqlite_store;
mod store;
mod validation;

use axum::{
    extract::DefaultBodyLimit,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use chrono::{DateTime, Utc};
use http::{header, HeaderValue};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::env;
use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Instant;
use tower_http::{
    services::{ServeDir, ServeFile},
    set_header::SetResponseHeaderLayer,
};
use tracing::info;
use tracing_subscriber::EnvFilter;
use uuid::Uuid;

/// Maximum request size accepted by JSON and form extractors.
///
/// This is intentionally generous for bulk ingest while bounding memory use
/// for malformed or unauthenticated requests. Individual payload fields still
/// need domain validation at their handlers.
const MAX_REQUEST_BODY_BYTES: usize = 8 * 1024 * 1024;
/// Maximum number of links expanded into an in-memory coverage matrix.
/// Requests above this bound must use a future paged/export path instead of
/// allowing an unbounded response allocation.
const MAX_COVERAGE_LINKS: usize = 25_000;
const PUBLIC_BIND_MODE_ENV: &str = "TRACERA_PUBLIC_BIND_MODE";
const AUTH_TOKEN_ENV: &str = "TRACERA_AUTH_TOKEN";
const AUTHENTICATED_PROXY_MODE: &str = "authenticated-proxy";
const LOOPBACK_PUBLISHED_MODE: &str = "loopback-published";
const PRIVATE_NETWORK_MODE: &str = "private-network";
use validation::{
    validate_text, MAX_ID_CHARS, MAX_INGEST_ISSUES, MAX_LONG_TEXT_CHARS, MAX_METADATA_BYTES,
    MAX_SHORT_TEXT_CHARS, MAX_URL_CHARS,
};

use store::{EvidenceItem, ListParams, Problem, Sprint, Store, Story, TeamRow, TraceLink};

// ---------------------------------------------------------------------------
// App state — Arc<dyn Store> replaces the bare PgPool.
// DATABASE_URL scheme determines which backend is initialised at startup:
//   postgres://...   → PgStore  (server/hosted tier, Postgres)
//   sqlite://...     → SqliteStore (on-device/per-project tier, SQLite)
//   <path>.db        → SqliteStore (convenience: plain file path)
// Both are fail-loud on missing/unreachable URL — no silent fallback.
// ---------------------------------------------------------------------------
#[derive(Clone)]
struct AppState {
    version: String,
    backend: &'static str,
    started_at: Instant,
    store: Arc<dyn Store>,
}

/// Reject non-loopback listeners unless a bearer token is configured. Network
/// mode remains an explicit deployment assertion, while the in-process token
/// prevents an accidental direct launch from exposing unauthenticated writes.
fn validate_bind_address(
    addr: SocketAddr,
    public_bind_mode: Option<&str>,
    auth_token: Option<&str>,
) -> Result<(), String> {
    if addr.ip().is_loopback() {
        return Ok(());
    }

    if !matches!(
        public_bind_mode,
        Some(AUTHENTICATED_PROXY_MODE | LOOPBACK_PUBLISHED_MODE | PRIVATE_NETWORK_MODE)
    ) {
        return Err(format!(
            "refusing non-loopback bind to {addr}; set {PUBLIC_BIND_MODE_ENV} to an explicit authenticated-proxy, loopback-published, or private-network deployment mode"
        ));
    }

    if auth_token.is_some_and(|token| !token.is_empty()) {
        return Ok(());
    }

    Err(format!(
        "refusing non-loopback bind to {addr}; {AUTH_TOKEN_ENV} must contain a bearer token"
    ))
}

// ---------------------------------------------------------------------------
// Generic response shapes
// ---------------------------------------------------------------------------
#[derive(Serialize)]
struct ErrorResponse {
    error: &'static str,
}

fn bad_request(field: &'static str) -> (axum::http::StatusCode, Json<ErrorResponse>) {
    (
        axum::http::StatusCode::BAD_REQUEST,
        Json(ErrorResponse { error: field }),
    )
}

fn validate_evidence(payload: &EvidenceCreate) -> Result<(), &'static str> {
    validate_text(
        &payload.artifact_id,
        "invalid artifact_id",
        MAX_ID_CHARS,
        true,
    )?;
    validate_text(&payload.kind, "invalid kind", MAX_SHORT_TEXT_CHARS, true)?;
    validate_text(&payload.url, "invalid url", MAX_URL_CHARS, true)?;
    if serde_json::to_vec(&payload.metadata)
        .map(|v| v.len())
        .unwrap_or(MAX_METADATA_BYTES + 1)
        > MAX_METADATA_BYTES
    {
        return Err("metadata too large");
    }
    Ok(())
}

fn validate_sprint(payload: &SprintCreate) -> Result<(), &'static str> {
    validate_text(&payload.name, "invalid name", MAX_SHORT_TEXT_CHARS, true)?;
    validate_text(&payload.goal, "invalid goal", MAX_LONG_TEXT_CHARS, true)?;
    if payload.end_date < payload.start_date {
        return Err("invalid date range");
    }
    Ok(())
}

fn validate_problem(payload: &ProblemCreateRequest) -> Result<(), &'static str> {
    validate_text(
        &payload.project_id,
        "invalid project_id",
        MAX_ID_CHARS,
        true,
    )?;
    validate_text(&payload.title, "invalid title", MAX_SHORT_TEXT_CHARS, true)?;
    for (value, field) in [
        (payload.description.as_deref(), "invalid description"),
        (
            payload.resolution_type.as_deref(),
            "invalid resolution_type",
        ),
        (payload.category.as_deref(), "invalid category"),
        (payload.sub_category.as_deref(), "invalid sub_category"),
        (payload.assigned_to.as_deref(), "invalid assigned_to"),
        (payload.assigned_team.as_deref(), "invalid assigned_team"),
        (payload.owner.as_deref(), "invalid owner"),
        (payload.known_error_id.as_deref(), "invalid known_error_id"),
    ] {
        if let Some(value) = value {
            validate_text(value, field, MAX_LONG_TEXT_CHARS, false)?;
        }
    }
    for (value, field) in [
        (&payload.status, "invalid status"),
        (&payload.impact_level, "invalid impact_level"),
        (&payload.urgency, "invalid urgency"),
        (&payload.priority, "invalid priority"),
    ] {
        validate_text(value, field, MAX_SHORT_TEXT_CHARS, true)?;
    }
    if let Some(tags) = &payload.tags {
        if serde_json::to_vec(tags)
            .map(|v| v.len())
            .unwrap_or(MAX_METADATA_BYTES + 1)
            > MAX_METADATA_BYTES
        {
            return Err("tags too large");
        }
    }
    Ok(())
}

fn validate_ingest_issues(issues: &[Value]) -> Result<(), &'static str> {
    if issues.len() > MAX_INGEST_ISSUES {
        return Err("too many issues");
    }
    if issues.iter().any(|issue| {
        serde_json::to_vec(issue)
            .map(|v| v.len())
            .unwrap_or(MAX_LONG_TEXT_CHARS + 1)
            > MAX_LONG_TEXT_CHARS
    }) {
        return Err("issue payload too large");
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// Trace-link types (coverage-matrix / impact / blast-radius / spec-check)
// These are computation-only — no persistence needed.
// ---------------------------------------------------------------------------
#[derive(Debug, Deserialize, Serialize, Clone)]
#[serde(rename_all = "snake_case")]
struct TraceLinkInput {
    source_id: String,
    target_id: String,
    relationship: String,
    confidence: f64,
    updated_at: Option<DateTime<Utc>>,
}

#[derive(Serialize)]
struct MatrixCellResponse {
    source_id: String,
    target_id: String,
    coverage: String,
    links: Vec<TraceLinkInput>,
}

#[derive(Deserialize)]
struct CoverageMatrixRequest {
    #[serde(default)]
    links: Vec<TraceLinkInput>,
    #[serde(default = "default_stale_after_days")]
    stale_after_days: u32,
}

#[derive(Serialize)]
struct CoverageMatrixResponse {
    generated_at: DateTime<Utc>,
    link_count: usize,
    cell_count: usize,
    stale_links: usize,
    cells: Vec<MatrixCellResponse>,
}

#[derive(Deserialize)]
struct ImpactRequest {
    #[serde(flatten)]
    matrix: CoverageMatrixRequest,
    changed_artifact_ids: Vec<String>,
    #[serde(default = "default_max_depth")]
    max_depth: u32,
}

#[derive(Serialize)]
struct ImpactNodeResponse {
    artifact_id: String,
    depth: u32,
    via: Vec<String>,
    score: f64,
}

#[derive(Serialize)]
struct ImpactResponse {
    seeds: Vec<String>,
    affected: Vec<ImpactNodeResponse>,
    total_score: f64,
    truncated: bool,
    max_depth_seen: u32,
    conflicts: Vec<TraceLinkInput>,
}

#[derive(Deserialize)]
struct ConfidenceRequest {
    requirement_text: String,
    artifact_text: String,
}

#[derive(Serialize)]
struct ConfidenceResponse {
    confidence: f64,
    rationale: String,
}

// --- governance spec-check (port of src/tracertm/governance.py) ---
#[derive(Deserialize)]
struct GovernanceSpec {
    spec_id: String,
    #[serde(default)]
    acceptance_criteria: Vec<String>,
    #[serde(default)]
    evidence_links: Vec<String>,
    #[serde(default = "default_status")]
    status: String,
}

#[derive(Deserialize)]
struct GovernanceTrace {
    spec_id: String,
    #[allow(dead_code)]
    target_id: String,
    kind: String,
}

#[derive(Deserialize)]
struct SpecCheckRequest {
    #[serde(default)]
    specs: Vec<GovernanceSpec>,
    #[serde(default)]
    traces: Vec<GovernanceTrace>,
}

#[derive(Serialize)]
struct GovernanceViolation {
    spec_id: String,
    code: &'static str,
    message: &'static str,
}

#[derive(Serialize)]
struct GovernanceReport {
    status: &'static str,
    spec_count: usize,
    trace_count: usize,
    violations: Vec<GovernanceViolation>,
}

// --- blast-radius / trace neighbors ---
#[derive(Deserialize)]
struct BlastRadiusRequest {
    #[serde(default)]
    links: Vec<TraceLinkInput>,
    changed_artifact_ids: Vec<String>,
}

#[derive(Serialize)]
struct BlastNodeResponse {
    artifact_id: String,
    distance: u32,
}

#[derive(Serialize)]
struct BlastRadiusResponse {
    seeds: Vec<String>,
    blast_radius: Vec<BlastNodeResponse>,
    total: usize,
}

#[derive(Deserialize)]
struct TraceQueryRequest {
    #[serde(default)]
    links: Vec<TraceLinkInput>,
}

#[derive(Serialize)]
struct TraceNeighborsResponse {
    artifact_id: String,
    direction: &'static str,
    neighbors: Vec<String>,
}

#[derive(Serialize)]
struct PersistedTraceLinkResponse {
    id: String,
    source_id: String,
    target_id: String,
    relationship: String,
    confidence: f64,
    source: String,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    direction: &'static str,
}

#[derive(Serialize)]
struct PersistedTraceLinkListResponse {
    artifact_id: String,
    count: usize,
    items: Vec<PersistedTraceLinkResponse>,
}

fn default_status() -> String {
    "draft".to_string()
}

// ---------------------------------------------------------------------------
// Evidence HTTP shapes (handlers delegate to store trait)
// ---------------------------------------------------------------------------
#[derive(Deserialize)]
struct EvidenceCreate {
    artifact_id: String,
    kind: String,
    url: String,
    #[serde(default = "empty_object")]
    metadata: Value,
}

#[derive(Serialize)]
struct EvidenceList {
    items: Vec<EvidenceItem>,
    count: usize,
}

fn empty_object() -> Value {
    Value::Object(serde_json::Map::new())
}

// ---------------------------------------------------------------------------
// SDLC-PM HTTP shapes
// ---------------------------------------------------------------------------
#[derive(Deserialize)]
struct SprintCreate {
    name: String,
    goal: String,
    start_date: DateTime<Utc>,
    end_date: DateTime<Utc>,
}

// --- org-intel (port of src/tracertm/api/routers/org_intel.py) ---
#[derive(Serialize)]
struct TeamResponse {
    id: String,
    name: String,
    description: String,
    members: Vec<String>,
}

#[derive(Serialize)]
struct ProjectResponse {
    id: String,
    name: String,
    description: Option<String>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    metadata: Value,
    problem_count: i64,
}

#[derive(Serialize)]
struct ProjectListResponse {
    count: usize,
    items: Vec<ProjectResponse>,
}

#[derive(Serialize)]
struct MetricsResponse {
    total_artifacts: usize,
    coverage_ratio: f64,
    open_gaps: u32,
}

// --- ingest (port of src/tracertm/services/{github,jira}_import_service.py) ---
//
// Two modes per endpoint:
//   1. Live fetch — if GITHUB_TOKEN+GITHUB_REPO (or JIRA_*) env vars are set,
//      the handler fetches issues directly from the API and ignores `issues`.
//   2. Payload push — caller-supplied `issues` array, ingested via the same
//      persist_issues path so records land in the store regardless of mode.
//
// Fail-loud policy: if neither source is configured AND the `issues` field
// is empty, the response contains an error entry (not a fake-success 0).
#[derive(Deserialize)]
struct GitHubIngestRequest {
    /// Target repo in `owner/repo` format. Optional — overridden by GITHUB_REPO env var.
    /// Stored for future use; currently GITHUB_REPO env var takes precedence.
    #[serde(default)]
    #[allow(dead_code)]
    repo: Option<String>,
    #[serde(default)]
    issues: Vec<Value>,
}

#[derive(Deserialize)]
struct JiraIngestRequest {
    #[serde(default)]
    issues: Vec<Value>,
}

#[derive(Serialize)]
pub struct BulkIngestionResult {
    pub total_processed: usize,
    pub requirements_created: usize,
    pub trace_links_created: usize,
    pub errors: Vec<String>,
}

// ---------------------------------------------------------------------------
// Startup — backend selection by DATABASE_URL scheme
// ---------------------------------------------------------------------------
#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::from_default_env().add_directive("tracera_server=info".parse().unwrap()),
        )
        .init();

    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| {
        eprintln!(
            "FATAL: DATABASE_URL environment variable is not set.\n\
             Set it to a connection string, e.g.:\n\
             DATABASE_URL=postgres://user:pass@localhost:5432/tracera\n\
             DATABASE_URL=sqlite:///path/to/tracera.db\n\
             DATABASE_URL=sqlite::memory:"
        );
        std::process::exit(1);
    });

    let (store, backend): (Arc<dyn Store>, &'static str) =
        if database_url.starts_with("postgres://") || database_url.starts_with("postgresql://") {
            info!("Backend: Postgres (server tier)");
            let pool = db::connect_postgres(&database_url)
                .await
                .unwrap_or_else(|e| {
                    eprintln!(
                        "FATAL: Cannot connect to Postgres at the provided DATABASE_URL.\n\
                 Error: {e}\n\
                 Ensure Postgres is running and DATABASE_URL is correct."
                    );
                    std::process::exit(1);
                });
            sqlx::migrate!("./migrations")
                .run(&pool)
                .await
                .unwrap_or_else(|e| {
                    eprintln!("FATAL: Postgres migration failed: {e}");
                    std::process::exit(1);
                });
            info!("Postgres migrations applied successfully");
            (Arc::new(pg_store::PgStore::new(pool)), "postgres")
        } else if database_url.starts_with("sqlite://")
            || database_url.starts_with("sqlite:")
            || database_url.ends_with(".db")
        {
            info!("Backend: SQLite (on-device tier)");
            let pool = db::connect_sqlite(&database_url).await.unwrap_or_else(|e| {
                eprintln!(
                    "FATAL: Cannot open SQLite database at the provided DATABASE_URL.\n\
                     Error: {e}\n\
                     Use DATABASE_URL=sqlite:///path/to/file.db or DATABASE_URL=sqlite::memory:"
                );
                std::process::exit(1);
            });
            sqlx::migrate!("./migrations-sqlite")
                .run(&pool)
                .await
                .unwrap_or_else(|e| {
                    eprintln!("FATAL: SQLite migration failed: {e}");
                    std::process::exit(1);
                });
            info!("SQLite migrations applied successfully");
            (Arc::new(sqlite_store::SqliteStore::new(pool)), "sqlite")
        } else {
            eprintln!(
                "FATAL: Unrecognised DATABASE_URL scheme.\n\
             Use postgres:// for Postgres or sqlite:// for SQLite on-device tier."
            );
            std::process::exit(1);
        };

    let state = AppState {
        version: env!("CARGO_PKG_VERSION").to_string(),
        backend,
        started_at: Instant::now(),
        store,
    };

    let auth_token = env::var(AUTH_TOKEN_ENV)
        .ok()
        .filter(|token| !token.is_empty())
        .map(Arc::<str>::from);
    let app = build_router_with_auth(state, auth_token.clone());

    let frontend_dist = env::var("TRACERA_FRONTEND_DIST")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("frontend/dist"));
    let index_html = frontend_dist.join("index.html");
    let serve_dir = ServeDir::new(&frontend_dist).fallback(ServeFile::new(&index_html));
    let app = app.fallback_service(serve_dir);

    let addr = env::var("TRACERA_BIND_ADDR")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or_else(|| SocketAddr::from(([127, 0, 0, 1], 8080)));

    let public_bind_mode = env::var(PUBLIC_BIND_MODE_ENV).ok();
    if let Err(error) = validate_bind_address(
        addr,
        public_bind_mode.as_deref(),
        auth_token.as_deref(),
    ) {
        eprintln!("FATAL: {error}");
        std::process::exit(1);
    }

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .unwrap_or_else(|error| {
            eprintln!("FATAL: cannot bind Tracera server to {addr}: {error}");
            std::process::exit(1);
        });
    info!("tracera-server listening on {addr}");
    if let Err(error) = axum::serve(listener, app).await {
        eprintln!("FATAL: Tracera server stopped unexpectedly: {error}");
        std::process::exit(1);
    }
}

fn build_router(state: AppState) -> Router {
    build_router_with_auth(state, None)
}

fn build_router_with_auth(state: AppState, auth_token: auth::AuthToken) -> Router {
    Router::new()
        .route("/healthz", get(health::healthz))
        .route("/health", get(health::health))
        .route("/readyz", get(health::readyz))
        .route("/ready", get(health::ready))
        .route("/api/v1/coverage-matrix", post(coverage_matrix))
        .route("/api/v1/impact", post(impact))
        .route("/api/v1/confidence", post(confidence))
        .route("/api/v1/blast-radius", post(blast_radius))
        .route("/api/v1/governance/spec-check", post(spec_check))
        .route("/api/v1/trace/forward/:artifact_id", post(trace_forward))
        .route("/api/v1/trace/reverse/:artifact_id", post(trace_reverse))
        .route(
            "/api/v1/trace/:artifact_id/links",
            get(list_persisted_trace_links),
        )
        .route("/evidence", get(list_evidence).post(create_evidence))
        .route("/evidence/health", get(health::health))
        .route("/ingest/github", post(ingest_github))
        .route("/ingest/jira", post(ingest_jira))
        .route("/sdlc-pm/health", get(health::health))
        .route("/sdlc-pm/sprints", get(list_sprints).post(create_sprint))
        .route("/sdlc-pm/stories", get(list_stories))
        .route("/api/v1/projects", get(list_projects))
        .route("/api/v1/projects/:project_id", get(get_project))
        .route("/problems", get(list_problems).post(create_problem))
        .route("/problems/health", get(health::health))
        .route("/org-intel/health", get(health::health))
        .route("/org-intel/teams", get(list_teams))
        .route("/org-intel/metrics", get(org_metrics))
        .with_state(state)
        .layer(axum::middleware::from_fn_with_state(
            auth_token,
            auth::require_bearer,
        ))
        .layer(DefaultBodyLimit::max(MAX_REQUEST_BODY_BYTES))
        .layer(SetResponseHeaderLayer::if_not_present(
            header::X_CONTENT_TYPE_OPTIONS,
            HeaderValue::from_static("nosniff"),
        ))
        .layer(SetResponseHeaderLayer::if_not_present(
            header::X_FRAME_OPTIONS,
            HeaderValue::from_static("DENY"),
        ))
        .layer(SetResponseHeaderLayer::if_not_present(
            header::REFERRER_POLICY,
            HeaderValue::from_static("no-referrer"),
        ))
        .layer(SetResponseHeaderLayer::if_not_present(
            header::CACHE_CONTROL,
            HeaderValue::from_static("no-store"),
        ))
}

// ---------------------------------------------------------------------------
// Computation-only handlers (no persistence)
// ---------------------------------------------------------------------------
async fn coverage_matrix(
    Json(request): Json<CoverageMatrixRequest>,
) -> Result<Json<CoverageMatrixResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    if request.links.len() > MAX_COVERAGE_LINKS {
        return Err((
            axum::http::StatusCode::PAYLOAD_TOO_LARGE,
            Json(ErrorResponse {
                error: "coverage matrix exceeds link limit; use a paged export",
            }),
        ));
    }
    Ok(Json(build_coverage_matrix(request)))
}

async fn impact(Json(request): Json<ImpactRequest>) -> Json<ImpactResponse> {
    let max_depth = request.max_depth;

    let links: Vec<TraceLinkInput> = request.matrix.links.clone();
    let adj = build_adjacency(&links);

    let conflicts: Vec<TraceLinkInput> = links
        .iter()
        .filter(|l| l.relationship == "conflicts_with")
        .cloned()
        .collect();

    let mut affected: Vec<ImpactNodeResponse> = request
        .changed_artifact_ids
        .iter()
        .map(|id| ImpactNodeResponse {
            artifact_id: id.clone(),
            depth: 0,
            via: vec![],
            score: 1.0,
        })
        .collect();

    let reachable = bfs_distances(&adj, &request.changed_artifact_ids);
    let mut truncated = false;
    let mut max_depth_seen: u32 = 0;

    for (node, dist) in reachable {
        if dist > max_depth {
            truncated = true;
            continue;
        }
        if dist > max_depth_seen {
            max_depth_seen = dist;
        }
        let score = (0.5_f64.powi(dist as i32)).max(0.1);
        let via: Vec<String> = links
            .iter()
            .filter(|l| l.target_id == node)
            .map(|l| l.source_id.clone())
            .collect();
        affected.push(ImpactNodeResponse {
            artifact_id: node,
            depth: dist,
            via,
            score,
        });
    }

    let total_score: f64 = affected.iter().map(|n| n.score).sum::<f64>().max(1.0);

    Json(ImpactResponse {
        seeds: request.changed_artifact_ids,
        affected,
        total_score,
        truncated,
        max_depth_seen,
        conflicts,
    })
}

async fn confidence(Json(request): Json<ConfidenceRequest>) -> Json<ConfidenceResponse> {
    let score = jaccard_score(&request.requirement_text, &request.artifact_text);
    Json(ConfidenceResponse {
        confidence: score,
        rationale: "Jaccard token overlap baseline".to_string(),
    })
}

async fn spec_check(Json(req): Json<SpecCheckRequest>) -> Json<GovernanceReport> {
    use std::collections::{BTreeSet, HashMap};
    let mut traces_by_spec: HashMap<&str, BTreeSet<&str>> = HashMap::new();
    for t in &req.traces {
        traces_by_spec
            .entry(t.spec_id.as_str())
            .or_default()
            .insert(t.kind.as_str());
    }
    let known: BTreeSet<&str> = req.specs.iter().map(|s| s.spec_id.as_str()).collect();
    let mut violations = Vec::new();
    let mut seen: BTreeSet<&str> = BTreeSet::new();
    for s in &req.specs {
        if !seen.insert(s.spec_id.as_str()) {
            violations.push(viol(&s.spec_id, "duplicate_spec", "Duplicate spec id"));
            continue;
        }
        if s.status != "approved" {
            violations.push(viol(&s.spec_id, "not_approved", "Spec must be approved"));
        }
        if s.acceptance_criteria.is_empty() {
            violations.push(viol(
                &s.spec_id,
                "missing_acceptance",
                "Acceptance criteria required",
            ));
        }
        if s.evidence_links.is_empty() {
            violations.push(viol(
                &s.spec_id,
                "missing_evidence",
                "Evidence links required",
            ));
        }
        let kinds = traces_by_spec.get(s.spec_id.as_str());
        let has = |k: &str| kinds.map(|set| set.contains(k)).unwrap_or(false);
        if !has("implementation") {
            violations.push(viol(
                &s.spec_id,
                "missing_implementation",
                "Implementation trace required",
            ));
        }
        if !has("test") {
            violations.push(viol(&s.spec_id, "missing_test", "Test trace required"));
        }
    }
    for t in &req.traces {
        if !known.contains(t.spec_id.as_str()) {
            violations.push(viol(&t.spec_id, "orphan_trace", "Trace target has no spec"));
        }
    }
    Json(GovernanceReport {
        status: if violations.is_empty() {
            "pass"
        } else {
            "fail"
        },
        spec_count: req.specs.len(),
        trace_count: req.traces.len(),
        violations,
    })
}

fn viol(spec_id: &str, code: &'static str, message: &'static str) -> GovernanceViolation {
    GovernanceViolation {
        spec_id: spec_id.to_string(),
        code,
        message,
    }
}

async fn blast_radius(Json(req): Json<BlastRadiusRequest>) -> Json<BlastRadiusResponse> {
    let adj = build_adjacency(&req.links);
    let mut blast = Vec::new();
    for node in bfs_distances(&adj, &req.changed_artifact_ids) {
        blast.push(BlastNodeResponse {
            artifact_id: node.0,
            distance: node.1,
        });
    }
    Json(BlastRadiusResponse {
        total: blast.len(),
        seeds: req.changed_artifact_ids,
        blast_radius: blast,
    })
}

async fn trace_forward(
    axum::extract::Path(artifact_id): axum::extract::Path<String>,
    Json(req): Json<TraceQueryRequest>,
) -> Json<TraceNeighborsResponse> {
    let neighbors = neighbors_of(&req.links, &artifact_id, true);
    Json(TraceNeighborsResponse {
        artifact_id,
        direction: "forward",
        neighbors,
    })
}

async fn trace_reverse(
    axum::extract::Path(artifact_id): axum::extract::Path<String>,
    Json(req): Json<TraceQueryRequest>,
) -> Json<TraceNeighborsResponse> {
    let neighbors = neighbors_of(&req.links, &artifact_id, false);
    Json(TraceNeighborsResponse {
        artifact_id,
        direction: "reverse",
        neighbors,
    })
}

async fn list_persisted_trace_links(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Path(artifact_id): axum::extract::Path<String>,
) -> Result<Json<PersistedTraceLinkListResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    validate_text(&artifact_id, "invalid artifact_id", MAX_ID_CHARS, true).map_err(bad_request)?;
    let links = state
        .store
        .list_trace_links_for_artifact(artifact_id.clone())
        .await
        .map_err(|e| {
            tracing::error!("list persisted trace links store error: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "trace link listing failed",
                }),
            )
        })?;
    let items: Vec<PersistedTraceLinkResponse> = links
        .into_iter()
        .map(|link| persisted_trace_link_response(link, &artifact_id))
        .collect();

    Ok(Json(PersistedTraceLinkListResponse {
        artifact_id,
        count: items.len(),
        items,
    }))
}

fn persisted_trace_link_response(link: TraceLink, artifact_id: &str) -> PersistedTraceLinkResponse {
    PersistedTraceLinkResponse {
        direction: if link.source_id == artifact_id {
            "forward"
        } else {
            "reverse"
        },
        id: link.id,
        source_id: link.source_id,
        target_id: link.target_id,
        relationship: link.relationship,
        confidence: link.confidence,
        source: link.source,
        created_at: link.created_at,
        updated_at: link.updated_at,
    }
}

// ---------------------------------------------------------------------------
// Evidence handlers — delegate to store trait
// ---------------------------------------------------------------------------
async fn list_evidence(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<EvidenceList>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let items = state.store.list_evidence().await.map_err(|e| {
        tracing::error!("list_evidence store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "evidence listing failed",
            }),
        )
    })?;
    Ok(Json(EvidenceList {
        count: items.len(),
        items,
    }))
}

async fn create_evidence(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<EvidenceCreate>,
) -> Result<
    (axum::http::StatusCode, Json<EvidenceItem>),
    (axum::http::StatusCode, Json<ErrorResponse>),
> {
    validate_evidence(&payload).map_err(bad_request)?;
    let now = Utc::now();
    let id = format!("ev-{}", Uuid::new_v4());
    let meta =
        serde_json::to_value(&payload.metadata).unwrap_or(Value::Object(serde_json::Map::new()));

    let item = state
        .store
        .create_evidence(
            id,
            payload.artifact_id,
            payload.kind,
            payload.url,
            meta,
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_evidence store insert failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "evidence persistence failed",
                }),
            )
        })?;

    Ok((axum::http::StatusCode::CREATED, Json(item)))
}

// ---------------------------------------------------------------------------
// Sprint handlers — delegate to store trait
// ---------------------------------------------------------------------------
async fn list_sprints(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<Vec<Sprint>>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let sprints = state.store.list_sprints().await.map_err(|e| {
        tracing::error!("list_sprints store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "sprint listing failed",
            }),
        )
    })?;
    Ok(Json(sprints))
}

async fn create_sprint(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<SprintCreate>,
) -> Result<(axum::http::StatusCode, Json<Sprint>), (axum::http::StatusCode, Json<ErrorResponse>)> {
    validate_sprint(&payload).map_err(bad_request)?;
    let now = Utc::now();
    let id = format!("sprint-{}", Uuid::new_v4());

    let sprint = state
        .store
        .create_sprint(
            id,
            payload.name,
            payload.goal,
            payload.start_date,
            payload.end_date,
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_sprint store insert failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "sprint persistence failed",
                }),
            )
        })?;

    Ok((axum::http::StatusCode::CREATED, Json(sprint)))
}

// ---------------------------------------------------------------------------
// Problem handlers (ITIL problem-management) — recovered domain
// ---------------------------------------------------------------------------
#[derive(Deserialize)]
struct ProblemCreateRequest {
    project_id: String,
    #[serde(default)]
    title: String,
    #[serde(default)]
    description: Option<String>,
    #[serde(default = "default_problem_status")]
    status: String,
    #[serde(default)]
    resolution_type: Option<String>,
    #[serde(default)]
    category: Option<String>,
    #[serde(default)]
    sub_category: Option<String>,
    #[serde(default)]
    tags: Option<Value>,
    #[serde(default = "default_impact")]
    impact_level: String,
    #[serde(default = "default_impact")]
    urgency: String,
    #[serde(default = "default_impact")]
    priority: String,
    #[serde(default)]
    rca_performed: bool,
    #[serde(default)]
    root_cause_identified: bool,
    #[serde(default)]
    workaround_available: bool,
    #[serde(default)]
    permanent_fix_available: bool,
    #[serde(default)]
    assigned_to: Option<String>,
    #[serde(default)]
    assigned_team: Option<String>,
    #[serde(default)]
    owner: Option<String>,
    #[serde(default)]
    known_error_id: Option<String>,
}

fn default_problem_status() -> String {
    "open".to_string()
}

fn default_impact() -> String {
    "medium".to_string()
}

#[derive(Serialize)]
struct ProblemListResponse {
    project_id: String,
    count: usize,
    items: Vec<Problem>,
}

#[derive(serde::Deserialize, Default)]
struct ProblemQuery {
    project_id: Option<String>,
    status: Option<String>,
    #[serde(flatten)]
    pagination: ListParams,
}

async fn list_problems(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Query(params): axum::extract::Query<ProblemQuery>,
) -> Result<Json<ProblemListResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let pagination = params.pagination.validated().map_err(|_| bad_request("invalid pagination"))?;
    let project_id = params.project_id.unwrap_or_default();
    let status_filter = params.status;
    let items = state
        .store
        .list_problems(project_id.clone(), status_filter.clone(), pagination)
        .await
        .map_err(|e| {
            tracing::error!("list_problems store error: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "problem listing failed",
                }),
            )
        })?;
    let total = state
        .store
        .count_problems_filtered(project_id.clone(), status_filter)
        .await
        .map_err(|e| {
            tracing::error!("count_problems store error: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse { error: "problem count failed" }),
            )
        })?;
    Ok(Json(ProblemListResponse {
        project_id,
        count: total.max(0) as usize,
        items,
    }))
}

#[allow(clippy::too_many_arguments)]
async fn create_problem(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<ProblemCreateRequest>,
) -> Result<(axum::http::StatusCode, Json<Problem>), (axum::http::StatusCode, Json<ErrorResponse>)>
{
    validate_problem(&payload).map_err(bad_request)?;
    let now = Utc::now();
    let id = format!("prob-{}", Uuid::new_v4());
    // Human-readable problem number: P-YYYYMMDD-<8 hex>. Date-derived prefix
    // matches the Python implementation's `_generate_problem_number`.
    let problem_number = format!(
        "P-{}-{}",
        now.format("%Y%m%d"),
        Uuid::new_v4().simple().to_string()[..8].to_uppercase()
    );

    let problem = state
        .store
        .create_problem(
            id,
            payload.project_id,
            problem_number,
            payload.title,
            payload.description,
            payload.status,
            payload.resolution_type,
            payload.category,
            payload.sub_category,
            payload.tags,
            payload.impact_level,
            payload.urgency,
            payload.priority,
            payload.rca_performed,
            payload.root_cause_identified,
            payload.workaround_available,
            payload.permanent_fix_available,
            payload.assigned_to,
            payload.assigned_team,
            payload.owner,
            payload.known_error_id,
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_problem store insert failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "problem persistence failed",
                }),
            )
        })?;

    Ok((axum::http::StatusCode::CREATED, Json(problem)))
}

// ---------------------------------------------------------------------------
// Story handlers
// ---------------------------------------------------------------------------
async fn list_stories(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<Vec<Story>>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let stories = state.store.list_stories().await.map_err(|e| {
        tracing::error!("list_stories store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "story listing failed",
            }),
        )
    })?;
    Ok(Json(stories))
}

// ---------------------------------------------------------------------------
// Teams handler
// ---------------------------------------------------------------------------
async fn list_teams(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<Vec<TeamResponse>>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let rows: Vec<TeamRow> = state.store.list_teams().await.map_err(|e| {
        tracing::error!("list_teams store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "team listing failed",
            }),
        )
    })?;
    Ok(Json(
        rows.into_iter()
            .map(|r| TeamResponse {
                id: r.id,
                name: r.name,
                description: r.description,
                members: r.members,
            })
            .collect(),
    ))
}

async fn list_projects(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Query(params): axum::extract::Query<ListParams>,
) -> Result<Json<ProjectListResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let pagination = params.validated().map_err(|_| bad_request("invalid pagination"))?;
    let projects = state.store.list_projects(pagination).await.map_err(|e| {
        tracing::error!("list_projects store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "project listing failed",
            }),
        )
    })?;
    let total = state.store.count_projects().await.map_err(|e| {
        tracing::error!("count_projects store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse { error: "project count failed" }),
        )
    })?;
    Ok(Json(ProjectListResponse {
        count: total.max(0) as usize,
        items: projects
            .into_iter()
            .map(|project| ProjectResponse {
                id: project.id,
                name: project.name,
                description: project.description,
                created_at: project.created_at,
                updated_at: project.updated_at,
                metadata: project.metadata,
                problem_count: project.problem_count,
            })
            .collect(),
    }))
}

async fn get_project(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Path(project_id): axum::extract::Path<String>,
) -> axum::response::Response {
    match state.store.get_project(project_id.clone()).await {
        Ok(Some(project)) => Json(ProjectResponse {
            id: project.id,
            name: project.name,
            description: project.description,
            created_at: project.created_at,
            updated_at: project.updated_at,
            metadata: project.metadata,
            problem_count: project.problem_count,
        })
        .into_response(),
        Ok(None) => axum::http::StatusCode::NOT_FOUND.into_response(),
        Err(error) => {
            tracing::error!("get_project store error: {error}");
            axum::http::StatusCode::INTERNAL_SERVER_ERROR.into_response()
        }
    }
}

// ---------------------------------------------------------------------------
// Org metrics
// ---------------------------------------------------------------------------
async fn org_metrics(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<MetricsResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let count = state.store.count_evidence().await.map_err(|e| {
        tracing::error!("org_metrics store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "organization metrics failed",
            }),
        )
    })?;
    Ok(Json(MetricsResponse {
        total_artifacts: count as usize,
        coverage_ratio: 0.75,
        open_gaps: 3,
    }))
}

// ---------------------------------------------------------------------------
// Ingest handlers — real persistence via Store trait
// ---------------------------------------------------------------------------

/// POST /ingest/github
///
/// If `GITHUB_TOKEN` and `GITHUB_REPO` are set, fetches issues live from
/// GitHub and ignores the `issues` payload field.  Otherwise falls back to
/// the caller-supplied `issues` array.  Fails loud if neither source has data.
async fn ingest_github(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(req): Json<GitHubIngestRequest>,
) -> (axum::http::StatusCode, Json<BulkIngestionResult>) {
    if let Err(error) = validate_ingest_issues(&req.issues) {
        return (
            axum::http::StatusCode::BAD_REQUEST,
            Json(BulkIngestionResult {
                total_processed: 0,
                requirements_created: 0,
                trace_links_created: 0,
                errors: vec![error.to_string()],
            }),
        );
    }
    // Try live GitHub fetch first
    if ingest::GitHubConfig::from_env().is_some() {
        match ingest::ingest_live(&state.store).await {
            Ok(result) => return (axum::http::StatusCode::OK, Json(result)),
            Err(ingest::IngestError::NoSourceConfigured) => {} // fall through
            Err(e) => {
                tracing::error!("GitHub live ingest failed: {e}");
                let result = BulkIngestionResult {
                    total_processed: 0,
                    requirements_created: 0,
                    trace_links_created: 0,
                    errors: vec![format!("live ingest error: {e}")],
                };
                return (axum::http::StatusCode::BAD_GATEWAY, Json(result));
            }
        }
    }

    // Fall back to payload-based ingest
    if req.issues.is_empty() {
        let result = BulkIngestionResult {
            total_processed: 0,
            requirements_created: 0,
            trace_links_created: 0,
            errors: vec![
                "no ingest source configured: set GITHUB_TOKEN+GITHUB_REPO, \
                 or supply issues[] in the request body"
                    .to_string(),
            ],
        };
        return (axum::http::StatusCode::UNPROCESSABLE_ENTITY, Json(result));
    }

    let result = ingest::ingest_from_payload(&req.issues, "number", "github", &state.store).await;
    (axum::http::StatusCode::OK, Json(result))
}

/// POST /ingest/jira
///
/// If `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY` are
/// all set, fetches issues live from Jira.  Otherwise uses the `issues` payload.
/// Fails loud if neither source has data.
async fn ingest_jira(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(req): Json<JiraIngestRequest>,
) -> (axum::http::StatusCode, Json<BulkIngestionResult>) {
    if let Err(error) = validate_ingest_issues(&req.issues) {
        return (
            axum::http::StatusCode::BAD_REQUEST,
            Json(BulkIngestionResult {
                total_processed: 0,
                requirements_created: 0,
                trace_links_created: 0,
                errors: vec![error.to_string()],
            }),
        );
    }
    // Try live Jira fetch first
    if ingest::JiraConfig::from_env().is_some() {
        match ingest::ingest_live(&state.store).await {
            Ok(result) => return (axum::http::StatusCode::OK, Json(result)),
            Err(ingest::IngestError::NoSourceConfigured) => {}
            Err(e) => {
                tracing::error!("Jira live ingest failed: {e}");
                let result = BulkIngestionResult {
                    total_processed: 0,
                    requirements_created: 0,
                    trace_links_created: 0,
                    errors: vec![format!("live ingest error: {e}")],
                };
                return (axum::http::StatusCode::BAD_GATEWAY, Json(result));
            }
        }
    }

    // Fall back to payload-based ingest
    if req.issues.is_empty() {
        let result = BulkIngestionResult {
            total_processed: 0,
            requirements_created: 0,
            trace_links_created: 0,
            errors: vec![
                "no ingest source configured: set JIRA_URL+JIRA_EMAIL+JIRA_API_TOKEN+JIRA_PROJECT_KEY, \
                 or supply issues[] in the request body"
                    .to_string(),
            ],
        };
        return (axum::http::StatusCode::UNPROCESSABLE_ENTITY, Json(result));
    }

    let result = ingest::ingest_from_payload(&req.issues, "key", "jira", &state.store).await;
    (axum::http::StatusCode::OK, Json(result))
}

// ---------------------------------------------------------------------------
// Pure-function utilities (no DB interaction — unit-testable without a store)
// ---------------------------------------------------------------------------
fn neighbors_of(links: &[TraceLinkInput], id: &str, forward: bool) -> Vec<String> {
    links
        .iter()
        .filter_map(|l| {
            if forward && l.source_id == id {
                Some(l.target_id.clone())
            } else if !forward && l.target_id == id {
                Some(l.source_id.clone())
            } else {
                None
            }
        })
        .collect()
}

fn build_adjacency(links: &[TraceLinkInput]) -> std::collections::HashMap<String, Vec<String>> {
    let mut adj: std::collections::HashMap<String, Vec<String>> = std::collections::HashMap::new();
    for l in links {
        adj.entry(l.source_id.clone())
            .or_default()
            .push(l.target_id.clone());
    }
    adj
}

fn bfs_distances(
    adj: &std::collections::HashMap<String, Vec<String>>,
    seeds: &[String],
) -> Vec<(String, u32)> {
    use std::collections::{HashSet, VecDeque};
    let mut visited: HashSet<String> = seeds.iter().cloned().collect();
    let mut queue: VecDeque<(String, u32)> = seeds.iter().map(|s| (s.clone(), 0)).collect();
    let mut out = Vec::new();
    while let Some((node, dist)) = queue.pop_front() {
        if let Some(targets) = adj.get(&node) {
            for t in targets {
                if visited.insert(t.clone()) {
                    out.push((t.clone(), dist + 1));
                    queue.push_back((t.clone(), dist + 1));
                }
            }
        }
    }
    out
}

fn build_coverage_matrix(request: CoverageMatrixRequest) -> CoverageMatrixResponse {
    let now = Utc::now();
    let mut cells = Vec::new();
    let mut stale_links = 0usize;
    for link in &request.links {
        if let Some(updated_at) = link.updated_at {
            if (now - updated_at).num_days() as u32 > request.stale_after_days {
                stale_links += 1;
            }
        }
        cells.push(MatrixCellResponse {
            source_id: link.source_id.clone(),
            target_id: link.target_id.clone(),
            coverage: classify_coverage(link),
            links: vec![link.clone()],
        });
    }
    CoverageMatrixResponse {
        generated_at: now,
        link_count: request.links.len(),
        cell_count: cells.len(),
        stale_links,
        cells,
    }
}

fn classify_coverage(link: &TraceLinkInput) -> String {
    if link.relationship == "conflicts_with" {
        "conflict".to_string()
    } else if matches!(link.relationship.as_str(), "verifies" | "satisfies")
        && link.confidence >= 0.9
    {
        "covered".to_string()
    } else if matches!(link.relationship.as_str(), "verifies" | "satisfies") {
        "partial".to_string()
    } else {
        "missing".to_string()
    }
}

fn jaccard_score(a: &str, b: &str) -> f64 {
    let a_tokens: std::collections::BTreeSet<_> = a.split_whitespace().collect();
    let b_tokens: std::collections::BTreeSet<_> = b.split_whitespace().collect();
    let inter = a_tokens.intersection(&b_tokens).count() as f64;
    let union = a_tokens.union(&b_tokens).count() as f64;
    if union == 0.0 {
        0.0
    } else {
        inter / union
    }
}

fn default_stale_after_days() -> u32 {
    90
}

fn default_max_depth() -> u32 {
    10
}

// ---------------------------------------------------------------------------
// Unit tests — no live DB required for pure-function tests.
// SQLite in-memory round-trip tests prove on-device tier works standalone.
// ---------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::Body;
    use chrono::TimeZone;
    use http::{Request, StatusCode};
    use sqlx::{postgres::PgPoolOptions, PgPool, Row};
    use tower::ServiceExt;

    const PG_STORE_CONTRACT_POOL_CONNECTIONS: u32 = 4;

    struct PgStoreContractFixture {
        pool: PgPool,
        schema_name: String,
    }

    impl PgStoreContractFixture {
        fn store(&self) -> crate::pg_store::PgStore {
            crate::pg_store::PgStore::new(self.pool.clone())
        }

        async fn assert_all_connection_search_paths(&self) -> Result<(), String> {
            let (first, second, third, fourth) = tokio::join!(
                self.pool.acquire(),
                self.pool.acquire(),
                self.pool.acquire(),
                self.pool.acquire(),
            );
            let mut first = first.map_err(|error| format!("acquire connection 1: {error}"))?;
            let mut second = second.map_err(|error| format!("acquire connection 2: {error}"))?;
            let mut third = third.map_err(|error| format!("acquire connection 3: {error}"))?;
            let mut fourth = fourth.map_err(|error| format!("acquire connection 4: {error}"))?;
            let (first, second, third, fourth) = tokio::join!(
                sqlx::query_scalar::<_, String>("SELECT current_schema()").fetch_one(&mut *first),
                sqlx::query_scalar::<_, String>("SELECT current_schema()").fetch_one(&mut *second),
                sqlx::query_scalar::<_, String>("SELECT current_schema()").fetch_one(&mut *third),
                sqlx::query_scalar::<_, String>("SELECT current_schema()").fetch_one(&mut *fourth),
            );
            for (connection, active_schema) in [
                ("connection 1", first),
                ("connection 2", second),
                ("connection 3", third),
                ("connection 4", fourth),
            ] {
                let active_schema = active_schema
                    .map_err(|error| format!("read {connection} search_path: {error}"))?;
                if active_schema != self.schema_name {
                    return Err(format!(
                        "{connection} used schema {active_schema}, expected {}",
                        self.schema_name
                    ));
                }
            }
            Ok(())
        }

        async fn cleanup(self) -> Result<(), sqlx::Error> {
            let result = drop_pg_store_contract_schema(&self.pool, &self.schema_name).await;
            self.pool.close().await;
            result
        }
    }

    async fn drop_pg_store_contract_schema(
        pool: &PgPool,
        schema_name: &str,
    ) -> Result<(), sqlx::Error> {
        // `schema_name` is generated exclusively from UUID::simple below.
        let drop_schema = format!("DROP SCHEMA IF EXISTS {schema_name} CASCADE");
        sqlx::query(sqlx::AssertSqlSafe(drop_schema))
            .execute(pool)
            .await
            .map(|_| ())
    }

    async fn make_pg_store_contract_fixture() -> PgStoreContractFixture {
        let database_url = env::var("TRACERA_TEST_DATABASE_URL")
            .expect("TRACERA_TEST_DATABASE_URL is required for the ignored PgStore contract test");
        let schema_name = format!("tracera_pgstore_test_{}", Uuid::new_v4().simple());
        let bootstrap_pool = PgPoolOptions::new()
            .max_connections(1)
            .connect(&database_url)
            .await
            .expect("connect to TRACERA_TEST_DATABASE_URL");
        let create_schema = format!("CREATE SCHEMA {}", schema_name);
        // `schema_name` is generated exclusively from UUID::simple above.
        sqlx::query(sqlx::AssertSqlSafe(create_schema))
            .execute(&bootstrap_pool)
            .await
            .expect("create generated Postgres test schema");
        let search_path = format!("{}, public", schema_name);
        let pool = match PgPoolOptions::new()
            .max_connections(PG_STORE_CONTRACT_POOL_CONNECTIONS)
            .after_connect(move |connection, _| {
                let search_path = search_path.clone();
                Box::pin(async move {
                    sqlx::query("SELECT set_config('search_path', $1, false)")
                        .bind(search_path)
                        .execute(connection)
                        .await
                        .map(|_| ())
                })
            })
            .connect(&database_url)
            .await
        {
            Ok(pool) => pool,
            Err(error) => {
                if let Err(cleanup_error) =
                    drop_pg_store_contract_schema(&bootstrap_pool, &schema_name).await
                {
                    eprintln!("fixture cleanup after pool connection failure: {cleanup_error}");
                }
                bootstrap_pool.close().await;
                panic!("connect PgStore pool with generated-schema search_path: {error}");
            }
        };
        bootstrap_pool.close().await;
        if let Err(error) = sqlx::migrate!("./migrations")
            .run(&pool)
            .await
        {
            if let Err(cleanup_error) = drop_pg_store_contract_schema(&pool, &schema_name).await {
                eprintln!("fixture cleanup after migration failure: {cleanup_error}");
            }
            pool.close().await;
            panic!("apply production Postgres migrations to generated schema: {error}");
        }

        PgStoreContractFixture { pool, schema_name }
    }

    #[tokio::test]
    async fn api_router_emits_readiness_and_security_contract() {
        let store = make_sqlite_store().await;
        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        let response = app
            .oneshot(
                Request::builder()
                    .uri("/readyz")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");

        assert_eq!(response.status(), StatusCode::OK);
        assert_eq!(
            response.headers()[header::X_CONTENT_TYPE_OPTIONS],
            "nosniff"
        );
        assert_eq!(response.headers()[header::X_FRAME_OPTIONS], "DENY");
        assert_eq!(response.headers()[header::REFERRER_POLICY], "no-referrer");
        assert_eq!(response.headers()[header::CACHE_CONTROL], "no-store");
    }

    #[tokio::test]
    async fn public_auth_requires_bearer_for_application_routes_but_not_probes() {
        let store = make_sqlite_store().await;
        let app = build_router_with_auth(
            AppState {
                version: env!("CARGO_PKG_VERSION").to_string(),
                backend: "sqlite",
                started_at: Instant::now(),
                store: Arc::new(store),
            },
            Some(Arc::<str>::from("secret")),
        );

        let unauthorized = app
            .clone()
            .oneshot(
                Request::builder()
                    .uri("/evidence")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");
        assert_eq!(unauthorized.status(), StatusCode::UNAUTHORIZED);
        assert_eq!(unauthorized.headers()[header::WWW_AUTHENTICATE], "Bearer");

        let health = app
            .clone()
            .oneshot(
                Request::builder()
                    .uri("/health")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");
        assert_eq!(health.status(), StatusCode::OK);

        let authorized = app
            .oneshot(
                Request::builder()
                    .uri("/evidence")
                    .header(header::AUTHORIZATION, "Bearer secret")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");
        assert_eq!(authorized.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn readiness_fails_closed_when_the_store_is_unavailable() {
        let store = make_sqlite_store().await;
        store.pool.close().await;
        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        let response = app
            .oneshot(
                Request::builder()
                    .uri("/readyz")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");

        assert_eq!(response.status(), StatusCode::SERVICE_UNAVAILABLE);
        let body = axum::body::to_bytes(response.into_body(), 1024)
            .await
            .expect("body");
        assert_eq!(
            body.as_ref(),
            br#"{"status":"not_ready","service":"tracera-server"}"#
        );
    }

    #[tokio::test]
    async fn api_router_serves_project_contract_from_store() {
        let store = make_sqlite_store().await;
        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        let response = app
            .clone()
            .oneshot(
                Request::builder()
                    .uri("/api/v1/projects")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");

        assert_eq!(response.status(), StatusCode::OK);
        assert_eq!(
            response.headers()[header::CONTENT_TYPE],
            "application/json"
        );

        let body = axum::body::to_bytes(response.into_body(), 1024)
            .await
            .expect("body");
        let payload: serde_json::Value = serde_json::from_slice(&body).expect("json body");
        assert_eq!(payload["count"], 0);
        assert_eq!(payload["items"], serde_json::json!([]));
    }

    #[tokio::test]
    async fn api_router_lists_persisted_trace_links_for_an_artifact() {
        use crate::store::Store as _;

        let store = make_sqlite_store().await;
        let now = Utc::now();
        store
            .create_trace_link(
                "link-1".to_string(),
                "REQ-001".to_string(),
                "src/lib.rs".to_string(),
                "implemented_by".to_string(),
                0.91,
                "github".to_string(),
                now,
            )
            .await
            .expect("seed persisted trace link");
        store
            .create_trace_link(
                "link-2".to_string(),
                "src/lib.rs".to_string(),
                "test/lib_test.rs".to_string(),
                "verified_by".to_string(),
                0.87,
                "manual".to_string(),
                now,
            )
            .await
            .expect("seed second persisted trace link");

        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        let response = app
            .oneshot(
                Request::builder()
                    .uri("/api/v1/trace/src%2Flib.rs/links")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");

        assert_eq!(response.status(), StatusCode::OK);
        let body = axum::body::to_bytes(response.into_body(), 1024)
            .await
            .expect("body");
        let payload: serde_json::Value = serde_json::from_slice(&body).expect("json body");
        assert_eq!(payload["artifact_id"], "src/lib.rs");
        assert_eq!(payload["count"], 2);
        assert_eq!(payload["items"][0]["id"], "link-1");
        assert_eq!(payload["items"][0]["direction"], "reverse");
        assert_eq!(payload["items"][0]["relationship"], "implemented_by");
        assert_eq!(payload["items"][0]["confidence"], 0.91);
        assert_eq!(payload["items"][0]["source"], "github");
        assert_eq!(payload["items"][1]["id"], "link-2");
        assert_eq!(payload["items"][1]["direction"], "forward");
        assert_eq!(payload["items"][1]["relationship"], "verified_by");
    }

    #[tokio::test]
    async fn api_router_rejects_malformed_json_and_oversized_bodies() {
        let store = make_sqlite_store().await;
        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        let malformed = app
            .clone()
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/api/v1/coverage-matrix")
                    .header(header::CONTENT_TYPE, "application/json")
                    .body(Body::from("{"))
                    .expect("request"),
            )
            .await
            .expect("response");
        assert_eq!(malformed.status(), StatusCode::BAD_REQUEST);

        let too_many_links = serde_json::json!({
            "links": (0..=MAX_COVERAGE_LINKS)
                .map(|index| serde_json::json!({
                    "source_id": format!("source-{index}"),
                    "target_id": format!("target-{index}"),
                    "relationship": "verifies",
                    "confidence": 1.0
                }))
                .collect::<Vec<_>>()
        });
        let limited = app
            .clone()
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/api/v1/coverage-matrix")
                    .header(header::CONTENT_TYPE, "application/json")
                    .body(Body::from(serde_json::to_vec(&too_many_links).unwrap()))
                    .expect("request"),
            )
            .await
            .expect("response");
        assert_eq!(limited.status(), StatusCode::PAYLOAD_TOO_LARGE);

        let oversized = app
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/evidence")
                    .header(header::CONTENT_TYPE, "application/json")
                    .body(Body::from(vec![b'x'; MAX_REQUEST_BODY_BYTES + 1]))
                    .expect("request"),
            )
            .await
            .expect("response");
        assert_eq!(oversized.status(), StatusCode::PAYLOAD_TOO_LARGE);
    }

    #[tokio::test]
    async fn api_router_sanitizes_persistence_failures() {
        let store = make_sqlite_store().await;
        store.pool.close().await;
        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        let response = app
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/evidence")
                    .header(header::CONTENT_TYPE, "application/json")
                    .body(Body::from(
                        r#"{"artifact_id":"artifact-1","kind":"test","url":"https://example.test"}"#,
                    ))
                    .expect("request"),
            )
            .await
            .expect("response");

        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
        let body = axum::body::to_bytes(response.into_body(), 1024)
            .await
            .expect("body");
        assert_eq!(body.as_ref(), br#"{"error":"evidence persistence failed"}"#);
    }

    #[tokio::test]
    async fn project_listing_returns_structured_5xx_when_store_is_unavailable() {
        let store = make_sqlite_store().await;
        store.pool.close().await;
        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        let response = app
            .oneshot(
                Request::builder()
                    .uri("/api/v1/projects")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");

        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
        let body = axum::body::to_bytes(response.into_body(), 1024)
            .await
            .expect("body");
        assert_eq!(body.as_ref(), br#"{"error":"project listing failed"}"#);
    }

    #[tokio::test]
    async fn problem_listing_returns_structured_5xx_when_store_is_unavailable() {
        let store = make_sqlite_store().await;
        store.pool.close().await;
        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        let response = app
            .oneshot(
                Request::builder()
                    .uri("/problems?project_id=project-1")
                    .body(Body::empty())
                    .expect("request"),
            )
            .await
            .expect("response");

        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
        let body = axum::body::to_bytes(response.into_body(), 1024)
            .await
            .expect("body");
        assert_eq!(body.as_ref(), br#"{"error":"problem listing failed"}"#);
    }

    #[tokio::test]
    async fn remaining_list_handlers_return_structured_5xx_when_store_is_unavailable() {
        let store = make_sqlite_store().await;
        store.pool.close().await;
        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(store),
        });

        for (uri, error) in [
            ("/evidence", "evidence listing failed"),
            ("/sdlc-pm/sprints", "sprint listing failed"),
            ("/sdlc-pm/stories", "story listing failed"),
            ("/org-intel/teams", "team listing failed"),
            ("/org-intel/metrics", "organization metrics failed"),
        ] {
            let response = app
                .clone()
                .oneshot(
                    Request::builder()
                        .uri(uri)
                        .body(Body::empty())
                        .expect("request"),
                )
                .await
                .expect("response");

            assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR, "{uri}");
            let body = axum::body::to_bytes(response.into_body(), 1024)
                .await
                .expect("body");
            let expected = format!(r#"{{"error":"{error}"}}"#);
            assert_eq!(body.as_ref(), expected.as_bytes(), "{uri}");
        }
    }

    /// Consumer-facing v1 contract: evidence is stored/listed, then the same
    /// artifact is traversed through request-supplied explicit trace links.
    #[tokio::test]
    async fn observability_ledger_consumer_v1_fixture_round_trip() {
        let fixture: Value = serde_json::from_str(include_str!(
            "../testdata/observability-ledger-consumer-v1.json"
        ))
        .expect("consumer fixture is valid JSON");
        let evidence = fixture["evidence"].clone();
        let artifact_id = fixture["trace"]["artifact_id"]
            .as_str()
            .expect("trace artifact_id");
        let expected_count = fixture["expected"]["evidence_count"]
            .as_u64()
            .expect("expected evidence count");
        let expected_neighbors = fixture["expected"]["trace_neighbors"].clone();

        let app = build_router(AppState {
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store: Arc::new(make_sqlite_store().await),
        });

        let created = app
            .clone()
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/evidence")
                    .header(header::CONTENT_TYPE, "application/json")
                    .body(Body::from(
                        serde_json::to_vec(&evidence).expect("evidence JSON"),
                    ))
                    .expect("create evidence request"),
            )
            .await
            .expect("create evidence response");
        assert_eq!(created.status(), StatusCode::CREATED);
        let created_body: Value = serde_json::from_slice(
            &axum::body::to_bytes(created.into_body(), MAX_REQUEST_BODY_BYTES)
                .await
                .expect("created evidence body"),
        )
        .expect("created evidence JSON");
        assert!(created_body["id"]
            .as_str()
            .is_some_and(|id| id.starts_with("ev-")));
        assert_eq!(created_body["artifact_id"], evidence["artifact_id"]);
        assert_eq!(created_body["kind"], evidence["kind"]);
        assert_eq!(created_body["url"], evidence["url"]);
        assert_eq!(created_body["metadata"], evidence["metadata"]);
        for field in ["trace_id", "span_id", "parent_span_id", "correlation_id"] {
            assert!(created_body["metadata"][field].as_str().is_some());
        }
        assert_eq!(created_body["metadata"]["producer"], "PhenoObservability");

        let listed = app
            .clone()
            .oneshot(
                Request::builder()
                    .uri("/evidence")
                    .body(Body::empty())
                    .expect("list evidence request"),
            )
            .await
            .expect("list evidence response");
        assert_eq!(listed.status(), StatusCode::OK);
        let listed_body: Value = serde_json::from_slice(
            &axum::body::to_bytes(listed.into_body(), MAX_REQUEST_BODY_BYTES)
                .await
                .expect("listed evidence body"),
        )
        .expect("listed evidence JSON");
        assert_eq!(listed_body["count"], expected_count);
        assert_eq!(
            listed_body["items"].as_array().map(Vec::len),
            Some(expected_count as usize)
        );
        assert_eq!(
            listed_body["items"][0]["artifact_id"],
            evidence["artifact_id"]
        );
        assert_eq!(listed_body["items"][0]["metadata"], evidence["metadata"]);

        let trace = app
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri(format!("/api/v1/trace/forward/{artifact_id}"))
                    .header(header::CONTENT_TYPE, "application/json")
                    .body(Body::from(
                        serde_json::to_vec(&fixture["trace"]).expect("trace JSON"),
                    ))
                    .expect("trace request"),
            )
            .await
            .expect("trace response");
        assert_eq!(trace.status(), StatusCode::OK);
        let trace_body: Value = serde_json::from_slice(
            &axum::body::to_bytes(trace.into_body(), MAX_REQUEST_BODY_BYTES)
                .await
                .expect("trace body"),
        )
        .expect("trace JSON");
        assert_eq!(trace_body["artifact_id"], artifact_id);
        assert_eq!(trace_body["direction"], "forward");
        assert_eq!(trace_body["neighbors"], expected_neighbors);
    }

    #[tokio::test]
    async fn health_and_readiness_response_shapes_are_stable() {
        let health = health::healthz().await.0;
        assert_eq!(health.status, "ok");
        assert_eq!(health.service, "tracera-server");

        let store = Arc::new(make_sqlite_store().await);
        let state = AppState {
            version: "0.1.3-test".to_string(),
            backend: "sqlite",
            started_at: Instant::now(),
            store,
        };
        let ready = match health::readyz(axum::extract::State(state)).await {
            Ok(response) => response.0,
            Err(_) => panic!("healthy store is ready"),
        };
        assert_eq!(ready.status, "ready");
        assert_eq!(ready.service, "tracera-server");
        assert_eq!(ready.version, "0.1.3-test");
        assert_eq!(ready.backend, "sqlite");
        assert!(ready.uptime_seconds < 2);
    }

    #[test]
    fn non_loopback_bind_requires_authenticated_proxy_acknowledgement() {
        let loopback = "127.0.0.1:8080".parse().expect("loopback address");
        let public = "0.0.0.0:8080".parse().expect("public address");

        assert!(validate_bind_address(loopback, None, None).is_ok());
        assert!(validate_bind_address(public, None, None).is_err());
        assert!(validate_bind_address(public, Some("authenticated-proxy"), None).is_err());
        assert!(validate_bind_address(public, Some("loopback-published"), Some("secret")).is_ok());
        assert!(validate_bind_address(public, Some("private-network"), Some("secret")).is_ok());
        assert!(validate_bind_address(public, Some("anything-else"), Some("secret")).is_err());
        assert!(validate_bind_address(public, Some("private-network"), Some("")).is_err());
    }

    #[test]
    fn malformed_json_is_rejected_before_domain_validation() {
        let malformed = serde_json::from_str::<EvidenceCreate>(r#"{"artifact_id":"unterminated"}"#);
        assert!(
            malformed.is_err(),
            "axum Json must reject malformed payloads"
        );
    }

    #[test]
    fn request_limits_reject_oversized_evidence_and_ingest_batches() {
        let payload = EvidenceCreate {
            artifact_id: "a".into(),
            kind: "test".into(),
            url: "https://example.test".into(),
            metadata: serde_json::json!({"body": "x".repeat(MAX_METADATA_BYTES)}),
        };
        assert_eq!(validate_evidence(&payload), Err("metadata too large"));
        let issues = vec![serde_json::json!({"title": "x"}); MAX_INGEST_ISSUES + 1];
        assert_eq!(validate_ingest_issues(&issues), Err("too many issues"));
    }

    #[test]
    fn request_limits_reject_invalid_sprint_dates_and_empty_problem_title() {
        let sprint = SprintCreate {
            name: "Sprint".into(),
            goal: "Goal".into(),
            start_date: Utc::now(),
            end_date: Utc::now() - chrono::Duration::days(1),
        };
        assert_eq!(validate_sprint(&sprint), Err("invalid date range"));
        let problem = ProblemCreateRequest {
            project_id: "project".into(),
            title: String::new(),
            description: None,
            status: default_problem_status(),
            resolution_type: None,
            category: None,
            sub_category: None,
            tags: None,
            impact_level: default_impact(),
            urgency: default_impact(),
            priority: default_impact(),
            rca_performed: false,
            root_cause_identified: false,
            workaround_available: false,
            permanent_fix_available: false,
            assigned_to: None,
            assigned_team: None,
            owner: None,
            known_error_id: None,
        };
        assert_eq!(validate_problem(&problem), Err("invalid title"));
    }

    // -----------------------------------------------------------------------
    // Impact traversal tests (from PR #706 — impact handler fix)
    // -----------------------------------------------------------------------

    fn chain_links() -> Vec<TraceLinkInput> {
        vec![
            TraceLinkInput {
                source_id: "seed".into(),
                target_id: "hop1".into(),
                relationship: "depends_on".into(),
                confidence: 1.0,
                updated_at: None,
            },
            TraceLinkInput {
                source_id: "hop1".into(),
                target_id: "hop2".into(),
                relationship: "depends_on".into(),
                confidence: 1.0,
                updated_at: None,
            },
            TraceLinkInput {
                source_id: "hop2".into(),
                target_id: "hop3".into(),
                relationship: "depends_on".into(),
                confidence: 1.0,
                updated_at: None,
            },
        ]
    }

    fn run_impact(
        links: Vec<TraceLinkInput>,
        seeds: Vec<String>,
        max_depth: u32,
    ) -> ImpactResponse {
        let adj = build_adjacency(&links);
        let reachable = bfs_distances(&adj, &seeds);

        let mut affected: Vec<ImpactNodeResponse> = seeds
            .iter()
            .map(|id| ImpactNodeResponse {
                artifact_id: id.clone(),
                depth: 0,
                via: vec![],
                score: 1.0,
            })
            .collect();

        let mut truncated = false;
        let mut max_depth_seen: u32 = 0;

        for (node, dist) in reachable {
            if dist > max_depth {
                truncated = true;
                continue;
            }
            if dist > max_depth_seen {
                max_depth_seen = dist;
            }
            let score = (0.5_f64.powi(dist as i32)).max(0.1);
            let via: Vec<String> = links
                .iter()
                .filter(|l| l.target_id == node)
                .map(|l| l.source_id.clone())
                .collect();
            affected.push(ImpactNodeResponse {
                artifact_id: node,
                depth: dist,
                via,
                score,
            });
        }

        let conflicts: Vec<TraceLinkInput> = links
            .iter()
            .filter(|l| l.relationship == "conflicts_with")
            .cloned()
            .collect();

        let total_score = affected.iter().map(|n| n.score).sum::<f64>().max(1.0);

        ImpactResponse {
            seeds: seeds.clone(),
            affected,
            total_score,
            truncated,
            max_depth_seen,
            conflicts,
        }
    }

    fn affected_ids(resp: &ImpactResponse) -> Vec<&str> {
        resp.affected
            .iter()
            .map(|n| n.artifact_id.as_str())
            .collect()
    }

    #[test]
    fn impact_traverses_multi_hop_at_depth_3() {
        let links = chain_links();
        let seeds = vec!["seed".to_string()];
        let resp = run_impact(links, seeds, 3);

        let ids = affected_ids(&resp);
        assert!(ids.contains(&"seed"), "seed must be in affected");
        assert!(
            ids.contains(&"hop1"),
            "hop1 (depth 1) must be in affected at max_depth=3"
        );
        assert!(
            ids.contains(&"hop2"),
            "hop2 (depth 2) must be in affected at max_depth=3"
        );
        assert!(
            ids.contains(&"hop3"),
            "hop3 (depth 3) must be in affected at max_depth=3"
        );
        assert!(
            !resp.truncated,
            "no truncation expected at max_depth=3 for a 3-hop chain"
        );
        assert_eq!(resp.max_depth_seen, 3);
    }

    #[test]
    fn impact_depth_1_excludes_2_hop_node() {
        let links = chain_links();
        let seeds = vec!["seed".to_string()];
        let resp = run_impact(links, seeds, 1);

        let ids = affected_ids(&resp);
        assert!(ids.contains(&"seed"), "seed present");
        assert!(
            ids.contains(&"hop1"),
            "hop1 (depth 1) reachable within max_depth=1"
        );
        assert!(
            !ids.contains(&"hop2"),
            "hop2 (depth 2) must NOT appear at max_depth=1"
        );
        assert!(
            !ids.contains(&"hop3"),
            "hop3 (depth 3) must NOT appear at max_depth=1"
        );
        assert!(
            resp.truncated,
            "truncated flag must be set when nodes are clamped"
        );
        assert_eq!(resp.max_depth_seen, 1);
    }

    #[test]
    fn impact_depth_0_returns_only_seeds() {
        let links = chain_links();
        let seeds = vec!["seed".to_string()];
        let resp = run_impact(links, seeds, 0);

        let ids = affected_ids(&resp);
        assert_eq!(ids, vec!["seed"]);
        assert!(
            resp.truncated,
            "must be truncated when max_depth=0 and edges exist"
        );
        assert_eq!(resp.max_depth_seen, 0);
    }

    #[test]
    fn bfs_distances_basic() {
        let links = chain_links();
        let adj = build_adjacency(&links);
        let distances = bfs_distances(&adj, &["seed".to_string()]);
        let dist_map: std::collections::HashMap<_, _> = distances.into_iter().collect();
        assert_eq!(dist_map["hop1"], 1);
        assert_eq!(dist_map["hop2"], 2);
        assert_eq!(dist_map["hop3"], 3);
    }

    // -----------------------------------------------------------------------
    // PG-persistence logic tests (no live DB required)
    // -----------------------------------------------------------------------

    fn make_link(src: &str, tgt: &str, rel: &str, conf: f64) -> TraceLinkInput {
        TraceLinkInput {
            source_id: src.to_string(),
            target_id: tgt.to_string(),
            relationship: rel.to_string(),
            confidence: conf,
            updated_at: None,
        }
    }

    #[test]
    fn jaccard_identical() {
        assert!((jaccard_score("a b c", "a b c") - 1.0).abs() < 1e-9);
    }

    #[test]
    fn jaccard_disjoint() {
        assert!((jaccard_score("a b", "c d") - 0.0).abs() < 1e-9);
    }

    #[test]
    fn jaccard_partial_overlap() {
        let score = jaccard_score("a b", "b c");
        assert!((score - 1.0 / 3.0).abs() < 1e-9);
    }

    #[test]
    fn jaccard_empty() {
        assert!((jaccard_score("", "") - 0.0).abs() < 1e-9);
    }

    #[test]
    fn coverage_conflict() {
        let link = make_link("a", "b", "conflicts_with", 0.5);
        assert_eq!(classify_coverage(&link), "conflict");
    }

    #[test]
    fn coverage_covered() {
        let link = make_link("a", "b", "verifies", 0.95);
        assert_eq!(classify_coverage(&link), "covered");
    }

    #[test]
    fn coverage_partial() {
        let link = make_link("a", "b", "satisfies", 0.5);
        assert_eq!(classify_coverage(&link), "partial");
    }

    #[test]
    fn coverage_missing() {
        let link = make_link("a", "b", "related_to", 0.9);
        assert_eq!(classify_coverage(&link), "missing");
    }

    #[test]
    fn neighbors_forward() {
        let links = vec![
            make_link("req-1", "impl-1", "satisfies", 0.9),
            make_link("req-1", "test-1", "verifies", 0.8),
            make_link("req-2", "impl-2", "satisfies", 0.7),
        ];
        let mut ns = neighbors_of(&links, "req-1", true);
        ns.sort();
        assert_eq!(ns, vec!["impl-1", "test-1"]);
    }

    #[test]
    fn neighbors_reverse() {
        let links = vec![
            make_link("req-1", "impl-1", "satisfies", 0.9),
            make_link("req-2", "impl-1", "satisfies", 0.7),
        ];
        let mut ns = neighbors_of(&links, "impl-1", false);
        ns.sort();
        assert_eq!(ns, vec!["req-1", "req-2"]);
    }

    #[test]
    fn bfs_linear_chain() {
        let mut adj = std::collections::HashMap::new();
        adj.insert("a".to_string(), vec!["b".to_string()]);
        adj.insert("b".to_string(), vec!["c".to_string()]);
        let result = bfs_distances(&adj, &["a".to_string()]);
        let map: std::collections::HashMap<_, _> = result.into_iter().collect();
        assert_eq!(map["b"], 1);
        assert_eq!(map["c"], 2);
        assert!(!map.contains_key("a"));
    }

    #[test]
    fn bfs_no_outgoing_edges() {
        let adj = std::collections::HashMap::new();
        let result = bfs_distances(&adj, &["a".to_string()]);
        assert!(result.is_empty());
    }

    /// Payload ingest with all valid issues creates stories for each.
    #[tokio::test]
    async fn ingest_all_valid() {
        let store = make_sqlite_store().await;
        let store_arc: std::sync::Arc<dyn crate::store::Store> = std::sync::Arc::new(store);
        let issues = vec![
            serde_json::json!({"title": "Fix login", "number": 1, "html_url": "", "state": "open"}),
            serde_json::json!({"title": "Add tests", "number": 2, "html_url": "", "state": "open"}),
        ];
        let r = crate::ingest::ingest_from_payload(&issues, "number", "github", &store_arc).await;
        assert_eq!(r.total_processed, 2);
        assert_eq!(r.requirements_created, 2);
        assert!(r.errors.is_empty());
    }

    /// Payload ingest skips issues with missing or empty title.
    /// `total_processed` reflects only valid (non-filtered) issues.
    #[tokio::test]
    async fn ingest_missing_title() {
        let store = make_sqlite_store().await;
        let store_arc: std::sync::Arc<dyn crate::store::Store> = std::sync::Arc::new(store);
        let issues = vec![
            serde_json::json!({"number": 42, "html_url": "", "state": "open"}),
            serde_json::json!({"title": "", "number": 43, "html_url": "", "state": "open"}),
        ];
        let r = crate::ingest::ingest_from_payload(&issues, "number", "github", &store_arc).await;
        // Both issues have missing/empty title; filter_map drops them before persist.
        // total_processed reflects the filtered-in count, not the raw input count.
        assert_eq!(r.total_processed, 0, "no valid issues to process");
        assert_eq!(r.requirements_created, 0);
        assert!(r.errors.is_empty(), "no error entries for filtered issues");
    }

    #[test]
    fn coverage_matrix_stale_link() {
        let old_ts = Utc.with_ymd_and_hms(2020, 1, 1, 0, 0, 0).unwrap();
        let links = vec![TraceLinkInput {
            source_id: "a".to_string(),
            target_id: "b".to_string(),
            relationship: "verifies".to_string(),
            confidence: 0.9,
            updated_at: Some(old_ts),
        }];
        let req = CoverageMatrixRequest {
            links,
            stale_after_days: 30,
        };
        let resp = build_coverage_matrix(req);
        assert_eq!(resp.stale_links, 1);
        assert_eq!(resp.link_count, 1);
        assert_eq!(resp.cell_count, 1);
    }

    #[test]
    fn evidence_item_serde_roundtrip() {
        let item = EvidenceItem {
            id: "ev-abc".to_string(),
            artifact_id: "req-1".to_string(),
            kind: "test_result".to_string(),
            url: "https://ci.example.com/run/1".to_string(),
            metadata: serde_json::json!({"passed": true}),
            created_at: Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            updated_at: Utc.with_ymd_and_hms(2025, 1, 2, 0, 0, 0).unwrap(),
        };
        let json = serde_json::to_string(&item).unwrap();
        assert!(json.contains("ev-abc"));
        assert!(json.contains("test_result"));
        assert!(json.contains("passed"));
    }

    #[test]
    fn sprint_serde() {
        let sprint = Sprint {
            id: "sprint-1".to_string(),
            name: "Sprint 1".to_string(),
            goal: "Ship persistence".to_string(),
            start_date: Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2025, 1, 14, 0, 0, 0).unwrap(),
            status: "planned".to_string(),
            created_at: Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            updated_at: Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
        };
        let json = serde_json::to_string(&sprint).unwrap();
        assert!(json.contains("sprint-1"));
        assert!(json.contains("planned"));
    }

    #[test]
    fn story_optional_fields() {
        let story = Story {
            id: "story-1".to_string(),
            sprint_id: None,
            title: "Add PG".to_string(),
            description: String::new(),
            status: "open".to_string(),
            story_points: None,
            created_at: Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            updated_at: Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
        };
        let json = serde_json::to_string(&story).unwrap();
        assert!(json.contains("story-1"));
        assert!(json.contains("\"sprint_id\":null"));
        assert!(json.contains("\"story_points\":null"));
    }

    #[test]
    fn team_response_serde() {
        let team = TeamRow {
            id: "team-1".to_string(),
            name: "Platform Team".to_string(),
            description: "Core platform engineering".to_string(),
            members: vec![],
        };
        let json = serde_json::to_string(&team).unwrap();
        assert!(json.contains("Platform Team"));
        assert!(json.contains("\"members\":[]"));
    }

    /// SQLite team round-trip: JSON-encoded members decode back into Vec<String>.
    #[tokio::test]
    async fn sqlite_team_list_decodes_members_json_array() {
        let store = make_sqlite_store().await;

        sqlx::query(
            "INSERT INTO teams (id, name, description, members, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
        )
        .bind("team-decoding-1")
        .bind("Platform Team")
        .bind("Core platform engineering")
        .bind(r#"["alice","bob","carol"]"#)
        .bind("2026-07-29T00:00:00Z")
        .bind("2026-07-29T00:00:00Z")
        .execute(&store.pool)
        .await
        .expect("insert team row");

        let teams = store.list_teams().await.expect("list_teams");
        let team = teams
            .into_iter()
            .find(|row| row.id == "team-decoding-1")
            .expect("inserted team should be returned");

        assert_eq!(team.name, "Platform Team");
        assert_eq!(team.description, "Core platform engineering");
        assert_eq!(
            team.members,
            vec!["alice".to_string(), "bob".to_string(), "carol".to_string()]
        );
    }

    // -----------------------------------------------------------------------
    // SQLite in-memory round-trip tests — on-device tier proof
    // No external DB required; uses sqlx SqlitePool with sqlite::memory:
    // -----------------------------------------------------------------------

    async fn make_sqlite_store() -> crate::sqlite_store::SqliteStore {
        let pool = sqlx::SqlitePool::connect("sqlite::memory:")
            .await
            .expect("open in-memory SQLite");
        // Apply SQLite migrations manually using the embedded SQL
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS evidence (
                id TEXT PRIMARY KEY,
                artifact_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                url TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )",
        )
        .execute(&pool)
        .await
        .expect("create evidence table");
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS sprints (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                goal TEXT NOT NULL DEFAULT '',
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'planned',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )",
        )
        .execute(&pool)
        .await
        .expect("create sprints table");
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS stories (
                id TEXT PRIMARY KEY,
                sprint_id TEXT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'open',
                story_points INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )",
        )
        .execute(&pool)
        .await
        .expect("create stories table");
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                members TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            )",
        )
        .execute(&pool)
        .await
        .expect("create teams table");
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS trace_links (
                id           TEXT    PRIMARY KEY,
                source_id    TEXT    NOT NULL,
                target_id    TEXT    NOT NULL,
                relationship TEXT    NOT NULL,
                confidence   REAL    NOT NULL DEFAULT 1.0,
                source       TEXT    NOT NULL DEFAULT 'manual',
                created_at   TEXT    NOT NULL,
                updated_at   TEXT    NOT NULL
            )",
        )
        .execute(&pool)
        .await
        .expect("create trace_links table");
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS problems (
                id                     TEXT    PRIMARY KEY,
                project_id             TEXT    NOT NULL,
                problem_number         TEXT    NOT NULL UNIQUE,
                title                  TEXT    NOT NULL,
                description             TEXT,
                status                 TEXT    NOT NULL DEFAULT 'open',
                resolution_type        TEXT,
                category               TEXT,
                sub_category           TEXT,
                tags                   TEXT,
                impact_level           TEXT    NOT NULL DEFAULT 'medium',
                urgency                TEXT    NOT NULL DEFAULT 'medium',
                priority               TEXT    NOT NULL DEFAULT 'medium',
                rca_performed          INTEGER NOT NULL DEFAULT 0,
                root_cause_identified  INTEGER NOT NULL DEFAULT 0,
                workaround_available   INTEGER NOT NULL DEFAULT 0,
                permanent_fix_available INTEGER NOT NULL DEFAULT 0,
                assigned_to            TEXT,
                assigned_team          TEXT,
                owner                  TEXT,
                known_error_id         TEXT,
                created_at             TEXT    NOT NULL,
                updated_at             TEXT    NOT NULL,
                deleted_at             TEXT
            )",
        )
        .execute(&pool)
        .await
        .expect("create problems table");

        crate::sqlite_store::SqliteStore::new(pool)
    }

    #[tokio::test]
    async fn sqlite_migrations_support_problems_backed_projects() {
        let pool = sqlx::SqlitePool::connect("sqlite::memory:")
            .await
            .expect("open in-memory SQLite");
        sqlx::migrate!("./migrations-sqlite")
            .run(&pool)
            .await
            .expect("apply production SQLite migrations");
        let store = crate::sqlite_store::SqliteStore::new(pool);
        let now = Utc::now();

        store
            .create_problem(
                "prob-migration-1".to_string(),
                "project-migration-1".to_string(),
                "P-20260729-00000001".to_string(),
                "Production migration contract".to_string(),
                None,
                "open".to_string(),
                None,
                None,
                None,
                None,
                "medium".to_string(),
                "medium".to_string(),
                "medium".to_string(),
                false,
                false,
                false,
                false,
                None,
                None,
                None,
                None,
                now,
            )
            .await
            .expect("persist problem after production migrations");

        let projects = store.list_projects(ListParams::default()).await.expect("list projects");
        assert_eq!(projects.len(), 1);
        assert_eq!(projects[0].id, "project-migration-1");
        assert_eq!(projects[0].problem_count, 1);
        assert!(store
            .get_project("project-migration-1".to_string())
            .await
            .expect("get project")
            .is_some());
    }

    /// Live Postgres contract for textual project IDs.  This test is explicit
    /// opt-in because it creates and drops an isolated schema in the database
    /// named by `TRACERA_TEST_DATABASE_URL`.
    #[tokio::test]
    #[ignore = "requires TRACERA_TEST_DATABASE_URL and CREATE/DROP SCHEMA privileges"]
    async fn pg_store_contract_supports_textual_project_ids_in_an_isolated_schema() {
        let fixture = make_pg_store_contract_fixture().await;
        let contract_result = run_pg_store_textual_project_id_contract(&fixture).await;
        let cleanup_result = fixture.cleanup().await;

        match (contract_result, cleanup_result) {
            (Ok(()), Ok(())) => {}
            (Err(primary_error), cleanup_result) => {
                if let Err(cleanup_error) = cleanup_result {
                    eprintln!("fixture cleanup after contract failure: {cleanup_error}");
                }
                panic!("PgStore textual project-id contract failed: {primary_error}");
            }
            (Ok(()), Err(cleanup_error)) => {
                panic!("generated-schema cleanup failed after contract success: {cleanup_error}");
            }
        }
    }

    async fn run_pg_store_textual_project_id_contract(
        fixture: &PgStoreContractFixture,
    ) -> Result<(), String> {
        let store = fixture.store();
        let project_id = "project/external-not-a-uuid".to_string();
        let other_project_id = "project/isolated-other".to_string();
        let now = Utc::now();

        if !store
            .list_problems(project_id.clone(), None, ListParams::default())
            .await
            .map_err(|error| format!("list empty generated schema: {error}"))?
            .is_empty()
        {
            return Err("generated schema was not empty".to_string());
        }

        store
            .create_problem(
                "pg-problem-text-id".to_string(),
                project_id.clone(),
                "P-PG-TEXT-0001".to_string(),
                "PgStore accepts a textual project identifier".to_string(),
                None,
                "open".to_string(),
                None,
                None,
                None,
                None,
                "medium".to_string(),
                "medium".to_string(),
                "medium".to_string(),
                false,
                false,
                false,
                false,
                None,
                None,
                None,
                None,
                now,
            )
            .await
            .map_err(|error| format!("create a problem with a non-UUID project id: {error}"))?;

        store
            .create_problem(
                "pg-problem-other-project".to_string(),
                other_project_id.clone(),
                "P-PG-TEXT-0002".to_string(),
                "Fixture isolation sentinel".to_string(),
                None,
                "closed".to_string(),
                None,
                None,
                None,
                None,
                "medium".to_string(),
                "medium".to_string(),
                "medium".to_string(),
                false,
                false,
                false,
                false,
                None,
                None,
                None,
                None,
                now,
            )
            .await
            .map_err(|error| format!("create a problem in the other fixture project: {error}"))?;

        let listed = store
            .list_problems(project_id.clone(), None, ListParams::default())
            .await
            .map_err(|error| format!("list text-id project: {error}"))?;
        if listed.len() != 1 || listed[0].project_id != project_id {
            return Err(format!("expected one problem for textual project id, got {listed:?}"));
        }

        if !store
            .list_problems(project_id.clone(), Some("closed".to_string()), ListParams::default())
            .await
            .map_err(|error| format!("filter text-id project: {error}"))?
            .is_empty()
        {
            return Err("closed filter returned another project's problem".to_string());
        }
        let project_count = store
            .count_problems(project_id)
            .await
            .map_err(|error| format!("count text-id project: {error}"))?;
        let other_project_count = store
            .count_problems(other_project_id)
            .await
            .map_err(|error| format!("count other fixture project: {error}"))?;
        if project_count != 1 || other_project_count != 1 {
            return Err(format!(
                "expected one problem in each fixture project, got {project_count} and {other_project_count}"
            ));
        }
        fixture.assert_all_connection_search_paths().await
    }

    /// SQLite evidence round-trip: create then list returns the same item.
    #[tokio::test]
    async fn sqlite_evidence_create_then_list() {
        let store = make_sqlite_store().await;

        // Empty initially
        let initial = store.list_evidence().await.expect("list_evidence");
        assert!(initial.is_empty(), "store should be empty initially");

        let now = Utc::now();
        let ev = store
            .create_evidence(
                "ev-test-1".to_string(),
                "req-001".to_string(),
                "test_result".to_string(),
                "https://ci.example.com/run/42".to_string(),
                serde_json::json!({"passed": true, "suite": "unit"}),
                now,
            )
            .await
            .expect("create_evidence");

        assert_eq!(ev.id, "ev-test-1");
        assert_eq!(ev.artifact_id, "req-001");
        assert_eq!(ev.kind, "test_result");

        let listed = store
            .list_evidence()
            .await
            .expect("list_evidence after create");
        assert_eq!(listed.len(), 1, "exactly one evidence item");
        let found = &listed[0];
        assert_eq!(found.id, "ev-test-1");
        assert_eq!(found.metadata["passed"], true);

        // count_evidence reflects the insert
        let count = store.count_evidence().await.expect("count_evidence");
        assert_eq!(count, 1);
    }

    /// SQLite sprint round-trip: create then list returns the sprint with status=planned.
    #[tokio::test]
    async fn sqlite_sprint_create_then_list() {
        let store = make_sqlite_store().await;

        let now = Utc::now();
        let start = Utc.with_ymd_and_hms(2026, 1, 1, 0, 0, 0).unwrap();
        let end = Utc.with_ymd_and_hms(2026, 1, 14, 0, 0, 0).unwrap();

        let sprint = store
            .create_sprint(
                "sprint-sqlite-1".to_string(),
                "On-device Sprint 1".to_string(),
                "Prove SQLite tier works without a server".to_string(),
                start,
                end,
                now,
            )
            .await
            .expect("create_sprint");

        assert_eq!(sprint.id, "sprint-sqlite-1");
        assert_eq!(sprint.status, "planned");

        let listed = store.list_sprints().await.expect("list_sprints");
        assert_eq!(listed.len(), 1);
        assert_eq!(listed[0].name, "On-device Sprint 1");
    }

    /// SQLite problem round-trip: create then list returns the problem with
    /// the same project_id + status, count reflects the insert.
    #[tokio::test]
    async fn sqlite_problem_create_then_list() {
        let store = make_sqlite_store().await;

        // Empty initially
        let initial = store
            .list_problems("proj-1".to_string(), None, ListParams::default())
            .await
            .expect("list_problems empty");
        assert!(initial.is_empty(), "store should be empty initially");

        let now = Utc::now();
        let problem = store
            .create_problem(
                "prob-test-1".to_string(),
                "proj-1".to_string(),
                "P-20260101-ABCD1234".to_string(),
                "Login latency spikes every Friday".to_string(),
                Some("Investigating p99 latency".to_string()),
                "in_investigation".to_string(),
                None,
                Some("performance".to_string()),
                None,
                Some(serde_json::json!(["latency", "weekend"])),
                "high".to_string(),
                "medium".to_string(),
                "high".to_string(),
                false,
                false,
                false,
                false,
                Some("oncall@example.com".to_string()),
                Some("platform".to_string()),
                None,
                None,
                now,
            )
            .await
            .expect("create_problem");

        assert_eq!(problem.id, "prob-test-1");
        assert_eq!(problem.project_id, "proj-1");
        assert_eq!(problem.problem_number, "P-20260101-ABCD1234");
        assert_eq!(problem.status, "in_investigation");
        assert_eq!(problem.priority, "high");

        // list (no status filter) returns the row
        let listed = store
            .list_problems("proj-1".to_string(), None, ListParams::default())
            .await
            .expect("list_problems after create");
        assert_eq!(listed.len(), 1, "exactly one problem");
        let found = &listed[0];
        assert_eq!(found.id, "prob-test-1");
        assert_eq!(
            found
                .tags
                .as_ref()
                .and_then(|v| v.as_array())
                .map(|a| a.len()),
            Some(2),
            "tags round-trip as JSON array"
        );

        // list with status filter narrows correctly
        let filtered = store
            .list_problems("proj-1".to_string(), Some("closed".to_string()), ListParams::default())
            .await
            .expect("list_problems filtered");
        assert!(filtered.is_empty(), "no problems in 'closed' status");

        // count_problems reflects the insert
        let count = store
            .count_problems("proj-1".to_string())
            .await
            .expect("count_problems");
        assert_eq!(count, 1, "count_problems == 1");
    }

    // -----------------------------------------------------------------------
    // Real ingest path tests — SQLite in-memory, no live GitHub/Jira required
    // -----------------------------------------------------------------------

    /// Fixture that represents a minimal GitHub issue payload.
    fn gh_issue_fixture(number: u64, title: &str, body: &str) -> Value {
        serde_json::json!({
            "number": number,
            "title": title,
            "body": body,
            "html_url": format!("https://github.com/owner/repo/issues/{number}"),
            "state": "open"
        })
    }

    /// Fixture that represents a minimal Jira issue payload.
    fn jira_issue_fixture(key: &str, summary: &str, body: &str) -> Value {
        serde_json::json!({
            "key": key,
            "title": summary,
            "body": body,
            "status": "open"
        })
    }

    /// Payload-based GitHub ingest: fixture issues are persisted as stories + evidence.
    #[tokio::test]
    async fn sqlite_ingest_github_payload_creates_stories() {
        let store = make_sqlite_store().await;
        let store_arc: std::sync::Arc<dyn crate::store::Store> = std::sync::Arc::new(store);

        let issues = vec![
            gh_issue_fixture(1, "Fix login bug", "Closes REQ-001"),
            gh_issue_fixture(2, "Add dark mode", "Relates to SPEC-007"),
        ];

        let result =
            crate::ingest::ingest_from_payload(&issues, "number", "github", &store_arc).await;

        assert_eq!(result.total_processed, 2, "both issues processed");
        assert_eq!(result.requirements_created, 2, "two stories created");
        assert!(result.errors.is_empty(), "no errors: {:?}", result.errors);

        // Evidence items should be created (one per issue)
        let evidence = store_arc.list_evidence().await.expect("list_evidence");
        assert_eq!(evidence.len(), 2, "two evidence items created");
        assert_eq!(evidence[0].kind, "github_issue");
    }

    /// Payload-based ingest creates trace-links when body references REQ-NNN.
    #[tokio::test]
    async fn sqlite_ingest_creates_trace_links_from_req_refs() {
        let store = make_sqlite_store().await;
        let store_arc: std::sync::Arc<dyn crate::store::Store> = std::sync::Arc::new(store);

        let issues = vec![gh_issue_fixture(
            10,
            "Auth improvement",
            "This satisfies REQ-001 and also references SPEC-042 per design doc.",
        )];

        let result =
            crate::ingest::ingest_from_payload(&issues, "number", "github", &store_arc).await;

        assert_eq!(result.requirements_created, 1);
        // REQ-001 and SPEC-042 → 2 trace-links
        assert_eq!(result.trace_links_created, 2, "two trace-links expected");
        assert!(result.errors.is_empty(), "no errors: {:?}", result.errors);
    }

    /// Payload with missing/empty titles: skipped entries don't create stories.
    #[tokio::test]
    async fn sqlite_ingest_skips_empty_title_issues() {
        let store = make_sqlite_store().await;
        let store_arc: std::sync::Arc<dyn crate::store::Store> = std::sync::Arc::new(store);

        let issues = vec![
            serde_json::json!({"number": 5, "title": "", "body": "", "html_url": "", "state": "open"}),
            serde_json::json!({"number": 6, "body": "no title field", "html_url": "", "state": "open"}),
            gh_issue_fixture(7, "Valid issue", "REQ-010"),
        ];

        let result =
            crate::ingest::ingest_from_payload(&issues, "number", "github", &store_arc).await;

        // filter_map drops the 2 invalid issues before persist; total_processed = 1
        assert_eq!(
            result.total_processed, 1,
            "only 1 issue survived title filter"
        );
        assert_eq!(
            result.requirements_created, 1,
            "only the valid issue creates a story"
        );
        assert_eq!(result.trace_links_created, 1, "REQ-010 → 1 trace-link");
    }

    /// Jira payload ingest works identically to GitHub payload ingest.
    #[tokio::test]
    async fn sqlite_ingest_jira_payload_creates_stories() {
        let store = make_sqlite_store().await;
        let store_arc: std::sync::Arc<dyn crate::store::Store> = std::sync::Arc::new(store);

        let issues = vec![
            jira_issue_fixture("PROJ-1", "Initial setup", "REQ-100"),
            jira_issue_fixture("PROJ-2", "Auth flow", ""),
        ];

        let result = crate::ingest::ingest_from_payload(&issues, "key", "jira", &store_arc).await;

        assert_eq!(result.total_processed, 2);
        assert_eq!(result.requirements_created, 2);
        // PROJ-1 has REQ-100 ref → 1 trace-link; PROJ-2 has none → 0
        assert_eq!(result.trace_links_created, 1);
        assert!(result.errors.is_empty());
    }

    /// create_story and create_trace_link persist and are visible via list_stories.
    #[tokio::test]
    async fn sqlite_create_story_and_trace_link_round_trip() {
        use crate::store::Store as _;
        let store = make_sqlite_store().await;
        let now = Utc::now();

        let story = store
            .create_story(
                "story-gh-42".to_string(),
                None,
                "Implement rate limiting".to_string(),
                "Closes REQ-009. See also NFR-03.".to_string(),
                "open".to_string(),
                Some(3),
                now,
            )
            .await
            .expect("create_story");

        assert_eq!(story.id, "story-gh-42");
        assert_eq!(story.story_points, Some(3));

        let listed = store.list_stories().await.expect("list_stories");
        assert_eq!(listed.len(), 1);
        assert_eq!(listed[0].title, "Implement rate limiting");

        let link = store
            .create_trace_link(
                "tl-test-1".to_string(),
                "story-gh-42".to_string(),
                "REQ-009".to_string(),
                "satisfies".to_string(),
                0.8,
                "github".to_string(),
                now,
            )
            .await
            .expect("create_trace_link");

        assert_eq!(link.id, "tl-test-1");
        assert_eq!(link.source_id, "story-gh-42");
        assert_eq!(link.target_id, "REQ-009");
        assert_eq!(link.relationship, "satisfies");
        assert!((link.confidence - 0.8).abs() < 1e-9);
        assert_eq!(link.source, "github");

        let row = sqlx::query(
            "SELECT id, source_id, target_id, relationship, confidence, source, created_at, updated_at \
             FROM trace_links WHERE id = ?1",
        )
        .bind("tl-test-1")
        .fetch_one(&store.pool)
        .await
        .expect("trace link row should persist");

        let persisted_source_id: String = row.try_get("source_id").unwrap_or_default();
        let persisted_target_id: String = row.try_get("target_id").unwrap_or_default();
        let persisted_relationship: String = row.try_get("relationship").unwrap_or_default();
        let persisted_confidence: f64 = row.try_get("confidence").unwrap_or_default();
        let persisted_source: String = row.try_get("source").unwrap_or_default();

        assert_eq!(persisted_source_id, "story-gh-42");
        assert_eq!(persisted_target_id, "REQ-009");
        assert_eq!(persisted_relationship, "satisfies");
        assert!((persisted_confidence - 0.8).abs() < 1e-9);
        assert_eq!(persisted_source, "github");
    }

    #[tokio::test]
    async fn sqlite_store_lists_only_trace_links_incident_to_the_artifact() {
        use crate::store::Store as _;

        let store = make_sqlite_store().await;
        let now = Utc::now();
        for (id, source_id, target_id) in [
            ("trace-source", "artifact-1", "artifact-2"),
            ("trace-target", "artifact-3", "artifact-1"),
            ("trace-other", "artifact-4", "artifact-5"),
        ] {
            store
                .create_trace_link(
                    id.to_string(),
                    source_id.to_string(),
                    target_id.to_string(),
                    "verifies".to_string(),
                    1.0,
                    "manual".to_string(),
                    now,
                )
                .await
                .expect("seed persisted trace link");
        }

        let links = store
            .list_trace_links_for_artifact("artifact-1".to_string())
            .await
            .expect("list persisted trace links");

        assert_eq!(
            links
                .iter()
                .map(|link| link.id.as_str())
                .collect::<Vec<_>>(),
            ["trace-source", "trace-target",]
        );
        assert!(links
            .iter()
            .all(|link| link.source_id == "artifact-1" || link.target_id == "artifact-1"));
    }
}
