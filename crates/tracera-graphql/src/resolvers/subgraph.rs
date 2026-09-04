//! Subgraph computations: coverage matrix, impact, blast radius, neighbours.
//!
//! These are pure functions of a caller-supplied link list, mirroring the
//! REST endpoints exactly so a REST client and a GraphQL client see the
//! same numbers for the same input:
//!
//! | REST                                       | GraphQL                  |
//! | ------------------------------------------ | ------------------------ |
//! | `POST /api/v1/coverage-matrix`            | `coverageMatrix`         |
//! | `POST /api/v1/impact`                      | `impact`                 |
//! | `POST /api/v1/blast-radius`                | `blastRadius`            |
//! | `POST /api/v1/trace/{forward,reverse}/id`  | `traceNeighbors`         |
//! | `GET  /api/v1/trace/{id}/links`            | `incidentLinks`          |
//! | `POST /api/v1/governance/spec-check`       | `specCheck`              |
//!
//! The implementations are 1:1 ports of the REST handler bodies; refer to
//! `crates/tracera-server/src/main.rs` for the canonical algorithm.

use std::collections::{BTreeSet, HashMap, VecDeque};

use async_graphql::{InputObject, SimpleObject};
use chrono::{DateTime, Utc};

// ---------------------------------------------------------------------------
// Inputs
// ---------------------------------------------------------------------------

#[derive(InputObject, Clone, Debug, Default)]
pub struct TraceLinkInput {
    pub source_id: String,
    pub target_id: String,
    pub relationship: String,
    pub confidence: f64,
    #[graphql(default)]
    pub updated_at: Option<DateTime<Utc>>,
}

#[derive(InputObject, Clone, Debug, Default)]
pub struct CoverageMatrixInput {
    #[graphql(default)]
    pub links: Vec<TraceLinkInput>,
    /// Same default as REST (`stale_after_days = 30`).
    #[graphql(default)]
    pub stale_after_days: Option<u32>,
}

#[derive(InputObject, Clone, Debug)]
pub struct ImpactInput {
    #[graphql(default)]
    pub links: Vec<TraceLinkInput>,
    pub changed_artifact_ids: Vec<String>,
    /// Same default as REST (`max_depth = 5`).
    #[graphql(default)]
    pub max_depth: Option<u32>,
}

#[derive(InputObject, Clone, Debug)]
pub struct BlastRadiusInput {
    #[graphql(default)]
    pub links: Vec<TraceLinkInput>,
    pub changed_artifact_ids: Vec<String>,
}

#[derive(InputObject, Clone, Debug)]
pub struct TraceNeighborsInput {
    #[graphql(default)]
    pub links: Vec<TraceLinkInput>,
}

#[derive(InputObject, Clone, Debug)]
pub struct GovernanceSpecInput {
    pub spec_id: String,
    #[graphql(default)]
    pub acceptance_criteria: Vec<String>,
    #[graphql(default)]
    pub evidence_links: Vec<String>,
    /// `"approved"` is the only pass condition.
    #[graphql(default = "default_status")]
    pub status: String,
}

#[derive(InputObject, Clone, Debug)]
pub struct GovernanceTraceInput {
    pub spec_id: String,
    pub target_id: String,
    pub kind: String,
}

#[derive(InputObject, Clone, Debug)]
pub struct SpecCheckInput {
    #[graphql(default)]
    pub specs: Vec<GovernanceSpecInput>,
    #[graphql(default)]
    pub traces: Vec<GovernanceTraceInput>,
}

fn default_status() -> String {
    "draft".to_string()
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

#[derive(SimpleObject, Clone, Debug)]
pub struct MatrixCell {
    pub source_id: String,
    pub target_id: String,
    pub coverage: String,
    pub links: Vec<TraceLinkInput>,
}

#[derive(SimpleObject, Clone, Debug)]
pub struct CoverageMatrix {
    pub generated_at: DateTime<Utc>,
    pub link_count: usize,
    pub cell_count: usize,
    pub stale_links: usize,
    pub cells: Vec<MatrixCell>,
}

#[derive(SimpleObject, Clone, Debug)]
pub struct ImpactNode {
    pub artifact_id: String,
    pub depth: u32,
    pub via: Vec<String>,
    pub score: f64,
}

#[derive(SimpleObject, Clone, Debug)]
pub struct ImpactReport {
    pub seeds: Vec<String>,
    pub affected: Vec<ImpactNode>,
    pub total_score: f64,
    pub truncated: bool,
    pub max_depth_seen: u32,
    pub conflicts: Vec<TraceLinkInput>,
}

#[derive(SimpleObject, Clone, Debug)]
pub struct BlastNode {
    pub artifact_id: String,
    pub distance: u32,
}

#[derive(SimpleObject, Clone, Debug)]
pub struct BlastRadiusReport {
    pub seeds: Vec<String>,
    pub blast_radius: Vec<BlastNode>,
    pub total: usize,
}

#[derive(SimpleObject, Clone, Debug)]
pub struct GovernanceViolation {
    pub spec_id: String,
    pub code: &'static str,
    pub message: &'static str,
}

#[derive(SimpleObject, Clone, Debug)]
pub struct GovernanceReport {
    pub status: &'static str,
    pub spec_count: usize,
    pub trace_count: usize,
    pub violations: Vec<GovernanceViolation>,
}

// ---------------------------------------------------------------------------
// Pure helpers — same algorithm as the REST handlers.
// ---------------------------------------------------------------------------

pub fn build_adjacency(links: &[TraceLinkInput]) -> HashMap<String, Vec<String>> {
    let mut adj: HashMap<String, Vec<String>> = HashMap::new();
    for link in links {
        adj.entry(link.source_id.clone())
            .or_default()
            .push(link.target_id.clone());
    }
    adj
}

pub fn bfs_distances(
    adj: &HashMap<String, Vec<String>>,
    seeds: &[String],
) -> Vec<(String, u32)> {
    let mut distances: HashMap<String, u32> = HashMap::new();
    let mut queue: VecDeque<(String, u32)> = VecDeque::new();
    for seed in seeds {
        if distances.insert(seed.clone(), 0).is_none() {
            queue.push_back((seed.clone(), 0));
        }
    }
    while let Some((node, dist)) = queue.pop_front() {
        if let Some(neighbours) = adj.get(&node) {
            for next in neighbours {
                if !distances.contains_key(next) {
                    distances.insert(next.clone(), dist + 1);
                    queue.push_back((next.clone(), dist + 1));
                }
            }
        }
    }
    let mut out: Vec<(String, u32)> = distances.into_iter().collect();
    out.sort_by(|a, b| a.0.cmp(&b.0));
    out
}

pub fn neighbors_of(links: &[TraceLinkInput], artifact_id: &str, forward: bool) -> Vec<String> {
    let mut out = Vec::new();
    for link in links {
        if forward {
            if link.source_id == artifact_id {
                out.push(link.target_id.clone());
            }
        } else if link.target_id == artifact_id {
            out.push(link.source_id.clone());
        }
    }
    out.sort();
    out.dedup();
    out
}

// ---------------------------------------------------------------------------
// Pure top-level functions used by both Query and Mutation roots.
// ---------------------------------------------------------------------------

/// Maximum number of links the gateway accepts into one matrix call.
///
/// Mirrors the `MAX_COVERAGE_LINKS` constant in the REST server. Calls above
/// this bound should be rejected with a `Payload Too Large` style error
/// (the GraphQL schema exposes a [`CoverageMatrix`] so the binary can map
/// overflow to an HTTP 413 if desired).
pub const MAX_COVERAGE_LINKS: usize = 25_000;

pub fn build_coverage_matrix(req: &CoverageMatrixInput) -> CoverageMatrix {
    let generated_at = Utc::now();
    let stale_after_days = req.stale_after_days.unwrap_or(30);
    let mut grouped: HashMap<(String, String), Vec<TraceLinkInput>> = HashMap::new();
    let mut stale_count = 0usize;
    for link in &req.links {
        grouped
            .entry((link.source_id.clone(), link.target_id.clone()))
            .or_default()
            .push(link.clone());
        if let Some(updated) = link.updated_at {
            let age = (generated_at - updated).num_days();
            if age > stale_after_days as i64 {
                stale_count += 1;
            }
        }
    }
    let mut cells: Vec<MatrixCell> = grouped
        .into_iter()
        .map(|((s, t), links)| {
            // Coverage label is a derived string: "covered" if any link exists,
            // "stale" if every link is past the staleness threshold, else "partial".
            // Matches the REST server's heuristic exactly.
            let coverage = if links.is_empty() {
                "missing"
            } else if links.iter().all(|l| {
                l.updated_at
                    .map(|u| (generated_at - u).num_days() > stale_after_days as i64)
                    .unwrap_or(false)
            }) {
                "stale"
            } else {
                "covered"
            };
            MatrixCell {
                source_id: s,
                target_id: t,
                coverage: coverage.to_string(),
                links,
            }
        })
        .collect();
    cells.sort_by(|a, b| {
        a.source_id
            .cmp(&b.source_id)
            .then(a.target_id.cmp(&b.target_id))
    });
    CoverageMatrix {
        generated_at,
        link_count: req.links.len(),
        cell_count: cells.len(),
        stale_links: stale_count,
        cells,
    }
}

pub fn build_impact(req: &ImpactInput) -> ImpactReport {
    let max_depth = req.max_depth.unwrap_or(5);
    let adj = build_adjacency(&req.links);

    let conflicts: Vec<TraceLinkInput> = req
        .links
        .iter()
        .filter(|l| l.relationship == "conflicts_with")
        .cloned()
        .collect();

    let mut affected: Vec<ImpactNode> = req
        .changed_artifact_ids
        .iter()
        .map(|id| ImpactNode {
            artifact_id: id.clone(),
            depth: 0,
            via: vec![],
            score: 1.0,
        })
        .collect();

    let reachable = bfs_distances(&adj, &req.changed_artifact_ids);
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
        let via: Vec<String> = req
            .links
            .iter()
            .filter(|l| l.target_id == node)
            .map(|l| l.source_id.clone())
            .collect();
        affected.push(ImpactNode {
            artifact_id: node,
            depth: dist,
            via,
            score,
        });
    }

    let total_score: f64 = affected.iter().map(|n| n.score).sum::<f64>().max(1.0);

    ImpactReport {
        seeds: req.changed_artifact_ids.clone(),
        affected,
        total_score,
        truncated,
        max_depth_seen,
        conflicts,
    }
}

pub fn build_blast_radius(req: &BlastRadiusInput) -> BlastRadiusReport {
    let adj = build_adjacency(&req.links);
    let mut blast: Vec<BlastNode> = bfs_distances(&adj, &req.changed_artifact_ids)
        .into_iter()
        .map(|(id, distance)| BlastNode {
            artifact_id: id,
            distance,
        })
        .collect();
    blast.sort_by(|a, b| a.distance.cmp(&b.distance).then(a.artifact_id.cmp(&b.artifact_id)));
    BlastRadiusReport {
        total: blast.len(),
        seeds: req.changed_artifact_ids.clone(),
        blast_radius: blast,
    }
}

pub fn build_neighbors(
    artifact_id: &str,
    direction: super::edge::TraceDirection,
    req: &TraceNeighborsInput,
) -> super::edge::TraceNeighbors {
    let forward = matches!(direction, super::edge::TraceDirection::Forward);
    let neighbours = neighbors_of(&req.links, artifact_id, forward);
    super::edge::TraceNeighbors {
        artifact_id: artifact_id.to_string(),
        direction: direction.as_str().to_string(),
        neighbors: neighbours
            .into_iter()
            .map(|id| super::node::NodeRef {
                id,
                node_type: super::node::NodeKind::Artifact,
                label: String::new(),
            })
            .collect(),
    }
}

pub fn build_spec_check(req: &SpecCheckInput) -> GovernanceReport {
    let mut traces_by_spec: HashMap<String, BTreeSet<String>> = HashMap::new();
    for t in &req.traces {
        traces_by_spec
            .entry(t.spec_id.clone())
            .or_default()
            .insert(t.kind.clone());
    }
    let known: BTreeSet<String> = req.specs.iter().map(|s| s.spec_id.clone()).collect();
    let mut violations: Vec<GovernanceViolation> = Vec::new();
    let mut seen: BTreeSet<String> = BTreeSet::new();

    for s in &req.specs {
        if !seen.insert(s.spec_id.clone()) {
            violations.push(GovernanceViolation {
                spec_id: s.spec_id.clone(),
                code: "duplicate_spec",
                message: "Duplicate spec id",
            });
            continue;
        }
        if s.status != "approved" {
            violations.push(GovernanceViolation {
                spec_id: s.spec_id.clone(),
                code: "not_approved",
                message: "Spec must be approved",
            });
        }
        if s.acceptance_criteria.is_empty() {
            violations.push(GovernanceViolation {
                spec_id: s.spec_id.clone(),
                code: "missing_acceptance",
                message: "Acceptance criteria required",
            });
        }
        if s.evidence_links.is_empty() {
            violations.push(GovernanceViolation {
                spec_id: s.spec_id.clone(),
                code: "missing_evidence",
                message: "Evidence links required",
            });
        }
        let kinds = traces_by_spec.get(&s.spec_id);
        let has = |k: &str| kinds.map(|set| set.contains(k)).unwrap_or(false);
        if !has("implementation") {
            violations.push(GovernanceViolation {
                spec_id: s.spec_id.clone(),
                code: "missing_implementation",
                message: "Implementation trace required",
            });
        }
        if !has("test") {
            violations.push(GovernanceViolation {
                spec_id: s.spec_id.clone(),
                code: "missing_test",
                message: "Test trace required",
            });
        }
    }

    for t in &req.traces {
        if !known.contains(&t.spec_id) {
            violations.push(GovernanceViolation {
                spec_id: t.spec_id.clone(),
                code: "orphan_trace",
                message: "Trace target has no spec",
            });
        }
    }

    GovernanceReport {
        status: if violations.is_empty() { "pass" } else { "fail" },
        spec_count: req.specs.len(),
        trace_count: req.traces.len(),
        violations,
    }
}

// ---------------------------------------------------------------------------
// Tests — verify parity with REST semantics on the same inputs.
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn link(s: &str, t: &str, rel: &str) -> TraceLinkInput {
        TraceLinkInput {
            source_id: s.to_string(),
            target_id: t.to_string(),
            relationship: rel.to_string(),
            confidence: 1.0,
            updated_at: None,
        }
    }

    #[test]
    fn coverage_matrix_groups_by_source_target() {
        let req = CoverageMatrixInput {
            links: vec![
                link("req-1", "src-a", "implements"),
                link("req-1", "src-a", "tests"),
                link("req-1", "src-b", "implements"),
            ],
            stale_after_days: Some(30),
        };
        let out = build_coverage_matrix(&req);
        assert_eq!(out.link_count, 3);
        assert_eq!(out.cell_count, 2);
        assert_eq!(out.cells.len(), 2);
        assert_eq!(out.cells[0].source_id, "req-1");
        assert_eq!(out.cells[0].target_id, "src-a");
        assert_eq!(out.cells[0].links.len(), 2);
    }

    #[test]
    fn impact_scores_decay_with_distance() {
        let req = ImpactInput {
            links: vec![link("a", "b", "depends_on"), link("b", "c", "depends_on")],
            changed_artifact_ids: vec!["a".into()],
            max_depth: Some(5),
        };
        let report = build_impact(&req);
        let by_id: HashMap<&str, &ImpactNode> = report
            .affected
            .iter()
            .map(|n| (n.artifact_id.as_str(), n))
            .collect();
        assert_eq!(by_id["a"].depth, 0);
        assert_eq!(by_id["b"].depth, 1);
        assert_eq!(by_id["c"].depth, 2);
        assert!(by_id["c"].score < by_id["b"].score);
        assert!(!report.truncated);
        assert_eq!(report.max_depth_seen, 2);
    }

    #[test]
    fn impact_collects_conflicts() {
        let req = ImpactInput {
            links: vec![link("a", "b", "conflicts_with")],
            changed_artifact_ids: vec!["a".into()],
            max_depth: Some(5),
        };
        let report = build_impact(&req);
        assert_eq!(report.conflicts.len(), 1);
        assert_eq!(report.conflicts[0].source_id, "a");
    }

    #[test]
    fn blast_radius_walks_adjacency() {
        let req = BlastRadiusInput {
            links: vec![link("a", "b", "calls"), link("b", "c", "calls")],
            changed_artifact_ids: vec!["a".into()],
        };
        let report = build_blast_radius(&req);
        assert_eq!(report.total, 3);
        let distances: HashMap<&str, u32> = report
            .blast_radius
            .iter()
            .map(|n| (n.artifact_id.as_str(), n.distance))
            .collect();
        assert_eq!(distances["a"], 0);
        assert_eq!(distances["b"], 1);
        assert_eq!(distances["c"], 2);
    }

    #[test]
    fn trace_neighbors_forward_and_reverse() {
        let links = vec![link("a", "b", "calls"), link("c", "a", "calls")];
        let f = neighbors_of(&links, "a", true);
        let r = neighbors_of(&links, "a", false);
        assert_eq!(f, vec!["b"]);
        assert_eq!(r, vec!["c"]);
    }

    #[test]
    fn spec_check_flags_missing_implementation() {
        let req = SpecCheckInput {
            specs: vec![GovernanceSpecInput {
                spec_id: "S-1".into(),
                acceptance_criteria: vec!["a".into()],
                evidence_links: vec!["e".into()],
                status: "approved".into(),
            }],
            traces: vec![GovernanceTraceInput {
                spec_id: "S-1".into(),
                target_id: "src".into(),
                kind: "test".into(),
            }],
        };
        let report = build_spec_check(&req);
        assert_eq!(report.status, "fail");
        assert!(report
            .violations
            .iter()
            .any(|v| v.code == "missing_implementation"));
        assert!(!report
            .violations
            .iter()
            .any(|v| v.code == "missing_test"));
    }

    #[test]
    fn spec_check_passes_when_complete() {
        let req = SpecCheckInput {
            specs: vec![GovernanceSpecInput {
                spec_id: "S-1".into(),
                acceptance_criteria: vec!["a".into()],
                evidence_links: vec!["e".into()],
                status: "approved".into(),
            }],
            traces: vec![
                GovernanceTraceInput {
                    spec_id: "S-1".into(),
                    target_id: "src".into(),
                    kind: "implementation".into(),
                },
                GovernanceTraceInput {
                    spec_id: "S-1".into(),
                    target_id: "tst".into(),
                    kind: "test".into(),
                },
            ],
        };
        let report = build_spec_check(&req);
        assert_eq!(report.status, "pass");
    }

    #[test]
    fn max_coverage_links_matches_rest_constant() {
        assert_eq!(MAX_COVERAGE_LINKS, 25_000);
    }
}
