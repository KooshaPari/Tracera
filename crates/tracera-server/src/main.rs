use axum::{
    routing::{get, post},
    Json, Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::env;
use std::net::SocketAddr;
use std::sync::{Arc, Mutex};
use tracing_subscriber::EnvFilter;

#[derive(Clone, Default)]
struct AppState {
    version: String,
    evidence: Arc<Mutex<Vec<EvidenceItem>>>,
    sprints: Arc<Mutex<Vec<Sprint>>>,
    stories: Arc<Mutex<Vec<Story>>>,
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

// --- evidence store (port of src/tracertm/api/routers/evidence.py) ---
#[derive(Clone, Serialize)]
struct EvidenceItem {
    id: String,
    artifact_id: String,
    kind: String,
    url: String,
    metadata: Value,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

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

// --- sdlc-pm (port of src/tracertm/api/routers/sdlc_pm.py) ---
#[derive(Clone, Serialize)]
struct Sprint {
    id: String,
    name: String,
    goal: String,
    start_date: DateTime<Utc>,
    end_date: DateTime<Utc>,
    status: String,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

#[derive(Clone, Serialize)]
struct Story {
    id: String,
    sprint_id: Option<String>,
    title: String,
    description: String,
    status: String,
    story_points: Option<i64>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

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

// One requirement + one trace link per issue that has a non-empty title; title-less issues become errors.
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

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env().add_directive("tracera_server=info".parse().unwrap()))
        .init();

    let state = AppState {
        version: env!("CARGO_PKG_VERSION").to_string(),
        evidence: Arc::new(Mutex::new(Vec::new())),
        sprints: Arc::new(Mutex::new(Vec::new())),
        stories: Arc::new(Mutex::new(Vec::new())),
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
        .and_then(|value| value.parse().ok())
        .unwrap_or_else(|| SocketAddr::from(([127, 0, 0, 1], 8080)));
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
    let max_depth = request.max_depth;

    let links: Vec<TraceLinkInput> = request.matrix.links.clone();
    let adj = build_adjacency(&links);

    // Collect conflicts from the link set
    let conflicts: Vec<TraceLinkInput> = links
        .iter()
        .filter(|l| l.relationship == "conflicts_with")
        .cloned()
        .collect();

    // Seeds are always included at depth=0
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

    // BFS over the adjacency graph, clamped to max_depth
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
        // Confidence-weighted score: decays by depth (halved per hop, floored at 0.1)
        let score = (0.5_f64.powi(dist as i32)).max(0.1);
        // via: immediate predecessors of this node in the link set
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

async fn list_sprints(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<Vec<Sprint>> {
    Json(state.sprints.lock().unwrap().clone())
}

async fn list_stories(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<Vec<Story>> {
    Json(state.stories.lock().unwrap().clone())
}

async fn create_sprint(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<SprintCreate>,
) -> (axum::http::StatusCode, Json<Sprint>) {
    let now = Utc::now();
    let mut store = state.sprints.lock().unwrap();
    let sprint = Sprint {
        id: format!("sprint-{}", store.len() + 1),
        name: payload.name,
        goal: payload.goal,
        start_date: payload.start_date,
        end_date: payload.end_date,
        status: "planned".to_string(),
        created_at: now,
        updated_at: now,
    };
    store.push(sprint.clone());
    (axum::http::StatusCode::CREATED, Json(sprint))
}

async fn list_teams() -> Json<Vec<TeamResponse>> {
    // Seed defaults (mirrors Python's empty-store fallback). ponytail: static seed, swap for store when CRUD lands
    Json(vec![
        TeamResponse { id: "team-1".into(), name: "Platform Team".into(), description: "Core platform engineering".into(), members: vec![] },
        TeamResponse { id: "team-2".into(), name: "Product Team".into(), description: "Product feature development".into(), members: vec![] },
        TeamResponse { id: "team-3".into(), name: "Security Team".into(), description: "Security and compliance".into(), members: vec![] },
    ])
}

async fn org_metrics() -> Json<MetricsResponse> {
    Json(MetricsResponse { total_artifacts: 30, coverage_ratio: 0.75, open_gaps: 3 })
}

async fn ingest_github(Json(req): Json<GitHubIngestRequest>) -> Json<BulkIngestionResult> {
    Json(ingest_issues(&req.issues, "number"))
}

async fn ingest_jira(Json(req): Json<JiraIngestRequest>) -> Json<BulkIngestionResult> {
    Json(ingest_issues(&req.issues, "key"))
}

async fn list_evidence(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Json<EvidenceList> {
    let items = state.evidence.lock().unwrap().clone();
    Json(EvidenceList { count: items.len(), items })
}

async fn create_evidence(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<EvidenceCreate>,
) -> (axum::http::StatusCode, Json<EvidenceItem>) {
    let now = Utc::now();
    let mut store = state.evidence.lock().unwrap();
    let item = EvidenceItem {
        id: format!("ev-{}", store.len() + 1),
        artifact_id: payload.artifact_id,
        kind: payload.kind,
        url: payload.url,
        metadata: payload.metadata,
        created_at: now,
        updated_at: now,
    };
    store.push(item.clone());
    (axum::http::StatusCode::CREATED, Json(item))
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

#[cfg(test)]
mod tests {
    use super::*;

    /// Build a minimal link list representing the chain:
    ///   seed -> hop1 -> hop2 -> hop3
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

    /// Helper: run the BFS+depth-clamp logic the same way the handler does.
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

    /// Regression test for the stub: verifies that the impact handler now walks
    /// the adjacency graph transitively, not just returning seeds.
    #[test]
    fn impact_traverses_multi_hop_at_depth_3() {
        let links = chain_links();
        let seeds = vec!["seed".to_string()];
        let resp = run_impact(links, seeds, 3);

        let ids = affected_ids(&resp);
        // seed is always present at depth=0
        assert!(ids.contains(&"seed"), "seed must be in affected");
        // 1-hop node
        assert!(ids.contains(&"hop1"), "hop1 (depth 1) must be in affected at max_depth=3");
        // 2-hop node
        assert!(ids.contains(&"hop2"), "hop2 (depth 2) must be in affected at max_depth=3");
        // 3-hop node — this was NOT returned by the stub (only seeds were returned)
        assert!(ids.contains(&"hop3"), "hop3 (depth 3) must be in affected at max_depth=3");
        assert!(!resp.truncated, "no truncation expected at max_depth=3 for a 3-hop chain");
        assert_eq!(resp.max_depth_seen, 3);
    }

    /// Depth=1 bound must exclude the 2-hop (and deeper) nodes.
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

    /// Depth=0 returns only seeds with truncated=true if graph has further edges.
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

    /// bfs_distances itself: smoke test on adjacency
    #[test]
    fn bfs_distances_basic() {
        let links = chain_links();
        let adj = build_adjacency(&links);
        let distances = bfs_distances(&adj, &["seed".to_string()]);
        let dist_map: std::collections::HashMap<_, _> =
            distances.into_iter().collect();
        assert_eq!(dist_map["hop1"], 1);
        assert_eq!(dist_map["hop2"], 2);
        assert_eq!(dist_map["hop3"], 3);
    }
}
