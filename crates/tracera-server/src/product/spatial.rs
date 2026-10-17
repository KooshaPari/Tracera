//! Read-only deterministic semantic spatial projection (TRACERA-SPEC-015).
//!
//! This is a renderer-independent domain adapter. It does NOT claim to render
//! physical geometry, infer graph facts, authorize data, or mutate product state.
//! Callers MUST pass an already authorized and snapshot-pinned graph slice.
//! The compiler rejects inconsistent input rather than drawing convincing lies.

use std::collections::{HashMap, HashSet};

use serde::{Deserialize, Serialize};

/// A semantic assembly, flow view, or physical/semantic hybrid representation.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ViewKind {
    Assembly,
    Flow,
    Environment,
    Hybrid,
}

/// Source truth class of a glyph, NOT a quality or health assessment.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum GeometryTruth {
    Physical,
    Measured,
    Semantic,
    Illustrative,
}

/// Input node from a *single already-authorized* product graph snapshot.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct SpatialNode {
    pub id: String,
    pub product_id: String,
    pub baseline_revision: u64,
    pub kind: String,
    pub label: String,
    pub geometry_truth: GeometryTruth,
    /// Immutable external CAD/design or source evidence reference where applicable.
    pub geometry_source_ref: Option<String>,
}

/// Input canonical directed relationship; it cannot be inferred from proximity.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct SpatialRelation {
    pub id: String,
    pub source_id: String,
    pub target_id: String,
    pub kind: String,
    pub source_ref: Option<String>,
}

/// Projection is pinned to the product identity and baseline; budgets limit
/// visible geometry, not the underlying canonical model.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct ProjectionScope {
    pub product_id: String,
    pub baseline_revision: u64,
    pub view: ViewKind,
    pub max_nodes: usize,
    pub max_relations: usize,
}

/// A visual glyph retains canonical identity and accessible text.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct SpatialGlyph {
    pub entity_ref: String,
    pub kind: String,
    pub label: String,
    pub geometry_truth: GeometryTruth,
    pub geometry_source_ref: Option<String>,
    /// Scene-grid coordinates, purely presentational (NOT millimeters/meters).
    pub position: [i32; 3],
}

/// A rendered conduit is only a view of a canonical typed relationship.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct SpatialConduit {
    pub relation_ref: String,
    pub source_ref: String,
    pub target_ref: String,
    pub kind: String,
    pub source_evidence_ref: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct SpatialProjection {
    pub scope: ProjectionScope,
    pub glyphs: Vec<SpatialGlyph>,
    pub conduits: Vec<SpatialConduit>,
    pub omitted_nodes: usize,
    pub omitted_relations: usize,
    pub truncated: bool,
    /// Never promote this to true if the caller's canonical data is partial.
    pub input_complete: bool,
    pub read_only: bool,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ProjectionError {
    InvalidScope,
    InvalidBudget,
    InvalidNode(String),
    DuplicateNode(String),
    InvalidRelation(String),
    DuplicateRelation(String),
    MissingEndpoint(String),
    MissingGeometrySource(String),
}

impl std::fmt::Display for ProjectionError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for ProjectionError {}

/// Compile a deterministic bounded scene for a trusted caller's authorized
/// product slice. No data is fetched, persisted, or changed here.
pub fn compile_spatial_projection(
    scope: ProjectionScope,
    nodes: &[SpatialNode],
    relations: &[SpatialRelation],
    input_complete: bool,
) -> Result<SpatialProjection, ProjectionError> {
    if scope.product_id.trim().is_empty() {
        return Err(ProjectionError::InvalidScope);
    }
    if scope.max_nodes == 0 || scope.max_relations == 0 {
        return Err(ProjectionError::InvalidBudget);
    }

    let mut node_ids = HashSet::new();
    for node in nodes {
        if node.id.trim().is_empty()
            || node.kind.trim().is_empty()
            || node.label.trim().is_empty()
            || node.product_id != scope.product_id
            || node.baseline_revision != scope.baseline_revision
        {
            return Err(ProjectionError::InvalidNode(node.id.clone()));
        }
        if matches!(node.geometry_truth, GeometryTruth::Physical | GeometryTruth::Measured)
            && node
                .geometry_source_ref
                .as_deref()
                .is_none_or(|source| source.trim().is_empty())
        {
            return Err(ProjectionError::MissingGeometrySource(node.id.clone()));
        }
        if !node_ids.insert(node.id.as_str()) {
            return Err(ProjectionError::DuplicateNode(node.id.clone()));
        }
    }

    let mut relation_ids = HashSet::new();
    for relation in relations {
        if relation.id.trim().is_empty() || relation.kind.trim().is_empty() {
            return Err(ProjectionError::InvalidRelation(relation.id.clone()));
        }
        if !relation_ids.insert(relation.id.as_str()) {
            return Err(ProjectionError::DuplicateRelation(relation.id.clone()));
        }
        if !node_ids.contains(relation.source_id.as_str())
            || !node_ids.contains(relation.target_id.as_str())
        {
            return Err(ProjectionError::MissingEndpoint(relation.id.clone()));
        }
    }

    let mut ordered_nodes: Vec<_> = nodes.iter().collect();
    ordered_nodes.sort_by(|a, b| a.id.cmp(&b.id));
    let glyphs: Vec<_> = ordered_nodes
        .iter()
        .take(scope.max_nodes)
        .enumerate()
        .map(|(index, node)| SpatialGlyph {
            entity_ref: node.id.clone(),
            kind: node.kind.clone(),
            label: node.label.clone(),
            geometry_truth: node.geometry_truth,
            geometry_source_ref: node.geometry_source_ref.clone(),
            position: [
                ((index % 8) as i32) * 4,
                ((index / 8) as i32) * 4,
                0,
            ],
        })
        .collect();
    let displayed_ids: HashMap<&str, ()> = glyphs
        .iter()
        .map(|glyph| (glyph.entity_ref.as_str(), ()))
        .collect();

    let mut ordered_relations: Vec<_> = relations.iter().collect();
    ordered_relations.sort_by(|a, b| a.id.cmp(&b.id));
    let conduits: Vec<_> = ordered_relations
        .iter()
        .filter(|relation| {
            displayed_ids.contains_key(relation.source_id.as_str())
                && displayed_ids.contains_key(relation.target_id.as_str())
        })
        .take(scope.max_relations)
        .map(|relation| SpatialConduit {
            relation_ref: relation.id.clone(),
            source_ref: relation.source_id.clone(),
            target_ref: relation.target_id.clone(),
            kind: relation.kind.clone(),
            source_evidence_ref: relation.source_ref.clone(),
        })
        .collect();

    let omitted_nodes = nodes.len() - glyphs.len();
    let omitted_relations = relations.len() - conduits.len();
    Ok(SpatialProjection {
        scope,
        glyphs,
        conduits,
        omitted_nodes,
        omitted_relations,
        truncated: omitted_nodes > 0 || omitted_relations > 0 || !input_complete,
        input_complete,
        read_only: true,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn scope() -> ProjectionScope {
        ProjectionScope {
            product_id: "tracera".into(),
            baseline_revision: 3,
            view: ViewKind::Assembly,
            max_nodes: 100,
            max_relations: 100,
        }
    }
    fn node(id: &str) -> SpatialNode {
        SpatialNode {
            id: id.into(),
            product_id: "tracera".into(),
            baseline_revision: 3,
            kind: "component".into(),
            label: id.into(),
            geometry_truth: GeometryTruth::Semantic,
            geometry_source_ref: None,
        }
    }
    fn edge() -> SpatialRelation {
        SpatialRelation {
            id: "depends:ab".into(),
            source_id: "a".into(),
            target_id: "b".into(),
            kind: "depends_on".into(),
            source_ref: Some("source:accepted-test".into()),
        }
    }

    #[test]
    fn identity_and_edge_direction_round_trip() {
        let scene = compile_spatial_projection(
            scope(), &[node("b"), node("a")], &[edge()], true,
        ).unwrap();
        assert_eq!(scene.glyphs[0].entity_ref, "a");
        assert_eq!(scene.conduits[0].source_ref, "a");
        assert_eq!(scene.conduits[0].target_ref, "b");
        assert_eq!(scene.conduits[0].source_evidence_ref.as_deref(), Some("source:accepted-test"));
        assert!(scene.read_only);
        assert!(scene.input_complete);
        let again: SpatialProjection =
            serde_json::from_str(&serde_json::to_string(&scene).unwrap()).unwrap();
        assert_eq!(again, scene);
    }

    #[test]
    fn order_independent_stable_positions() {
        let forward = compile_spatial_projection(scope(), &[node("a"), node("b")], &[edge()], true).unwrap();
        let backward = compile_spatial_projection(scope(), &[node("b"), node("a")], &[edge()], true).unwrap();
        assert_eq!(forward, backward);
    }

    #[test]
    fn invalid_cross_product_or_version_rejected() {
        let mut other = node("other");
        other.product_id = "different".into();
        assert_eq!(
            compile_spatial_projection(scope(), &[other], &[], true).unwrap_err(),
            ProjectionError::InvalidNode("other".into())
        );
        let mut old = node("old");
        old.baseline_revision = 2;
        assert!(matches!(
            compile_spatial_projection(scope(), &[old], &[], true),
            Err(ProjectionError::InvalidNode(_))
        ));
    }

    #[test]
    fn physical_geometry_requires_traceable_source() {
        let mut part = node("gear");
        part.geometry_truth = GeometryTruth::Physical;
        assert_eq!(
            compile_spatial_projection(scope(), &[part.clone()], &[], true).unwrap_err(),
            ProjectionError::MissingGeometrySource("gear".into())
        );
        part.geometry_source_ref = Some("cad:assembly/revision7".into());
        let result = compile_spatial_projection(scope(), &[part], &[], true).unwrap();
        assert_eq!(result.glyphs[0].geometry_truth, GeometryTruth::Physical);
    }

    #[test]
    fn reject_phantom_links_and_duplicate_ids() {
        assert!(matches!(
            compile_spatial_projection(scope(), &[node("a")], &[edge()], true),
            Err(ProjectionError::MissingEndpoint(_))
        ));
        assert!(matches!(
            compile_spatial_projection(scope(), &[node("a"), node("a")], &[], true),
            Err(ProjectionError::DuplicateNode(_))
        ));
        assert!(matches!(
            compile_spatial_projection(scope(), &[node("a"), node("b")], &[edge(), edge()], true),
            Err(ProjectionError::DuplicateRelation(_))
        ));
    }

    #[test]
    fn budget_never_implies_complete_world() {
        let mut q = scope();
        q.max_nodes = 1;
        let scene = compile_spatial_projection(q, &[node("a"), node("b")], &[edge()], false).unwrap();
        assert_eq!(scene.glyphs.len(), 1);
        assert!(scene.conduits.is_empty());
        assert_eq!(scene.omitted_nodes, 1);
        assert_eq!(scene.omitted_relations, 1);
        assert!(scene.truncated);
        assert!(!scene.input_complete);
    }

    #[test]
    fn cannot_silently_compile_empty_budget() {
        let mut q = scope();
        q.max_nodes = 0;
        assert_eq!(
            compile_spatial_projection(q, &[], &[], true).unwrap_err(),
            ProjectionError::InvalidBudget
        );
    }
    #[test]
    fn dense_graph_is_bounded_with_visible_incompleteness() {
        let nodes: Vec<SpatialNode> = (0..20_000)
            .map(|i| node(&format!("capability-{i:05}")))
            .collect();
        let input = ProjectionScope {
            max_nodes: 128, max_relations: 256, ..scope()
        };
        let scene = compile_spatial_projection(input, &nodes, &[], true).unwrap();
        assert_eq!(scene.glyphs.len(), 128);
        assert_eq!(scene.omitted_nodes, 19_872);
        assert!(scene.truncated);
        assert!(scene.input_complete);
        assert!(scene.glyphs.windows(2).all(|w| w[0].entity_ref < w[1].entity_ref));
    }

    #[test]
    fn invalid_metadata_never_renders_as_literal_geometry() {
        let mut part = node("actuator");
        part.geometry_truth = GeometryTruth::Measured;
        part.geometry_source_ref = Some("  ".into());
        assert!(matches!(
            compile_spatial_projection(scope(), &[part], &[], false),
            Err(ProjectionError::MissingGeometrySource(_))
        ));
    }

}
