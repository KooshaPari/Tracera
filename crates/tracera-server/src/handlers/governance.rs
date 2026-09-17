use axum::Json;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use crate::graph::{bfs_distances, build_adjacency, build_coverage_matrix, neighbors_of};
use crate::validation::{validate_text, MAX_ID_CHARS};
use crate::{bad_request, ErrorResponse};

// ---------------------------------------------------------------------------
// Trace-link types (coverage-matrix / impact / blast-radius / spec-check)
// These are computation-only -- no persistence needed.
// ---------------------------------------------------------------------------
#[derive(Debug, Deserialize, Serialize, Clone)]
#[serde(rename_all = "snake_case")]
pub(crate) struct TraceLinkInput {
    pub(crate) source_id: String,
    pub(crate) target_id: String,
    pub(crate) relationship: String,
    pub(crate) confidence: f64,
    pub(crate) updated_at: Option<DateTime<Utc>>,
}

#[derive(Serialize)]
pub(crate) struct MatrixCellResponse {
    pub(crate) source_id: String,
    pub(crate) target_id: String,
    pub(crate) coverage: String,
    pub(crate) links: Vec<TraceLinkInput>,
}

#[derive(Deserialize)]
pub(crate) struct CoverageMatrixRequest {
    #[serde(default)]
    pub(crate) links: Vec<TraceLinkInput>,
    #[serde(default = "default_stale_after_days")]
    pub(crate) stale_after_days: u32,
}

#[derive(Serialize)]
pub(crate) struct CoverageMatrixResponse {
    pub(crate) generated_at: DateTime<Utc>,
    pub(crate) link_count: usize,
    pub(crate) cell_count: usize,
    pub(crate) stale_links: usize,
    pub(crate) cells: Vec<MatrixCellResponse>,
}

#[derive(Deserialize)]
pub(crate) struct ImpactRequest {
    #[serde(flatten)]
    pub(crate) matrix: CoverageMatrixRequest,
    pub(crate) changed_artifact_ids: Vec<String>,
    #[serde(default = "default_max_depth")]
    pub(crate) max_depth: u32,
}

#[derive(Serialize)]
pub(crate) struct ImpactNodeResponse {
    pub(crate) artifact_id: String,
    pub(crate) depth: u32,
    pub(crate) via: Vec<String>,
    pub(crate) score: f64,
}

#[derive(Serialize)]
pub(crate) struct ImpactResponse {
    pub(crate) seeds: Vec<String>,
    pub(crate) affected: Vec<ImpactNodeResponse>,
    pub(crate) total_score: f64,
    pub(crate) truncated: bool,
    pub(crate) max_depth_seen: u32,
    pub(crate) conflicts: Vec<TraceLinkInput>,
}

#[derive(Deserialize)]
pub(crate) struct ConfidenceRequest {
    pub(crate) requirement_text: String,
    pub(crate) artifact_text: String,
}

#[derive(Serialize)]
pub(crate) struct ConfidenceResponse {
    pub(crate) confidence: f64,
    pub(crate) rationale: String,
}

// --- governance spec-check (port of src/tracertm/governance.py) ---
#[derive(Deserialize)]
pub(crate) struct GovernanceSpec {
    pub(crate) spec_id: String,
    #[serde(default)]
    pub(crate) acceptance_criteria: Vec<String>,
    #[serde(default)]
    pub(crate) evidence_links: Vec<String>,
    #[serde(default = "default_status")]
    pub(crate) status: String,
}

#[derive(Deserialize)]
pub(crate) struct GovernanceTrace {
    pub(crate) spec_id: String,
    #[allow(dead_code)]
    pub(crate) target_id: String,
    pub(crate) kind: String,
}

#[derive(Deserialize)]
pub(crate) struct SpecCheckRequest {
    #[serde(default)]
    pub(crate) specs: Vec<GovernanceSpec>,
    #[serde(default)]
    pub(crate) traces: Vec<GovernanceTrace>,
}

#[derive(Serialize)]
pub(crate) struct GovernanceViolation {
    pub(crate) spec_id: String,
    pub(crate) code: &'static str,
    pub(crate) message: &'static str,
}

#[derive(Serialize)]
pub(crate) struct GovernanceReport {
    pub(crate) status: &'static str,
    pub(crate) spec_count: usize,
    pub(crate) trace_count: usize,
    pub(crate) violations: Vec<GovernanceViolation>,
}

// --- blast-radius / trace neighbors ---
#[derive(Deserialize)]
pub(crate) struct BlastRadiusRequest {
    #[serde(default)]
    pub(crate) links: Vec<TraceLinkInput>,
    pub(crate) changed_artifact_ids: Vec<String>,
}

#[derive(Serialize)]
pub(crate) struct BlastNodeResponse {
    pub(crate) artifact_id: String,
    pub(crate) distance: u32,
}

#[derive(Serialize)]
pub(crate) struct BlastRadiusResponse {
    pub(crate) seeds: Vec<String>,
    pub(crate) blast_radius: Vec<BlastNodeResponse>,
    pub(crate) total: usize,
}

#[derive(Deserialize)]
pub(crate) struct TraceQueryRequest {
    #[serde(default)]
    pub(crate) links: Vec<TraceLinkInput>,
}

#[derive(Serialize)]
pub(crate) struct TraceNeighborsResponse {
    pub(crate) artifact_id: String,
    pub(crate) direction: &'static str,
    pub(crate) neighbors: Vec<String>,
}

#[derive(Serialize)]
pub(crate) struct PersistedTraceLinkResponse {
    pub(crate) id: String,
    pub(crate) source_id: String,
    pub(crate) target_id: String,
    pub(crate) relationship: String,
    pub(crate) confidence: f64,
    pub(crate) source: String,
    pub(crate) created_at: DateTime<Utc>,
    pub(crate) updated_at: DateTime<Utc>,
    pub(crate) direction: &'static str,
}

#[derive(Serialize)]
pub(crate) struct PersistedTraceLinkListResponse {
    pub(crate) artifact_id: String,
    pub(crate) count: usize,
    pub(crate) items: Vec<PersistedTraceLinkResponse>,
}

/// Maximum number of links expanded into an in-memory coverage matrix.
/// Requests above this bound must use a future paged/export path instead of
/// allowing an unbounded response allocation.
pub(crate) const MAX_COVERAGE_LINKS: usize = 25_000;

pub(crate) fn default_status() -> String {
    "draft".to_string()
}

pub(crate) fn default_stale_after_days() -> u32 {
    90
}

pub(crate) fn default_max_depth() -> u32 {
    10
}

// ---------------------------------------------------------------------------
// Handler functions
// ---------------------------------------------------------------------------

pub(crate) async fn coverage_matrix(
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

pub(crate) async fn impact(Json(request): Json<ImpactRequest>) -> Json<ImpactResponse> {
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

pub(crate) async fn confidence(Json(request): Json<ConfidenceRequest>) -> Json<ConfidenceResponse> {
    let score = crate::graph::jaccard_score(&request.requirement_text, &request.artifact_text);
    Json(ConfidenceResponse {
        confidence: score,
        rationale: "Jaccard token overlap baseline".to_string(),
    })
}

pub(crate) async fn spec_check(Json(req): Json<SpecCheckRequest>) -> Json<GovernanceReport> {
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

pub(crate) fn viol(
    spec_id: &str,
    code: &'static str,
    message: &'static str,
) -> GovernanceViolation {
    GovernanceViolation {
        spec_id: spec_id.to_string(),
        code,
        message,
    }
}

pub(crate) async fn blast_radius(Json(req): Json<BlastRadiusRequest>) -> Json<BlastRadiusResponse> {
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

pub(crate) async fn trace_forward(
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

pub(crate) async fn trace_reverse(
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

pub(crate) async fn list_persisted_trace_links(
    axum::extract::State(state): axum::extract::State<super::super::AppState>,
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

pub(crate) fn persisted_trace_link_response(
    link: crate::store::TraceLink,
    artifact_id: &str,
) -> PersistedTraceLinkResponse {
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
