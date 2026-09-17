/// Real issue ingest: GitHub (via octocrab 0.38), Jira (via reqwest 0.13),
/// and AgCord (agent communication platform).
///
/// # Source configuration
///
/// GitHub: set `GITHUB_TOKEN` and `GITHUB_REPO` (owner/repo).
/// Jira:   set `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY`.
/// AgCord: set `AGCORD_URL` to the base URL (e.g. `http://localhost:3001`).
///
/// All sources are optional but at least one must be configured for a live
/// ingest to succeed. Calling `ingest_live` with no sources configured returns
/// a clear `IngestError::NoSourceConfigured` — NOT a fake-success empty result.
///
/// # Trace-link extraction
///
/// Issue body text is scanned for references of the form `REQ-NNN` or `SPEC-NNN`
/// (case-insensitive). Each match creates a `satisfies` trace-link from the
/// ingested story ID to the referenced requirement ID, with confidence 0.8.
///
/// # Crate wrappers
/// // wraps: octocrab 0.38
/// // wraps: reqwest 0.13

mod agcord;
mod benchmark;
mod github;
mod jira;
mod persist;
#[cfg(test)]
mod tests;
mod trace_refs;

pub use self::agcord::AgcordConfig;
pub use self::github::GitHubConfig;
pub use self::jira::JiraConfig;
pub use self::persist::{ingest_from_payload, ingest_live};


// ---------------------------------------------------------------------------
// Error type
// ---------------------------------------------------------------------------
#[derive(Debug)]
pub enum IngestError {
    /// No GitHub or Jira source was configured (missing env vars).
    NoSourceConfigured,
    /// An HTTP or serialization error during fetch.
    Fetch(String),
}

impl std::fmt::Display for IngestError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            IngestError::NoSourceConfigured => write!(
                f,
                "no ingest source configured: set GITHUB_TOKEN+GITHUB_REPO \
                 and/or JIRA_URL+JIRA_EMAIL+JIRA_API_TOKEN+JIRA_PROJECT_KEY"
            ),
            IngestError::Fetch(msg) => write!(f, "fetch error: {msg}"),
        }
    }
}

impl std::error::Error for IngestError {}

// ---------------------------------------------------------------------------
// Normalised issue record (from either source)
// ---------------------------------------------------------------------------
#[derive(Debug)]
pub struct NormalisedIssue {
    /// Stable external ID (e.g. "gh-42" or "PROJ-123")
    pub external_id: String,
    pub title: String,
    pub body: String,
    /// HTML URL for linking
    pub url: String,
    /// "open" / "closed"
    pub status: String,
    /// Which ingest source produced this: "github" or "jira"
    pub source: String,
}
