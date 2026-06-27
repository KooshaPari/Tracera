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
