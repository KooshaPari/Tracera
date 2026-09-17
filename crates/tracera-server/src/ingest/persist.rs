use std::sync::Arc;

use chrono::Utc;
use serde_json::Value;
use uuid::Uuid;

use crate::handlers::ingest_api::BulkIngestionResult;
use crate::store::Store;

use super::agcord::{fetch_agcord_agents, fetch_agcord_tasks, AgcordConfig};
use super::github::{fetch_github_issues, GitHubConfig};
use super::jira::{fetch_jira_issues, JiraConfig};
use super::trace_refs::extract_req_refs;
use super::{IngestError, NormalisedIssue};

/// Ingest a slice of normalised issues into the store.
///
/// For each issue:
/// - Creates a `Story` record (id = `"story-{external_id}"`).
/// - Creates an `EvidenceItem` linking back to the issue URL.
/// - Scans the body for requirement references and creates `TraceLink` records.
///
/// Returns a `BulkIngestionResult` summary.
pub async fn persist_issues(
    issues: &[NormalisedIssue],
    store: &Arc<dyn Store>,
) -> Result<BulkIngestionResult, IngestError> {
    let mut requirements_created = 0usize;
    let mut trace_links_created = 0usize;
    let mut errors: Vec<String> = Vec::new();
    let now = Utc::now();

    for issue in issues {
        if issue.title.trim().is_empty() {
            errors.push(format!("skipping {}: empty title", issue.external_id));
            continue;
        }

        let story_id = format!("story-{}", issue.external_id);

        // 1. Persist story record
        match store
            .create_story(
                story_id.clone(),
                None,
                issue.title.clone(),
                issue.body.clone(),
                issue.status.clone(),
                None,
                now,
            )
            .await
        {
            Ok(_) => requirements_created += 1,
            Err(e) => {
                errors.push(format!("create_story {}: {e}", issue.external_id));
                continue;
            }
        }

        // 2. Persist evidence item (back-link to issue URL)
        if !issue.url.is_empty() {
            let ev_id = format!("ev-{}", Uuid::new_v4());
            let meta = serde_json::json!({
                "source": issue.source,
                "external_id": issue.external_id,
                "status": issue.status,
            });
            if let Err(e) = store
                .create_evidence(
                    ev_id,
                    story_id.clone(),
                    format!("{}_issue", issue.source),
                    issue.url.clone(),
                    meta,
                    now,
                )
                .await
            {
                errors.push(format!("create_evidence {}: {e}", issue.external_id));
            }
        }

        // 3. Extract req references and create trace-links
        for req_ref in extract_req_refs(&issue.body) {
            let link_id = format!("tl-{}", Uuid::new_v4());
            match store
                .create_trace_link(
                    link_id,
                    story_id.clone(),
                    req_ref.clone(),
                    "satisfies".to_string(),
                    0.8,
                    issue.source.clone(),
                    now,
                )
                .await
            {
                Ok(_) => trace_links_created += 1,
                Err(e) => {
                    errors.push(format!(
                        "create_trace_link {} -> {req_ref}: {e}",
                        issue.external_id
                    ));
                }
            }
        }
    }

    Ok(BulkIngestionResult {
        total_processed: issues.len(),
        requirements_created,
        trace_links_created,
        errors,
    })
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
