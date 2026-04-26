//! Domain entities - core business objects with identity
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Base entity trait for all domain objects
pub trait Entity: Send + Sync {
    fn id(&self) -> Uuid;
    fn created_at(&self) -> DateTime<Utc>;
    fn updated_at(&self) -> DateTime<Utc>;
}

/// Example domain entity
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Example {
    id: Uuid,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    name: String,
    description: Option<String>,
    active: bool,
}

impl Example {
    /// Create a new example entity
    pub fn new(name: String, description: Option<String>) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            created_at: now,
            updated_at: now,
            name,
            description,
            active: true,
        }
    }

    /// Validate domain rules
    pub fn validate(&self) -> Result<(), crate::domain::errors::DomainError> {
        if self.name.is_empty() {
            return Err(crate::domain::errors::DomainError::Validation {
                field: "name".to_string(),
                message: "name cannot be empty".to_string(),
            });
        }
        if self.name.len() > 100 {
            return Err(crate::domain::errors::DomainError::Validation {
                field: "name".to_string(),
                message: "name cannot exceed 100 characters".to_string(),
            });
        }
        Ok(())
    }

    // Getters
    pub fn id(&self) -> Uuid { self.id }
    pub fn created_at(&self) -> DateTime<Utc> { self.created_at }
    pub fn updated_at(&self) -> DateTime<Utc> { self.updated_at }
    pub fn name(&self) -> &str { &self.name }
    pub fn description(&self) -> Option<&str> { self.description.as_deref() }
    pub fn active(&self) -> bool { self.active }

    /// Deactivate entity
    pub fn deactivate(&mut self) {
        self.active = false;
        self.updated_at = Utc::now();
    }
}

impl Entity for Example {
    fn id(&self) -> Uuid { self.id }
    fn created_at(&self) -> DateTime<Utc> { self.created_at }
    fn updated_at(&self) -> DateTime<Utc> { self.updated_at }
}
