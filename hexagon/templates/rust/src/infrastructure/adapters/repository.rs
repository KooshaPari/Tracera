use async_trait::async_trait;
use sqlx::{Pool, Sqlite};
use crate::domain::entities::ExampleEntity;
use crate::application::ports::outbound::Repository as RepositoryPort;

pub struct SqliteRepository {
    pool: Pool<Sqlite>,
}

impl SqliteRepository {
    pub fn new(pool: Pool<Sqlite>) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl RepositoryPort for SqliteRepository {
    async fn save(&self, entity: &ExampleEntity) -> anyhow::Result<()> {
        // TODO: Implement SQLx query
        Ok(())
    }
}
