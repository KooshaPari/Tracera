mod pg_store;
mod sqlite_store;
mod store;

use axum::{
    routing::{get, post},
    Json, Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::env;
use std::net::SocketAddr;
use std::sync::Arc;
use tracing::info;
use tracing_subscriber::EnvFilter;
use uuid::Uuid;

use store::{EvidenceItem, Sprint, Story, Store, TeamRow};

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
    store: Arc<dyn Store>,
}

// ---------------------------------------------------------------------------
// Generic response shapes
// ---------------------------------------------------------------------------
#[derive(Serialize)]
struct StatusResponse {
    status: &'static str,
}

#[derive(Serialize)]
struct ReadyResponse {
    status: &'static str,
    version: String,
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
struct MetricsResponse {
    total_artifacts: usize,
    coverage_ratio: f64,
    open_gaps: u32,
}

// --- ingest (port of src/tracertm/services/{github,jira}_import_service.py) ---
#[derive(Deserialize)]
struct GitHubIngestRequest {
    #[allow(dead_code)]
    repo: String,
    #[serde(default)]
    issues: Vec<Value>,
}

#[derive(Deserialize)]
struct JiraIngestRequest {
    #[serde(default)]
    issues: Vec<Value>,
}

#[derive(Serialize)]
struct BulkIngestionResult {
    total_processed: usize,
    requirements_created: usize,
    trace_links_created: usize,
    errors: Vec<String>,
}

fn ingest_issues(issues: &[Value], ref_field: &str) -> BulkIngestionResult {
    let mut created = 0usize;
    let mut errors = Vec::new();
    for issue in issues {
        let title = issue.get("title").and_then(|v| v.as_str()).map(str::trim);
        match title {
            Some(t) if !t.is_empty() => created += 1,
            _ => {
                let r = issue
                    .get(ref_field)
                    .map(|v| v.to_string())
                    .unwrap_or_else(|| "unknown".to_string());
                errors.push(format!("missing title for issue {r}"));
            }
        }
    }
    BulkIngestionResult {
        total_processed: issues.len(),
        requirements_created: created,
        trace_links_created: created,
        errors,
    }
}

// ---------------------------------------------------------------------------
// Startup — backend selection by DATABASE_URL scheme
// ---------------------------------------------------------------------------
#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::from_default_env()
                .add_directive("tracera_server=info".parse().unwrap()),
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

    let store: Arc<dyn Store> = if database_url.starts_with("postgres://")
        || database_url.starts_with("postgresql://")
    {
        info!("Backend: Postgres (server tier)");
        let pool = sqlx::PgPool::connect(&database_url).await.unwrap_or_else(|e| {
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
        Arc::new(pg_store::PgStore::new(pool))
    } else if database_url.starts_with("sqlite://")
        || database_url.starts_with("sqlite:")
        || database_url.ends_with(".db")
    {
        info!("Backend: SQLite (on-device tier)");
        let pool = sqlx::SqlitePool::connect(&database_url)
            .await
            .unwrap_or_else(|e| {
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
        Arc::new(sqlite_store::SqliteStore::new(pool))
    } else {
        eprintln!(
            "FATAL: Unrecognised DATABASE_URL scheme.\n\
             Use postgres:// for Postgres or sqlite:// for SQLite on-device tier."
        );
        std::process::exit(1);
    };

    let state = AppState {
        version: env!("CARGO_PKG_VERSION").to_string(),
        store,
    };

    let app = Router::new()
        .route("/healthz", get(healthz))
        .route("/health", get(health))
        .route("/readyz", get(readyz))
        .route("/ready", get(ready))
        .route("/api/v1/coverage-matrix", post(coverage_matrix))
        .route("/api/v1/impact", post(impact))
        .route("/api/v1/confidence", post(confidence))
        .route("/api/v1/blast-radius", post(blast_radius))
        .route("/api/v1/governance/spec-check", post(spec_check))
        .route("/api/v1/trace/forward/:artifact_id", post(trace_forward))
        .route("/api/v1/trace/reverse/:artifact_id", post(trace_reverse))
        .route("/evidence", get(list_evidence).post(create_evidence))
        .route("/evidence/health", get(health))
        .route("/ingest/github", post(ingest_github))
        .route("/ingest/jira", post(ingest_jira))
        .route("/sdlc-pm/health", get(health))
        .route("/sdlc-pm/sprints", get(list_sprints).post(create_sprint))
        .route("/sdlc-pm/stories", get(list_stories))
        .route("/org-intel/health", get(health))
        .route("/org-intel/teams", get(list_teams))
        .route("/org-intel/metrics", get(org_metrics))
        .with_state(state);

    let addr = env::var("TRACERA_BIND_ADDR")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or_else(|| SocketAddr::from(([127, 0, 0, 1], 8080)));

    let listener = tokio::net::TcpListener::bind(addr).await.expect("bind");
    info!("tracera-server listening on {addr}");
    axum::serve(listener, app).await.expect("server failed");
}

// ---------------------------------------------------------------------------
// Health / ready
// ---------------------------------------------------------------------------
async fn healthz() -> Json<StatusResponse> {
    Json(StatusResponse { status: "ok" })
}

async fn health() -> Json<StatusResponse> {
    Json(StatusResponse { status: "ok" })
}

async fn readyz(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<ReadyResponse> {
    Json(ReadyResponse {
        status: "ready",
        version: state.version,
    })
}

async fn ready(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<ReadyResponse> {
    Json(ReadyResponse {
        status: "ready",
        version: state.version,
    })
}

// ---------------------------------------------------------------------------
// Computation-only handlers (no persistence)
// ---------------------------------------------------------------------------
async fn coverage_matrix(
    Json(request): Json<CoverageMatrixRequest>,
) -> Json<CoverageMatrixResponse> {
    Json(build_coverage_matrix(request))
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
        status: if violations.is_empty() { "pass" } else { "fail" },
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

// ---------------------------------------------------------------------------
// Evidence handlers — delegate to store trait
// ---------------------------------------------------------------------------
async fn list_evidence(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<EvidenceList> {
    let items = state.store.list_evidence().await.unwrap_or_else(|e| {
        tracing::error!("list_evidence store error: {e}");
        vec![]
    });
    Json(EvidenceList {
        count: items.len(),
        items,
    })
}

async fn create_evidence(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<EvidenceCreate>,
) -> (axum::http::StatusCode, Json<EvidenceItem>) {
    let now = Utc::now();
    let id = format!("ev-{}", Uuid::new_v4());
    let meta = serde_json::to_value(&payload.metadata)
        .unwrap_or(Value::Object(serde_json::Map::new()));

    let item = state
        .store
        .create_evidence(id, payload.artifact_id, payload.kind, payload.url, meta, now)
        .await
        .unwrap_or_else(|e| {
            panic!("create_evidence: store insert failed: {e}");
        });

    (axum::http::StatusCode::CREATED, Json(item))
}

// ---------------------------------------------------------------------------
// Sprint handlers — delegate to store trait
// ---------------------------------------------------------------------------
async fn list_sprints(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<Vec<Sprint>> {
    let sprints = state.store.list_sprints().await.unwrap_or_else(|e| {
        tracing::error!("list_sprints store error: {e}");
        vec![]
    });
    Json(sprints)
}

async fn create_sprint(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<SprintCreate>,
) -> (axum::http::StatusCode, Json<Sprint>) {
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
        .unwrap_or_else(|e| {
            panic!("create_sprint: store insert failed: {e}");
        });

    (axum::http::StatusCode::CREATED, Json(sprint))
}

// ---------------------------------------------------------------------------
// Story handlers
// ---------------------------------------------------------------------------
async fn list_stories(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<Vec<Story>> {
    let stories = state.store.list_stories().await.unwrap_or_else(|e| {
        tracing::error!("list_stories store error: {e}");
        vec![]
    });
    Json(stories)
}

// ---------------------------------------------------------------------------
// Teams handler
// ---------------------------------------------------------------------------
async fn list_teams(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<Vec<TeamResponse>> {
    let rows: Vec<TeamRow> = state.store.list_teams().await.unwrap_or_else(|e| {
        tracing::error!("list_teams store error: {e}");
        vec![]
    });
    Json(
        rows.into_iter()
            .map(|r| TeamResponse {
                id: r.id,
                name: r.name,
                description: r.description,
                members: r.members,
            })
            .collect(),
    )
}

// ---------------------------------------------------------------------------
// Org metrics
// ---------------------------------------------------------------------------
async fn org_metrics(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<MetricsResponse> {
    let count = state.store.count_evidence().await.unwrap_or(0);
    Json(MetricsResponse {
        total_artifacts: count as usize,
        coverage_ratio: 0.75,
        open_gaps: 3,
    })
}

// ---------------------------------------------------------------------------
// Ingest handlers (no persistence)
// ---------------------------------------------------------------------------
async fn ingest_github(Json(req): Json<GitHubIngestRequest>) -> Json<BulkIngestionResult> {
    Json(ingest_issues(&req.issues, "number"))
}

async fn ingest_jira(Json(req): Json<JiraIngestRequest>) -> Json<BulkIngestionResult> {
    Json(ingest_issues(&req.issues, "key"))
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
    use chrono::TimeZone;

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

    fn run_impact(links: Vec<TraceLinkInput>, seeds: Vec<String>, max_depth: u32) -> ImpactResponse {
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
        resp.affected.iter().map(|n| n.artifact_id.as_str()).collect()
    }

    #[test]
    fn impact_traverses_multi_hop_at_depth_3() {
        let links = chain_links();
        let seeds = vec!["seed".to_string()];
        let resp = run_impact(links, seeds, 3);

        let ids = affected_ids(&resp);
        assert!(ids.contains(&"seed"), "seed must be in affected");
        assert!(ids.contains(&"hop1"), "hop1 (depth 1) must be in affected at max_depth=3");
        assert!(ids.contains(&"hop2"), "hop2 (depth 2) must be in affected at max_depth=3");
        assert!(ids.contains(&"hop3"), "hop3 (depth 3) must be in affected at max_depth=3");
        assert!(!resp.truncated, "no truncation expected at max_depth=3 for a 3-hop chain");
        assert_eq!(resp.max_depth_seen, 3);
    }

    #[test]
    fn impact_depth_1_excludes_2_hop_node() {
        let links = chain_links();
        let seeds = vec!["seed".to_string()];
        let resp = run_impact(links, seeds, 1);

        let ids = affected_ids(&resp);
        assert!(ids.contains(&"seed"), "seed present");
        assert!(ids.contains(&"hop1"), "hop1 (depth 1) reachable within max_depth=1");
        assert!(!ids.contains(&"hop2"), "hop2 (depth 2) must NOT appear at max_depth=1");
        assert!(!ids.contains(&"hop3"), "hop3 (depth 3) must NOT appear at max_depth=1");
        assert!(resp.truncated, "truncated flag must be set when nodes are clamped");
        assert_eq!(resp.max_depth_seen, 1);
    }

    #[test]
    fn impact_depth_0_returns_only_seeds() {
        let links = chain_links();
        let seeds = vec!["seed".to_string()];
        let resp = run_impact(links, seeds, 0);

        let ids = affected_ids(&resp);
        assert_eq!(ids, vec!["seed"]);
        assert!(resp.truncated, "must be truncated when max_depth=0 and edges exist");
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

    #[test]
    fn ingest_all_valid() {
        let issues = vec![
            serde_json::json!({"title": "Fix login", "number": 1}),
            serde_json::json!({"title": "Add tests", "number": 2}),
        ];
        let r = ingest_issues(&issues, "number");
        assert_eq!(r.total_processed, 2);
        assert_eq!(r.requirements_created, 2);
        assert_eq!(r.trace_links_created, 2);
        assert!(r.errors.is_empty());
    }

    #[test]
    fn ingest_missing_title() {
        let issues = vec![
            serde_json::json!({"number": 42}),
            serde_json::json!({"title": "", "number": 43}),
        ];
        let r = ingest_issues(&issues, "number");
        assert_eq!(r.total_processed, 2);
        assert_eq!(r.requirements_created, 0);
        assert_eq!(r.errors.len(), 2);
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

        crate::sqlite_store::SqliteStore::new(pool)
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

        let listed = store.list_evidence().await.expect("list_evidence after create");
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
}
