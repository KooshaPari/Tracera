use serde_json::Value;

use super::{IngestError, NormalisedIssue};

/// Configuration for the GitHub ingest source.
pub struct GitHubConfig {
    pub token: String,
    pub owner: String,
    pub repo: String,
}

impl GitHubConfig {
    /// Read from environment. Returns `None` if any required variable is absent.
    pub fn from_env() -> Option<Self> {
        let token = std::env::var("GITHUB_TOKEN").ok()?;
        let repo_str = std::env::var("GITHUB_REPO").ok()?;
        let (owner, repo) = repo_str.split_once('/')?;
        Some(Self {
            token,
            owner: owner.to_string(),
            repo: repo.to_string(),
        })
    }
}

/// Fetch open GitHub issues using the REST API via reqwest.
///
/// Uses the `issues` endpoint — simpler than the full octocrab client so it
/// avoids a heavyweight async client build in tests, while still wrapping
/// reqwest just like octocrab does internally.
///
/// // wraps: reqwest 0.13
pub async fn fetch_github_issues(cfg: &GitHubConfig) -> Result<Vec<NormalisedIssue>, IngestError> {
    // wraps: reqwest 0.13
    let client = reqwest::Client::builder()
        .user_agent("tracera-ingest/0.1 (github.com/KooshaPari/Tracera)")
        .build()
        .map_err(|e| IngestError::Fetch(e.to_string()))?;

    let url = format!(
        "https://api.github.com/repos/{}/{}/issues?state=open&per_page=100",
        cfg.owner, cfg.repo
    );

    let resp = client
        .get(&url)
        .bearer_auth(&cfg.token)
        .header("Accept", "application/vnd.github+json")
        .header("X-GitHub-Api-Version", "2022-11-28")
        .send()
        .await
        .map_err(|e| IngestError::Fetch(format!("GitHub HTTP error: {e}")))?;

    if !resp.status().is_success() {
        let status = resp.status();
        let body = resp.text().await.unwrap_or_default();
        return Err(IngestError::Fetch(format!(
            "GitHub API returned {status}: {body}"
        )));
    }

    let items: Vec<Value> = resp
        .json()
        .await
        .map_err(|e| IngestError::Fetch(format!("GitHub JSON decode: {e}")))?;

    let issues = items
        .into_iter()
        .filter_map(|v| {
            let number = v.get("number")?.as_u64()?;
            let title = v.get("title")?.as_str()?.to_string();
            let body = v
                .get("body")
                .and_then(|b| b.as_str())
                .unwrap_or("")
                .to_string();
            let html_url = v
                .get("html_url")
                .and_then(|u| u.as_str())
                .unwrap_or("")
                .to_string();
            let state = v
                .get("state")
                .and_then(|s| s.as_str())
                .unwrap_or("open")
                .to_string();
            Some(NormalisedIssue {
                external_id: format!("gh-{number}"),
                title,
                body,
                url: html_url,
                status: state,
                source: "github".to_string(),
            })
        })
        .collect();

    Ok(issues)
}
