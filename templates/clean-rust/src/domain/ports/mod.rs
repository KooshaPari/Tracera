//! Ports - interfaces that define boundaries between layers
use async_trait::async_trait;
use uuid::Uuid;
use crate::domain::entities::Example;
use crate::domain::errors::DomainError;

/// Repository port - outbound interface for persistence
#[async_trait]
pub trait Repository: Send + Sync {
    async fn save(&self, entity: &Example) -> Result<(), DomainError>;
    async fn find_by_id(&self, id: Uuid) -> Result<Option<Example>, DomainError>;
    async fn delete(&self, id: Uuid) -> Result<(), DomainError>;
    async fn list(&self, page: u32, page_size: u32) -> Result<Vec<Example>, DomainError>;
}
