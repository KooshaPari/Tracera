//! Pattern fingerprinting, counting, and batch distillation.

use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};

use super::config::DistillationConfig;
use super::graph_input::GraphSnapshot;
use super::memory::{now_epoch, MemoryEntry};

/// Compute a deterministic fingerprint string for a short path through the
/// graph so that identical structural motifs map to the same pattern key.
pub fn fingerprint_path(node_types: &[String], edge_types: &[String]) -> String {
    let mut parts = Vec::with_capacity(node_types.len() + edge_types.len());
    for (i, nt) in node_types.iter().enumerate() {
        parts.push(nt.clone());
        if let Some(et) = edge_types.get(i) {
            parts.push(et.clone());
        }
    }
    if let Some(last) = node_types.last() {
        if parts.last().map_or(true, |p| p != last) {
            parts.push(last.clone());
        }
    }
    parts.join("->")
}

/// Extract all simple paths of a given length (in edges) starting from a
/// node, returning the type-sequence fingerprint for each.
pub fn extract_paths(snapshot: &GraphSnapshot, start_id: u64, depth: usize) -> Vec<String> {
    let mut results = Vec::new();
    let mut stack: Vec<(u64, Vec<String>, Vec<String>, Vec<u64>)> = Vec::new();

    if let Some(start_node) = snapshot.nodes.iter().find(|n| n.id == start_id) {
        stack.push((
            start_id,
            vec![start_node.node_type.clone()],
            vec![],
            vec![start_id],
        ));
    }

    while let Some((current, node_types, edge_types, visited)) = stack.pop() {
        if edge_types.len() >= depth {
            results.push(fingerprint_path(&node_types, &edge_types));
            continue;
        }
        if let Some(neighbors) = snapshot.adjacency.get(&current) {
            for &neighbor in neighbors {
                if visited.contains(&neighbor) {
                    continue;
                }
                let neighbor_node = snapshot.nodes.iter().find(|n| n.id == neighbor);
                let edge = snapshot
                    .edges
                    .iter()
                    .find(|e| e.source_id == current && e.target_id == neighbor);
                if let (Some(nn), Some(e)) = (neighbor_node, edge) {
                    let mut nt = node_types.clone();
                    let mut et = edge_types.clone();
                    let mut v = visited.clone();
                    nt.push(nn.node_type.clone());
                    et.push(e.edge_type.clone());
                    v.push(neighbor);
                    stack.push((nn.id, nt, et, v));
                }
            }
        }
    }
    results
}

/// Count occurrences of each unique pattern fingerprint in the provided
/// list of fingerprints.
pub fn count_patterns(fingerprints: &[String]) -> HashMap<String, usize> {
    let mut counts: HashMap<String, usize> = HashMap::new();
    for fp in fingerprints {
        *counts.entry(fp.clone()).or_insert(0) += 1;
    }
    counts
}

/// Compute a confidence score for a pattern based on its occurrence count
/// relative to the total number of paths extracted.
pub fn pattern_confidence(occurrence: usize, total_paths: usize) -> f64 {
    if total_paths == 0 {
        return 0.0;
    }
    (occurrence as f64 / total_paths as f64).min(1.0)
}

/// Main distillation function. Given a graph snapshot and configuration,
/// extracts patterns from every reachable node and returns the qualifying
/// memory entries.
pub fn distill_patterns(snapshot: &GraphSnapshot, config: &DistillationConfig) -> Vec<MemoryEntry> {
    let mut pattern_counts: HashMap<String, (usize, Vec<u64>, Vec<String>)> = HashMap::new();
    let mut total_paths: usize = 0;

    for node in &snapshot.nodes {
        let paths = extract_paths(snapshot, node.id, 3);
        total_paths += paths.len();
        for fp in &paths {
            let entry = pattern_counts
                .entry(fp.clone())
                .or_insert_with(|| (0, Vec::new(), Vec::new()));
            entry.0 += 1;
            if !entry.1.contains(&node.id) {
                entry.1.push(node.id);
            }
        }
    }

    let id_counter = AtomicU64::new(1);
    let mut entries: Vec<MemoryEntry> = Vec::new();

    for (fp, (count, source_nodes, _)) in &pattern_counts {
        if *count < config.min_pattern_occurrences {
            continue;
        }
        let conf = pattern_confidence(*count, total_paths);
        if conf < config.confidence_threshold {
            continue;
        }
        let id = id_counter.fetch_add(1, Ordering::Relaxed);
        let edge_types: Vec<String> = fp
            .split("->")
            .filter(|s| !s.is_empty())
            .map(|s| s.to_string())
            .collect();
        let entry = MemoryEntry {
            id,
            pattern: fp.clone(),
            confidence: conf,
            last_seen: now_epoch(),
            source_nodes: source_nodes.clone(),
            occurrence_count: *count,
            edge_types,
        };
        entries.push(entry);
    }

    entries.sort_by(|a, b| {
        b.confidence
            .partial_cmp(&a.confidence)
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    entries.truncate(config.max_memory_size);
    entries
}
