//! Row records that map 1:1 to ClickHouse tables.
//!
//! Every record implements `clickhouse::Row` (via derive) and `serde::Serialize`
//! for inserts and `serde::Deserialize` for analytics reads. Timestamps are
//! stored as `DateTime64(9)` (nanoseconds since epoch) using the
//! `clickhouse::serde::chrono::datetime64::nanos` adapter so sub-millisecond
//! precision is preserved across ingest/query boundaries.
//!
//! The `clickhouse::serde::*` adapters expose bare `serialize`/`deserialize`
//! functions (not modules), so each adapter is wrapped here in a module
//! shape that `#[serde(with = "...")]` expects.

use chrono::{DateTime, Utc};
use clickhouse::Row;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

// ---------------------------------------------------------------------------
// Adapter modules — bridge from `clickhouse::serde::*` (bare fns) into the
// `#[serde(with = "<module>")]` shape.
// ---------------------------------------------------------------------------

/// Ser/de `chrono::DateTime<Utc>` ↔ `DateTime64(9)` (nanoseconds).
pub mod dt_nanos {
    use chrono::{DateTime, Utc};
    use serde::{Deserialize, Deserializer, Serialize, Serializer};

    pub fn serialize<S: Serializer>(dt: &DateTime<Utc>, s: S) -> Result<S::Ok, S::Error> {
        clickhouse::serde::chrono::datetime64::nanos::serialize(dt, s)
    }

    pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<DateTime<Utc>, D::Error> {
        clickhouse::serde::chrono::datetime64::nanos::deserialize(d)
    }
}

/// Ser/de `Option<chrono::DateTime<Utc>>` ↔ `Nullable(DateTime64(9))`.
pub mod dt_nanos_opt {
    use chrono::{DateTime, Utc};
    use serde::{Deserialize, Deserializer, Serializer};

    pub fn serialize<S: Serializer>(dt: &Option<DateTime<Utc>>, s: S) -> Result<S::Ok, S::Error> {
        clickhouse::serde::chrono::datetime64::nanos::option::serialize(dt, s)
    }

    pub fn deserialize<'de, D: Deserializer<'de>>(
        d: D,
    ) -> Result<Option<DateTime<Utc>>, D::Error> {
        clickhouse::serde::chrono::datetime64::nanos::option::deserialize(d)
    }
}

/// Ser/de `uuid::Uuid` ↔ `UUID`.
pub mod id_uuid {
    use serde::{Deserialize, Deserializer, Serializer};
    use uuid::Uuid;

    pub fn serialize<S: Serializer>(id: &Uuid, s: S) -> Result<S::Ok, S::Error> {
        clickhouse::serde::uuid::serialize(id, s)
    }

    pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<Uuid, D::Error> {
        clickhouse::serde::uuid::deserialize(d)
    }
}

/// Ser/de `chrono::NaiveDate` ↔ `Date`.
pub mod naive_date {
    use chrono::NaiveDate;
    use serde::{Deserialize, Deserializer, Serializer};

    pub fn serialize<S: Serializer>(d: &NaiveDate, s: S) -> Result<S::Ok, S::Error> {
        clickhouse::serde::chrono::date::serialize(d, s)
    }

    pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<NaiveDate, D::Error> {
        clickhouse::serde::chrono::date::deserialize(d)
    }
}

// Convenience re-exports with semantically meaningful names so other modules
// (e.g. analytics result rows) can attach a ClickHouse-friendly serde adapter
// without needing to declare their own.
pub use id_uuid as uuid_deploy;
pub use dt_nanos as dt_deploy;
pub use naive_date as day;

// ---------------------------------------------------------------------------
// agent_runs
// ---------------------------------------------------------------------------

/// Lifecycle status for an `agent_runs` row.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Row)]
#[serde(rename_all = "snake_case")]
#[clickhouse(crate = "clickhouse")]
#[repr(u8)]
pub enum AgentRunStatus {
    /// Agent run was created but execution has not started.
    Pending = 0,
    /// Agent is actively running.
    Running = 1,
    /// Agent completed successfully.
    Succeeded = 2,
    /// Agent failed (see `error_message` for details).
    Failed = 3,
    /// Agent run was cancelled by an operator.
    Cancelled = 4,
}

/// One row per agent execution.
#[derive(Debug, Clone, Serialize, Deserialize, Row)]
#[clickhouse(crate = "clickhouse")]
pub struct AgentRun {
    /// Stable identifier for this run.
    #[serde(with = "id_uuid")]
    pub run_id: Uuid,
    /// Logical agent identifier (e.g. `code-review`, `pr-fixer`).
    pub agent: String,
    /// Environment label (`dev`, `prod`, ...).
    pub environment: String,
    /// Lifecycle status.
    pub status: AgentRunStatus,
    /// Start of the run (UTC).
    #[serde(with = "dt_nanos")]
    pub started_at: DateTime<Utc>,
    /// End of the run (UTC). `None` for `Pending` / `Running`.
    #[serde(with = "dt_nanos_opt")]
    pub ended_at: Option<DateTime<Utc>>,
    /// Optional human-readable error message on `Failed` status.
    pub error_message: Option<String>,
    /// Free-form metadata (JSON-encoded for forward-compatibility).
    pub metadata: String,
}

// ---------------------------------------------------------------------------
// decisions
// ---------------------------------------------------------------------------

/// One row per decision made by an agent during a run.
///
/// Stores both the decision text and any resulting trace link (e.g. to the
/// evidence the decision was based on).
#[derive(Debug, Clone, Serialize, Deserialize, Row)]
#[clickhouse(crate = "clickhouse")]
pub struct Decision {
    /// Stable identifier for this decision.
    #[serde(with = "id_uuid")]
    pub decision_id: Uuid,
    /// The agent run that produced this decision.
    #[serde(with = "id_uuid")]
    pub run_id: Uuid,
    /// Short label (`promote-evidence`, `reject-link`, ...).
    pub kind: String,
    /// Free-form justification / explanation.
    pub rationale: String,
    /// Optional trace link to evidence, story, or another decision.
    pub trace_link_id: Option<String>,
    /// When the decision was made (UTC).
    #[serde(with = "dt_nanos")]
    pub decided_at: DateTime<Utc>,
}

// ---------------------------------------------------------------------------
// deploys
// ---------------------------------------------------------------------------

/// Target environment for a deploy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Row)]
#[serde(rename_all = "snake_case")]
#[clickhouse(crate = "clickhouse")]
#[repr(u8)]
pub enum DeployEnvironment {
    /// Local developer workstation.
    Local = 0,
    /// CI ephemeral environment.
    Ci = 1,
    /// Staging.
    Staging = 2,
    /// Production.
    Production = 3,
}

/// One row per deploy event.
#[derive(Debug, Clone, Serialize, Deserialize, Row)]
#[clickhouse(crate = "clickhouse")]
pub struct Deploy {
    /// Stable identifier for this deploy.
    #[serde(with = "id_uuid")]
    pub deploy_id: Uuid,
    /// Component being deployed (e.g. `tracera-server`).
    pub component: String,
    /// Target environment.
    pub environment: DeployEnvironment,
    /// Commit SHA being deployed.
    pub commit_sha: String,
    /// Optional human-readable version label.
    pub version: Option<String>,
    /// When the deploy completed (UTC).
    #[serde(with = "dt_nanos")]
    pub deployed_at: DateTime<Utc>,
    /// Deploy duration in milliseconds.
    pub duration_ms: u32,
    /// Whether the deploy succeeded.
    pub succeeded: bool,
}

// ---------------------------------------------------------------------------
// traces — distributed-trace spans (OpenTelemetry-style).
// ---------------------------------------------------------------------------

/// One row per distributed-trace span.
#[derive(Debug, Clone, Serialize, Deserialize, Row)]
#[clickhouse(crate = "clickhouse")]
pub struct TraceSpan {
    /// 16-byte trace id, hex-encoded for compactness.
    pub trace_id: String,
    /// 8-byte span id, hex-encoded.
    pub span_id: String,
    /// Parent span id (`None` for root spans).
    pub parent_span_id: Option<String>,
    /// Logical operation (e.g. `http.server.request`).
    pub name: String,
    /// Service producing this span (e.g. `tracera-server`).
    pub service: String,
    /// Start of the span (UTC).
    #[serde(with = "dt_nanos")]
    pub started_at: DateTime<Utc>,
    /// Duration in nanoseconds.
    pub duration_ns: u64,
    /// Span status code (`OK`, `ERROR`, `UNSET`).
    pub status_code: String,
    /// Span attributes encoded as JSON.
    pub attributes: String,
}

// ---------------------------------------------------------------------------
// llm_calls
// ---------------------------------------------------------------------------

/// One row per LLM call.
#[derive(Debug, Clone, Serialize, Deserialize, Row)]
#[clickhouse(crate = "clickhouse")]
pub struct LlmCall {
    /// Stable identifier for this LLM call.
    #[serde(with = "id_uuid")]
    pub call_id: Uuid,
    /// Optional trace this call belongs to.
    pub trace_id: Option<String>,
    /// Provider (`openai`, `anthropic`, ...).
    pub provider: String,
    /// Model identifier (`gpt-4o`, `claude-3-opus`, ...).
    pub model: String,
    /// Tokens in the prompt.
    pub prompt_tokens: u32,
    /// Tokens in the completion.
    pub completion_tokens: u32,
    /// Total wall-clock latency in milliseconds.
    pub latency_ms: u32,
    /// Whether the call succeeded.
    pub succeeded: bool,
    /// When the call was made (UTC).
    #[serde(with = "dt_nanos")]
    pub called_at: DateTime<Utc>,
}

// ---------------------------------------------------------------------------
// Event union — used by the `events-ingest` CLI to dispatch NDJSON rows.
// ---------------------------------------------------------------------------

/// Tagged enum that maps directly to the five stream tables. Each variant
/// contains the typed row that belongs in that table.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "stream", rename_all = "snake_case")]
pub enum Event {
    /// An `agent_runs` row.
    AgentRun(AgentRun),
    /// A `decisions` row.
    Decision(Decision),
    /// A `deploys` row.
    Deploy(Deploy),
    /// A `traces` row.
    Trace(TraceSpan),
    /// An `llm_calls` row.
    LlmCall(LlmCall),
}

impl Event {
    /// Logical stream name for this event (matches the `stream` tag).
    pub fn stream(&self) -> &'static str {
        match self {
            Event::AgentRun(_) => "agent_run",
            Event::Decision(_) => "decision",
            Event::Deploy(_) => "deploy",
            Event::Trace(_) => "trace",
            Event::LlmCall(_) => "llm_call",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stream_names_are_stable() {
        // These names are wire-format — pin them so accidental renames break tests.
        assert_eq!(
            Event::AgentRun(AgentRun {
                run_id: Uuid::nil(),
                agent: "x".into(),
                environment: "test".into(),
                status: AgentRunStatus::Pending,
                started_at: Utc::now(),
                ended_at: None,
                error_message: None,
                metadata: "{}".into(),
            })
            .stream(),
            "agent_run"
        );
        assert_eq!(
            Event::LlmCall(LlmCall {
                call_id: Uuid::nil(),
                trace_id: None,
                provider: "openai".into(),
                model: "gpt-4o".into(),
                prompt_tokens: 1,
                completion_tokens: 2,
                latency_ms: 3,
                succeeded: true,
                called_at: Utc::now(),
            })
            .stream(),
            "llm_call"
        );
    }

    #[test]
    fn event_roundtrips_as_ndjson() {
        let evt = Event::Trace(TraceSpan {
            trace_id: "00000000000000000000000000000001".into(),
            span_id: "0000000000000001".into(),
            parent_span_id: None,
            name: "root".into(),
            service: "tracera-server".into(),
            started_at: Utc::now(),
            duration_ns: 42,
            status_code: "OK".into(),
            attributes: "{}".into(),
        });
        let json = serde_json::to_string(&evt).unwrap();
        let back: Event = serde_json::from_str(&json).unwrap();
        assert_eq!(back.stream(), "trace");
    }
}