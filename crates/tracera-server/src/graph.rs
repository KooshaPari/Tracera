use chrono::Utc;

use crate::handlers::governance::{
    CoverageMatrixRequest, CoverageMatrixResponse, MatrixCellResponse, TraceLinkInput,
};

/// Find neighbors of a given artifact ID in the trace link graph.
pub(crate) fn neighbors_of(links: &[TraceLinkInput], id: &str, forward: bool) -> Vec<String> {
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

/// Build an adjacency list from trace links.
pub(crate) fn build_adjacency(
    links: &[TraceLinkInput],
) -> std::collections::HashMap<String, Vec<String>> {
    let mut adj: std::collections::HashMap<String, Vec<String>> = std::collections::HashMap::new();
    for l in links {
        adj.entry(l.source_id.clone())
            .or_default()
            .push(l.target_id.clone());
    }
    adj
}

/// BFS from seed nodes, returning (node, distance) pairs.
pub(crate) fn bfs_distances(
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

/// Build a full coverage matrix from a request.
pub(crate) fn build_coverage_matrix(request: CoverageMatrixRequest) -> CoverageMatrixResponse {
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

/// Classify the coverage level of a single trace link.
pub(crate) fn classify_coverage(link: &TraceLinkInput) -> String {
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

/// Compute Jaccard similarity between two whitespace-tokenized strings.
pub(crate) fn jaccard_score(a: &str, b: &str) -> f64 {
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
