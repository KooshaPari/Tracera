//! CI bridge: normalise CI events from external providers into SDLC events.
//!
//! Atlas consumes CI events out-of-band — most commonly from GitHub
//! Actions webhooks — and turns them into the same `SdlcEvent` vocabulary
//! the rest of the crate speaks. The bridge is intentionally provider-
//! agnostic: a new provider only needs to implement [`CiProviderAdapter`].
//!
//! The bridge does NOT itself publish events onto a bus. It produces
//! [`NormalizedCiEvent`]s and [`publish_ci_event`] turns those into
//! [`crate::observability::SdlcEvent`]s; callers (the `atlas-server`
//! binary, a CLI one-shot, or a unit test) then hand the event to the
//! engine. This keeps the bridge pure and easy to test.

use crate::delegation::WorkItemId;
use crate::observability::{SdlcEvent, SdlcEventKind, SdlcStage};
use chrono::{DateTime, Utc};
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};
use thiserror::Error;

// ---------- Errors ----------

/// Errors returned by the CI bridge.
#[derive(Debug, Error)]
pub enum CiEventError {
    /// Payload was not valid JSON.
    #[error("invalid JSON payload: {0}")]
    InvalidJson(#[from] serde_json::Error),
    /// A required field was missing from the payload.
    #[error("missing required field: {0}")]
    MissingField(&'static str),
    /// The payload was structurally valid but not in a state we recognise
    /// (e.g. an unknown workflow_run status we don't have a mapping for).
    #[error("unsupported value for field {field}: {value:?}")]
    UnsupportedValue {
        /// The field name.
        field: &'static str,
        /// The unsupported value.
        value: String,
    },
    /// The provider itself could not be determined from the payload.
    #[error("could not identify CI provider from payload")]
    UnknownProvider,
}

// ---------- Provider taxonomy ----------

/// The CI providers Atlas knows how to ingest.
///
/// New providers should be added here AND have a constructor that builds a
/// [`CiBridge`] from their native payload shape.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CiProvider {
    /// GitHub Actions.
    GithubActions,
    /// Generic / manual ingestion (no provider-specific payload).
    Generic,
}

/// Sub-kind of CI event, post-normalisation.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CiEventKind {
    /// The CI run started (queued, requested, in_progress).
    RunStarted,
    /// The CI run succeeded.
    RunSucceeded,
    /// The CI run failed.
    RunFailed,
    /// The CI run was cancelled.
    RunCancelled,
    /// The CI run timed out.
    RunTimedOut,
    /// Unknown / unhandled outcome; recorded verbatim.
    Other,
}

impl CiEventKind {
    /// Map this kind to a stable string suitable for metric labels.
    #[must_use]
    pub fn as_str(self) -> &'static str {
        match self {
            Self::RunStarted => "run_started",
            Self::RunSucceeded => "run_succeeded",
            Self::RunFailed => "run_failed",
            Self::RunCancelled => "run_cancelled",
            Self::RunTimedOut => "run_timed_out",
            Self::Other => "other",
        }
    }
}

// ---------- Normalised event ----------

/// Normalised CI event ready for ingestion into the Atlas event bus.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct NormalizedCiEvent {
    /// Originating provider.
    pub provider: CiProvider,
    /// Native event kind, post-normalisation.
    pub kind: CiEventKind,
    /// Stable id for the workflow run (provider-supplied).
    pub run_id: Option<String>,
    /// Workflow file name (e.g. `ci.yml`).
    pub workflow: Option<String>,
    /// Branch the run targeted, if known.
    pub branch: Option<String>,
    /// Commit SHA, if known.
    pub commit_sha: Option<String>,
    /// Repository identifier (`owner/repo`), if known.
    pub repository: Option<String>,
    /// Triggering actor (GitHub login, etc.).
    pub actor: Option<String>,
    /// Wall-clock time the underlying CI event was emitted.
    pub at: DateTime<Utc>,
    /// Free-form provider fields, preserved for downstream filtering.
    #[serde(default)]
    pub raw: serde_json::Value,
}

// ---------- GitHub Actions payload ----------

/// Top-level shape of a GitHub Actions `workflow_run` webhook payload.
///
/// We only model the fields we actually consume; extra fields are
/// tolerated by serde and preserved via the raw `"*"` capture below.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct GitHubActionsEvent {
    /// Always `"workflow_run"` for the events we care about.
    #[serde(default)]
    pub event: Option<String>,
    /// The embedded `workflow_run` object.
    #[serde(default)]
    pub workflow_run: Option<GitHubWorkflowRun>,
    /// The repository the run targeted.
    #[serde(default)]
    pub repository: Option<GitHubRepository>,
    /// The sender (login of the actor that triggered the run).
    #[serde(default)]
    pub sender: Option<GitHubSender>,
}

/// Subset of GitHub's `workflow_run` object we consume.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct GitHubWorkflowRun {
    /// Database id of the run.
    #[serde(default)]
    pub id: Option<u64>,
    /// Display name of the run.
    #[serde(default)]
    pub name: Option<String>,
    /// Path of the workflow file (e.g. `.github/workflows/ci.yml`).
    #[serde(default)]
    pub path: Option<String>,
    /// Current status: `queued`, `in_progress`, `completed`, …
    #[serde(default)]
    pub status: Option<String>,
    /// Final conclusion: `success`, `failure`, `cancelled`, `timed_out`,
    /// `neutral`, `stale`, `skipped`, `action_required`. Only meaningful
    /// when `status == "completed"`.
    #[serde(default)]
    pub conclusion: Option<String>,
    /// Branch the run targeted.
    #[serde(default)]
    pub head_branch: Option<String>,
    /// Commit SHA the run targeted.
    #[serde(default)]
    pub head_sha: Option<String>,
    /// HTML URL of the run.
    #[serde(default)]
    pub html_url: Option<String>,
    /// `created_at` timestamp.
    #[serde(default)]
    pub created_at: Option<String>,
    /// `updated_at` timestamp.
    #[serde(default)]
    pub updated_at: Option<String>,
}

/// Subset of GitHub's `repository` object we consume.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct GitHubRepository {
    /// `owner/name`.
    #[serde(default)]
    pub full_name: Option<String>,
    /// HTML URL.
    #[serde(default)]
    pub html_url: Option<String>,
}

/// Subset of GitHub's `sender` object we consume.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct GitHubSender {
    /// Login (handle) of the triggering user.
    #[serde(default)]
    pub login: Option<String>,
}

// ---------- Bridge ----------

/// Core bridge that normalises CI provider payloads into [`NormalizedCiEvent`].
#[derive(Debug, Clone, Default)]
pub struct CiBridge;

impl CiBridge {
    /// Construct a new bridge.
    #[must_use]
    pub fn new() -> Self {
        Self
    }

    /// Normalise a GitHub Actions webhook payload.
    ///
    /// `raw_json` is the verbatim JSON body of the incoming webhook. It is
    /// preserved on the returned [`NormalizedCiEvent::raw`] field so
    /// downstream subscribers can inspect provider-specific fields without
    /// us having to model them all up front.
    pub fn from_github_actions(&self, raw_json: &str) -> Result<NormalizedCiEvent, CiEventError> {
        let event: GitHubActionsEvent = serde_json::from_str(raw_json)?;
        let run = event.workflow_run.ok_or(CiEventError::MissingField("workflow_run"))?;
        let status = run.status.as_deref().unwrap_or("");
        let kind = map_github_status_to_kind(status, run.conclusion.as_deref())?;

        let at = run
            .updated_at
            .as_deref()
            .or(run.created_at.as_deref())
            .and_then(parse_github_timestamp)
            .unwrap_or_else(Utc::now);

        let raw: serde_json::Value = serde_json::from_str(raw_json).unwrap_or(serde_json::Value::Null);

        Ok(NormalizedCiEvent {
            provider: CiProvider::GithubActions,
            kind,
            run_id: run.id.map(|i| i.to_string()),
            workflow: run.path.or(run.name),
            branch: run.head_branch,
            commit_sha: run.head_sha,
            repository: event.repository.and_then(|r| r.full_name),
            actor: event.sender.and_then(|s| s.login),
            at,
            raw,
        })
    }

    /// Best-effort auto-detect of the provider from a raw JSON payload.
    ///
    /// Inspects the `"X-GitHub-Event"` shape (presence of `workflow_run`)
    /// and returns the right provider; falls back to [`CiProvider::Generic`]
    /// when nothing recognisable is present.
    pub fn detect_and_normalise(&self, raw_json: &str) -> Result<NormalizedCiEvent, CiEventError> {
        // Cheap pre-check: does the payload look like GitHub Actions?
        if let Ok(value) = serde_json::from_str::<serde_json::Value>(raw_json) {
            if value.get("workflow_run").is_some() {
                return self.from_github_actions(raw_json);
            }
        }
        Err(CiEventError::UnknownProvider)
    }
}

/// Provider-agnostic hook for CI bridge implementations.
pub trait CiProviderAdapter {
    /// Provider identifier.
    fn provider(&self) -> CiProvider;
    /// Normalise a raw payload into a `NormalizedCiEvent`.
    fn normalize(&self, raw_json: &str) -> Result<NormalizedCiEvent, CiEventError>;
}

impl CiProviderAdapter for CiBridge {
    fn provider(&self) -> CiProvider {
        CiProvider::GithubActions
    }
    fn normalize(&self, raw_json: &str) -> Result<NormalizedCiEvent, CiEventError> {
        self.from_github_actions(raw_json)
    }
}

// ---------- Helpers ----------

fn map_github_status_to_kind(
    status: &str,
    conclusion: Option<&str>,
) -> Result<CiEventKind, CiEventError> {
    if status == "completed" {
        return match conclusion.unwrap_or("") {
            "success" => Ok(CiEventKind::RunSucceeded),
            "failure" => Ok(CiEventKind::RunFailed),
            "cancelled" => Ok(CiEventKind::RunCancelled),
            "timed_out" => Ok(CiEventKind::RunTimedOut),
            "" | "neutral" | "skipped" | "stale" | "action_required" => Ok(CiEventKind::Other),
            other => Err(CiEventError::UnsupportedValue {
                field: "workflow_run.conclusion",
                value: other.to_string(),
            }),
        };
    }
    if matches!(status, "queued" | "in_progress" | "requested" | "waiting") {
        return Ok(CiEventKind::RunStarted);
    }
    Err(CiEventError::UnsupportedValue {
        field: "workflow_run.status",
        value: status.to_string(),
    })
}

fn parse_github_timestamp(s: &str) -> Option<DateTime<Utc>> {
    DateTime::parse_from_rfc3339(s)
        .ok()
        .map(|dt| dt.with_timezone(&Utc))
}

// ---------- Publishing to the SDLC event bus ----------

/// Convert a [`NormalizedCiEvent`] into an [`SdlcEvent`] ready to publish.
///
/// The returned event uses the [`SdlcEventKind::CiRunCompleted`] variant
/// and tags it with `provider`, `run_id`, `branch`, `commit`, `workflow`,
/// and `actor` so downstream subscribers can filter without re-parsing the
/// raw payload.
///
/// `work_item_id` is optional; callers that have resolved the run to a
/// specific work item pass its id here so the event lands in the right
/// per-work-item timeline. Otherwise the event is emitted against a
/// zero-uuid "unscoped" placeholder that subscribers can recognise.
pub fn publish_ci_event(
    event: &NormalizedCiEvent,
    work_item_id: WorkItemId,
) -> SdlcEvent {
    let outcome = event.kind.as_str();
    let provider_str = match event.provider {
        CiProvider::GithubActions => "github_actions",
        CiProvider::Generic => "generic",
    };

    let mut tags = IndexMap::new();
    tags.insert("provider".to_string(), provider_str.to_string());
    tags.insert("kind".to_string(), outcome.to_string());
    if let Some(run_id) = &event.run_id {
        tags.insert("run_id".to_string(), run_id.clone());
    }
    if let Some(branch) = &event.branch {
        tags.insert("branch".to_string(), branch.clone());
    }
    if let Some(commit) = &event.commit_sha {
        tags.insert("commit".to_string(), commit.clone());
    }
    if let Some(workflow) = &event.workflow {
        tags.insert("workflow".to_string(), workflow.clone());
    }
    if let Some(repo) = &event.repository {
        tags.insert("repository".to_string(), repo.clone());
    }
    if let Some(actor) = &event.actor {
        tags.insert("actor".to_string(), actor.clone());
    }

    SdlcEvent {
        id: uuid::Uuid::new_v4(),
        work_item_id,
        // CI events don't drive the work-item state machine, so the stage
        // is reported as `InProgress` by convention. Subscribers should
        // rely on `tags["kind"]` to determine what actually happened.
        stage: SdlcStage::InProgress,
        at: event.at,
        kind: SdlcEventKind::CiRunCompleted {
            provider: provider_str.to_string(),
            run_id: event.run_id.clone(),
            outcome: outcome.to_string(),
        },
        tags,
    }
}

// ---------- Tests ----------

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE_PAYLOAD: &str = r#"{
        "event": "workflow_run",
        "workflow_run": {
            "id": 1234567890,
            "name": "CI",
            "path": ".github/workflows/ci.yml",
            "status": "completed",
            "conclusion": "success",
            "head_branch": "main",
            "head_sha": "abc1234567890",
            "html_url": "https://github.com/example/repo/actions/runs/1234567890",
            "created_at": "2026-09-01T12:00:00Z",
            "updated_at": "2026-09-01T12:05:00Z"
        },
        "repository": {
            "full_name": "example/repo",
            "html_url": "https://github.com/example/repo"
        },
        "sender": {
            "login": "koosh"
        }
    }"#;

    #[test]
    fn parses_github_success() {
        let bridge = CiBridge::new();
        let ev = bridge.from_github_actions(SAMPLE_PAYLOAD).unwrap();
        assert_eq!(ev.provider, CiProvider::GithubActions);
        assert_eq!(ev.kind, CiEventKind::RunSucceeded);
        assert_eq!(ev.run_id.as_deref(), Some("1234567890"));
        assert_eq!(ev.workflow.as_deref(), Some(".github/workflows/ci.yml"));
        assert_eq!(ev.branch.as_deref(), Some("main"));
        assert_eq!(ev.commit_sha.as_deref(), Some("abc1234567890"));
        assert_eq!(ev.repository.as_deref(), Some("example/repo"));
        assert_eq!(ev.actor.as_deref(), Some("koosh"));
    }

    #[test]
    fn parses_github_failure() {
        let bridge = CiBridge::new();
        let payload = SAMPLE_PAYLOAD.replace("\"success\"", "\"failure\"");
        let ev = bridge.from_github_actions(&payload).unwrap();
        assert_eq!(ev.kind, CiEventKind::RunFailed);
    }

    #[test]
    fn parses_github_in_progress() {
        let bridge = CiBridge::new();
        let payload = SAMPLE_PAYLOAD.replace("\"completed\"", "\"in_progress\"");
        let ev = bridge.from_github_actions(&payload).unwrap();
        assert_eq!(ev.kind, CiEventKind::RunStarted);
    }

    #[test]
    fn parses_github_cancelled_and_timed_out() {
        let bridge = CiBridge::new();
        let cancelled = SAMPLE_PAYLOAD.replace("\"success\"", "\"cancelled\"");
        let ev = bridge.from_github_actions(&cancelled).unwrap();
        assert_eq!(ev.kind, CiEventKind::RunCancelled);

        let timed_out = SAMPLE_PAYLOAD.replace("\"success\"", "\"timed_out\"");
        let ev = bridge.from_github_actions(&timed_out).unwrap();
        assert_eq!(ev.kind, CiEventKind::RunTimedOut);
    }

    #[test]
    fn unknown_status_is_unsupported_value() {
        let bridge = CiBridge::new();
        let payload = SAMPLE_PAYLOAD.replace("\"completed\"", "\"exploded\"");
        let err = bridge.from_github_actions(&payload).unwrap_err();
        assert!(matches!(err, CiEventError::UnsupportedValue { .. }));
    }

    #[test]
    fn missing_workflow_run_is_missing_field() {
        let bridge = CiBridge::new();
        let err = bridge.from_github_actions("{}").unwrap_err();
        assert!(matches!(err, CiEventError::MissingField("workflow_run")));
    }

    #[test]
    fn detect_and_normalise_routes_to_github() {
        let bridge = CiBridge::new();
        let ev = bridge.detect_and_normalise(SAMPLE_PAYLOAD).unwrap();
        assert_eq!(ev.provider, CiProvider::GithubActions);
    }

    #[test]
    fn detect_and_normalise_rejects_unknown() {
        let bridge = CiBridge::new();
        let err = bridge.detect_and_normalise("{}").unwrap_err();
        assert!(matches!(err, CiEventError::UnknownProvider));
    }

    #[test]
    fn raw_payload_is_preserved() {
        let bridge = CiBridge::new();
        let ev = bridge.from_github_actions(SAMPLE_PAYLOAD).unwrap();
        assert_eq!(
            ev.raw.get("event").and_then(|v| v.as_str()),
            Some("workflow_run")
        );
    }

    #[test]
    fn malformed_json_surfaces_serde_error() {
        let bridge = CiBridge::new();
        let err = bridge.from_github_actions("{not json").unwrap_err();
        assert!(matches!(err, CiEventError::InvalidJson(_)));
    }

    #[test]
    fn publish_ci_event_populates_tags() {
        let bridge = CiBridge::new();
        let ev = bridge.from_github_actions(SAMPLE_PAYLOAD).unwrap();
        let sdlc = publish_ci_event(&ev, WorkItemId::new());
        assert!(matches!(
            sdlc.kind,
            SdlcEventKind::CiRunCompleted { ref outcome, .. } if outcome == "run_succeeded"
        ));
        assert_eq!(sdlc.tags.get("provider").map(String::as_str), Some("github_actions"));
        assert_eq!(sdlc.tags.get("branch").map(String::as_str), Some("main"));
        assert_eq!(sdlc.tags.get("commit").map(String::as_str), Some("abc1234567890"));
        assert_eq!(sdlc.tags.get("actor").map(String::as_str), Some("koosh"));
        assert_eq!(sdlc.stage, SdlcStage::InProgress);
    }
}
