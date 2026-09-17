//! Graph input types for the distillation pipeline.

use std::collections::HashMap;

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
