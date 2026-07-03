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
}
