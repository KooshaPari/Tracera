//! Tracera spec 008 P1+P2: phenodag fleet-queue absorption.
//!
//! Ports the full phenodag v0.3.0 (Go) surface into Tracera's Rust core.
//! See docs/specs/008-phenodag-absorption.md.

// The queue API is an opt-in absorption surface. Until HTTP/service wiring
// consumes every port, keep the implementation compilable under
// `--all-features` without turning intentionally dormant exports into errors.
#![allow(dead_code, unused_imports)]

pub mod beads_compat;
pub mod claim;
pub mod dedup;
pub mod export;
pub mod heartbeat;
pub mod init;
pub mod lifecycle;
pub mod scanner;
pub mod sqlite_init;
pub mod status;

pub use beads_compat::{bd_call, BeadsError};
pub use claim::{atomic_claim, ClaimError};
pub use dedup::{find_dupes, levenshtein, similarity, DedupError, DupGroup};
pub use export::{to_json, AgentSnapshot, QueueSnapshot, TaskSnapshot};
pub use heartbeat::{reclaim_stale, record_heartbeat, AgentHeartbeat, HeartbeatError};
pub use init::{init_queue, seed_default_agent, InitError, DEFAULT_AGENT};
pub use lifecycle::{complete_task, fail_task, release_task, LifecycleError};
pub use scanner::{scan_dir, ScanEntry, ScanError};
pub use sqlite_init::{open_with_wal, run_migrations, SqliteInitError};
pub use status::{StatusError, StatusReport};
