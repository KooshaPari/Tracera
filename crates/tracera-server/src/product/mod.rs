//! Product identity, baseline, and observation types (WP-02).
//!
//! This module introduces the stable identity layer that sits **above** the
//! SWEE evidence graph. It provides:
//!
//! - **Identity** (`identity`) — stable [`ProductId`], [`BaselineRevision`],
//!   and the intent model (requirements, obligations, capabilities, targets).
//! - **Baseline** (`baseline`) — versioned baseline snapshots and the
//!   proposal workflow for changing them.
//! - **Observation** (`observation`) — measurements and findings anchored to
//!   a specific product baseline.
//!
//! These types are the foundation for WP-07 (Observation ingestion pipeline)
//! and WP-08 (Graph sync bridge).

pub mod baseline;
pub mod identity;
pub mod observation;

pub use baseline::{BaselineDelta, BaselineProposal, ProductBaseline, ProposalStatus};
pub use identity::{AcceptedIntent, BaselineRevision, IntentKind, IntentStatus, ProductId};
pub use observation::{Observation, ObservationKind, ObservationResult, ObservationSource};
