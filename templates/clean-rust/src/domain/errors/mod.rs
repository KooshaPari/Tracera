//! Domain errors - use thiserror for rich error types
use thiserror::Error;

/// Domain error types
#[derive(Error, Debug)]
pub enum DomainError {
    #[error("entity not found: {0}")]
    NotFound(String),

    #[error("entity already exists: {0}")]
    AlreadyExists(String),

    #[error("validation error: {field} - {message}")]
    Validation { field: String, message: String },

    #[error("concurrency conflict: {0}")]
    Concurrency(String),

    #[error("business rule violation: {0}")]
    BusinessRule(String),
}

/// Result type for domain operations
pub type DomainResult<T> = Result<T, DomainError>;
