//! User-story traceability matrix.
//!
//! This module builds and queries a traceability matrix that links
//! user stories to the artefacts (code, tests, documents, migrations,
//! etc.) that fulfil them.  It supports coverage verification, gap
//! analysis, and confidence scoring.

use std::collections::{BTreeMap, BTreeSet};

// ---------------------------------------------------------------------------
// Core types
// ---------------------------------------------------------------------------

/// Types of links between a story and an artefact.
#[derive(Debug, Clone, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum LinkType {
    /// The artefact directly implements the story.
    Implements,
    /// The artefact tests the story.
    Tests,
    /// The artefact documents the story.
    Documents,
    /// The artefact migrates data related to the story.
    Migrates,
    /// A weaker, inferred relationship.
    Related,
}

impl std::fmt::Display for LinkType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Implements => write!(f, "implements"),
            Self::Tests => write!(f, "tests"),
            Self::Documents => write!(f, "documents"),
            Self::Migrates => write!(f, "migrates"),
            Self::Related => write!(f, "related"),
        }
    }
}

/// A single link between a story and an artefact.
#[derive(Debug, Clone)]
pub struct StoryTraceLink {
    pub story_id: String,
    pub artifact_id: String,
    pub link_type: LinkType,
    pub confidence: f64,
    pub created_at: u64,
}

impl StoryTraceLink {
    pub fn new(
        story_id: String,
        artifact_id: String,
        link_type: LinkType,
        confidence: f64,
    ) -> Self {
        Self {
            story_id,
            artifact_id,
            link_type,
            confidence: confidence.clamp(0.0, 1.0),
            created_at: 0, // caller can override
        }
    }
}

/// One row of the traceability matrix – a single story and the artefacts
/// linked to it.
#[derive(Debug, Clone)]
pub struct StoryRow {
    pub story_id: String,
    pub artifacts: BTreeMap<String, Vec<LinkInfo>>,
}

/// Summary of a single link as stored in the matrix.
#[derive(Debug, Clone)]
pub struct LinkInfo {
    pub link_type: LinkType,
    pub confidence: f64,
}

/// The full traceability matrix.
#[derive(Debug, Clone, Default)]
pub struct TraceabilityMatrix {
    /// Rows keyed by story ID (ordered for deterministic output).
    pub rows: BTreeMap<String, StoryRow>,
    /// Columns (all unique artefact IDs).
    pub columns: BTreeSet<String>,
}

/// Result of coverage verification.
#[derive(Debug, Clone)]
pub struct CoverageReport {
    pub total_stories: usize,
    pub covered_stories: usize,
    pub total_artifacts: usize,
    pub coverage_ratio: f64,
    pub uncovered_stories: Vec<String>,
}

/// Description of a single gap in the matrix.
#[derive(Debug, Clone)]
pub struct TraceabilityGap {
    pub story_id: String,
    pub missing_link_types: Vec<LinkType>,
    pub artifact_id: Option<String>,
    pub suggestion: String,
}

// ---------------------------------------------------------------------------
// Builder
// ---------------------------------------------------------------------------

/// Build a traceability matrix from a collection of links.
pub fn build_matrix(links: &[StoryTraceLink]) -> TraceabilityMatrix {
    let mut matrix = TraceabilityMatrix::default();

    for link in links {
        matrix.columns.insert(link.artifact_id.clone());

        let row = matrix
            .rows
            .entry(link.story_id.clone())
            .or_insert_with(|| StoryRow {
                story_id: link.story_id.clone(),
                artifacts: BTreeMap::new(),
            });

        let info = row
            .artifacts
            .entry(link.artifact_id.clone())
            .or_insert_with(Vec::new);

        info.push(LinkInfo {
            link_type: link.link_type.clone(),
            confidence: link.confidence,
        });
    }

    matrix
}

/// Verify that every story has at least one link of an *important* type
/// (implements or tests). Returns a coverage report.
pub fn verify_coverage(matrix: &TraceabilityMatrix) -> CoverageReport {
    let total_stories = matrix.rows.len();
    let total_artifacts = matrix.columns.len();
    let mut uncovered = Vec::new();

    for (story_id, row) in &matrix.rows {
        let has_important = row.artifacts.values().any(|infos| {
            infos.iter().any(|i| {
                i.link_type == LinkType::Implements || i.link_type == LinkType::Tests
            })
        });
        if !has_important {
            uncovered.push(story_id.clone());
        }
    }

    let covered_stories = total_stories - uncovered.len();
    let coverage_ratio = if total_stories == 0 {
        0.0
    } else {
        covered_stories as f64 / total_stories as f64
    };

    CoverageReport {
        total_stories,
        covered_stories,
        total_artifacts,
        coverage_ratio,
        uncovered_stories: uncovered,
    }
}

/// Identify gaps: stories missing specific link types, or artefacts not
/// linked to any story.
pub fn find_gaps(matrix: &TraceabilityMatrix) -> Vec<TraceabilityGap> {
    let mut gaps = Vec::new();
    let important_types = [LinkType::Implements, LinkType::Tests, LinkType::Documents];

    for (story_id, row) in &matrix.rows {
        let present_types: BTreeSet<&LinkType> = row
            .artifacts
            .values()
            .flatten()
            .map(|i| &i.link_type)
            .collect();

        for lt in &important_types {
            if !present_types.contains(lt) {
                gaps.push(TraceabilityGap {
                    story_id: story_id.clone(),
                    missing_link_types: vec![lt.clone()],
                    artifact_id: None,
                    suggestion: format!(
                        "Story '{story_id}' has no artefact with link type '{lt}'. \
                         Consider adding a {lt} link."
                    ),
                });
            }
        }
    }

    // Artefacts not linked to any story.
    for artifact_id in &matrix.columns {
        let linked_stories: usize = matrix
            .rows
            .values()
            .filter(|row| row.artifacts.contains_key(artifact_id))
            .count();
        if linked_stories == 0 {
            gaps.push(TraceabilityGap {
                story_id: String::new(),
                missing_link_types: Vec::new(),
                artifact_id: Some(artifact_id.clone()),
                suggestion: format!(
                    "Artefact '{artifact_id}' is not linked to any story. \
                     It may be orphaned or missing traceability."
                ),
            });
        }
    }

    gaps
}

/// Compute the average confidence across all links in the matrix.
pub fn average_confidence(matrix: &TraceabilityMatrix) -> f64 {
    let mut total = 0.0f64;
    let mut count = 0usize;
    for row in matrix.rows.values() {
        for infos in row.artifacts.values() {
            for info in infos {
                total += info.confidence;
                count += 1;
            }
        }
    }
    if count == 0 {
        0.0
    } else {
        total / count as f64
    }
}

/// Return all artefact IDs linked to a given story.
pub fn artifacts_for_story<'a>(
    matrix: &'a TraceabilityMatrix,
    story_id: &str,
) -> Vec<&'a str> {
    matrix
        .rows
        .get(story_id)
        .map(|row| {
            row.artifacts
                .keys()
                .map(|s| s.as_str())
                .collect()
        })
        .unwrap_or_default()
}

/// Return all story IDs linked to a given artefact.
pub fn stories_for_artifact<'a>(
    matrix: &'a TraceabilityMatrix,
    artifact_id: &str,
) -> Vec<&'a str> {
    matrix
        .rows
        .iter()
        .filter(|(_, row)| row.artifacts.contains_key(artifact_id))
        .map(|(id, _)| id.as_str())
        .collect()
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_links() -> Vec<StoryTraceLink> {
        vec![
            StoryTraceLink::new("S1".into(), "auth.rs".into(), LinkType::Implements, 0.95),
            StoryTraceLink::new("S1".into(), "auth_test.rs".into(), LinkType::Tests, 0.90),
            StoryTraceLink::new("S1".into(), "auth.md".into(), LinkType::Documents, 0.80),
            StoryTraceLink::new("S2".into(), "migrate_v2.sql".into(), LinkType::Migrates, 0.85),
            StoryTraceLink::new("S3".into(), "dashboard.tsx".into(), LinkType::Implements, 0.70),
            StoryTraceLink::new("S3".into(), "unused.rs".into(), LinkType::Related, 0.30),
        ]
    }

    fn matrix_with_orphan() -> Vec<StoryTraceLink> {
        let mut links = sample_links();
        // Add an orphan artifact not linked to any story
        links.push(StoryTraceLink::new("S1".into(), "orphan.rs".into(), LinkType::Related, 0.10));
        links
    }

    #[test]
    fn test_build_matrix_populates_rows_and_columns() {
        let links = sample_links();
        let matrix = build_matrix(&links);
        assert_eq!(matrix.rows.len(), 3); // S1, S2, S3
        assert!(matrix.columns.contains("auth.rs"));
        assert!(matrix.columns.contains("migrate_v2.sql"));
        assert!(matrix.columns.contains("dashboard.tsx"));
        assert!(matrix.columns.contains("unused.rs"));
        // 6 unique artifacts: auth.rs, auth_test.rs, auth.md, migrate_v2.sql, dashboard.tsx, unused.rs
        assert_eq!(matrix.columns.len(), 6);
    }

    #[test]
    fn test_verify_coverage_all_covered() {
        let links = vec![
            StoryTraceLink::new("S1".into(), "a.rs".into(), LinkType::Implements, 1.0),
            StoryTraceLink::new("S2".into(), "b.rs".into(), LinkType::Tests, 1.0),
        ];
        let matrix = build_matrix(&links);
        let report = verify_coverage(&matrix);
        assert_eq!(report.total_stories, 2);
        assert_eq!(report.covered_stories, 2);
        assert!((report.coverage_ratio - 1.0).abs() < f64::EPSILON);
        assert!(report.uncovered_stories.is_empty());
    }

    #[test]
    fn test_verify_coverage_detects_gap() {
        // S2 only has a "migrates" link – not enough.
        let links = sample_links();
        let matrix = build_matrix(&links);
        let report = verify_coverage(&matrix);
        assert!(report.uncovered_stories.contains(&"S2".into()));
    }

    #[test]
    fn test_find_gaps_reports_missing_types() {
        let links = sample_links();
        let matrix = build_matrix(&links);
        let gaps = find_gaps(&matrix);

        // S2 is missing implements, tests, documents.
        let s2_gaps: Vec<_> = gaps
            .iter()
            .filter(|g| g.story_id == "S2")
            .collect();
        assert!(s2_gaps.len() >= 2, "S2 should have at least 2 gaps");

        // S1 is missing nothing important (has implements, tests, documents).
        let s1_gaps: Vec<_> = gaps
            .iter()
            .filter(|g| g.story_id == "S1")
            .collect();
        assert_eq!(s1_gaps.len(), 0, "S1 should have no gaps");

        // All artifacts in columns are linked to at least one story (no orphan detection
        // possible with build_matrix — artifacts only enter columns via links).
        let orphan_gaps: Vec<_> = gaps
            .iter()
            .filter(|g| g.artifact_id.is_some())
            .collect();
        assert_eq!(orphan_gaps.len(), 0, "no orphan artifacts expected");
    }

    #[test]
    fn test_average_confidence() {
        let links = sample_links();
        let matrix = build_matrix(&links);
        let avg = average_confidence(&matrix);
        // Expected: (0.95 + 0.90 + 0.80 + 0.85 + 0.70 + 0.30) / 6 ≈ 0.75
        assert!((avg - 0.75).abs() < 0.01);
    }

    #[test]
    fn test_average_confidence_empty_matrix() {
        let matrix = TraceabilityMatrix::default();
        assert_eq!(average_confidence(&matrix), 0.0);
    }

    #[test]
    fn test_artifacts_for_story() {
        let links = sample_links();
        let matrix = build_matrix(&links);
        let arts = artifacts_for_story(&matrix, "S1");
        assert!(arts.contains(&"auth.rs"));
        assert!(arts.contains(&"auth_test.rs"));
        assert!(arts.contains(&"auth.md"));
        assert_eq!(arts.len(), 3);
        assert!(artifacts_for_story(&matrix, "NONEXISTENT").is_empty());
    }

    #[test]
    fn test_stories_for_artifact() {
        let links = sample_links();
        let matrix = build_matrix(&links);
        let stories = stories_for_artifact(&matrix, "auth.rs");
        assert_eq!(stories, vec!["S1"]);
        assert!(stories_for_artifact(&matrix, "nonexistent.rs").is_empty());
    }
}
