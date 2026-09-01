#![allow(dead_code)]
#![allow(clippy::type_complexity)]
#![allow(clippy::unnecessary_map_or)]
//! Memory distillation from SWEE graph patterns.
//!
//! This module provides mechanisms for distilling recurring graph patterns
//! into reusable memory entries that capture learned behavior, common
//! traversal motifs, and semantic relationships discovered during
//! graph analysis.

use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/// Controls how the distiller selects and retains patterns.
#[derive(Debug, Clone)]
pub struct DistillationConfig {
    /// Minimum elapsed time between distillation passes.
    pub interval: Duration,
    /// A pattern must appear at least this many times before it qualifies.
    pub min_pattern_occurrences: usize,
    /// Maximum number of memory entries the distiller will retain.
    pub max_memory_size: usize,
    /// Confidence threshold below which entries are pruned (0.0 – 1.0).
    pub confidence_threshold: f64,
    /// Decay factor applied to confidence on each prune cycle.
    pub decay_factor: f64,
}

impl Default for DistillationConfig {
    fn default() -> Self {
        Self {
            interval: Duration::from_secs(300),
            min_pattern_occurrences: 3,
            max_memory_size: 10_000,
            confidence_threshold: 0.3,
            decay_factor: 0.9,
        }
    }
}

// ---------------------------------------------------------------------------
// Graph inputs
// ---------------------------------------------------------------------------

/// A lightweight representation of a node in the SWEE graph used as input
/// to the distillation pipeline.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct GraphNode {
    pub id: u64,
    pub node_type: String,
    pub label: String,
}

/// An edge connecting two nodes.
#[derive(Debug, Clone)]
pub struct GraphEdge {
    pub source_id: u64,
    pub target_id: u64,
    pub edge_type: String,
    pub weight: f64,
}

/// Snapshot of graph data supplied to the distiller.
#[derive(Debug, Clone, Default)]
pub struct GraphSnapshot {
    pub nodes: Vec<GraphNode>,
    pub edges: Vec<GraphEdge>,
    /// Pre-computed adjacency list for fast traversal.
    pub adjacency: HashMap<u64, Vec<u64>>,
}

impl GraphSnapshot {
    /// Build the adjacency list from the raw edge list.
    pub fn build_adjacency(&mut self) {
        let mut adj: HashMap<u64, Vec<u64>> = HashMap::new();
        for edge in &self.edges {
            adj.entry(edge.source_id).or_default().push(edge.target_id);
        }
        self.adjacency = adj;
    }
}

// ---------------------------------------------------------------------------
// Memory entry
// ---------------------------------------------------------------------------

/// A distilled memory capturing a recurring graph pattern.
#[derive(Debug, Clone)]
pub struct MemoryEntry {
    /// Unique identifier for this entry.
    pub id: u64,
    /// Human-readable description of the pattern.
    pub pattern: String,
    /// Normalised confidence score (0.0 – 1.0).
    pub confidence: f64,
    /// Timestamp (seconds since UNIX epoch) when this pattern was last seen.
    pub last_seen: u64,
    /// IDs of source nodes that contributed to this pattern.
    pub source_nodes: Vec<u64>,
    /// Number of times the pattern has been observed.
    pub occurrence_count: usize,
    /// Edge types involved in the pattern.
    pub edge_types: Vec<String>,
}

impl MemoryEntry {
    /// Create a new entry with an initial confidence of 1.0.
    pub fn new(id: u64, pattern: String, source_nodes: Vec<u64>, edge_types: Vec<String>) -> Self {
        Self {
            id,
            pattern,
            confidence: 1.0,
            last_seen: now_epoch(),
            source_nodes,
            occurrence_count: 1,
            edge_types,
        }
    }

    /// Bump the occurrence count and refresh the last-seen timestamp.
    pub fn touch(&mut self) {
        self.occurrence_count += 1;
        self.last_seen = now_epoch();
        self.confidence = (self.confidence + 1.0).min(1.0);
    }

    /// Apply a decay factor to confidence.
    pub fn decay(&mut self, factor: f64) {
        self.confidence *= factor;
    }
}

// ---------------------------------------------------------------------------
// Pattern fingerprinting
// ---------------------------------------------------------------------------

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

    // Seed the stack with the starting node's type.
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
                    continue; // avoid cycles
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

// ---------------------------------------------------------------------------
// Distillation core
// ---------------------------------------------------------------------------

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

    // Sort by confidence descending, then truncate to max size.
    entries.sort_by(|a, b| {
        b.confidence
            .partial_cmp(&a.confidence)
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    entries.truncate(config.max_memory_size);
    entries
}

// ---------------------------------------------------------------------------
// MemoryDistiller – high-level API
// ---------------------------------------------------------------------------

/// High-level distiller that maintains internal state and exposes
/// incremental distillation, query, and pruning operations.
pub struct MemoryDistiller {
    config: DistillationConfig,
    memories: Vec<MemoryEntry>,
    last_distill: Option<Instant>,
    next_id: u64,
}

impl MemoryDistiller {
    /// Create a new distiller with the given configuration.
    pub fn new(config: DistillationConfig) -> Self {
        Self {
            config,
            memories: Vec::new(),
            last_distill: None,
            next_id: 1,
        }
    }

    /// Run a distillation pass on the provided snapshot, merging new
    /// patterns into the existing memory store.
    pub fn distill(&mut self, snapshot: &GraphSnapshot) -> usize {
        // Rate-limit distillation.
        if let Some(prev) = self.last_distill {
            if prev.elapsed() < self.config.interval {
                return 0;
            }
        }

        let new_entries = distill_patterns(snapshot, &self.config);
        let mut added = 0;

        for entry in new_entries {
            // Check if a pattern already exists; if so, merge.
            if let Some(existing) = self
                .memories
                .iter_mut()
                .find(|m| m.pattern == entry.pattern)
            {
                existing.touch();
                // Merge source nodes.
                for &src in &entry.source_nodes {
                    if !existing.source_nodes.contains(&src) {
                        existing.source_nodes.push(src);
                    }
                }
            } else if self.memories.len() < self.config.max_memory_size {
                let mut entry = entry;
                entry.id = self.next_id;
                self.next_id += 1;
                self.memories.push(entry);
                added += 1;
            }
        }

        self.last_distill = Some(Instant::now());
        added
    }

    /// Return a reference to all current memory entries.
    pub fn get_memories(&self) -> &[MemoryEntry] {
        &self.memories
    }

    /// Find a memory entry by its pattern fingerprint.
    pub fn find_memory(&self, pattern: &str) -> Option<&MemoryEntry> {
        self.memories.iter().find(|m| m.pattern == pattern)
    }

    /// Prune low-confidence entries and apply decay.
    pub fn prune(&mut self) -> usize {
        let before = self.memories.len();

        for mem in &mut self.memories {
            mem.decay(self.config.decay_factor);
        }

        self.memories
            .retain(|m| m.confidence >= self.config.confidence_threshold);
        before - self.memories.len()
    }

    /// Return the total number of stored memories.
    pub fn memory_count(&self) -> usize {
        self.memories.len()
    }

    /// Clear all memories.
    pub fn clear(&mut self) {
        self.memories.clear();
        self.next_id = 1;
    }

    /// Return memories whose confidence exceeds the given threshold.
    pub fn high_confidence(&self, threshold: f64) -> Vec<&MemoryEntry> {
        self.memories
            .iter()
            .filter(|m| m.confidence >= threshold)
            .collect()
    }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Current time as seconds since the UNIX epoch.
fn now_epoch() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn make_snapshot() -> GraphSnapshot {
        let nodes = vec![
            GraphNode {
                id: 1,
                node_type: "Query".into(),
                label: "select".into(),
            },
            GraphNode {
                id: 2,
                node_type: "Filter".into(),
                label: "where".into(),
            },
            GraphNode {
                id: 3,
                node_type: "Join".into(),
                label: "inner".into(),
            },
            GraphNode {
                id: 4,
                node_type: "Aggregate".into(),
                label: "group_by".into(),
            },
            GraphNode {
                id: 5,
                node_type: "Sort".into(),
                label: "order".into(),
            },
        ];
        let edges = vec![
            GraphEdge {
                source_id: 1,
                target_id: 2,
                edge_type: "flow".into(),
                weight: 1.0,
            },
            GraphEdge {
                source_id: 2,
                target_id: 3,
                edge_type: "flow".into(),
                weight: 1.0,
            },
            GraphEdge {
                source_id: 3,
                target_id: 4,
                edge_type: "flow".into(),
                weight: 1.0,
            },
            GraphEdge {
                source_id: 4,
                target_id: 5,
                edge_type: "flow".into(),
                weight: 1.0,
            },
            GraphEdge {
                source_id: 1,
                target_id: 3,
                edge_type: "skip".into(),
                weight: 0.5,
            },
        ];
        let mut snap = GraphSnapshot {
            nodes,
            edges,
            adjacency: HashMap::new(),
        };
        snap.build_adjacency();
        snap
    }

    #[test]
    fn test_fingerprint_path_basic() {
        let node_types = vec!["A".into(), "B".into(), "C".into()];
        let edge_types = vec!["e1".into(), "e2".into()];
        let fp = fingerprint_path(&node_types, &edge_types);
        assert_eq!(fp, "A->e1->B->e2->C");
    }

    #[test]
    fn test_count_patterns() {
        let fps = vec!["A->e1->B".into(), "A->e1->B".into(), "B->e2->C".into()];
        let counts = count_patterns(&fps);
        assert_eq!(counts.get("A->e1->B"), Some(&2));
        assert_eq!(counts.get("B->e2->C"), Some(&1));
    }

    #[test]
    fn test_pattern_confidence_zero_total() {
        assert_eq!(pattern_confidence(5, 0), 0.0);
    }

    #[test]
    fn test_pattern_confidence_normal() {
        let conf = pattern_confidence(3, 10);
        assert!((conf - 0.3).abs() < f64::EPSILON);
    }

    #[test]
    fn test_pattern_confidence_capped() {
        let conf = pattern_confidence(20, 10);
        assert!((conf - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_extract_paths_from_snapshot() {
        let snap = make_snapshot();
        let paths = extract_paths(&snap, 1, 2);
        assert!(!paths.is_empty());
        // All paths should start with "Query"
        for p in &paths {
            assert!(p.starts_with("Query"), "expected Query prefix, got: {p}");
        }
    }

    #[test]
    fn test_distill_patterns_qualifying() {
        let snap = make_snapshot();
        let config = DistillationConfig {
            min_pattern_occurrences: 1,
            confidence_threshold: 0.01,
            ..Default::default()
        };
        let entries = distill_patterns(&snap, &config);
        assert!(
            !entries.is_empty(),
            "should produce at least one memory entry"
        );
        for e in &entries {
            assert!(e.confidence >= 0.0 && e.confidence <= 1.0);
        }
    }

    #[test]
    fn test_distill_patterns_filters_low_occurrence() {
        let snap = make_snapshot();
        let config = DistillationConfig {
            min_pattern_occurrences: 100,
            confidence_threshold: 0.0,
            ..Default::default()
        };
        let entries = distill_patterns(&snap, &config);
        assert!(entries.is_empty(), "no pattern appears 100 times");
    }

    #[test]
    fn test_memory_entry_touch_increments() {
        let mut entry = MemoryEntry::new(1, "test".into(), vec![], vec![]);
        assert_eq!(entry.occurrence_count, 1);
        entry.touch();
        assert_eq!(entry.occurrence_count, 2);
    }

    #[test]
    fn test_memory_entry_decay() {
        let mut entry = MemoryEntry::new(1, "test".into(), vec![], vec![]);
        entry.decay(0.5);
        assert!((entry.confidence - 0.5).abs() < f64::EPSILON);
    }

    #[test]
    fn test_distiller_lifecycle() {
        let config = DistillationConfig {
            min_pattern_occurrences: 1,
            confidence_threshold: 0.01,
            interval: Duration::from_millis(0),
            ..Default::default()
        };
        let mut distiller = MemoryDistiller::new(config);
        let snap = make_snapshot();

        let added = distiller.distill(&snap);
        assert!(added > 0, "first distillation should add memories");
        assert_eq!(distiller.memory_count(), added);

        // Second immediate distillation should be rate-limited.
        let added2 = distiller.distill(&snap);
        assert_eq!(added2, 0);

        // Prune should not crash.
        let _pruned = distiller.prune();

        // High confidence query.
        let hc = distiller.high_confidence(0.9);
        // Might or might not find any; just verify it doesn't panic.
        let _ = hc;
    }

    #[test]
    fn test_distiller_find_memory() {
        let config = DistillationConfig {
            min_pattern_occurrences: 1,
            confidence_threshold: 0.01,
            interval: Duration::from_millis(0),
            ..Default::default()
        };
        let mut distiller = MemoryDistiller::new(config);
        let snap = make_snapshot();
        distiller.distill(&snap);

        if let Some(first) = distiller.get_memories().first() {
            let pattern = first.pattern.clone();
            assert!(distiller.find_memory(&pattern).is_some());
        }
        assert!(distiller.find_memory("nonexistent_pattern_xyz").is_none());
    }

    #[test]
    fn test_distiller_clear() {
        let config = DistillationConfig {
            min_pattern_occurrences: 1,
            confidence_threshold: 0.01,
            interval: Duration::from_millis(0),
            ..Default::default()
        };
        let mut distiller = MemoryDistiller::new(config);
        let snap = make_snapshot();
        distiller.distill(&snap);
        assert!(distiller.memory_count() > 0);
        distiller.clear();
        assert_eq!(distiller.memory_count(), 0);
    }
}
