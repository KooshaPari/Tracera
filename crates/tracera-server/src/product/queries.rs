#![allow(dead_code)]

//! Bounded product queries, views, and invalidation tracking (WP-08).
//!
//! This module provides the read-side query types and in-memory evaluation
//! functions for the product graph.  All queries are **bounded** — they
//! enforce a maximum result count to keep API responses predictable and
//! prevent unbounded scans over large intent sets.
//!
//! Part of WP-08 (Bounded product queries and views):
//!
//! - **R12** — Product graph queries must be bounded and paginated.
//! - **R13** — Read models (views) provide a denormalized snapshot for
//!   efficient rendering without deserializing the full intent graph.
//! - **R14** — An invalidation index tracks when cached views become stale.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use super::identity::{AcceptedIntent, BaselineRevision, IntentKind, IntentStatus};
use super::observation::Observation;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// Default maximum number of results per query page.
pub const DEFAULT_QUERY_LIMIT: usize = 100;

/// Hard upper bound on query limit — callers cannot request more than this.
pub const MAX_QUERY_LIMIT: usize = 500;

// ---------------------------------------------------------------------------
// ProductQuery — structured query for the product graph
// ---------------------------------------------------------------------------

/// Structured query parameters for the product graph.
///
/// All filter fields are optional.  When `None`, no filter is applied for that
/// dimension.  `limit` and `offset` control bounded pagination.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProductQuery {
    /// Filter to a specific product ID.
    pub product_id: Option<String>,
    /// Filter by intent kind: `"capability"`, `"obligation"`, `"target"`, or
    /// `"requirement"`.
    pub intent_kind: Option<String>,
    /// Filter by intent status: `"accepted"`, `"deferred"`, or `"retired"`.
    pub status: Option<String>,
    /// Filter to intents accepted at or after this baseline revision.
    pub baseline: Option<u64>,
    /// Maximum number of results (bounded, clamped to [`MAX_QUERY_LIMIT`]).
    pub limit: usize,
    /// Number of results to skip.
    pub offset: usize,
}

impl Default for ProductQuery {
    fn default() -> Self {
        Self {
            product_id: None,
            intent_kind: None,
            status: None,
            baseline: None,
            limit: DEFAULT_QUERY_LIMIT,
            offset: 0,
        }
    }
}

impl ProductQuery {
    /// Returns a validated copy with `limit` clamped to [`MAX_QUERY_LIMIT`].
    pub fn validated(mut self) -> Self {
        if self.limit > MAX_QUERY_LIMIT {
            self.limit = MAX_QUERY_LIMIT;
        }
        self
    }
}

// ---------------------------------------------------------------------------
// ProductView — read model for a product node
// ---------------------------------------------------------------------------

/// Denormalized read model for a single product node.
///
/// Built by [`build_product_view`] from a slice of intents and observations.
/// The `children_count` and `observations_count` fields let the API return
/// summary information without the caller needing to perform separate
/// aggregation queries.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ProductView {
    /// Stable product identifier.
    pub id: String,
    /// Product ID (same as `id` for the top-level node).
    pub product_id: String,
    /// Primary kind label (e.g. `"capability"`, `"requirement"`).
    pub kind: String,
    /// Short human-readable title.
    pub title: String,
    /// Longer description.
    pub description: String,
    /// Lifecycle status as a string.
    pub status: String,
    /// Baseline revision this view reflects.
    pub baseline_revision: u64,
    /// Number of child intents (capabilities, obligations, targets).
    pub children_count: usize,
    /// Number of observations referencing this product.
    pub observations_count: usize,
}

// ---------------------------------------------------------------------------
// ProductStats — aggregate statistics
// ---------------------------------------------------------------------------

/// Aggregate statistics for a product across all tracked intents and
/// observations.
///
/// Built by [`compute_product_stats`].
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ProductStats {
    /// The product these stats belong to.
    pub product_id: String,
    /// Count of intents with kind [`IntentKind::Capability`].
    pub total_capabilities: usize,
    /// Count of intents with kind [`IntentKind::Obligation`].
    pub total_obligations: usize,
    /// Count of intents with kind [`IntentKind::Target`].
    pub total_targets: usize,
    /// Count of intents with status [`IntentStatus::Accepted`].
    pub accepted_count: usize,
    /// Count of intents with status [`IntentStatus::Deferred`].
    pub deferred_count: usize,
    /// Count of intents with status [`IntentStatus::Retired`].
    pub retired_count: usize,
    /// The latest observation epoch across all observations for this product.
    pub observation_epoch: u64,
}

// ---------------------------------------------------------------------------
// InvalidationIndex — staleness tracking
// ---------------------------------------------------------------------------

/// Tracks when cached product views become stale.
///
/// Clients consult this index to decide whether to re-fetch product data.
/// A capability is considered stale when its most recent observation is older
/// than the most recent baseline change.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InvalidationIndex {
    /// Timestamp of the most recent baseline change for this product.
    pub last_baseline_change: DateTime<Utc>,
    /// Timestamp of the most recent observation for this product.
    pub last_observation: DateTime<Utc>,
    /// IDs of capabilities whose latest observation predates the last
    /// baseline change (i.e. they are stale).
    pub stale_capabilities: Vec<String>,
}

impl InvalidationIndex {
    /// Returns `true` if the given capability ID is in the stale list.
    pub fn is_stale(&self, capability_id: &str) -> bool {
        self.stale_capabilities.iter().any(|id| id == capability_id)
    }
}

// ---------------------------------------------------------------------------
// In-memory query functions
// ---------------------------------------------------------------------------

/// Parse a string into an [`IntentKind`].
fn parse_intent_kind(s: &str) -> Option<IntentKind> {
    match s {
        "requirement" => Some(IntentKind::Requirement),
        "obligation" => Some(IntentKind::Obligation),
        "capability" => Some(IntentKind::Capability),
        "target" => Some(IntentKind::Target),
        _ => None,
    }
}

/// Parse a string into an [`IntentStatus`].
fn parse_intent_status(s: &str) -> Option<IntentStatus> {
    match s {
        "accepted" => Some(IntentStatus::Accepted),
        "deferred" => Some(IntentStatus::Deferred),
        "retired" => Some(IntentStatus::Retired),
        _ => None,
    }
}

/// Execute a [`ProductQuery`] against an in-memory list of intents.
///
/// Returns a bounded, paginated slice of matching intents.
pub fn query_intents<'a>(
    intents: &'a [AcceptedIntent],
    query: &ProductQuery,
) -> Vec<&'a AcceptedIntent> {
    let limit = query.limit.min(MAX_QUERY_LIMIT);
    let wanted_kind = query.intent_kind.as_deref().and_then(parse_intent_kind);
    let wanted_status = query.status.as_deref().and_then(parse_intent_status);
    let wanted_baseline = query.baseline.map(BaselineRevision);

    intents
        .iter()
        .filter(|i| {
            if let Some(ref kind) = wanted_kind {
                if i.kind != *kind {
                    return false;
                }
            }
            if let Some(ref status) = wanted_status {
                if i.status != *status {
                    return false;
                }
            }
            if let Some(rev) = wanted_baseline {
                if i.baseline < rev {
                    return false;
                }
            }
            true
        })
        .skip(query.offset)
        .take(limit)
        .collect()
}

/// Build a [`ProductView`] from a product ID and its associated intents and
/// observations.
///
/// The view aggregates children and observation counts without deserializing
/// the full graph.
pub fn build_product_view(
    product_id: &str,
    intents: &[AcceptedIntent],
    observations: &[Observation],
    baseline: BaselineRevision,
) -> ProductView {
    let children_count = intents.iter().filter(|i| i.baseline == baseline).count();
    let observations_count = observations
        .iter()
        .filter(|o| o.product_id.as_str() == product_id && o.baseline == baseline)
        .count();

    // Use the first matching intent as the representative node, or provide a
    // sensible default when the product has no intents yet.
    let (kind, title, description, status) =
        if let Some(first) = intents.iter().find(|i| i.baseline == baseline) {
            (
                intent_kind_label(&first.kind),
                first.title.clone(),
                first.description.clone(),
                intent_status_label(&first.status),
            )
        } else {
            (
                "unknown".to_string(),
                product_id.to_string(),
                String::new(),
                "pending".to_string(),
            )
        };

    ProductView {
        id: product_id.to_string(),
        product_id: product_id.to_string(),
        kind,
        title,
        description,
        status,
        baseline_revision: baseline.number(),
        children_count,
        observations_count,
    }
}

/// Compute aggregate [`ProductStats`] for a product across its intents and
/// observations.
pub fn compute_product_stats(
    product_id: &str,
    intents: &[AcceptedIntent],
    observations: &[Observation],
) -> ProductStats {
    let total_capabilities = intents
        .iter()
        .filter(|i| i.kind == IntentKind::Capability)
        .count();
    let total_obligations = intents
        .iter()
        .filter(|i| i.kind == IntentKind::Obligation)
        .count();
    let total_targets = intents
        .iter()
        .filter(|i| i.kind == IntentKind::Target)
        .count();
    let accepted_count = intents
        .iter()
        .filter(|i| i.status == IntentStatus::Accepted)
        .count();
    let deferred_count = intents
        .iter()
        .filter(|i| i.status == IntentStatus::Deferred)
        .count();
    let retired_count = intents
        .iter()
        .filter(|i| i.status == IntentStatus::Retired)
        .count();

    let observation_epoch = observations
        .iter()
        .map(|o| o.recorded_at.timestamp() as u64)
        .max()
        .unwrap_or(0);

    ProductStats {
        product_id: product_id.to_string(),
        total_capabilities,
        total_obligations,
        total_targets,
        accepted_count,
        deferred_count,
        retired_count,
        observation_epoch,
    }
}

/// Build an [`InvalidationIndex`] from intents and observations.
///
/// A capability is flagged as stale when its latest observation predates the
/// most recent baseline change.
pub fn build_invalidation_index(
    intents: &[AcceptedIntent],
    observations: &[Observation],
) -> InvalidationIndex {
    let last_baseline_change = intents
        .iter()
        .map(|i| i.baseline.0)
        .max()
        .map(|rev| {
            // Synthesize a timestamp from the revision number; in production
            // this would come from the baseline record itself.
            DateTime::from_timestamp(rev as i64, 0).unwrap_or_default()
        })
        .unwrap_or_else(Utc::now);

    let last_observation = observations
        .iter()
        .map(|o| o.recorded_at)
        .max()
        .unwrap_or_else(Utc::now);

    // Find capability intents whose latest observation is older than the last
    // baseline change.
    let mut stale_capabilities = Vec::new();
    for intent in intents.iter().filter(|i| i.kind == IntentKind::Capability) {
        let latest_obs = observations
            .iter()
            .filter(|o| o.product_id.as_str() == intent.id)
            .map(|o| o.recorded_at)
            .max();
        if let Some(latest) = latest_obs {
            if latest < last_baseline_change {
                stale_capabilities.push(intent.id.clone());
            }
        } else {
            // No observations at all for this capability — also stale.
            stale_capabilities.push(intent.id.clone());
        }
    }
    stale_capabilities.sort();

    InvalidationIndex {
        last_baseline_change,
        last_observation,
        stale_capabilities,
    }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn intent_kind_label(kind: &IntentKind) -> String {
    match kind {
        IntentKind::Requirement => "requirement".to_string(),
        IntentKind::Obligation => "obligation".to_string(),
        IntentKind::Capability => "capability".to_string(),
        IntentKind::Target => "target".to_string(),
    }
}

fn intent_status_label(status: &IntentStatus) -> String {
    match status {
        IntentStatus::Accepted => "accepted".to_string(),
        IntentStatus::Deferred => "deferred".to_string(),
        IntentStatus::Retired => "retired".to_string(),
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::identity::{BaselineRevision, ProductId};
    use crate::product::observation::{ObservationKind, ObservationResult, ObservationSource};

    // ----- helpers -----

    fn ts(secs: i64) -> DateTime<Utc> {
        DateTime::from_timestamp(secs, 0).unwrap()
    }

    fn sample_intents() -> Vec<AcceptedIntent> {
        vec![
            AcceptedIntent {
                id: "cap-1".to_string(),
                kind: IntentKind::Capability,
                title: "Data ingestion".to_string(),
                description: "Ingest data from external sources.".to_string(),
                status: IntentStatus::Accepted,
                baseline: BaselineRevision(1),
            },
            AcceptedIntent {
                id: "cap-2".to_string(),
                kind: IntentKind::Capability,
                title: "Data export".to_string(),
                description: "Export data to downstream systems.".to_string(),
                status: IntentStatus::Deferred,
                baseline: BaselineRevision(2),
            },
            AcceptedIntent {
                id: "obl-1".to_string(),
                kind: IntentKind::Obligation,
                title: "Audit logging".to_string(),
                description: "All mutations must be audit-logged.".to_string(),
                status: IntentStatus::Accepted,
                baseline: BaselineRevision(1),
            },
            AcceptedIntent {
                id: "tgt-1".to_string(),
                kind: IntentKind::Target,
                title: "p99 latency < 200ms".to_string(),
                description: "Target p99 query latency.".to_string(),
                status: IntentStatus::Retired,
                baseline: BaselineRevision(3),
            },
            AcceptedIntent {
                id: "req-1".to_string(),
                kind: IntentKind::Requirement,
                title: "Stable product ID".to_string(),
                description: "Products must have a stable identifier.".to_string(),
                status: IntentStatus::Accepted,
                baseline: BaselineRevision(1),
            },
        ]
    }

    fn sample_observations() -> Vec<Observation> {
        vec![
            Observation {
                id: "obs-1".to_string(),
                product_id: ProductId::new("cap-1"),
                baseline: BaselineRevision(1),
                kind: ObservationKind::TestResult,
                result: ObservationResult::Passed,
                source: ObservationSource {
                    collector: "cargo-test".to_string(),
                    version: "0.1.0".to_string(),
                    artifact_ref: None,
                },
                recorded_at: ts(1000),
                capability_id: None,
            },
            Observation {
                id: "obs-2".to_string(),
                product_id: ProductId::new("cap-1"),
                baseline: BaselineRevision(1),
                kind: ObservationKind::Measurement,
                result: ObservationResult::Passed,
                source: ObservationSource {
                    collector: "bench".to_string(),
                    version: "0.2.0".to_string(),
                    artifact_ref: None,
                },
                recorded_at: ts(2000),
                capability_id: None,
            },
        ]
    }

    // ----- ProductQuery tests -----

    #[test]
    fn query_defaults_are_bounded() {
        let q = ProductQuery::default();
        assert_eq!(q.limit, DEFAULT_QUERY_LIMIT);
        assert_eq!(q.offset, 0);
        assert!(q.product_id.is_none());
        assert!(q.intent_kind.is_none());
        assert!(q.status.is_none());
        assert!(q.baseline.is_none());
    }

    #[test]
    fn query_limit_clamped_to_max() {
        let q = ProductQuery {
            limit: 9999,
            ..Default::default()
        }
        .validated();
        assert_eq!(q.limit, MAX_QUERY_LIMIT);
    }

    #[test]
    fn query_filter_by_intent_kind() {
        let intents = sample_intents();
        let q = ProductQuery {
            intent_kind: Some("capability".to_string()),
            limit: 10,
            ..Default::default()
        };
        let results = query_intents(&intents, &q);
        assert_eq!(results.len(), 2);
        assert!(results.iter().all(|i| i.kind == IntentKind::Capability));
    }

    #[test]
    fn query_filter_by_status() {
        let intents = sample_intents();
        let q = ProductQuery {
            status: Some("accepted".to_string()),
            limit: 10,
            ..Default::default()
        };
        let results = query_intents(&intents, &q);
        assert_eq!(results.len(), 3);
        assert!(results.iter().all(|i| i.status == IntentStatus::Accepted));
    }

    #[test]
    fn query_filter_by_baseline() {
        let intents = sample_intents();
        let q = ProductQuery {
            baseline: Some(2),
            limit: 10,
            ..Default::default()
        };
        let results = query_intents(&intents, &q);
        // cap-2 (rev 2), tgt-1 (rev 3) — cap-2 and tgt-1
        assert_eq!(results.len(), 2);
        assert!(results.iter().all(|i| i.baseline >= BaselineRevision(2)));
    }

    #[test]
    fn query_bounded_limit_enforcement() {
        // Create more intents than the limit.
        let mut intents: Vec<AcceptedIntent> = (0..200)
            .map(|i| AcceptedIntent {
                id: format!("item-{i}"),
                kind: IntentKind::Capability,
                title: format!("Item {i}"),
                description: String::new(),
                status: IntentStatus::Accepted,
                baseline: BaselineRevision(1),
            })
            .collect();

        // Add one from rev 2 so baseline filter has something.
        intents.push(AcceptedIntent {
            id: "item-extra".to_string(),
            kind: IntentKind::Obligation,
            title: "Extra".to_string(),
            description: String::new(),
            status: IntentStatus::Accepted,
            baseline: BaselineRevision(2),
        });

        let q = ProductQuery {
            limit: 10,
            ..Default::default()
        };
        let results = query_intents(&intents, &q);
        assert_eq!(results.len(), 10);

        // With offset we can page through.
        let q_page2 = ProductQuery {
            limit: 10,
            offset: 10,
            ..Default::default()
        };
        let results2 = query_intents(&intents, &q_page2);
        assert_eq!(results2.len(), 10);
        assert_ne!(results[0].id, results2[0].id);
    }

    #[test]
    fn query_combined_filters() {
        let intents = sample_intents();
        let q = ProductQuery {
            intent_kind: Some("capability".to_string()),
            status: Some("accepted".to_string()),
            limit: 10,
            ..Default::default()
        };
        let results = query_intents(&intents, &q);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].id, "cap-1");
    }

    // ----- ProductView tests -----

    #[test]
    fn build_product_view_basic() {
        let intents = sample_intents();
        let observations = sample_observations();
        let view = build_product_view("cap-1", &intents, &observations, BaselineRevision(1));

        assert_eq!(view.product_id, "cap-1");
        assert_eq!(view.kind, "capability");
        assert_eq!(view.baseline_revision, 1);
        assert_eq!(view.observations_count, 2);
        // cap-1 and obl-1 at rev 1
        assert!(view.children_count >= 1);
    }

    #[test]
    fn build_product_view_no_intents() {
        let view = build_product_view("empty-product", &[], &[], BaselineRevision(0));
        assert_eq!(view.kind, "unknown");
        assert_eq!(view.status, "pending");
        assert_eq!(view.children_count, 0);
        assert_eq!(view.observations_count, 0);
    }

    // ----- ProductStats tests -----

    #[test]
    fn compute_product_stats_counts() {
        let intents = sample_intents();
        let observations = sample_observations();
        let stats = compute_product_stats("tracera", &intents, &observations);

        assert_eq!(stats.total_capabilities, 2); // cap-1, cap-2
        assert_eq!(stats.total_obligations, 1); // obl-1
        assert_eq!(stats.total_targets, 1); // tgt-1
        assert_eq!(stats.accepted_count, 3); // cap-1, obl-1, req-1
        assert_eq!(stats.deferred_count, 1); // cap-2
        assert_eq!(stats.retired_count, 1); // tgt-1
        assert!(stats.observation_epoch > 0);
    }

    #[test]
    fn compute_product_stats_empty() {
        let stats = compute_product_stats("empty", &[], &[]);
        assert_eq!(stats.total_capabilities, 0);
        assert_eq!(stats.total_obligations, 0);
        assert_eq!(stats.total_targets, 0);
        assert_eq!(stats.accepted_count, 0);
        assert_eq!(stats.deferred_count, 0);
        assert_eq!(stats.retired_count, 0);
        assert_eq!(stats.observation_epoch, 0);
    }

    // ----- InvalidationIndex tests -----

    #[test]
    fn invalidation_index_staleness_detection() {
        let intents = vec![
            AcceptedIntent {
                id: "cap-old".to_string(),
                kind: IntentKind::Capability,
                title: "Old capability".to_string(),
                description: String::new(),
                status: IntentStatus::Accepted,
                baseline: BaselineRevision(500),
            },
            AcceptedIntent {
                id: "cap-fresh".to_string(),
                kind: IntentKind::Capability,
                title: "Fresh capability".to_string(),
                description: String::new(),
                status: IntentStatus::Accepted,
                baseline: BaselineRevision(500),
            },
        ];

        let observations = vec![
            Observation {
                id: "obs-old".to_string(),
                product_id: ProductId::new("cap-old"),
                baseline: BaselineRevision(500),
                kind: ObservationKind::TestResult,
                result: ObservationResult::Passed,
                source: ObservationSource {
                    collector: "test".to_string(),
                    version: "0.1.0".to_string(),
                    artifact_ref: None,
                },
                // Observed BEFORE the baseline was finalized.
                recorded_at: ts(100),
                capability_id: None,
            },
            Observation {
                id: "obs-fresh".to_string(),
                product_id: ProductId::new("cap-fresh"),
                baseline: BaselineRevision(500),
                kind: ObservationKind::TestResult,
                result: ObservationResult::Passed,
                source: ObservationSource {
                    collector: "test".to_string(),
                    version: "0.1.0".to_string(),
                    artifact_ref: None,
                },
                // Observed AFTER the baseline was finalized.
                recorded_at: ts(10000),
                capability_id: None,
            },
        ];

        let index = build_invalidation_index(&intents, &observations);
        assert!(index.is_stale("cap-old"));
        assert!(!index.is_stale("cap-fresh"));
        assert_eq!(index.stale_capabilities.len(), 1);
        assert_eq!(index.stale_capabilities[0], "cap-old");
    }

    #[test]
    fn invalidation_index_no_observations_is_stale() {
        let intents = vec![AcceptedIntent {
            id: "cap-never-observed".to_string(),
            kind: IntentKind::Capability,
            title: "Never observed".to_string(),
            description: String::new(),
            status: IntentStatus::Accepted,
            baseline: BaselineRevision(1),
        }];

        let index = build_invalidation_index(&intents, &[]);
        assert!(index.is_stale("cap-never-observed"));
    }

    #[test]
    fn invalidation_index_empty() {
        let index = build_invalidation_index(&[], &[]);
        assert!(index.stale_capabilities.is_empty());
    }

    // ----- Serialization roundtrip tests -----

    #[test]
    fn product_query_roundtrip() {
        let q = ProductQuery {
            product_id: Some("tracera".to_string()),
            intent_kind: Some("capability".to_string()),
            status: Some("accepted".to_string()),
            baseline: Some(3),
            limit: 25,
            offset: 10,
        };
        let json = serde_json::to_string(&q).unwrap();
        let roundtrip: ProductQuery = serde_json::from_str(&json).unwrap();
        assert_eq!(roundtrip.product_id, q.product_id);
        assert_eq!(roundtrip.limit, 25);
    }

    #[test]
    fn product_view_roundtrip() {
        let view = ProductView {
            id: "cap-1".to_string(),
            product_id: "cap-1".to_string(),
            kind: "capability".to_string(),
            title: "Ingest".to_string(),
            description: "Ingest data.".to_string(),
            status: "accepted".to_string(),
            baseline_revision: 1,
            children_count: 3,
            observations_count: 2,
        };
        let json = serde_json::to_string(&view).unwrap();
        let roundtrip: ProductView = serde_json::from_str(&json).unwrap();
        assert_eq!(roundtrip, view);
    }

    #[test]
    fn product_stats_roundtrip() {
        let stats = ProductStats {
            product_id: "tracera".to_string(),
            total_capabilities: 2,
            total_obligations: 1,
            total_targets: 1,
            accepted_count: 3,
            deferred_count: 1,
            retired_count: 1,
            observation_epoch: 42,
        };
        let json = serde_json::to_string(&stats).unwrap();
        let roundtrip: ProductStats = serde_json::from_str(&json).unwrap();
        assert_eq!(roundtrip, stats);
    }

    #[test]
    fn invalidation_index_roundtrip() {
        let idx = InvalidationIndex {
            last_baseline_change: ts(5),
            last_observation: ts(10),
            stale_capabilities: vec!["cap-a".to_string(), "cap-b".to_string()],
        };
        let json = serde_json::to_string(&idx).unwrap();
        let roundtrip: InvalidationIndex = serde_json::from_str(&json).unwrap();
        assert_eq!(roundtrip.stale_capabilities, idx.stale_capabilities);
        assert!(roundtrip.is_stale("cap-a"));
        assert!(!roundtrip.is_stale("cap-c"));
    }
}
