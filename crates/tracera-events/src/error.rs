//! Crate-wide error type.
//!
//! All public APIs in `tracera-events` return [`Result<T>`] aliased to this
//! enum. Driver-level errors from `clickhouse-rs` are wrapped via the
//! [`Error::ClickHouse`] variant so callers don't need to depend on the
//! driver crate directly.

use thiserror::Error;

/// Result alias for this crate.
pub type Result<T> = std::result::Result<T, Error>;

/// Errors emitted from the `tracera-events` crate.
#[derive(Debug, Error)]
pub enum Error {
    /// Configuration was invalid (missing URL, bad credentials, etc).
    #[error("invalid ClickHouse configuration: {0}")]
    Config(String),

    /// ClickHouse driver / network error.
    #[error("clickhouse error: {0}")]
    ClickHouse(#[from] clickhouse::error::Error),

    /// A row failed to deserialize from a query response.
    #[error("failed to deserialize row from `{table}`: {message}")]
    Decode {
        /// Table the failing row came from.
        table: &'static str,
        /// Human-readable description of the failure.
        message: String,
    },

    /// I/O error (reading NDJSON, opening files, …).
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),

    /// The input event was rejected as invalid (e.g. missing required field).
    #[error("invalid event in stream `{stream}`: {message}")]
    InvalidEvent {
        /// Which stream the bad event belonged to.
        stream: &'static str,
        /// Why it was rejected.
        message: String,
    },

    /// A generic catch-all for unexpected conditions. New variants should
    /// be preferred over using this in new code.
    #[error("events error: {message}")]
    Other {
        /// Free-form description.
        message: String,
    },
}

impl Error {
    /// Convenience constructor for [`Error::InvalidEvent`].
    pub fn invalid_event(stream: &'static str, message: impl Into<String>) -> Self {
        Self::InvalidEvent {
            stream,
            message: message.into(),
        }
    }

    /// Convenience constructor for [`Error::Decode`].
    pub fn decode(table: &'static str, message: impl Into<String>) -> Self {
        Self::Decode {
            table,
            message: message.into(),
        }
    }

    /// Convenience constructor for [`Error::Other`].
    pub fn other(message: impl Into<String>) -> Self {
        Self::Other {
            message: message.into(),
        }
    }
}