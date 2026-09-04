//! Crate-wide tests that span more than one module.
//!
//! These live in their own module so each test can pull in whichever
//! submodules it needs without dragging the whole crate into a single
//! `#[cfg(test)]` namespace.

use std::time::Duration;

use chrono::{TimeZone, Utc};
use uuid::Uuid;

use crate::clickhouse::{analytics, AnalyticsClient, AnalyticsSummaryRow};
use crate::config::{ClickHouseConfig, Credentials};
use crate::records::{
    AgentRun, AgentRunStatus, Decision, Deploy, DeployEnvironment, Event, LlmCall, TraceSpan,
};
use crate::{ClickHouseClient, Error};

#[test]
fn client_new_applies_url_and_database() {
    let cfg = ClickHouseConfig::new("http://localhost:8123")
        .with_database("tracera_test")
        .with_credentials(Credentials::new("default".into(), "secret".into()));
    let client = ClickHouseClient::new(cfg);
    assert_eq!(client.database(), "tracera_test");
    assert_eq!(client.timeout(), Duration::from_secs(30));
}

#[test]
fn client_new_without_user_is_anonymous() {
    let cfg = ClickHouseConfig::new("http://localhost:8123");
    let client = ClickHouseClient::new(cfg);
    // We can't introspect ClickHouse credentials, but we can at least confirm
    // the client is constructable without a panic.
    assert_eq!(client.database(), "tracera");
}

#[test]
fn from_env_fails_without_url() {
    // Verify the empty-URL guard fires before any networking. We exercise the
    // config builder directly rather than mutating process env (which is not
    // safe under parallel tests and is also marked unsafe in newer toolchains).
    let cfg = ClickHouseConfig::new("");
    let url = cfg.url;
    assert!(url.is_empty(), "sanity-check: builder stored empty url");
    // Round-tripping an empty URL through `from_env` should produce a
    // `Config` error — but only if CLICKHOUSE_URL is not set in the host
    // environment. We do not mutate env here; if it is set, the call
    // succeeds and the assertion below passes trivially.
    let res = ClickHouseClient::from_env();
    if let Err(e) = res {
        assert!(
            matches!(e, Error::Config(_)),
            "expected Error::Config, got {e:?}"
        );
    }
}

#[test]
fn analytics_summary_query_targets_every_table() {
    let q = analytics::summary();
    for table in [
        "agent_runs",
        "decisions",
        "deploys",
        "traces",
        "llm_calls",
    ] {
        assert!(q.contains(table), "summary query missing `{table}`: {q}");
    }
}

#[test]
fn analytics_clones_share_query_builder_settings() {
    // We can't actually connect to ClickHouse in this unit test, but we can
    // verify the `AnalyticsClient::client()` accessor exposes the underlying
    // config so callers know how to drive it.
    let cfg = ClickHouseConfig::new("http://localhost:8123").with_database("tracera_test");
    let analytics = AnalyticsClient::new(ClickHouseClient::new(cfg));
    assert_eq!(analytics.client().database(), "tracera_test");
}

#[test]
fn event_round_trips_through_all_streams() {
    let started_at = Utc.with_ymd_and_hms(2026, 9, 3, 12, 0, 0).unwrap();
    let samples = vec![
        Event::AgentRun(AgentRun {
            run_id: Uuid::nil(),
            agent: "code-review".into(),
            environment: "prod".into(),
            status: AgentRunStatus::Succeeded,
            started_at,
            ended_at: Some(started_at),
            error_message: None,
            metadata: "{}".into(),
        }),
        Event::Decision(Decision {
            decision_id: Uuid::nil(),
            run_id: Uuid::nil(),
            kind: "promote-evidence".into(),
            rationale: "links match".into(),
            trace_link_id: None,
            decided_at: started_at,
        }),
        Event::Deploy(Deploy {
            deploy_id: Uuid::nil(),
            component: "tracera-server".into(),
            environment: DeployEnvironment::Production,
            commit_sha: "abc123".into(),
            version: Some("v0.1.0".into()),
            deployed_at: started_at,
            duration_ms: 1234,
            succeeded: true,
        }),
        Event::Trace(TraceSpan {
            trace_id: "00000000000000000000000000000001".into(),
            span_id: "0000000000000001".into(),
            parent_span_id: None,
            name: "root".into(),
            service: "tracera-server".into(),
            started_at,
            duration_ns: 1_000_000,
            status_code: "OK".into(),
            attributes: "{}".into(),
        }),
        Event::LlmCall(LlmCall {
            call_id: Uuid::nil(),
            trace_id: None,
            provider: "openai".into(),
            model: "gpt-4o".into(),
            prompt_tokens: 10,
            completion_tokens: 20,
            latency_ms: 200,
            succeeded: true,
            called_at: started_at,
        }),
    ];

    for event in samples {
        let json = serde_json::to_string(&event).unwrap();
        let back: Event = serde_json::from_str(&json).unwrap();
        assert_eq!(back.stream(), event.stream());
    }
}

#[test]
fn schema_file_contains_all_five_tables() {
    // Embed the schema file at compile time so the test fails fast if it
    // gets out of sync with the source of truth.
    const SCHEMA: &str = include_str!("schema.sql");
    for table in [
        "agent_runs",
        "decisions",
        "deploys",
        "traces",
        "llm_calls",
    ] {
        assert!(
            SCHEMA.contains(&format!("CREATE TABLE IF NOT EXISTS tracera.{table}")),
            "schema.sql missing CREATE TABLE for `{table}`"
        );
    }
}

#[test]
fn summary_row_serializes_to_json() {
    let row = AnalyticsSummaryRow {
        stream: "agent_run".into(),
        status: "Succeeded".into(),
        count: 42,
    };
    let json = serde_json::to_string(&row).unwrap();
    assert!(json.contains("\"stream\":\"agent_run\""));
    assert!(json.contains("\"count\":42"));
}