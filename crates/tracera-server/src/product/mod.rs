//! Product identity, baseline, observation, assessment, and detection (WP-02..11).
//!
//! This module introduces the stable identity and assessment layer that sits
//! **above** the SWEE evidence graph. It provides:
//!
//! - **Identity** (`identity`) — stable [`ProductId`], [`BaselineRevision`],
//!   and the intent model (requirements, obligations, capabilities, targets).
//! - **Baseline** (`baseline`) — versioned baseline snapshots and the
//!   proposal workflow for changing them.
//! - **Observation** (`observation`) — measurements and findings anchored to
//!   a specific product baseline.
//! - **Traversal** (`traversal`) — bounded graph traversal with cycle detection.
//! - **Queries** (`queries`) — product views, invalidation index, and search.
//! - **Ingest** (`ingest`) — observation ingestion with idempotency.
//! - **Assessment** (`assessment`) — deterministic product health assessment.
//! - **Detectors** (`detectors`) — freshness, coverage, and contradiction detectors.

pub mod assessment;
pub mod baseline;
pub mod detectors;
pub mod identity;
pub mod ingest;
pub mod observation;
pub mod queries;
pub mod traversal;

pub use assessment::{
    AssessmentEngine, AssessmentFinding, AssessmentResult, AssessmentStatus, FindingSeverity,
};
pub use baseline::{BaselineDelta, BaselineProposal, ProductBaseline, ProposalStatus};
pub use detectors::{
    DetectorFinding, DetectorResult, DetectorVersion, FindingKind,
    FindingSeverity as DetectorSeverity, FreshnessDetector, ProductDetectorSuite,
};
pub use identity::{AcceptedIntent, BaselineRevision, IntentKind, IntentStatus, ProductId};
pub use ingest::{IngestResult, ObservationIngestRequest, ObservationStore};
pub use observation::{Observation, ObservationKind, ObservationResult, ObservationSource};
pub use queries::{
    build_invalidation_index, build_product_view, compute_product_stats, query_intents,
    InvalidationIndex, ProductQuery, ProductStats, ProductView, DEFAULT_QUERY_LIMIT,
    MAX_QUERY_LIMIT,
};
pub use traversal::{
    build_adjacency, GraphTraversal, TraversalBudget, TraversalNode, TraversalResult,
};
