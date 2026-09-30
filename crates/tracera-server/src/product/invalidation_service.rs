//! Application service for bounded invalidation planning.
//!
//! It produces append-only invalidation events; persistence remains behind
//! ProductPersistence.

use chrono::Utc;
use super::{
    dependencies::{propagate_dependency_change, DependencyEdge},
    invalidation::PropagationResult,
    persistence::InvalidationEvent,
};

#[derive(Debug, Clone)]
pub struct InvalidationPlan {
    pub propagation: PropagationResult,
    pub events: Vec<InvalidationEvent>,
}

/// Plan invalidation events for a dependency change.
///
/// The caller supplies a stable trigger reference and target kind. If traversal
/// is incomplete, returned events cover only the visited frontier and
/// propagation.complete=false tells the caller more work remains.
pub fn plan_dependency_invalidation(
    changed:&[String],
    edges:&[DependencyEdge],
    revision:&str,
    max_nodes:usize,
    trigger_ref:&str,
    target_kind:&str,
)->InvalidationPlan{
    let propagation=propagate_dependency_change(changed,edges,revision,max_nodes);
    let now=Utc::now();
    let events=propagation.affected.iter()
        .filter(|target| !changed.contains(target))
        .enumerate()
        .map(|(i,target)|InvalidationEvent{
            invalidation_id:format!("inv:{}:{}:{}",trigger_ref,target,i),
            trigger_kind:"dependency_changed".into(),
            trigger_ref:trigger_ref.into(),
            target_kind:target_kind.into(),
            target_ref:target.clone(),
            prior_state:Some("current_valid".into()),
            new_state:"suspect".into(),
            reason:format!("dependency change propagated under revision {revision}"),
            occurred_at:now,
        }).collect();
    InvalidationPlan{propagation,events}
}

pub fn plan_certificate_revocation(
    certificate_ref:&str,
    reuse_decision_ids:&[String],
)->InvalidationPlan{
    let now=Utc::now();
    let events=reuse_decision_ids.iter().enumerate().map(|(i,id)|InvalidationEvent{
        invalidation_id:format!("inv:cert:{}:{i}",certificate_ref),
        trigger_kind:"certificate_revoked".into(),
        trigger_ref:certificate_ref.into(),
        target_kind:"reuse_decision".into(),
        target_ref:id.clone(),
        prior_state:Some("current_valid".into()),
        new_state:"suspect".into(),
        reason:"compatibility certificate revoked".into(),
        occurred_at:now,
    }).collect::<Vec<_>>();
    InvalidationPlan{
        propagation:PropagationResult{affected:reuse_decision_ids.to_vec(),continuation:Vec::new(),complete:true},
        events,
    }
}

#[cfg(test)]
mod tests{
 use super::*;
 use crate::product::dependencies::{DependencyAuthority,DependencyEdge};
 #[test] fn budget_partial_survives_service_boundary(){
  let edges=vec![
   DependencyEdge{dependency:"a".into(),dependent:"b".into(),authority:DependencyAuthority::Accepted,revision:"r1".into(),active:true},
   DependencyEdge{dependency:"b".into(),dependent:"c".into(),authority:DependencyAuthority::Accepted,revision:"r1".into(),active:true},
  ];
  let plan=plan_dependency_invalidation(&["a".into()],&edges,"r1",2,"change-1","criterion");
  assert!(!plan.propagation.complete);
  assert_eq!(plan.events.len(),1);
  assert_eq!(plan.events[0].target_ref,"b");
 }
 #[test] fn certificate_revocation_targets_reuse_not_observation(){
  let plan=plan_certificate_revocation("cert:c1",&["reuse:r1".into()]);
  assert_eq!(plan.events[0].target_kind,"reuse_decision");
  assert_eq!(plan.events[0].new_state,"suspect");
 }
}
