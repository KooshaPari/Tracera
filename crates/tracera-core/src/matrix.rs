//! Matrix operations: build, query, diff.
//!
//! Phase 2 of the 2026-06-09 Tracera decouple plan.
//! Ported from `Tracera/backend/internal/services/matrix_service.go`.

use serde::{Deserialize, Serialize};
use std::collections::{BTreeSet, HashMap};
use uuid::Uuid;

use crate::ids::RequirementId;
use crate::{CoverageMatrix, CoverageState, MatrixCell, TraceLink};

/// Result of a single matrix-build operation: the matrix plus provenance.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct BuildResult {
    pub matrix: CoverageMatrix,
    pub built_at: chrono::DateTime<chrono::Utc>,
    pub link_count: usize,
    pub cell_count: usize,
    pub stale_links: usize,
}

/// Build a coverage matrix from a flat list of trace links, using the
/// canonical `(source, target)` Uuid projection. Cells are keyed by the
/// two artifact UUIDs (one per cell), coverage is computed per cell from
/// the trace link set.
pub fn build_matrix(links: &[TraceLink]) -> BuildResult {
    let mut cell_map: HashMap<(String, String), MatrixCell> = HashMap::new();

    for link in links {
        let key = (
            link.source_artifact_id.to_string(),
            link.target_artifact_id.to_string(),
        );
        let cell = cell_map.entry(key.clone()).or_insert_with(|| MatrixCell {
            from: key.0.clone(),
            to: key.1.clone(),
            trace_links: Vec::new(),
            coverage: CoverageState::Missing,
        });
        cell.trace_links.push(link.clone());
    }

    for cell in cell_map.values_mut() {
        cell.coverage = classify_cell(&cell.trace_links);
    }

    let cell_count = cell_map.len();
    let link_count = links.len();
    let stale_links = links.iter().filter(|l| is_stale_link(l)).count();

    let mut cells: indexmap::IndexMap<(String, String), MatrixCell> =
        indexmap::IndexMap::with_hasher(Default::default());
    for (k, v) in cell_map {
        cells.insert(k, v);
    }
    cells.sort_keys();

    BuildResult {
        matrix: CoverageMatrix {
            cells,
            generated_at: chrono::Utc::now(),
        },
        built_at: chrono::Utc::now(),
        link_count,
        cell_count,
        stale_links,
    }
}

/// Query: for a given requirement UUID, return all matrix cells that involve it.
pub fn neighbors<'a>(matrix: &'a CoverageMatrix, req_id: &Uuid) -> Vec<&'a MatrixCell> {
    let key_str = req_id.to_string();
    matrix
        .cells
        .values()
        .filter(|c| c.from == key_str || c.to == key_str)
        .collect()
}

/// Diff: which (from, to) pairs are in `new` but not in `old`.
pub fn added<'a>(old: &'a CoverageMatrix, new: &'a CoverageMatrix) -> Vec<&'a MatrixCell> {
    new.cells
        .values()
        .filter(|n| !old.cells.contains_key(&(n.from.clone(), n.to.clone())))
        .collect()
}

/// Diff: which (from, to) pairs are in `old` but not in `new`.
pub fn removed<'a>(old: &'a CoverageMatrix, new: &'a CoverageMatrix) -> Vec<&'a MatrixCell> {
    old.cells
        .values()
        .filter(|o| !new.cells.contains_key(&(o.from.clone(), o.to.clone())))
        .collect()
}

/// Diff: which (from, to) pairs are in both, but the link set or coverage changed.
pub fn changed<'a>(
    old: &'a CoverageMatrix,
    new: &'a CoverageMatrix,
) -> Vec<(&'a MatrixCell, &'a MatrixCell)> {
    let mut out = Vec::new();
    for (k, n) in &new.cells {
        if let Some(o) = old.cells.get(k) {
            if o.coverage != n.coverage || o.trace_links != n.trace_links {
                out.push((o, n));
            }
        }
    }
    out
}

fn classify_cell(links: &[TraceLink]) -> CoverageState {
    if links.is_empty() {
        return CoverageState::Missing;
    }
    let verifying: Vec<&TraceLink> = links
        .iter()
        .filter(|l| matches!(l.link_type, crate::TraceLinkType::Verifies))
        .collect();
    let satisfying: Vec<&TraceLink> = links
        .iter()
        .filter(|l| matches!(l.link_type, crate::TraceLinkType::Satisfies))
        .collect();
    let conflict: Vec<&TraceLink> = links
        .iter()
        .filter(|l| matches!(l.link_type, crate::TraceLinkType::ConflictsWith))
        .collect();

    if !conflict.is_empty() {
        CoverageState::Conflict
    } else if verifying.iter().any(|l| l.confidence >= 0.9)
        || satisfying.iter().any(|l| l.confidence >= 0.9)
    {
        CoverageState::Covered
    } else if !verifying.is_empty() || !satisfying.is_empty() {
        CoverageState::Partial
    } else if is_stale_links(links) {
        CoverageState::Stale
    } else {
        CoverageState::Missing
    }
}

fn is_stale_links(links: &[TraceLink]) -> bool {
    links.iter().any(is_stale_link)
}

fn is_stale_link(l: &TraceLink) -> bool {
    if let (Some(ts), Some(updated)) = (l.created_at, l.updated_at) {
        (updated - ts).num_days() > 90
    } else {
        false
    }
}

/// Convenience builder for the common case of building a matrix from
/// `(requirement_id, BTreeSet<evidence_id_string>)` pairs. The req_id
/// is encoded into the link's metadata and the evidence strings become
/// target UUIDs (deterministic from the string via `Uuid::new_v5`).
pub fn build_from_pairs(pairs: &[(RequirementId, BTreeSet<String>)]) -> BuildResult {
    let mut links = Vec::new();
    let project = Uuid::new_v4();
    for (req, evidences) in pairs {
        let source = Uuid::new_v5(&Uuid::NAMESPACE_OID, req.as_str().as_bytes());
        for ev in evidences {
            let target = Uuid::new_v5(&Uuid::NAMESPACE_OID, ev.as_bytes());
            if source == target {
                continue;
            }
            let mut link = TraceLink::new(project, source, target, crate::TraceLinkType::Verifies)
                .expect("source != target");
            link.metadata.insert(
                "req_id".to_string(),
                serde_json::Value::String(req.as_str().to_string()),
            );
            link.metadata.insert(
                "evidence".to_string(),
                serde_json::Value::String(ev.clone()),
            );
            links.push(link);
        }
    }
    build_matrix(&links)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::LinkKind;
    use chrono::{Duration, Utc};
    use proptest::collection::{btree_set, vec};
    use proptest::prelude::*;

    fn make_link(link_type: crate::TraceLinkType, confidence: f32, age_days: i64) -> TraceLink {
        let project = Uuid::new_v4();
        let source = Uuid::new_v4();
        let target = Uuid::new_v4();
        let mut link = TraceLink::new(project, source, target, link_type).unwrap();
        link.confidence = confidence;
        let now = Utc::now();
        link.created_at = Some(now - Duration::days(age_days));
        link.updated_at = Some(now);
        link
    }

    #[test]
    fn empty_links_yields_empty_matrix() {
        let r = build_matrix(&[]);
        assert_eq!(r.link_count, 0);
        assert_eq!(r.cell_count, 0);
        assert!(r.matrix.cells.is_empty());
    }

    #[test]
    fn single_high_confidence_verifies_is_covered() {
        let link = make_link(crate::TraceLinkType::Verifies, 0.95, 1);
        let r = build_matrix(&[link]);
        assert_eq!(r.link_count, 1);
        assert_eq!(r.cell_count, 1);
        for cell in r.matrix.cells.values() {
            assert_eq!(cell.coverage, CoverageState::Covered);
        }
    }

    #[test]
    fn low_confidence_verifies_is_partial() {
        let link = make_link(crate::TraceLinkType::Verifies, 0.5, 1);
        let r = build_matrix(&[link]);
        for cell in r.matrix.cells.values() {
            assert_eq!(cell.coverage, CoverageState::Partial);
        }
    }

    #[test]
    fn conflict_overrides_covered() {
        let a = make_link(crate::TraceLinkType::Verifies, 0.95, 1);
        let mut b = make_link(crate::TraceLinkType::ConflictsWith, 0.95, 1);
        b.source_artifact_id = a.source_artifact_id;
        b.target_artifact_id = a.target_artifact_id;
        let r = build_matrix(&[a, b]);
        for cell in r.matrix.cells.values() {
            assert_eq!(cell.coverage, CoverageState::Conflict);
        }
    }

    #[test]
    fn old_links_marked_stale() {
        let link = make_link(crate::TraceLinkType::DerivesFrom, 0.5, 365);
        let r = build_matrix(&[link]);
        for cell in r.matrix.cells.values() {
            assert_eq!(cell.coverage, CoverageState::Stale);
        }
        assert_eq!(r.stale_links, 1);
    }

    #[test]
    fn added_removed_changed_diff() {
        let a = make_link(crate::TraceLinkType::Verifies, 0.95, 1);
        let b = make_link(crate::TraceLinkType::Verifies, 0.95, 1);
        let old = build_matrix(&[a.clone()]).matrix;
        let new = build_matrix(&[a, b]).matrix;
        assert_eq!(added(&old, &new).len(), 1);
        assert_eq!(removed(&old, &new).len(), 0);
        assert_eq!(changed(&old, &new).len(), 0);
    }

    #[test]
    fn link_kind_alias_reachable() {
        let _: LinkKind = LinkKind::Verifies;
    }

    #[test]
    fn build_from_pairs_produces_verifies_links() {
        let req = RequirementId::new();
        let mut evs = BTreeSet::new();
        evs.insert("ev-001".to_string());
        evs.insert("ev-002".to_string());
        let r = build_from_pairs(&[(req, evs)]);
        assert_eq!(r.link_count, 2);
        for cell in r.matrix.cells.values() {
            assert_eq!(cell.coverage, CoverageState::Covered);
        }
    }

    fn link_for_pair(source: Uuid, target: Uuid, kind: crate::TraceLinkType) -> TraceLink {
        let mut link = TraceLink::new(Uuid::new_v4(), source, target, kind).unwrap();
        link.created_at = Some(Utc::now());
        link.updated_at = Some(Utc::now());
        link
    }

    prop_compose! {
        fn uuid_pair()(source in any::<u128>(), target in any::<u128>())
            -> (Uuid, Uuid)
        {
            let source = Uuid::from_u128(source);
            let mut target = Uuid::from_u128(target);
            if source == target {
                target = Uuid::from_u128(target.as_u128().wrapping_add(1));
            }
            (source, target)
        }
    }

    proptest! {
        #[test]
        fn build_matrix_groups_links_by_source_target(pairs in vec(uuid_pair(), 0..80)) {
            let links: Vec<_> = pairs
                .iter()
                .map(|(source, target)| {
                    link_for_pair(*source, *target, crate::TraceLinkType::Verifies)
                })
                .collect();
            let unique_pairs: BTreeSet<_> = pairs
                .iter()
                .map(|(source, target)| (source.to_string(), target.to_string()))
                .collect();

            let result = build_matrix(&links);

            prop_assert_eq!(result.link_count, links.len());
            prop_assert_eq!(result.cell_count, unique_pairs.len());
            prop_assert_eq!(result.matrix.cells.len(), unique_pairs.len());
            for ((from, to), cell) in &result.matrix.cells {
                prop_assert_eq!(&(cell.from.clone(), cell.to.clone()), &(from.clone(), to.clone()));
                prop_assert!(unique_pairs.contains(&(from.clone(), to.clone())));
                prop_assert!(!cell.trace_links.is_empty());
            }
        }

        #[test]
        fn neighbors_returns_exact_incident_cells(pairs in vec(uuid_pair(), 0..50), needle in any::<u128>()) {
            let needle = Uuid::from_u128(needle);
            let mut links: Vec<_> = pairs
                .iter()
                .map(|(source, target)| {
                    link_for_pair(*source, *target, crate::TraceLinkType::Satisfies)
                })
                .collect();

            if let Some((_, target)) = pairs.first() {
                links.push(link_for_pair(needle, *target, crate::TraceLinkType::Verifies));
            }

            let matrix = build_matrix(&links).matrix;
            let expected = matrix
                .cells
                .values()
                .filter(|cell| cell.from == needle.to_string() || cell.to == needle.to_string())
                .count();

            prop_assert_eq!(neighbors(&matrix, &needle).len(), expected);
        }

        #[test]
        fn build_from_pairs_link_count_matches_unique_non_self_evidence(
            evidence_sets in vec(btree_set("[a-z0-9_-]{1,16}", 0..12), 0..20)
        ) {
            let pairs: Vec<_> = evidence_sets
                .into_iter()
                .map(|evidence| (RequirementId::new(), evidence))
                .collect();
            let expected = pairs
                .iter()
                .map(|(req, evidence)| {
                    let source = Uuid::new_v5(&Uuid::NAMESPACE_OID, req.as_str().as_bytes());
                    evidence
                        .iter()
                        .filter(|ev| Uuid::new_v5(&Uuid::NAMESPACE_OID, ev.as_bytes()) != source)
                        .count()
                })
                .sum::<usize>();

            let result = build_from_pairs(&pairs);

            prop_assert_eq!(result.link_count, expected);
            prop_assert_eq!(result.cell_count, expected);
        }

        #[test]
        fn added_and_removed_are_disjoint_set_differences(
            old_pairs in vec(uuid_pair(), 0..40),
            new_pairs in vec(uuid_pair(), 0..40)
        ) {
            let old_links: Vec<_> = old_pairs
                .iter()
                .map(|(source, target)| {
                    link_for_pair(*source, *target, crate::TraceLinkType::Verifies)
                })
                .collect();
            let new_links: Vec<_> = new_pairs
                .iter()
                .map(|(source, target)| {
                    link_for_pair(*source, *target, crate::TraceLinkType::Verifies)
                })
                .collect();
            let old = build_matrix(&old_links).matrix;
            let new = build_matrix(&new_links).matrix;
            let old_keys: BTreeSet<_> = old.cells.keys().cloned().collect();
            let new_keys: BTreeSet<_> = new.cells.keys().cloned().collect();
            let expected_added = new_keys.difference(&old_keys).count();
            let expected_removed = old_keys.difference(&new_keys).count();

            prop_assert_eq!(added(&old, &new).len(), expected_added);
            prop_assert_eq!(removed(&old, &new).len(), expected_removed);
        }
    }
}
