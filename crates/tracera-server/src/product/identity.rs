#![allow(dead_code)]

//! Product identity types — the stable, persistent identifiers and intent
//! model that sit **above** the SWEE evidence graph.
//!
//! These types implement the **Adopt stable identity, revision and portable
//! contract boundary** work package (WP-02) from the product program:
//!
//! - **R01** — Every product must have a stable identifier that survives repo
//!   renames and alias changes.
//! - **R03** — Product baselines are versioned via immutable revision numbers.
//! - **R11** — Intent items (requirements, obligations, capabilities, targets)
//!   are tracked explicitly within each baseline.

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Core identity newtypes
// ---------------------------------------------------------------------------

/// Stable product identifier that survives repo renames and alias changes.
///
/// This is the canonical identity for the entire product graph (R01).
/// The inner `String` is an opaque, URL-safe slug — not a UUID — so it
/// remains human-readable across tools and CLIs.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct ProductId(pub String);

impl ProductId {
    /// Create a new [`ProductId`] with basic validation.
    pub fn new(id: impl Into<String>) -> Self {
        Self(id.into())
    }

    /// Returns the inner string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// A specific accepted baseline revision of the product model.
///
/// Revisions are monotonically increasing and **immutable once accepted**
/// (R03). Observations always reference a specific baseline so that
/// historical results can be compared against the correct contract state.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct BaselineRevision(pub u64);

impl BaselineRevision {
    /// The initial baseline revision.
    pub const ZERO: Self = Self(0);

    /// Returns the inner revision number.
    pub fn number(&self) -> u64 {
        self.0
    }

    /// Returns the next sequential revision.
    pub fn next(&self) -> Self {
        Self(self.0 + 1)
    }
}

// ---------------------------------------------------------------------------
// Intent model
// ---------------------------------------------------------------------------

/// The category of an accepted intent item (R11).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum IntentKind {
    /// Something the product *must* satisfy.
    Requirement,
    /// Something the product *shall* do (process or policy obligation).
    Obligation,
    /// Something the product *can* do (functional capability).
    Capability,
    /// A measurable target or goal.
    Target,
}

/// Lifecycle status of an intent item within a baseline.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum IntentStatus {
    /// Actively accepted into the baseline.
    Accepted,
    /// Acknowledged but deferred to a future revision.
    Deferred,
    /// No longer relevant; retained for audit trail only.
    Retired,
}

/// A single accepted intent item in the product model (R11).
///
/// Each item belongs to exactly one [`BaselineRevision`] and carries a
/// lifecycle status that tracks its journey from acceptance to retirement.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct AcceptedIntent {
    /// Unique identifier for this intent item (scoped to the product).
    pub id: String,
    /// Category of the intent.
    pub kind: IntentKind,
    /// Short human-readable title.
    pub title: String,
    /// Longer description with rationale and acceptance criteria.
    pub description: String,
    /// Current lifecycle status.
    pub status: IntentStatus,
    /// Baseline this intent was accepted into.
    pub baseline: BaselineRevision,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn product_id_roundtrip() {
        let id = ProductId::new("tracera");
        assert_eq!(id.as_str(), "tracera");
        let serialized = serde_json::to_string(&id).unwrap();
        let deserialized: ProductId = serde_json::from_str(&serialized).unwrap();
        assert_eq!(id, deserialized);
    }

    #[test]
    fn baseline_revision_ordering() {
        let r1 = BaselineRevision(1);
        let r2 = BaselineRevision(2);
        assert!(r1 < r2);
        assert_eq!(r1.next(), r2);
    }

    #[test]
    fn baseline_revision_zero() {
        assert_eq!(BaselineRevision::ZERO, BaselineRevision(0));
    }

    #[test]
    fn accepted_intent_construction() {
        let intent = AcceptedIntent {
            id: "R-001".to_string(),
            kind: IntentKind::Requirement,
            title: "Stable identity".to_string(),
            description: "Products must have a stable ID.".to_string(),
            status: IntentStatus::Accepted,
            baseline: BaselineRevision(1),
        };
        assert_eq!(intent.kind, IntentKind::Requirement);
        assert_eq!(intent.status, IntentStatus::Accepted);
        assert_eq!(intent.baseline, BaselineRevision(1));
    }

    #[test]
    fn intent_kind_serialize() {
        let kinds = vec![
            IntentKind::Requirement,
            IntentKind::Obligation,
            IntentKind::Capability,
            IntentKind::Target,
        ];
        for kind in &kinds {
            let json = serde_json::to_string(kind).unwrap();
            let roundtrip: IntentKind = serde_json::from_str(&json).unwrap();
            assert_eq!(*kind, roundtrip);
        }
    }

    #[test]
    fn intent_status_serialize() {
        let statuses = vec![
            IntentStatus::Accepted,
            IntentStatus::Deferred,
            IntentStatus::Retired,
        ];
        for status in &statuses {
            let json = serde_json::to_string(status).unwrap();
            let roundtrip: IntentStatus = serde_json::from_str(&json).unwrap();
            assert_eq!(*status, roundtrip);
        }
    }
}
