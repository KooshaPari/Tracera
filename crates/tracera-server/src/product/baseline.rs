#![allow(dead_code)]

//! Baseline and versioning types for the product model.
//!
//! A **baseline** is an accepted snapshot of the product's intent contract.
//! Changes to the baseline go through a proposal workflow so that every
//! mutation is traceable and auditable.
//!
//! Part of WP-02 (Adopt stable identity, revision and portable contract
//! boundary) — specifically:
//!
//! - **R03** — Baselines are versioned via immutable revision numbers.
//! - **R06** — Baseline changes require explicit acceptance.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use super::identity::{AcceptedIntent, BaselineRevision, ProductId};

// ---------------------------------------------------------------------------
// Baseline
// ---------------------------------------------------------------------------

/// The current accepted baseline for a product (R03).
///
/// A baseline is an immutable snapshot of the product's accepted intent
/// contract at a specific point in time. It records the revision number,
/// the time of acceptance, and summary metadata used for quick lookups
/// without deserializing the full intent list.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProductBaseline {
    /// Which product this baseline belongs to.
    pub product_id: ProductId,
    /// Monotonically increasing revision number.
    pub revision: BaselineRevision,
    /// UTC timestamp when this baseline was accepted.
    pub accepted_at: DateTime<Utc>,
    /// Number of intent items in this baseline.
    pub intent_count: u32,
    /// Observation epoch — incremented when observations are re-baselined.
    pub observation_epoch: u64,
}

// ---------------------------------------------------------------------------
// Proposal workflow
// ---------------------------------------------------------------------------

/// Lifecycle status of a baseline proposal (R06).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ProposalStatus {
    /// Being drafted; not yet submitted for review.
    Draft,
    /// Submitted for review and acceptance.
    Submitted,
    /// Accepted and applied — a new [`ProductBaseline`] has been created.
    Accepted,
    /// Rejected; no baseline change occurs.
    Rejected,
}

/// A single atomic change to the baseline intent set.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BaselineDelta {
    /// Add a new intent item to the baseline.
    AddIntent(AcceptedIntent),
    /// Modify an existing intent item (matched by `AcceptedIntent::id`).
    ModifyIntent {
        /// ID of the intent to modify.
        id: String,
        /// Updated intent data.
        updated: AcceptedIntent,
    },
    /// Retire an intent item (sets status to [`IntentStatus::Retired`](super::identity::IntentStatus::Retired)).
    RetireIntent {
        /// ID of the intent to retire.
        id: String,
    },
}

/// A proposal to change the baseline (R06).
///
/// Proposals encapsulate one or more [`BaselineDelta`]s and travel through
/// the `Draft → Submitted → Accepted|Rejected` lifecycle. Only accepted
/// proposals result in a new [`ProductBaseline`] revision.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BaselineProposal {
    /// Identity of the person or agent that created this proposal.
    pub proposed_by: String,
    /// The baseline revision this proposal is based on.
    pub base_revision: BaselineRevision,
    /// Ordered list of changes to apply.
    pub deltas: Vec<BaselineDelta>,
    /// Current lifecycle status.
    pub status: ProposalStatus,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::identity::{IntentKind, IntentStatus};

    fn sample_baseline() -> ProductBaseline {
        ProductBaseline {
            product_id: ProductId::new("tracera"),
            revision: BaselineRevision(1),
            accepted_at: chrono::DateTime::parse_from_rfc3339("2026-09-17T00:00:00Z")
                .unwrap()
                .to_utc(),
            intent_count: 3,
            observation_epoch: 0,
        }
    }

    fn sample_intent(id: &str) -> AcceptedIntent {
        AcceptedIntent {
            id: id.to_string(),
            kind: IntentKind::Requirement,
            title: format!("Intent {id}"),
            description: "Description".to_string(),
            status: IntentStatus::Accepted,
            baseline: BaselineRevision(1),
        }
    }

    #[test]
    fn baseline_construction() {
        let b = sample_baseline();
        assert_eq!(b.product_id.as_str(), "tracera");
        assert_eq!(b.revision, BaselineRevision(1));
        assert_eq!(b.intent_count, 3);
    }

    #[test]
    fn baseline_serialization_roundtrip() {
        let b = sample_baseline();
        let json = serde_json::to_string(&b).unwrap();
        let roundtrip: ProductBaseline = serde_json::from_str(&json).unwrap();
        assert_eq!(roundtrip.revision, b.revision);
        assert_eq!(roundtrip.intent_count, b.intent_count);
    }

    #[test]
    fn proposal_draft_construction() {
        let proposal = BaselineProposal {
            proposed_by: "agent-1".to_string(),
            base_revision: BaselineRevision(1),
            deltas: vec![
                BaselineDelta::AddIntent(sample_intent("R-010")),
                BaselineDelta::RetireIntent {
                    id: "R-005".to_string(),
                },
            ],
            status: ProposalStatus::Draft,
        };
        assert_eq!(proposal.deltas.len(), 2);
        assert_eq!(proposal.status, ProposalStatus::Draft);
    }

    #[test]
    fn proposal_status_serialize() {
        let statuses = vec![
            ProposalStatus::Draft,
            ProposalStatus::Submitted,
            ProposalStatus::Accepted,
            ProposalStatus::Rejected,
        ];
        for status in &statuses {
            let json = serde_json::to_string(status).unwrap();
            let roundtrip: ProposalStatus = serde_json::from_str(&json).unwrap();
            assert_eq!(*status, roundtrip);
        }
    }

    #[test]
    fn delta_variant_construction() {
        let add = BaselineDelta::AddIntent(sample_intent("R-001"));
        let modify = BaselineDelta::ModifyIntent {
            id: "R-001".to_string(),
            updated: sample_intent("R-001"),
        };
        let retire = BaselineDelta::RetireIntent {
            id: "R-001".to_string(),
        };

        // Ensure they serialize without panicking
        let _ = serde_json::to_string(&add).unwrap();
        let _ = serde_json::to_string(&modify).unwrap();
        let _ = serde_json::to_string(&retire).unwrap();
    }
}
