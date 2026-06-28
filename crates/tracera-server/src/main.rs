use axum::{
    routing::{get, post},
    Json, Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tracing_subscriber::EnvFilter;

#[derive(Clone, Default)]
struct AppState {
    version: String,
}

#[derive(Serialize)]
struct StatusResponse {
    status: &'static str,
}

#[derive(Serialize)]
struct ReadyResponse {
    status: &'static str,
    version: String,
}

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

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env().add_directive("tracera_server=info".parse().unwrap()))
        .init();

    let state = AppState {
        version: env!("CARGO_PKG_VERSION").to_string(),
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
        .with_state(state);

    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    let listener = tokio::net::TcpListener::bind(addr).await.expect("bind");
    axum::serve(listener, app).await.expect("server failed");
}

async fn healthz() -> Json<StatusResponse> {
    Json(StatusResponse { status: "ok" })
}

async fn health() -> Json<StatusResponse> {
    Json(StatusResponse { status: "ok" })
}

async fn readyz(axum::extract::State(state): axum::extract::State<AppState>) -> Json<ReadyResponse> {
    Json(ReadyResponse {
        status: "ready",
        version: state.version,
    })
}

async fn ready(axum::extract::State(state): axum::extract::State<AppState>) -> Json<ReadyResponse> {
    Json(ReadyResponse {
        status: "ready",
        version: state.version,
    })
}

async fn coverage_matrix(Json(request): Json<CoverageMatrixRequest>) -> Json<CoverageMatrixResponse> {
    Json(build_coverage_matrix(request))
}

async fn impact(Json(request): Json<ImpactRequest>) -> Json<ImpactResponse> {
    let matrix = build_coverage_matrix(request.matrix);
    let mut affected = Vec::new();
    for seed in &request.changed_artifact_ids {
        affected.push(ImpactNodeResponse {
            artifact_id: seed.clone(),
            depth: 0,
            via: vec![],
            score: 1.0,
        });
    }
    Json(ImpactResponse {
        seeds: request.changed_artifact_ids,
        affected,
        total_score: 1.0_f64.max(matrix.cell_count as f64),
        truncated: request.max_depth == 0,
        max_depth_seen: 0,
        conflicts: vec![],
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
        traces_by_spec.entry(t.spec_id.as_str()).or_default().insert(t.kind.as_str());
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
            violations.push(viol(&s.spec_id, "missing_acceptance", "Acceptance criteria required"));
        }
        if s.evidence_links.is_empty() {
            violations.push(viol(&s.spec_id, "missing_evidence", "Evidence links required"));
        }
        let kinds = traces_by_spec.get(s.spec_id.as_str());
        let has = |k: &str| kinds.map(|set| set.contains(k)).unwrap_or(false);
        if !has("implementation") {
            violations.push(viol(&s.spec_id, "missing_implementation", "Implementation trace required"));
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
    GovernanceViolation { spec_id: spec_id.to_string(), code, message }
}

async fn blast_radius(Json(req): Json<BlastRadiusRequest>) -> Json<BlastRadiusResponse> {
    let adj = build_adjacency(&req.links);
    let mut blast = Vec::new();
    for node in bfs_distances(&adj, &req.changed_artifact_ids) {
        blast.push(BlastNodeResponse { artifact_id: node.0, distance: node.1 });
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
    Json(TraceNeighborsResponse { artifact_id, direction: "forward", neighbors })
}

async fn trace_reverse(
    axum::extract::Path(artifact_id): axum::extract::Path<String>,
    Json(req): Json<TraceQueryRequest>,
) -> Json<TraceNeighborsResponse> {
    let neighbors = neighbors_of(&req.links, &artifact_id, false);
    Json(TraceNeighborsResponse { artifact_id, direction: "reverse", neighbors })
}

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
        adj.entry(l.source_id.clone()).or_default().push(l.target_id.clone());
    }
    adj
}

// BFS forward reachability with distance; seeds are excluded from output. ponytail: O(V+E) plain BFS, fine for trace graphs
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
    } else if matches!(link.relationship.as_str(), "verifies" | "satisfies") && link.confidence >= 0.9 {
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
    if union == 0.0 { 0.0 } else { inter / union }
}

fn default_stale_after_days() -> u32 {
    90
}

fn default_max_depth() -> u32 {
    10
}
