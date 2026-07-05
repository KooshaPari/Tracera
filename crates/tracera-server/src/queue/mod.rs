//! Tracera spec 008 P1: phenodag fleet-queue absorption.
//!
//! Ports the atomic claim, heartbeat/reclaim, and lifecycle (release/done/fail)
//! operations from phenodag v0.3.0 (Go) into Tracera's Rust core.
//!
//! Source: github.com/KooshaPari/phenodag/blob/main/phenodag.go
//! Spec: docs/specs/008-phenodag-absorption.md (P1)
//!
//! The schema (tasks, agents, claims) is owned by this module's callers; the
//! functions assume the minimal columns used by phenodag. See
//! `crates/tracera-server/migrations/` for the corresponding migration that
//! creates the tables.

pub mod claim;
pub mod heartbeat;
pub mod lifecycle;

pub use claim::{atomic_claim, ClaimError};
pub use heartbeat::{record_heartbeat, reclaim_stale, AgentHeartbeat, HeartbeatError};
pub use lifecycle::{complete_task, fail_task, release_task, LifecycleError};
