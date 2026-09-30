//! Current applicability reduction and bounded invalidation traversal.

use std::collections::{HashMap, HashSet, VecDeque};
use super::persistence::InvalidationEvent;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ApplicabilityProjection {
    pub state: String,
    pub last_event_id: Option<String>,
}

pub fn reduce_applicability(initial_state: &str, events: &[InvalidationEvent]) -> ApplicabilityProjection {
    let mut state = initial_state.to_string();
    let mut last = None;
    for event in events {
        state = event.new_state.clone();
        last = Some(event.invalidation_id.clone());
    }
    ApplicabilityProjection { state, last_event_id: last }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PropagationResult {
    pub affected: Vec<String>,
    pub continuation: Vec<String>,
    pub complete: bool,
}

/// dependents[A] = [B,C] means a change to A can affect B/C.
/// Budget exhaustion is partial work, never proof that no more impact exists.
pub fn propagate_bounded(
    roots: &[String],
    dependents: &HashMap<String, Vec<String>>,
    max_nodes: usize,
) -> PropagationResult {
    let mut queue: VecDeque<String> = roots.iter().cloned().collect();
    let mut seen = HashSet::new();
    let mut affected = Vec::new();

    while let Some(node) = queue.pop_front() {
        if seen.contains(&node) {
            continue;
        }
        if affected.len() >= max_nodes {
            queue.push_front(node);
            return PropagationResult {
                affected,
                continuation: queue.into_iter().collect(),
                complete: false,
            };
        }
        seen.insert(node.clone());
        affected.push(node.clone());
        if let Some(next) = dependents.get(&node) {
            for dependent in next {
                if !seen.contains(dependent) {
                    queue.push_back(dependent.clone());
                }
            }
        }
    }

    PropagationResult { affected, continuation: Vec::new(), complete: true }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Utc;

    fn event(id: &str, state: &str) -> InvalidationEvent {
        InvalidationEvent {
            invalidation_id: id.into(),
            trigger_kind: "dependency".into(),
            trigger_ref: "dep".into(),
            target_kind: "reuse_decision".into(),
            target_ref: "reuse".into(),
            prior_state: None,
            new_state: state.into(),
            reason: "test".into(),
            occurred_at: Utc::now(),
        }
    }

    #[test]
    fn no_events_preserves_initial_state() {
        assert_eq!(reduce_applicability("current_valid", &[]).state, "current_valid");
    }

    #[test]
    fn ordered_events_define_current_projection() {
        let projection = reduce_applicability(
            "current_valid",
            &[event("i1", "suspect"), event("i2", "current_valid")],
        );
        assert_eq!(projection.state, "current_valid");
        assert_eq!(projection.last_event_id.as_deref(), Some("i2"));
    }

    #[test]
    fn budget_exhaustion_is_explicitly_partial() {
        let mut graph = HashMap::new();
        graph.insert("a".into(), vec!["b".into()]);
        graph.insert("b".into(), vec!["c".into()]);
        let result = propagate_bounded(&["a".into()], &graph, 2);
        assert!(!result.complete);
        assert_eq!(result.affected, vec!["a", "b"]);
        assert!(!result.continuation.is_empty());
    }
}
