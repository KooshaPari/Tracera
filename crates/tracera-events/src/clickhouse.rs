//! ClickHouse client wrapper and analytics query builders.
//!
//! [`ClickHouseClient`] is a thin newtype around [`clickhouse::Client`] that
//! knows the Tracera event-stream table layout. The two halves of the API are:
//!
//! * **Ingest** — `insert_agent_run`, `insert_decision`, `insert_deploy`,
//!   `insert_trace`, `insert_llm_call` (each takes a slice of typed rows and
//!   flushes them into the matching table).
//!
//! * **Analytics queries** — the [`analytics`] submodule exposes SQL builders
//!   that return [`String`] queries you can run via [`ClickHouseClient::query`]
//!   or feed directly into a [`clickhouse::Client::query`]. The returned
//!   structs ([`AnalyticsSummary`]) are typed results that can be deserialised
//!   from those queries.
//!
//! Connection pooling and HTTP transport are inherited from `clickhouse-rs`.
//! Cloning a [`ClickHouseClient`] is cheap and recommended — the underlying
//! `Client` clones share the same connection pool.

use std::time::Duration;

use serde::{Deserialize, Serialize};
use tracing::{debug, instrument};

use crate::config::ClickHouseConfig;
use crate::error::{Error, Result};
use crate::records::{
    AgentRun, Decision, Deploy, Event, LlmCall, TraceSpan,
};

// Re-export the driver error type under a stable alias so that downstream
// crates can match on `tracera_events::clickhouse::error::Error` without
// having to depend on `clickhouse` themselves.
pub use clickhouse::error;

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

/// Thin wrapper around [`clickhouse::Client`] scoped to the Tracera database.
///
/// Cheap to clone — the underlying client shares an HTTP pool.
#[derive(Debug, Clone)]
pub struct ClickHouseClient {
    inner: clickhouse::Client,
    config: ClickHouseConfig,
}

impl ClickHouseClient {
    /// Build a client from explicit configuration.
    pub fn new(config: ClickHouseConfig) -> Self {
        let mut client = clickhouse::Client::default()
            .with_url(&config.url)
            .with_database(&config.database);
        if let Some(user) = &config.credentials.user {
            client = client.with_user(user.clone());
            if let Some(pw) = &config.credentials.password {
                client = client.with_password(pw.clone());
            }
        }
        Self {
            inner: client,
            config,
        }
    }

    /// Build a client from the process environment
    /// (`CLICKHOUSE_URL`, `CLICKHOUSE_DATABASE`, `CLICKHOUSE_USER`,
    /// `CLICKHOUSE_PASSWORD`).
    pub fn from_env() -> Result<Self> {
        Ok(Self::new(ClickHouseConfig::from_env()?))
    }

    /// Borrow the underlying [`clickhouse::Client`].
    pub fn inner(&self) -> &clickhouse::Client {
        &self.inner
    }

    /// Effective database name.
    pub fn database(&self) -> &str {
        &self.config.database
    }

    /// Per-request timeout.
    pub fn timeout(&self) -> Duration {
        self.config.timeout
    }

    // -----------------------------------------------------------------------
    // Generic helpers — exposed for callers that want to run their own SQL.
    // -----------------------------------------------------------------------

    /// Start a typed query against the underlying client.
    pub fn query(&self, sql: &str) -> clickhouse::query::Query {
        self.inner.query(sql)
    }

    // -----------------------------------------------------------------------
    // Typed ingest helpers
    // -----------------------------------------------------------------------

    /// Insert one or more [`AgentRun`] rows into `agent_runs`.
    #[instrument(skip(self, rows), fields(count = rows.len()))]
    pub async fn insert_agent_run(&self, rows: &[AgentRun]) -> Result<()> {
        self.insert_rows("agent_runs", rows).await
    }

    /// Insert one or more [`Decision`] rows into `decisions`.
    #[instrument(skip(self, rows), fields(count = rows.len()))]
    pub async fn insert_decision(&self, rows: &[Decision]) -> Result<()> {
        self.insert_rows("decisions", rows).await
    }

    /// Insert one or more [`Deploy`] rows into `deploys`.
    #[instrument(skip(self, rows), fields(count = rows.len()))]
    pub async fn insert_deploy(&self, rows: &[Deploy]) -> Result<()> {
        self.insert_rows("deploys", rows).await
    }

    /// Insert one or more [`TraceSpan`] rows into `traces`.
    #[instrument(skip(self, rows), fields(count = rows.len()))]
    pub async fn insert_trace(&self, rows: &[TraceSpan]) -> Result<()> {
        self.insert_rows("traces", rows).await
    }

    /// Insert one or more [`LlmCall`] rows into `llm_calls`.
    #[instrument(skip(self, rows), fields(count = rows.len()))]
    pub async fn insert_llm_call(&self, rows: &[LlmCall]) -> Result<()> {
        self.insert_rows("llm_calls", rows).await
    }

    /// Insert rows of any single record type. Dispatches to the matching table
    /// based on the type marker.
    #[instrument(skip(self, event))]
    pub async fn insert_event(&self, event: &Event) -> Result<()> {
        match event {
            Event::AgentRun(row) => self.insert_agent_run(std::slice::from_ref(row)).await,
            Event::Decision(row) => self.insert_decision(std::slice::from_ref(row)).await,
            Event::Deploy(row) => self.insert_deploy(std::slice::from_ref(row)).await,
            Event::Trace(row) => self.insert_trace(std::slice::from_ref(row)).await,
            Event::LlmCall(row) => self.insert_llm_call(std::slice::from_ref(row)).await,
        }
    }

    // -----------------------------------------------------------------------
    // Internals
    // -----------------------------------------------------------------------

    async fn insert_rows<T>(&self, table: &str, rows: &[T]) -> Result<()>
    where
        T: clickhouse::RowOwned + serde::Serialize,
    {
        if rows.is_empty() {
            debug!(table, "skipping insert (empty batch)");
            return Ok(());
        }
        let mut insert: clickhouse::insert::Insert<T> = self.inner.insert(table).await?;
        for row in rows {
            insert.write(row).await?;
        }
        insert.end().await?;
        Ok(())
    }
}

// ---------------------------------------------------------------------------
// Analytics — query builders + typed result rows.
// ---------------------------------------------------------------------------

/// Analytics query helpers.
///
/// All functions in this module are pure SQL builders — they do not perform any
/// network I/O. They return the [`String`] SQL that should be passed to
/// [`ClickHouseClient::query`] or [`clickhouse::Client::query`].
pub mod analytics {
    //! ClickHouse analytics queries over the Tracera event streams.
    //!
    //! Every public function in this module returns a `String` SQL query. The
    //! queries use only standard ClickHouse SQL with `?` and `??` placeholders
    //! handled by the driver, plus named bind parameters where applicable.

    /// Build the standard summary query used by [`super::AnalyticsSummary`].
    ///
    /// Returns one row per stream + status (for `agent_runs`) or per stream
    /// with aggregate counters.
    pub fn summary() -> String {
        // The five CTEs each emit (stream, status, count). They are UNION ALL'd
        // so the result shape is uniform: `stream String, status String, count UInt64`.
        // We surface deploy / decision status from their boolean / enum columns.
        const Q: &str = r#"
SELECT stream,
       status,
       sum(c) AS count
FROM (
    SELECT 'agent_run' AS stream,
           toString(status) AS status,
           count() AS c
      FROM agent_runs
     GROUP BY status
    UNION ALL
    SELECT 'deploy' AS stream,
           if(succeeded, 'succeeded', 'failed') AS status,
           count() AS c
      FROM deploys
     GROUP BY succeeded
    UNION ALL
    SELECT 'decision' AS stream,
           kind AS status,
           count() AS c
      FROM decisions
     GROUP BY kind
    UNION ALL
    SELECT 'llm_call' AS stream,
           if(succeeded, 'succeeded', 'failed') AS status,
           count() AS c
      FROM llm_calls
     GROUP BY succeeded
    UNION ALL
    SELECT 'trace' AS stream,
           status_code AS status,
           count() AS c
      FROM traces
     GROUP BY status_code
)
GROUP BY stream, status
ORDER BY stream ASC, status ASC
"#;
        Q.trim().to_string()
    }

    /// Build a query that returns per-agent success / failure counters from
    /// `agent_runs`. Use [`super::AnalyticsClient::agent_outcomes`] to run.
    pub fn agent_outcomes() -> String {
        r#"
SELECT agent,
       environment,
       countIf(status = 'Succeeded')      AS succeeded,
       countIf(status = 'Failed')         AS failed,
       countIf(status = 'Running')        AS running,
       countIf(status = 'Pending')        AS pending,
       countIf(status = 'Cancelled')      AS cancelled,
       count()                            AS total
  FROM agent_runs
 GROUP BY agent, environment
 ORDER BY total DESC
"#
        .trim()
        .to_string()
    }

    /// Build a query that returns daily LLM token usage for the last `days`
    /// days (defaults to 7 if `None`). Use [`super::AnalyticsClient::llm_daily`].
    pub fn llm_daily(days: Option<u32>) -> String {
        let days = days.unwrap_or(7);
        format!(
            r#"
SELECT toDate(called_at)              AS day,
       provider,
       model,
       sum(prompt_tokens)              AS prompt_tokens,
       sum(completion_tokens)          AS completion_tokens,
       sum(prompt_tokens) + sum(completion_tokens) AS total_tokens,
       countIf(succeeded)              AS succeeded_calls,
       countIf(NOT succeeded)          AS failed_calls,
       avg(latency_ms)                 AS avg_latency_ms
  FROM llm_calls
 WHERE called_at >= now() - INTERVAL {days} DAY
 GROUP BY day, provider, model
 ORDER BY day DESC, total_tokens DESC
"#
        )
    }

    /// Build a query that returns the most recent `n` deploys.
    pub fn recent_deploys(n: u32) -> String {
        format!(
            r#"
SELECT deploy_id,
       component,
       toString(environment) AS environment,
       commit_sha,
       version,
       deployed_at,
       duration_ms,
       succeeded
  FROM deploys
 ORDER BY deployed_at DESC
 LIMIT {n}
"#
        )
    }

    /// Build a query that returns the trace spans for a given trace id.
    pub fn trace_by_id(trace_id: &str) -> String {
        format!(
            r#"
SELECT trace_id,
       span_id,
       parent_span_id,
       name,
       service,
       started_at,
       duration_ns,
       status_code,
       attributes
  FROM traces
 WHERE trace_id = '{trace_id}'
 ORDER BY started_at ASC
"#
        )
    }

    /// Build a query that returns the p50 / p95 / p99 latency for traces in
    /// the last `hours` hours.
    pub fn trace_latency_quantiles(hours: u32) -> String {
        format!(
            r#"
SELECT service,
       quantile(0.50)(duration_ns) / 1e6 AS p50_ms,
       quantile(0.95)(duration_ns) / 1e6 AS p95_ms,
       quantile(0.99)(duration_ns) / 1e6 AS p99_ms,
       count() AS samples
  FROM traces
 WHERE started_at >= now() - INTERVAL {hours} HOUR
 GROUP BY service
 ORDER BY p95_ms DESC
"#
        )
    }
}

// ---------------------------------------------------------------------------
// AnalyticsClient — convenience wrapper that runs the queries above and
// deserialises the typed results.
// ---------------------------------------------------------------------------

/// Typed analytics client.
///
/// Wraps a [`ClickHouseClient`] and runs the queries from [`analytics`],
/// returning strongly-typed result rows.
#[derive(Debug, Clone)]
pub struct AnalyticsClient {
    client: ClickHouseClient,
}

impl AnalyticsClient {
    /// Build a new analytics client over the given [`ClickHouseClient`].
    pub fn new(client: ClickHouseClient) -> Self {
        Self { client }
    }

    /// Borrow the underlying client.
    pub fn client(&self) -> &ClickHouseClient {
        &self.client
    }

    /// Run [`analytics::summary`] and return the aggregated result.
    pub async fn summary(&self) -> Result<Vec<AnalyticsSummaryRow>> {
        let sql = analytics::summary();
        let mut cursor = self.client.query(&sql).fetch::<AnalyticsSummaryRow>()?;
        let mut out = Vec::new();
        while let Some(row) = cursor.next().await.map_err(|e| Error::decode("summary", e.to_string()))? {
            out.push(row);
        }
        Ok(out)
    }

    /// Run [`analytics::agent_outcomes`] and return one row per agent/environment.
    pub async fn agent_outcomes(&self) -> Result<Vec<AgentOutcomeRow>> {
        let sql = analytics::agent_outcomes();
        let mut cursor = self
            .client
            .query(&sql)
            .fetch::<AgentOutcomeRow>()?;
        let mut out = Vec::new();
        while let Some(row) = cursor.next().await.map_err(|e| Error::decode("agent_outcomes", e.to_string()))? {
            out.push(row);
        }
        Ok(out)
    }

    /// Run [`analytics::llm_daily`] for the given lookback window.
    pub async fn llm_daily(&self, days: Option<u32>) -> Result<Vec<LlmDailyRow>> {
        let sql = analytics::llm_daily(days);
        let mut cursor = self.client.query(&sql).fetch::<LlmDailyRow>()?;
        let mut out = Vec::new();
        while let Some(row) = cursor.next().await.map_err(|e| Error::decode("llm_daily", e.to_string()))? {
            out.push(row);
        }
        Ok(out)
    }

    /// Run [`analytics::recent_deploys`].
    pub async fn recent_deploys(&self, n: u32) -> Result<Vec<DeploySummaryRow>> {
        let sql = analytics::recent_deploys(n);
        let mut cursor = self.client.query(&sql).fetch::<DeploySummaryRow>()?;
        let mut out = Vec::new();
        while let Some(row) = cursor.next().await.map_err(|e| Error::decode("recent_deploys", e.to_string()))? {
            out.push(row);
        }
        Ok(out)
    }

    /// Run [`analytics::trace_by_id`] for a single trace.
    pub async fn trace_by_id(&self, trace_id: &str) -> Result<Vec<TraceSpan>> {
        let sql = analytics::trace_by_id(trace_id);
        let mut cursor = self.client.query(&sql).fetch::<TraceSpan>()?;
        let mut out = Vec::new();
        while let Some(row) = cursor.next().await.map_err(|e| Error::decode("traces", e.to_string()))? {
            out.push(row);
        }
        Ok(out)
    }

    /// Run [`analytics::trace_latency_quantiles`].
    pub async fn trace_latency_quantiles(
        &self,
        hours: u32,
    ) -> Result<Vec<TraceLatencyRow>> {
        let sql = analytics::trace_latency_quantiles(hours);
        let mut cursor = self
            .client
            .query(&sql)
            .fetch::<TraceLatencyRow>()?;
        let mut out = Vec::new();
        while let Some(row) = cursor.next().await.map_err(|e| Error::decode("trace_latency", e.to_string()))? {
            out.push(row);
        }
        Ok(out)
    }

    /// Convenience aggregate: roll all per-stream counts into a single
    /// [`AnalyticsSummary`] snapshot. Equivalent to summing the rows returned
    /// by [`Self::summary`] but with a stable top-level shape for callers that
    /// just want one JSON blob.
    pub async fn snapshot(&self) -> Result<AnalyticsSummary> {
        let rows = self.summary().await?;
        let mut summary = AnalyticsSummary::default();
        for row in rows {
            let entry = summary
                .streams
                .entry(row.stream.clone())
                .or_default();
            entry.insert(row.status.clone(), row.count);
            summary.total += row.count;
        }
        Ok(summary)
    }
}

// ---------------------------------------------------------------------------
// Typed result rows for analytics queries.
// ---------------------------------------------------------------------------

/// One row of [`analytics::summary`].
#[derive(Debug, Clone, Serialize, Deserialize, clickhouse::Row)]
#[clickhouse(crate = "clickhouse")]
pub struct AnalyticsSummaryRow {
    /// Stream name (`agent_run`, `deploy`, …).
    pub stream: String,
    /// Status bucket for the row (status enum, env, or success flag).
    pub status: String,
    /// Number of rows in this bucket.
    pub count: u64,
}

/// Snapshot of all stream counts.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct AnalyticsSummary {
    /// `stream → status → count` map.
    pub streams: std::collections::BTreeMap<String, std::collections::BTreeMap<String, u64>>,
    /// Total number of rows summed across every stream.
    pub total: u64,
}

/// One row of [`analytics::agent_outcomes`].
#[derive(Debug, Clone, Serialize, Deserialize, clickhouse::Row)]
#[clickhouse(crate = "clickhouse")]
pub struct AgentOutcomeRow {
    /// Logical agent identifier.
    pub agent: String,
    /// Environment label.
    pub environment: String,
    /// Runs that finished `Succeeded`.
    pub succeeded: u64,
    /// Runs that finished `Failed`.
    pub failed: u64,
    /// Runs that are currently `Running`.
    pub running: u64,
    /// Runs that are `Pending`.
    pub pending: u64,
    /// Runs that were `Cancelled`.
    pub cancelled: u64,
    /// Total runs across all statuses.
    pub total: u64,
}

/// One row of [`analytics::llm_daily`].
#[derive(Debug, Clone, Serialize, Deserialize, clickhouse::Row)]
#[clickhouse(crate = "clickhouse")]
pub struct LlmDailyRow {
    /// Calendar day (UTC) the row aggregates.
    #[serde(with = "crate::records::day")]
    pub day: chrono::NaiveDate,
    /// Provider identifier.
    pub provider: String,
    /// Model identifier.
    pub model: String,
    /// Sum of prompt tokens for the day.
    pub prompt_tokens: u64,
    /// Sum of completion tokens for the day.
    pub completion_tokens: u64,
    /// Sum of `prompt + completion` tokens.
    pub total_tokens: u64,
    /// Number of successful calls.
    pub succeeded_calls: u64,
    /// Number of failed calls.
    pub failed_calls: u64,
    /// Average latency (ms).
    pub avg_latency_ms: f64,
}

/// One row of [`analytics::recent_deploys`].
#[derive(Debug, Clone, Serialize, Deserialize, clickhouse::Row)]
#[clickhouse(crate = "clickhouse")]
pub struct DeploySummaryRow {
    /// Deploy identifier.
    #[serde(with = "crate::records::uuid_deploy")]
    pub deploy_id: uuid::Uuid,
    /// Component name.
    pub component: String,
    /// Environment name as a string (`local`, `ci`, `staging`, `production`).
    pub environment: String,
    /// Commit SHA.
    pub commit_sha: String,
    /// Optional human-readable version.
    pub version: Option<String>,
    /// When the deploy completed.
    #[serde(with = "crate::records::dt_deploy")]
    pub deployed_at: chrono::DateTime<chrono::Utc>,
    /// Deploy duration (ms).
    pub duration_ms: u32,
    /// Whether the deploy succeeded.
    pub succeeded: bool,
}

/// One row of [`analytics::trace_latency_quantiles`].
#[derive(Debug, Clone, Serialize, Deserialize, clickhouse::Row)]
#[clickhouse(crate = "clickhouse")]
pub struct TraceLatencyRow {
    /// Service name.
    pub service: String,
    /// p50 latency (ms).
    pub p50_ms: f64,
    /// p95 latency (ms).
    pub p95_ms: f64,
    /// p99 latency (ms).
    pub p99_ms: f64,
    /// Number of samples that contributed to the quantiles.
    pub samples: u64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn summary_query_targets_all_five_tables() {
        let q = analytics::summary();
        for table in ["agent_runs", "decisions", "deploys", "traces", "llm_calls"] {
            assert!(
                q.contains(table),
                "summary query missing reference to `{table}`: {q}"
            );
        }
    }

    #[test]
    fn llm_daily_query_respects_window() {
        let q = analytics::llm_daily(Some(14));
        assert!(q.contains("INTERVAL 14 DAY"));
        let q = analytics::llm_daily(None);
        assert!(q.contains("INTERVAL 7 DAY"));
    }

    #[test]
    fn recent_deploys_query_has_limit() {
        let q = analytics::recent_deploys(50);
        assert!(q.contains("LIMIT 50"));
    }

    #[test]
    fn trace_by_id_injects_trace_id() {
        let q = analytics::trace_by_id("abc123");
        assert!(q.contains("WHERE trace_id = 'abc123'"));
    }

    #[test]
    fn trace_latency_quantiles_uses_quantile_aggregates() {
        let q = analytics::trace_latency_quantiles(24);
        assert!(q.contains("quantile(0.50)"));
        assert!(q.contains("quantile(0.95)"));
        assert!(q.contains("quantile(0.99)"));
        assert!(q.contains("INTERVAL 24 HOUR"));
    }

    #[test]
    fn snapshot_aggregates_per_stream_counts() {
        let rows = vec![
            AnalyticsSummaryRow {
                stream: "agent_run".into(),
                status: "Succeeded".into(),
                count: 3,
            },
            AnalyticsSummaryRow {
                stream: "agent_run".into(),
                status: "Failed".into(),
                count: 1,
            },
            AnalyticsSummaryRow {
                stream: "deploy".into(),
                status: "succeeded".into(),
                count: 2,
            },
        ];
        // We can't easily hit `AnalyticsClient::summary` in a unit test without
        // a live server, so emulate its aggregation logic directly.
        let mut summary = AnalyticsSummary::default();
        for row in rows {
            let entry = summary.streams.entry(row.stream.clone()).or_default();
            entry.insert(row.status.clone(), row.count);
            summary.total += row.count;
        }
        assert_eq!(summary.total, 6);
        assert_eq!(summary.streams["agent_run"]["Succeeded"], 3);
        assert_eq!(summary.streams["agent_run"]["Failed"], 1);
        assert_eq!(summary.streams["deploy"]["succeeded"], 2);
    }
}