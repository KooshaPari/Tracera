use async_trait::async_trait;
use crate::domain::entities::ExampleEntity;

#[async_trait]
pub trait Repository: Send + Sync {
    async fn find_by_id(&self, id: uuid::Uuid) -> anyhow::Result<Option<ExampleEntity>>;
    async fn save(&self, entity: &ExampleEntity) -> anyhow::Result<()>;
}

#[async_trait]
pub trait Service: Send + Sync {
    async fn create(&self, name: String) -> anyhow::Result<ExampleEntity>;
    async fn get(&self, id: uuid::Uuid) -> anyhow::Result<Option<ExampleEntity>>;
}
