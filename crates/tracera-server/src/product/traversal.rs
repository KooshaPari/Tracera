//! Bounded graph traversal over the product graph (WP-07, §6).
//!
//! This module provides a budget-limited depth-first traversal that is safe
//! against cycles, responsive on large graphs, and always reports when
//! truncation occurred.
//!
//! # Design
//!
//! The product graph lives in the `product_nodes` / `product_edges` tables.
//! An in-memory adjacency map is constructed from those rows, then fed into
//! [`GraphTraversal`] which performs DFS with three safety rails:
//!
//! 1. **Cycle detection** — a `visited` set prevents revisiting any node.
//! 2. **Node budget** — traversal stops after `max_nodes` nodes have been
//!    visited (prevents runaway on dense graphs).
//! 3. **Depth limit** — edges deeper than `max_depth` are not followed.
//!
//! Every traversal returns a [`TraversalResult`] that includes truncation
//! status, the set of cycles detected (as node-id back-edges), and the
//! full traversal path.

use std::collections::{HashMap, HashSet, VecDeque};

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/// Budget constraints for a single graph traversal.
///
/// Sensible defaults are provided by [`TraversalBudget::default`].
#[derive(Debug, Clone)]
pub struct TraversalBudget {
    /// Maximum number of nodes to visit before truncating (default: 1000).
    pub max_nodes: usize,
    /// Maximum depth from the start node (default: 50).
    pub max_depth: usize,
    /// If non-empty, only follow edges whose type is in this list.
    /// An empty list means "follow all edges".
    pub include_edges: Vec<String>,
}

impl Default for TraversalBudget {
    fn default() -> Self {
        Self {
            max_nodes: 1000,
            max_depth: 50,
            include_edges: Vec::new(),
        }
    }
}

// ---------------------------------------------------------------------------
// Results
// ---------------------------------------------------------------------------

/// A single node encountered during traversal.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize)]
pub struct TraversalNode {
    /// The node's unique identifier.
    pub id: String,
    /// The node kind: "product", "capability", "obligation", or "target".
    pub kind: String,
    /// The depth at which this node was first visited.
    pub depth: usize,
    /// Human-readable label / title.
    pub label: String,
}

/// The complete result of a bounded graph traversal.
#[derive(Debug, Clone, serde::Serialize)]
pub struct TraversalResult {
    /// Total number of distinct nodes visited.
    pub nodes_visited: usize,
    /// Total number of edges followed (including those to already-visited
    /// nodes that were skipped).
    pub edges_followed: usize,
    /// Whether the traversal was truncated before exhausting the graph.
    pub truncated: bool,
    /// Human-readable reason for truncation, if any.
    /// Values: `"max_nodes"`, `"max_depth"`, or `None`.
    pub truncation_reason: Option<String>,
    /// Node ids that were part of a detected cycle (back-edges).
    pub cycles_detected: Vec<String>,
    /// Ordered list of nodes as they were first visited.
    pub path: Vec<TraversalNode>,
}

// ---------------------------------------------------------------------------
// GraphTraversal
// ---------------------------------------------------------------------------

/// Bounded depth-first traverser over an in-memory product graph.
///
/// Build the adjacency map from `product_edges` rows, then call
/// [`GraphTraversal::traverse`].
///
/// # Example
///
/// ```ignore
/// let mut adj: HashMap<String, Vec<(String, String)>> = HashMap::new();
/// adj.insert("A".into(), vec![("B".into(), "product_has_capability".into())]);
/// adj.insert("B".into(), vec![("C".into(), "capability_satisfies_obligation".into())]);
///
/// let budget = TraversalBudget { max_depth: 10, max_nodes: 100, ..Default::default() };
/// let mut gt = GraphTraversal::new(adj, budget);
/// let result = gt.traverse("A");
/// assert_eq!(result.nodes_visited, 3);
/// assert!(!result.truncated);
/// ```
pub struct GraphTraversal {
    adjacency: HashMap<String, Vec<(String, String)>>,
    budget: TraversalBudget,
    /// Maps node id -> (kind, label) for producing [`TraversalNode`]s.
    node_info: HashMap<String, (String, String)>,
}

impl GraphTraversal {
    /// Create a new traverser.
    ///
    /// * `adjacency` — maps `source_id` → list of `(target_id, edge_type)`.
    /// * `budget`    — traversal constraints.
    pub fn new(
        adjacency: HashMap<String, Vec<(String, String)>>,
        budget: TraversalBudget,
    ) -> Self {
        Self {
            adjacency,
            budget,
            node_info: HashMap::new(),
        }
    }

    /// Create a new traverser with node metadata (kind + label).
    ///
    /// This overload allows the traversal to populate [`TraversalNode`]
    /// entries with human-readable kind and label information.
    pub fn with_node_info(
        adjacency: HashMap<String, Vec<(String, String)>>,
        budget: TraversalBudget,
        node_info: HashMap<String, (String, String)>,
    ) -> Self {
        Self {
            adjacency,
            budget,
            node_info,
        }
    }

    /// Perform a bounded depth-first traversal starting at `start_id`.
    ///
    /// Returns a [`TraversalResult`] describing what was visited, whether
    /// the traversal was truncated, and any cycles detected.
    ///
    /// Uses iterative DFS with a two-phase stack entry (`Visit` / `Finish`)
    /// to correctly detect back-edges (cycles) even without recursion.
    pub fn traverse(&mut self, start_id: &str) -> TraversalResult {
        let mut visited: HashSet<String> = HashSet::new();
        let mut on_stack: HashSet<String> = HashSet::new();
        let mut cycles_detected: Vec<String> = Vec::new();
        let mut path: Vec<TraversalNode> = Vec::new();
        let mut edges_followed: usize = 0;
        let mut truncated = false;
        let mut truncation_reason: Option<String> = None;

        /// Stack entry for two-phase iterative DFS.
        enum Entry {
            /// First encounter: visit the node and push children.
            Visit(String, usize),
            /// All children processed: remove from on_stack.
            Finish(String),
        }

        let mut stack: VecDeque<Entry> = VecDeque::new();
        stack.push_back(Entry::Visit(start_id.to_string(), 0));

        while let Some(entry) = stack.pop_back() {
            match entry {
                Entry::Finish(node_id) => {
                    on_stack.remove(&node_id);
                }
                Entry::Visit(node_id, depth) => {
                    // --- Budget: node count ---
                    if visited.len() >= self.budget.max_nodes {
                        truncated = true;
                        truncation_reason = Some("max_nodes".to_string());
                        break;
                    }

                    // --- Budget: depth ---
                    if depth > self.budget.max_depth {
                        truncated = true;
                        truncation_reason = Some("max_depth".to_string());
                        continue;
                    }

                    // --- Cycle detection ---
                    if visited.contains(&node_id) {
                        if on_stack.contains(&node_id) {
                            cycles_detected.push(node_id.clone());
                        }
                        continue;
                    }

                    // --- Visit the node ---
                    visited.insert(node_id.clone());
                    on_stack.insert(node_id.clone());

                    let (kind, label) = self
                        .node_info
                        .get(&node_id)
                        .cloned()
                        .unwrap_or_else(|| ("unknown".to_string(), node_id.clone()));

                    path.push(TraversalNode {
                        id: node_id.clone(),
                        kind,
                        depth,
                        label,
                    });

                    // Push finish marker so we clean up on_stack later
                    stack.push_back(Entry::Finish(node_id.clone()));

                    // --- Follow outgoing edges ---
                    if let Some(edges) = self.adjacency.get(&node_id) {
                        // Push in reverse order so the first edge is processed first
                        // (stack is LIFO).
                        for (target_id, edge_type) in edges.iter().rev() {
                            edges_followed += 1;

                            // Edge-type filter
                            if !self.budget.include_edges.is_empty()
                                && !self.budget.include_edges.contains(edge_type)
                            {
                                continue;
                            }

                            stack
                                .push_back(Entry::Visit(target_id.clone(), depth + 1));
                        }
                    }
                }
            }
        }

        TraversalResult {
            nodes_visited: visited.len(),
            edges_followed,
            truncated,
            truncation_reason,
            cycles_detected,
            path,
        }
    }
}

// ---------------------------------------------------------------------------
// Helper: build adjacency from edge list
// ---------------------------------------------------------------------------

/// Build an adjacency map from a list of `(source_id, target_id, edge_type)`.
pub fn build_adjacency(edges: &[(String, String, String)]) -> HashMap<String, Vec<(String, String)>> {
    let mut adj: HashMap<String, Vec<(String, String)>> = HashMap::new();
    for (source, target, edge_type) in edges {
        adj.entry(source.clone())
            .or_default()
            .push((target.clone(), edge_type.clone()));
    }
    adj
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    // Helper: build a simple adjacency map from edges
    fn adj(edges: &[(&str, &str, &str)]) -> HashMap<String, Vec<(String, String)>> {
        edges
            .iter()
            .map(|(s, t, e)| (s.to_string(), (t.to_string(), e.to_string())))
            .fold(HashMap::new(), |mut m, (s, te)| {
                m.entry(s).or_default().push(te);
                m
            })
    }

    fn node_info(entries: &[(&str, &str, &str)]) -> HashMap<String, (String, String)> {
        entries
            .iter()
            .map(|(id, kind, label)| (id.to_string(), (kind.to_string(), label.to_string())))
            .collect()
    }

    #[test]
    fn test_basic_tree_traversal() {
        // A -> B, A -> C, B -> D, B -> E
        let adjacency = adj(&[
            ("A", "B", "has"),
            ("A", "C", "has"),
            ("B", "D", "has"),
            ("B", "E", "has"),
        ]);
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 10,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        assert_eq!(result.nodes_visited, 5);
        assert!(!result.truncated);
        assert!(result.truncation_reason.is_none());
        assert!(result.cycles_detected.is_empty());
        assert_eq!(result.path.len(), 5);

        // First node should be A at depth 0
        assert_eq!(result.path[0].id, "A");
        assert_eq!(result.path[0].depth, 0);
    }

    #[test]
    fn test_cycle_detection_simple() {
        // A -> B -> C -> A  (cycle)
        let adjacency = adj(&[
            ("A", "B", "next"),
            ("B", "C", "next"),
            ("C", "A", "next"),
        ]);
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 100,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        // Should visit all 3 nodes before detecting the back-edge to A
        assert_eq!(result.nodes_visited, 3);
        assert!(!result.truncated);
        // The back-edge to A should be detected as a cycle
        assert!(
            result.cycles_detected.contains(&"A".to_string()),
            "Expected cycle on A, got: {:?}",
            result.cycles_detected
        );
    }

    #[test]
    fn test_cycle_detection_diamond() {
        // A -> B -> D, A -> C -> D, D -> B  (cycle back to B)
        let adjacency = adj(&[
            ("A", "B", "has"),
            ("A", "C", "has"),
            ("B", "D", "has"),
            ("C", "D", "has"),
            ("D", "B", "back"),
        ]);
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 100,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        // Should visit A, B, D (then D->B is a back-edge), then C
        // Note: D->C won't happen because C was pushed before D->B but D
        // was visited first from B. Let's just check core properties.
        assert!(result.nodes_visited >= 3);
        // B should appear as a cycle (D->B back-edge)
        assert!(
            result.cycles_detected.contains(&"B".to_string()),
            "Expected cycle on B, got: {:?}",
            result.cycles_detected
        );
    }

    #[test]
    fn test_budget_exhaustion_max_nodes() {
        // Chain of 10 nodes: 0->1->2->...->9
        let strings: Vec<(String, String, String)> = (0..9u32)
            .map(|i| (i.to_string(), (i + 1).to_string(), "chain".to_string()))
            .collect();
        let edges: Vec<(&str, &str, &str)> = strings
            .iter()
            .map(|(s, t, e)| (s.as_str(), t.as_str(), e.as_str()))
            .collect();

        let adjacency = adj(&edges);
        let budget = TraversalBudget {
            max_nodes: 5,
            max_depth: 100,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("0");

        assert_eq!(result.nodes_visited, 5);
        assert!(result.truncated);
        assert_eq!(result.truncation_reason.as_deref(), Some("max_nodes"));
    }

    #[test]
    fn test_depth_limit() {
        // Linear chain: A -> B -> C -> D -> E
        let adjacency = adj(&[
            ("A", "B", "next"),
            ("B", "C", "next"),
            ("C", "D", "next"),
            ("D", "E", "next"),
        ]);
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 2,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        // Should visit A(0), B(1), C(2) but not D(3) or E(4)
        assert_eq!(result.nodes_visited, 3);
        assert!(result.truncated);
        assert_eq!(result.truncation_reason.as_deref(), Some("max_depth"));

        let ids: Vec<&str> = result.path.iter().map(|n| n.id.as_str()).collect();
        assert!(ids.contains(&"A"));
        assert!(ids.contains(&"B"));
        assert!(ids.contains(&"C"));
        assert!(!ids.contains(&"D"));
        assert!(!ids.contains(&"E"));
    }

    #[test]
    fn test_edge_filtering() {
        // A has two outgoing edges: one "has" and one "observes"
        let adjacency = adj(&[
            ("A", "B", "has"),
            ("A", "C", "observes"),
            ("B", "D", "has"),
            ("C", "E", "observes"),
        ]);
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 100,
            include_edges: vec!["has".to_string()],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        // Only "has" edges should be followed: A->B->D
        let ids: Vec<&str> = result.path.iter().map(|n| n.id.as_str()).collect();
        assert!(ids.contains(&"A"));
        assert!(ids.contains(&"B"));
        assert!(ids.contains(&"D"));
        assert!(!ids.contains(&"C"));
        assert!(!ids.contains(&"E"));
        assert_eq!(result.nodes_visited, 3);
    }

    #[test]
    fn test_empty_graph_start_node_missing() {
        // Start node has no edges and no entry in adjacency
        let adjacency: HashMap<String, Vec<(String, String)>> = HashMap::new();
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 10,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("lonely");

        // Start node should still be visited
        assert_eq!(result.nodes_visited, 1);
        assert!(!result.truncated);
        assert!(result.cycles_detected.is_empty());
        assert_eq!(result.path.len(), 1);
        assert_eq!(result.path[0].id, "lonely");
    }

    #[test]
    fn test_single_node_no_edges() {
        let adjacency: HashMap<String, Vec<(String, String)>> = HashMap::new();
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 10,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("only");

        assert_eq!(result.nodes_visited, 1);
        assert_eq!(result.edges_followed, 0);
        assert!(!result.truncated);
        assert!(result.cycles_detected.is_empty());
        assert_eq!(result.path[0].id, "only");
    }

    #[test]
    fn test_node_info_populated() {
        let adjacency = adj(&[("A", "B", "has")]);
        let info = node_info(&[
            ("A", "product", "Tracera v2"),
            ("B", "capability", "Trace Graph"),
        ]);
        let budget = TraversalBudget::default();
        let mut gt = GraphTraversal::with_node_info(adjacency, budget, info);
        let result = gt.traverse("A");

        assert_eq!(result.path[0].kind, "product");
        assert_eq!(result.path[0].label, "Tracera v2");
        assert_eq!(result.path[1].kind, "capability");
        assert_eq!(result.path[1].label, "Trace Graph");
    }

    #[test]
    fn test_node_info_fallback_to_unknown() {
        let adjacency = adj(&[("X", "Y", "link")]);
        let budget = TraversalBudget::default();
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("X");

        assert_eq!(result.path[0].kind, "unknown");
        assert_eq!(result.path[0].label, "X");
    }

    #[test]
    fn test_budget_defaults() {
        let budget = TraversalBudget::default();
        assert_eq!(budget.max_nodes, 1000);
        assert_eq!(budget.max_depth, 50);
        assert!(budget.include_edges.is_empty());
    }

    #[test]
    fn test_multiple_cycles_detected() {
        // A -> B -> C -> A  and  A -> D -> E -> D
        let adjacency = adj(&[
            ("A", "B", "link"),
            ("A", "D", "link"),
            ("B", "C", "link"),
            ("C", "A", "link"),
            ("D", "E", "link"),
            ("E", "D", "link"),
        ]);
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 100,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        assert!(result.nodes_visited >= 3);
        // Both A (from C->A) and D (from E->D) should be detected as cycles
        assert!(
            result.cycles_detected.contains(&"A".to_string()),
            "Expected cycle on A, got: {:?}",
            result.cycles_detected
        );
        assert!(
            result.cycles_detected.contains(&"D".to_string()),
            "Expected cycle on D, got: {:?}",
            result.cycles_detected
        );
    }

    #[test]
    fn test_edges_followed_count() {
        // A -> B -> C, A -> D
        let adjacency = adj(&[
            ("A", "B", "has"),
            ("A", "D", "has"),
            ("B", "C", "has"),
        ]);
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 10,
            include_edges: vec![],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        // A has 2 edges, B has 1 edge, C and D have 0 = 3 total
        assert_eq!(result.edges_followed, 3);
    }

    #[test]
    fn test_edges_followed_with_filter() {
        let adjacency = adj(&[
            ("A", "B", "has"),
            ("A", "C", "observe"),
            ("B", "D", "has"),
        ]);
        let budget = TraversalBudget {
            max_nodes: 100,
            max_depth: 10,
            include_edges: vec!["has".to_string()],
        };
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        // All 3 edges are followed (counted), but only 2 are traversed
        assert_eq!(result.edges_followed, 3);
        assert_eq!(result.nodes_visited, 3); // A, B, D
    }

    #[test]
    fn test_build_adjacency_helper() {
        let edges = vec![
            ("A".to_string(), "B".to_string(), "has".to_string()),
            ("A".to_string(), "C".to_string(), "has".to_string()),
            ("B".to_string(), "D".to_string(), "link".to_string()),
        ];
        let adj_map = build_adjacency(&edges);

        assert_eq!(adj_map.len(), 2); // A and B
        assert_eq!(adj_map["A"].len(), 2);
        assert_eq!(adj_map["B"].len(), 1);
    }

    #[test]
    fn test_traversal_result_serializable() {
        let adjacency = adj(&[("A", "B", "has")]);
        let budget = TraversalBudget::default();
        let mut gt = GraphTraversal::new(adjacency, budget);
        let result = gt.traverse("A");

        // Should serialize without error
        let json = serde_json::to_string(&result).unwrap();
        assert!(json.contains("nodes_visited"));
        assert!(json.contains("truncated"));
    }
}
