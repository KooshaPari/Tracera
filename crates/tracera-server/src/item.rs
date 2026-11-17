//! Persisted Item wire contract. Optional extensions are preserved verbatim.
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Item {
    pub id: String,
    pub project_id: String,
    pub view: String,
    #[serde(rename = "type")]
    pub item_type: String,
    pub title: String,
    pub status: String,
    pub priority: String,
    pub version: u64,
    pub created_at: String,
    pub updated_at: String,
    #[serde(flatten)]
    pub extra: BTreeMap<String, Value>,
}

#[derive(Clone, Default)]
pub struct ItemFilter {
    pub project_id: Option<String>,
    pub status: Option<String>,
    pub view: Option<String>,
    pub priority: Option<String>,
}

pub struct ItemPage {
    pub items: Vec<Item>,
    pub total: i64,
}
