//! Typed dependency footprint projection into bounded invalidation traversal.

use std::collections::HashMap;
use super::invalidation::{propagate_bounded, PropagationResult};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DependencyAuthority {
    Deterministic,
    Accepted,
    Declared,
    Inferred,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DependencyEdge {
    pub dependency: String,
    pub dependent: String,
    pub authority: DependencyAuthority,
    pub revision: String,
    pub active: bool,
}

/// Build only positive, active dependency edges for a specific source revision.
/// Absence from this map is never evidence of independence.
pub fn dependency_graph(edges:&[DependencyEdge], revision:&str)->HashMap<String,Vec<String>>{
    let mut graph=HashMap::new();
    for edge in edges.iter().filter(|e|e.active && e.revision==revision){
        graph.entry(edge.dependency.clone()).or_insert_with(Vec::new).push(edge.dependent.clone());
    }
    graph
}

pub fn propagate_dependency_change(
    changed:&[String],
    edges:&[DependencyEdge],
    revision:&str,
    max_nodes:usize,
)->PropagationResult{
    let graph=dependency_graph(edges,revision);
    propagate_bounded(changed,&graph,max_nodes)
}

#[cfg(test)]
mod tests{
 use super::*;
 #[test] fn inferred_positive_can_conservatively_propagate(){
  let edges=vec![DependencyEdge{dependency:"schema".into(),dependent:"criterion".into(),authority:DependencyAuthority::Inferred,revision:"r1".into(),active:true}];
  let result=propagate_dependency_change(&["schema".into()],&edges,"r1",10);
  assert!(result.complete); assert_eq!(result.affected,vec!["schema","criterion"]);
 }
 #[test] fn stale_revision_edge_does_not_claim_current_dependency(){
  let edges=vec![DependencyEdge{dependency:"schema".into(),dependent:"criterion".into(),authority:DependencyAuthority::Deterministic,revision:"r0".into(),active:true}];
  let result=propagate_dependency_change(&["schema".into()],&edges,"r1",10);
  assert_eq!(result.affected,vec!["schema"]);
  // Critically, criterion's absence here is UNKNOWN independence, not proof
  // that it is safe to reuse evidence for criterion.
 }
}
