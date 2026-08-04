/// Pluggable storage abstraction for Tracera server.
///
/// Both `PgStore` (Postgres, server/hosted tier) and `SqliteStore`
/// (SQLite, on-device/per-project tier) implement this trait.
/// Handlers hold `Arc<dyn Store + Send + Sync>` and call only this interface.
use chrono::{DateTime, Utc};
use serde_json::Value;
use std::future::Future;
use std::pin::Pin;

// ---------------------------------------------------------------------------
// Shared error type
// ---------------------------------------------------------------------------
#[derive(Debug)]
pub enum StoreError {
    Database(String),
}

impl std::fmt::Display for StoreError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            StoreError::Database(msg) => write!(f, "database error: {msg}"),
        }
    }
}

impl std::error::Error for StoreError {}

impl From<sqlx::Error> for StoreError {
    fn from(e: sqlx::Error) -> Self {
        StoreError::Database(e.to_string())
    }
}

pub type StoreResult<T> = Result<T, StoreError>;

// ---------------------------------------------------------------------------
// Domain types (copied from main.rs — single source of truth here)
// ---------------------------------------------------------------------------
#[derive(Debug, Clone, serde::Serialize)]
pub struct EvidenceItem {
    pub id: String,
    pub artifact_id: String,
    pub kind: String,
    pub url: String,
    pub metadata: Value,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Sprint {
    pub id: String,
    pub name: String,
    pub goal: String,
    pub start_date: DateTime<Utc>,
    pub end_date: DateTime<Utc>,
    pub status: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Story {
    pub id: String,
    pub sprint_id: Option<String>,
    pub title: String,
    pub description: String,
    pub status: String,
    pub story_points: Option<i64>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct TeamRow {
    pub id: String,
    pub name: String,
    pub description: String,
    pub members: Vec<String>,
}

/// A persistent directed trace-link between two artifact IDs.
///
/// Populated by the real ingest pipeline (GitHub / Jira) and also
/// queryable as part of coverage-matrix / impact analysis.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct TraceLink {
    pub id: String,
    pub source_id: String,
    pub target_id: String,
    pub relationship: String,
    pub confidence: f64,
    /// Which ingest source produced this link: "github", "jira", or "manual".
    pub source: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// Verified benchmark-run provenance retained for replay and idempotency.
#[derive(Debug, Clone, serde::Serialize)]
pub struct BenchmarkRun {
    pub run_id: String,
    pub session_id: String,
    pub attempt_id: String,
    pub schema_version: String,
    pub replay_hash: String,
    pub outcome_sha256: String,
    pub key_id: String,
    pub signature_digest: String,
    pub status: String,
    pub metadata: Value,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// ITIL Problem-management domain record.
///
/// Recovered from the Python `src/tracertm/models/problem.py` model
/// (deleted in PR-554, originally authored in commit `2ece64691f`).
/// This is the Rust port — kept to the minimum viable column set that
/// preserves ITIL lifecycle semantics (status / impact / priority / RCA).
/// Full ~30-field Python model (workaround, permanent_fix, KED integration,
/// soft-delete, optimistic-locking version) is staged for follow-up work
/// once the recovery PR proves the schema and round-trip are stable.
///
/// Lifecycle statuses (mirrors `ProblemStatus` in the Python model):
///   open -> in_investigation -> pending_workaround | known_error -> awaiting_fix -> closed
#[derive(Debug, Clone, serde::Serialize)]
pub struct Problem {
    pub id: String,
    pub project_id: String,
    pub problem_number: String,
    pub title: String,
    pub description: Option<String>,
    /// ITIL lifecycle status (snake_case): open | in_investigation | pending_workaround | known_error | awaiting_fix | closed
    pub status: String,
    /// Resolution classification once closed: permanent_fix | workaround_only | cannot_reproduce | deferred | by_design
    pub resolution_type: Option<String>,
    pub category: Option<String>,
    pub sub_category: Option<String>,
    pub tags: Option<Value>,
    pub impact_level: String,
    pub urgency: String,
    pub priority: String,
    pub rca_performed: bool,
    pub root_cause_identified: bool,
    pub workaround_available: bool,
    pub permanent_fix_available: bool,
    pub assigned_to: Option<String>,
    pub assigned_team: Option<String>,
    pub owner: Option<String>,
    pub known_error_id: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    /// Soft-delete tombstone; non-null means the row is tombstoned.
    pub deleted_at: Option<DateTime<Utc>>,
}

// ---------------------------------------------------------------------------
// Store trait
// ---------------------------------------------------------------------------
pub type BoxFuture<'a, T> = Pin<Box<dyn Future<Output = T> + Send + 'a>>;

pub trait Store: Send + Sync {
    // Evidence
    fn list_evidence(&self) -> BoxFuture<'_, StoreResult<Vec<EvidenceItem>>>;
    fn create_evidence(
        &self,
        id: String,
        artifact_id: String,
        kind: String,
        url: String,
        metadata: Value,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<EvidenceItem>>;

    // Sprints
    fn list_sprints(&self) -> BoxFuture<'_, StoreResult<Vec<Sprint>>>;
    fn create_sprint(
        &self,
        id: String,
        name: String,
        goal: String,
        start_date: DateTime<Utc>,
        end_date: DateTime<Utc>,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<Sprint>>;

    // Stories — created by real ingest pipeline
    fn list_stories(&self) -> BoxFuture<'_, StoreResult<Vec<Story>>>;

    /// Create a story record.
    ///
    /// All fields are required for DB correctness; suppression is justified
    /// (clippy::too_many_arguments) because there is no optional field here
    /// and introducing an intermediate struct would add indirection without value.
    #[allow(clippy::too_many_arguments)]
    fn create_story(
        &self,
        id: String,
        sprint_id: Option<String>,
        title: String,
        description: String,
        status: String,
        story_points: Option<i64>,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<Story>>;

    // Trace-links — created by real ingest pipeline

    /// Create a persistent trace-link record.
    ///
    /// Suppressing clippy::too_many_arguments: all 8 parameters map 1-to-1 to
    /// DB columns; a wrapper struct would add indirection without value.
    #[allow(clippy::too_many_arguments)]
    fn create_trace_link(
        &self,
        id: String,
        source_id: String,
        target_id: String,
        relationship: String,
        confidence: f64,
        source: String,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<TraceLink>>;

    // Teams
    fn list_teams(&self) -> BoxFuture<'_, StoreResult<Vec<TeamRow>>>;

    // Metrics
    fn count_evidence(&self) -> BoxFuture<'_, StoreResult<i64>>;

    // Verified benchmark replay provenance.
    fn get_benchmark_run(&self, run_id: String)
        -> BoxFuture<'_, StoreResult<Option<BenchmarkRun>>>;

    /// Insert a benchmark run, or return the existing row when the stable
    /// run/replay identity is submitted again. A conflicting hash is an error.
    #[allow(clippy::too_many_arguments)]
    fn create_benchmark_run(
        &self,
        run_id: String,
        session_id: String,
        attempt_id: String,
        schema_version: String,
        replay_hash: String,
        outcome_sha256: String,
        key_id: String,
        signature_digest: String,
        status: String,
        metadata: Value,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<BenchmarkRun>>;

    // -----------------------------------------------------------------------
    // Problems (ITIL problem-management) — recovered from Python model
    // originally at `src/tracertm/models/problem.py` (commit 2ece64691f).
    // -----------------------------------------------------------------------

    /// List problems for a project, optionally filtering by status.
    ///
    /// `status_filter` of `None` returns all non-tombstoned problems.
    fn list_problems(
        &self,
        project_id: String,
        status_filter: Option<String>,
    ) -> BoxFuture<'_, StoreResult<Vec<Problem>>>;

    /// Persist a new problem record and return it.
    ///
    /// All 19 fields map 1-to-1 to `problems` table columns; a wrapper struct
    /// would add indirection without value at this size.
    #[allow(clippy::too_many_arguments)]
    fn create_problem(
        &self,
        id: String,
        project_id: String,
        problem_number: String,
        title: String,
        description: Option<String>,
        status: String,
        resolution_type: Option<String>,
        category: Option<String>,
        sub_category: Option<String>,
        tags: Option<Value>,
        impact_level: String,
        urgency: String,
        priority: String,
        rca_performed: bool,
        root_cause_identified: bool,
        workaround_available: bool,
        permanent_fix_available: bool,
        assigned_to: Option<String>,
        assigned_team: Option<String>,
        owner: Option<String>,
        known_error_id: Option<String>,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<Problem>>;

    /// Count of problems for a project, scoped to non-tombstoned rows.
    // Kept as part of the store contract for backend parity; production HTTP
    // handlers currently expose problem listings rather than aggregate counts.
    #[allow(dead_code)]
    fn count_problems(&self, project_id: String) -> BoxFuture<'_, StoreResult<i64>>;
}
