#![allow(dead_code)]
#![allow(clippy::type_complexity)]
#![allow(clippy::unnecessary_map_or)]
//! Memory distillation from SWEE graph patterns.
//!
//! This module provides mechanisms for distilling recurring graph patterns
//! into reusable memory entries that capture learned behavior, common
//! traversal motifs, and semantic relationships discovered during
//! graph analysis.

mod config;
mod distiller;
mod graph_input;
mod memory;
mod pattern;

#[allow(unused_imports)]
pub use config::DistillationConfig;
#[allow(unused_imports)]
pub use distiller::MemoryDistiller;
#[allow(unused_imports)]
pub use graph_input::{GraphEdge, GraphNode, GraphSnapshot};
#[allow(unused_imports)]
pub use memory::MemoryEntry;
#[allow(unused_imports)]
pub use pattern::{
    count_patterns, distill_patterns, extract_paths, fingerprint_path, pattern_confidence,
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;
    use std::time::Duration;

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

        let added2 = distiller.distill(&snap);
        assert_eq!(added2, 0);

        let _pruned = distiller.prune();

        let hc = distiller.high_confidence(0.9);
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
