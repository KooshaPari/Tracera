use regex::Regex;
use reqwest::Url;
use serde_json::Value;

use super::{IngestError, NormalisedIssue};

/// Configuration for the Jira ingest source.
pub struct JiraConfig {
    pub base_url: String,
    pub email: String,
    pub api_token: String,
    pub project_key: String,
}

pub(crate) const JIRA_ERROR_BODY_LIMIT: usize = 512;

pub(crate) fn validate_jira_base_url(raw: &str) -> Result<Url, IngestError> {
    let raw = raw.trim();
    let authority = raw
        .strip_prefix("https://")
        .filter(|authority| !authority.is_empty() && !authority.starts_with('/'));
    if authority.is_none() {
        return Err(IngestError::Fetch(
            "Jira URL must use HTTPS and include a host".to_string(),
        ));
    }
    let mut base =
        Url::parse(raw).map_err(|e| IngestError::Fetch(format!("invalid Jira URL: {e}")))?;
    if base.scheme() != "https" {
        return Err(IngestError::Fetch("Jira URL must use HTTPS".to_string()));
    }
    if base.host_str().is_none() || !base.username().is_empty() || base.password().is_some() {
        return Err(IngestError::Fetch(
            "Jira URL must contain a host and no embedded credentials".to_string(),
        ));
    }
    if base.query().is_some() || base.fragment().is_some() {
        return Err(IngestError::Fetch(
            "Jira URL must not contain a query or fragment".to_string(),
        ));
    }
    if !base.path().ends_with('/') {
        base.set_path(&format!("{}/", base.path()));
    }
    Ok(base)
}

pub(crate) fn redact_upstream_body(body: &str) -> String {
    let sensitive = Regex::new(
        r#"(?i)(authorization|api[_-]?token|password|secret|token)\s*[:=]\s*("[^"]*"|'[^']*'|[^,\s}]+)"#,
    )
    .expect("valid upstream redaction regex");
    let redacted = sensitive.replace_all(body, "$1=[REDACTED]");
    redacted.chars().take(JIRA_ERROR_BODY_LIMIT).collect()
}

impl JiraConfig {
    /// Read from environment. Returns `None` if any required variable is absent.
    pub fn from_env() -> Option<Self> {
        Some(Self {
            base_url: std::env::var("JIRA_URL").ok()?,
            email: std::env::var("JIRA_EMAIL").ok()?,
            api_token: std::env::var("JIRA_API_TOKEN").ok()?,
            project_key: std::env::var("JIRA_PROJECT_KEY").ok()?,
        })
    }
}

/// Fetch Jira issues via REST v3.
///
/// // wraps: reqwest 0.13
pub async fn fetch_jira_issues(cfg: &JiraConfig) -> Result<Vec<NormalisedIssue>, IngestError> {
    // wraps: reqwest 0.13
    let base_url = validate_jira_base_url(&cfg.base_url)?;
    let origin = (
        base_url.scheme().to_string(),
        base_url.host_str().unwrap_or_default().to_string(),
        base_url.port_or_known_default(),
    );
    let client = reqwest::Client::builder()
        .user_agent("tracera-ingest/0.1 (github.com/KooshaPari/Tracera)")
        // Never follow a redirect to another origin with Jira Basic auth.
        .redirect(reqwest::redirect::Policy::custom(move |attempt| {
            let target = attempt.url();
            let same_origin = target.scheme() == origin.0
                && target.host_str().unwrap_or_default() == origin.1
                && target.port_or_known_default() == origin.2;
            if same_origin {
                attempt.follow()
            } else {
                attempt.stop()
            }
        }))
        .build()
        .map_err(|e| IngestError::Fetch(e.to_string()))?;

    let mut url = base_url
        .join("rest/api/3/search")
        .map_err(|e| IngestError::Fetch(format!("invalid Jira URL: {e}")))?;
    url.query_pairs_mut()
        .append_pair("jql", &format!("project={}", cfg.project_key))
        .append_pair("maxResults", "100")
        .append_pair("fields", "summary,description,status,issuetype");

    use base64::Engine as _;
    let auth = base64::engine::general_purpose::STANDARD
        .encode(format!("{}:{}", cfg.email, cfg.api_token));

    let resp = client
        .get(url)
        .header("Authorization", format!("Basic {auth}"))
        .header("Accept", "application/json")
        .send()
        .await
        .map_err(|e| IngestError::Fetch(format!("Jira HTTP error: {e}")))?;

    if !resp.status().is_success() {
        let status = resp.status();
        let body = resp.text().await.unwrap_or_default();
        return Err(IngestError::Fetch(format!(
            "Jira API returned {status}: {}",
            redact_upstream_body(&body)
        )));
    }

    let payload: Value = resp
        .json()
        .await
        .map_err(|e| IngestError::Fetch(format!("Jira JSON decode: {e}")))?;

    let issues_arr = payload
        .get("issues")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();

    let issues = issues_arr
        .into_iter()
        .filter_map(|v| {
            let key = v.get("key")?.as_str()?.to_string();
            let fields = v.get("fields")?;
            let title = fields
                .get("summary")
                .and_then(|s| s.as_str())
                .unwrap_or("")
                .to_string();
            // Jira description is an Atlassian Document Format (ADF) object in v3;
            // we flatten it to a JSON string for body storage.
            let body = fields
                .get("description")
                .map(|d| d.to_string())
                .unwrap_or_default();
            let status = fields
                .get("status")
                .and_then(|s| s.get("name"))
                .and_then(|n| n.as_str())
                .unwrap_or("open")
                .to_lowercase();
            Some(NormalisedIssue {
                external_id: key.clone(),
                title,
                body,
                url: String::new(), // Jira REST v3 does not return htmlUrl in search
                status,
                source: "jira".to_string(),
            })
        })
        .collect();

    Ok(issues)
}
