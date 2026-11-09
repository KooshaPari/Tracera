use std::sync::Arc;

use chrono::Utc;
use serde_json::Value;
use uuid::Uuid;

use crate::handlers::ingest_api::BulkIngestionResult;
use crate::store::{IngestEvidence, IngestRecord, IngestTraceLink, Store};

use super::agcord::{fetch_agcord_agents, fetch_agcord_tasks, AgcordConfig};
use super::github::{fetch_github_issues, GitHubConfig};
use super::jira::{fetch_jira_issues, JiraConfig};
use super::trace_refs::extract_req_refs;
use super::{IngestError, NormalisedIssue};

/// Ingest a slice of normalised issues into the store.
///
/// The entire slice is written as **one atomic batch**: either every row is
/// committed or, on any database error, the transaction is rolled back and no
/// partial state is left behind.
///
/// The batch is idempotent. For each issue:
/// - `Story` id is `"story-{external_id}"` (the idempotency key).
/// - `EvidenceItem` id is `"ev-{source}-{external_id}"`.
/// - `TraceLink` id is `"tl-{story_id}-{requirement_ref}"` and the schema also
///   enforces a unique `(source_id, target_id, relationship)` edge.
///
/// Replaying the same issues therefore updates story/evidence fields in place
/// and creates no duplicate stories, evidence rows, or trace links.
///
/// Returns a `BulkIngestionResult` summary.
pub async fn persist_issues(
    issues: &[NormalisedIssue],
    store: &Arc<dyn Store>,
) -> Result<BulkIngestionResult, IngestError> {
    let mut errors: Vec<String> = Vec::new();
    let mut records: Vec<IngestRecord> = Vec::with_capacity(issues.len());

    for issue in issues {
        if issue.title.trim().is_empty() {
            errors.push(format!("skipping {}: empty title", issue.external_id));
            continue;
        }

        records.push(build_ingest_record(issue));
    }

    // One transaction for the whole slice. On failure every write is rolled
    // back, so callers never observe partially ingested issues.
    let outcome = store
        .persist_ingest_batch(records, Utc::now())
        .await
        .map_err(|e| IngestError::Store(e.to_string()))?;

    Ok(BulkIngestionResult {
        total_processed: issues.len(),
        requirements_created: outcome.stories_created,
        trace_links_created: outcome.trace_links_created,
        errors,
    })
}

/// Build the deterministic write-set for one normalised issue.
fn build_ingest_record(issue: &NormalisedIssue) -> IngestRecord {
    let story_id = format!("story-{}", issue.external_id);

    let evidence = (!issue.url.is_empty()).then(|| IngestEvidence {
        id: format!("ev-{}-{}", issue.source, issue.external_id),
        kind: format!("{}_issue", issue.source),
        url: issue.url.clone(),
        metadata: serde_json::json!({
            "source": issue.source,
            "external_id": issue.external_id,
            "status": issue.status,
        }),
    });

    let trace_links: Vec<IngestTraceLink> = extract_req_refs(&issue.body)
        .into_iter()
        .map(|req_ref| IngestTraceLink {
            id: format!("tl-{story_id}-{req_ref}"),
            target_id: req_ref,
            relationship: "satisfies".to_string(),
            confidence: 0.8,
            source: issue.source.clone(),
        })
        .collect();

    IngestRecord {
        story_id,
        title: issue.title.clone(),
        description: issue.body.clone(),
        status: issue.status.clone(),
        evidence,
        trace_links,
    }
}

/// Perform a live ingest from all configured sources (GitHub + Jira + AgCord).
///
/// Fails loud with `IngestError::NoSourceConfigured` if no source has
/// its required env vars set — never returns a fake-success empty result.
pub async fn ingest_live(store: &Arc<dyn Store>) -> Result<BulkIngestionResult, IngestError> {
    let gh_cfg = GitHubConfig::from_env();
    let jira_cfg = JiraConfig::from_env();
    let agcord_cfg = AgcordConfig::from_env();

    if gh_cfg.is_none() && jira_cfg.is_none() && agcord_cfg.is_none() {
        return Err(IngestError::NoSourceConfigured);
    }

    let mut all_issues: Vec<NormalisedIssue> = Vec::new();

    if let Some(cfg) = gh_cfg {
        let issues = fetch_github_issues(&cfg).await?;
        tracing::info!(
            "GitHub: fetched {} issues from {}/{}",
            issues.len(),
            cfg.owner,
            cfg.repo
        );
        all_issues.extend(issues);
    }

    if let Some(cfg) = jira_cfg {
        let issues = fetch_jira_issues(&cfg).await?;
        tracing::info!(
            "Jira: fetched {} issues from project {}",
            issues.len(),
            cfg.project_key
        );
        all_issues.extend(issues);
    }

    if let Some(cfg) = agcord_cfg {
        match fetch_agcord_agents(&cfg).await {
            Ok(agents) => {
                tracing::info!("AgCord: fetched {} agents", agents.len());
                all_issues.extend(agents);
            }
            Err(e) => {
                tracing::warn!("AgCord agents fetch failed: {e}");
            }
        }
        match fetch_agcord_tasks(&cfg).await {
            Ok(tasks) => {
                tracing::info!("AgCord: fetched {} tasks", tasks.len());
                all_issues.extend(tasks);
            }
            Err(e) => {
                tracing::warn!("AgCord tasks fetch failed: {e}");
            }
        }
    }

    persist_issues(&all_issues, store).await
}

/// Ingest from a caller-supplied JSON payload (the existing `/ingest/github`
/// and `/ingest/jira` handler path). This is additive to the live fetch:
/// callers can push issues directly without GITHUB_TOKEN being set.
pub async fn ingest_from_payload(
    issues: &[Value],
    ref_field: &str,
    source: &str,
    store: &Arc<dyn Store>,
) -> BulkIngestionResult {
    let normalised: Vec<NormalisedIssue> = issues
        .iter()
        .filter_map(|v| {
            // Support both "title" (GitHub/Jira) and "name" (AgCord) fields
            let title = v
                .get("title")
                .or_else(|| v.get("name"))
                .and_then(|t| t.as_str())
                .map(|t| t.trim().to_string())
                .filter(|t| !t.is_empty())?;
            let external_id = v
                .get(ref_field)
                .map(|x| x.to_string().trim_matches('"').to_string())
                .unwrap_or_else(|| Uuid::new_v4().to_string());
            let body = v
                .get("body")
                .and_then(|b| b.as_str())
                .unwrap_or("")
                .to_string();
            let url = v
                .get("html_url")
                .or_else(|| v.get("url"))
                .and_then(|u| u.as_str())
                .unwrap_or("")
                .to_string();
            let status = v
                .get("state")
                .or_else(|| v.get("status"))
                .and_then(|s| s.as_str())
                .unwrap_or("open")
                .to_string();
            Some(NormalisedIssue {
                external_id,
                title,
                body,
                url,
                status,
                source: source.to_string(),
            })
        })
        .collect();

    persist_issues(&normalised, store)
        .await
        .unwrap_or_else(|e| BulkIngestionResult {
            total_processed: issues.len(),
            requirements_created: 0,
            trace_links_created: 0,
            errors: vec![e.to_string()],
        })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sqlite_store::SqliteStore;
    use sqlx::sqlite::SqlitePoolOptions;

    async fn mem_store() -> SqliteStore {
        let pool = SqlitePoolOptions::new()
            .max_connections(1)
            .connect("sqlite::memory:")
            .await
            .expect("open in-memory sqlite");
        sqlx::migrate!("./migrations-sqlite")
            .run(&pool)
            .await
            .expect("apply sqlite migrations");
        SqliteStore::new(pool)
    }

    fn issue(external_id: &str, title: &str) -> NormalisedIssue {
        NormalisedIssue {
            external_id: external_id.to_string(),
            title: title.to_string(),
            body: "closes REQ-001".to_string(),
            url: format!("https://example.test/issues/{external_id}"),
            status: "open".to_string(),
            source: "github".to_string(),
        }
    }

    #[tokio::test]
    async fn persist_issues_replay_does_not_duplicate() {
        let store: Arc<dyn Store> = Arc::new(mem_store().await);
        let issues = vec![issue("42", "Fix login")];

        let first = persist_issues(&issues, &store).await.expect("first ingest");
        assert_eq!(first.requirements_created, 1);
        assert_eq!(first.trace_links_created, 1);

        let second = persist_issues(&issues, &store)
            .await
            .expect("replay ingest");
        assert_eq!(second.requirements_created, 0);
        assert_eq!(second.trace_links_created, 0);

        assert_eq!(store.list_stories().await.unwrap().len(), 1);
        assert_eq!(store.list_evidence().await.unwrap().len(), 1);
        assert_eq!(
            store
                .list_trace_links_for_artifact("story-42".to_string())
                .await
                .unwrap()
                .len(),
            1
        );
    }

    #[tokio::test]
    async fn persist_issues_rolls_back_whole_batch_on_store_error() {
        let sqlite = mem_store().await;
        sqlx::query(
            "CREATE TRIGGER fail_story BEFORE INSERT ON stories \
             WHEN NEW.id = 'story-99' \
             BEGIN SELECT RAISE(ABORT, 'injected story failure'); END",
        )
        .execute(&sqlite.pool)
        .await
        .expect("install failure trigger");
        let store: Arc<dyn Store> = Arc::new(sqlite);

        let issues = vec![issue("1", "good issue"), issue("99", "bad issue")];
        let err = persist_issues(&issues, &store)
            .await
            .expect_err("batch must fail");
        assert!(
            err.to_string().contains("injected story failure"),
            "unexpected error: {err}"
        );

        assert!(store.list_stories().await.unwrap().is_empty());
        assert!(store.list_evidence().await.unwrap().is_empty());
        assert!(store
            .list_trace_links_for_artifact("story-1".to_string())
            .await
            .unwrap()
            .is_empty());
    }

    #[tokio::test]
    async fn empty_titles_are_skipped_without_opening_a_transaction() {
        let store: Arc<dyn Store> = Arc::new(mem_store().await);
        let issues = vec![issue("1", "   ")];
        let result = persist_issues(&issues, &store).await.expect("ingest");
        assert_eq!(result.total_processed, 1);
        assert_eq!(result.requirements_created, 0);
        assert_eq!(result.errors.len(), 1);
        assert!(store.list_stories().await.unwrap().is_empty());
    }
}
