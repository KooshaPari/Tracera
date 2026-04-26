use async_trait::async_trait;
use crate::application::ports::outbound::Repository;
use crate::domain::entities::ExampleEntity;

#[async_trait]
pub trait CreateExample: Send + Sync {
    async fn execute(&self, name: String) -> anyhow::Result<ExampleEntity>;
}

pub struct CreateExampleUseCase<R: Repository> {
    repository: R,
}

impl<R: Repository> CreateExampleUseCase<R> {
    pub fn new(repository: R) -> Self {
        Self { repository }
    }
}

#[async_trait]
impl<R: Repository> CreateExample for CreateExampleUseCase<R> {
    async fn execute(&self, name: String) -> anyhow::Result<ExampleEntity> {
        let entity = ExampleEntity::new(name);
        self.repository.save(&entity).await?;
        Ok(entity)
    }
}
