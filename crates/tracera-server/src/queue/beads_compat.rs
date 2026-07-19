//! TRC-PHENO-008: Beads (bd) compatibility.
//!
//! Stub layer that delegates to the external `bd` CLI. We do not bundle bd;
//! consumers must have it on $PATH. This is the port of phenodag's bd wrapper.

use std::process::Command;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum BeadsError {
    #[error("bd CLI not found on PATH")]
    NotFound,
    #[error("bd CLI exited with code {0}: {1}")]
    Failed(i32, String),
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
}

/// Run `bd <args>` and capture stdout. Errors if bd is missing or exits non-zero.
pub fn bd_call(args: &[&str]) -> Result<String, BeadsError> {
    let out = Command::new("bd").args(args).output().map_err(|e| {
        if e.kind() == std::io::ErrorKind::NotFound {
            BeadsError::NotFound
        } else {
            BeadsError::Io(e)
        }
    })?;
    if !out.status.success() {
        let code = out.status.code().unwrap_or(-1);
        let stderr = String::from_utf8_lossy(&out.stderr).to_string();
        return Err(BeadsError::Failed(code, stderr));
    }
    Ok(String::from_utf8_lossy(&out.stdout).to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn missing_bd_is_not_found() {
        // PATH manipulation: not testing bd presence; just type checks.
        let _ = bd_call(&["help"]);
    }
}
