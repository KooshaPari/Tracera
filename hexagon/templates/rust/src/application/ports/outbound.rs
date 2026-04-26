use async_trait::async_trait;
use crate::domain::entities::ExampleEntity;

#[async_trait]
pub trait Repository: Send + Sync {
    async fn save(&self, entity: &ExampleEntity) -> anyhow::Result<()>;
}
