//! Tracera events/analytics crate.
//!
//! ClickHouse-backed ingest and analytics for the five primary event
//! streams that drive Tracera's observability layer:
//!
//! | Table        | What it stores                                              |
//! |--------------|------------------------------------------------------------|
//! | `agent_runs` | One row per agent execution (start/end, status, agent id) |
//! | `decisions`  | Decisions made during an agent run (trace links)          |
//! | `deploys`    | Deploy events for each release / environment              |
//! | `traces`     | Distributed-trace spans (OpenTelemetry-style)             |
//! | `llm_calls`  | LLM prompts / completions (token counts, latency)          |
//!
//! The crate is split into three pieces:
//!
//! 1. [`records`] — serde-friendly row structs that map 1:1 to ClickHouse.
//! 2. [`config`]   — connection config (URL, database, credentials).
//! 3. [`clickhouse`] — thin [`ClickHouseClient`] wrapper that exposes
//!    both ingest (`insert_*`) and analytics (`agent_*`, `deploy_*`)
//!    query helpers.
//!
//! The binary `events-ingest` (`src/bin/events-ingest.rs`) is a small CLI
//! that reads NDJSON event files from disk and forwards each one into the
//! matching table.

#![deny(unsafe_code)]
#![warn(missing_debug_implementations)]
#![warn(missing_docs)]

pub mod clickhouse;
pub mod config;
pub mod records;

pub mod error;

#[cfg(test)]
mod tests;

pub use clickhouse::{
    AnalyticsClient, AnalyticsSummary, AnalyticsSummaryRow, ClickHouseClient,
};
pub use config::{ClickHouseConfig, Credentials};
pub use error::{Error, Result};
pub use records::{
    AgentRun, AgentRunStatus, Decision, Deploy, DeployEnvironment, Event, LlmCall, TraceSpan,
};