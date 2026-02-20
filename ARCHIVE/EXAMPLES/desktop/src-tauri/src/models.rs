use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub synced_at: Option<DateTime<Utc>>,
    pub is_deleted: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {
    pub id: String,
    pub project_id: String,
    pub item_type: ItemType,
    pub title: String,
    pub content: String,
    pub status: String,
    pub priority: Option<String>,
    pub version: i32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub synced_at: Option<DateTime<Utc>>,
    pub is_deleted: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ItemType {
    Feature,
    Code,
    Test,
    Api,
    Database,
    Wireframe,
    Documentation,
    Deployment,
}

impl ItemType {
    pub fn as_str(&self) -> &str {
        match self {
            ItemType::Feature => "feature",
            ItemType::Code => "code",
            ItemType::Test => "test",
            ItemType::Api => "api",
            ItemType::Database => "database",
            ItemType::Wireframe => "wireframe",
            ItemType::Documentation => "documentation",
            ItemType::Deployment => "deployment",
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "feature" => Some(ItemType::Feature),
            "code" => Some(ItemType::Code),
            "test" => Some(ItemType::Test),
            "api" => Some(ItemType::Api),
            "database" => Some(ItemType::Database),
            "wireframe" => Some(ItemType::Wireframe),
            "documentation" => Some(ItemType::Documentation),
            "deployment" => Some(ItemType::Deployment),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Link {
    pub id: String,
    pub project_id: String,
    pub source_id: String,
    pub target_id: String,
    pub link_type: String,
    pub metadata: Option<String>,
    pub created_at: DateTime<Utc>,
    pub is_deleted: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Agent {
    pub id: String,
    pub project_id: String,
    pub name: String,
    pub role: String,
    pub status: String,
    pub config: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub synced_at: Option<DateTime<Utc>>,
    pub is_deleted: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncQueueItem {
    pub id: i64,
    pub entity_type: String,
    pub entity_id: String,
    pub operation: OperationType,
    pub payload: String,
    pub created_at: DateTime<Utc>,
    pub retry_count: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum OperationType {
    Create,
    Update,
    Delete,
}

impl OperationType {
    pub fn as_str(&self) -> &str {
        match self {
            OperationType::Create => "create",
            OperationType::Update => "update",
            OperationType::Delete => "delete",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Attachment {
    pub id: String,
    pub entity_type: String,
    pub entity_id: String,
    pub file_name: String,
    pub file_path: String,
    pub file_size: i64,
    pub mime_type: Option<String>,
    pub created_at: DateTime<Utc>,
    pub synced_at: Option<DateTime<Utc>>,
    pub is_deleted: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConflictItem {
    pub id: i64,
    pub entity_type: String,
    pub entity_id: String,
    pub local_version: String,
    pub remote_version: String,
    pub created_at: DateTime<Utc>,
    pub resolved: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_item_type_conversion() {
        assert_eq!(ItemType::from_str("feature"), Some(ItemType::Feature));
        assert_eq!(ItemType::from_str("code"), Some(ItemType::Code));
        assert_eq!(ItemType::from_str("test"), Some(ItemType::Test));
        assert_eq!(ItemType::from_str("invalid"), None);
    }

    #[test]
    fn test_item_type_to_string() {
        assert_eq!(ItemType::Feature.as_str(), "feature");
        assert_eq!(ItemType::Code.as_str(), "code");
        assert_eq!(ItemType::Test.as_str(), "test");
    }
}
