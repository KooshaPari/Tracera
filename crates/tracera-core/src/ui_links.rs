//! API navigation payloads for clickable traceability links.

use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{ArtifactRef, TraceLink, TraceLinkType};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TraceLinkUiLink {
    pub id: Uuid,
    pub href: String,
    pub source_href: String,
    pub target_href: String,
    pub source_label: String,
    pub target_label: String,
    pub link_type: TraceLinkType,
}

impl TraceLink {
    /// Build the API payload used by UIs to render this link as clickable navigation.
    pub fn ui_link(&self) -> TraceLinkUiLink {
        TraceLinkUiLink {
            id: self.id,
            href: format!("/trace-links/{}", self.id),
            source_href: self.from.href(),
            target_href: self.to.href(),
            source_label: self.from.label(),
            target_label: self.to.label(),
            link_type: self.link_type,
        }
    }
}

impl ArtifactRef {
    pub fn label(&self) -> String {
        match self {
            Self::Requirement { id } => id.as_str().to_string(),
            Self::NonFunctionalRequirement { id } => id.as_str().to_string(),
            Self::Test { id } | Self::Journey { id } | Self::AgentRun { id } => id.clone(),
            Self::CodeEntity { id, .. } => id.clone(),
            Self::Evidence { id, .. } => id.clone(),
            Self::Document { id, range } => range
                .as_ref()
                .map(|range| format!("{}#{}", id, range))
                .unwrap_or_else(|| id.clone()),
        }
    }

    pub fn href(&self) -> String {
        match self {
            Self::Requirement { id } => format!("/requirements/{}", id.as_str()),
            Self::NonFunctionalRequirement { id } => format!("/requirements/{}", id.as_str()),
            Self::Test { id } => format!("/tests/{}", url_path_segment(id)),
            Self::CodeEntity { id, .. } => format!("/code/{}", url_path_segment(id)),
            Self::Journey { id } => format!("/journeys/{}", url_path_segment(id)),
            Self::AgentRun { id } => format!("/agent-runs/{}", url_path_segment(id)),
            Self::Evidence { id, .. } => format!("/evidence/{}", url_path_segment(id)),
            Self::Document { id, range } => {
                let mut href = format!("/documents/{}", url_path_segment(id));
                if let Some(range) = range {
                    href.push('#');
                    href.push_str(&url_path_segment(range));
                }
                href
            }
        }
    }
}

fn url_path_segment(value: &str) -> String {
    value
        .bytes()
        .flat_map(|byte| match byte {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                vec![byte as char]
            }
            _ => format!("%{byte:02X}").chars().collect(),
        })
        .collect()
}
