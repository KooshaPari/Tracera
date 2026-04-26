use crate::domain::entities::ExampleEntity;

pub struct ExampleService;

impl ExampleService {
    pub fn new() -> Self {
        Self
    }
    
    pub fn create_entity(&self, name: impl Into<String>) -> ExampleEntity {
        ExampleEntity::new(name)
    }
}
