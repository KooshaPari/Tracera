//! TRC-PHENO-006: Mangled-git + no-git tolerant scanner.
//!
//! Port of phenodag's cmdScan. Scans a directory for git worktrees, falling
//! back to plain filesystem walk when no .git dir is present.

use std::path::{Path, PathBuf};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ScanError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
}

#[derive(Debug, Clone)]
pub struct ScanEntry {
    pub path: PathBuf,
    pub is_git: bool,
    pub head_sha: Option<String>,
}

/// Scan a directory for git worktrees. Tolerant of: missing .git, mangled
/// .git, shallow clones, worktrees-within-worktrees.
pub fn scan_dir(root: &Path) -> Result<Vec<ScanEntry>, ScanError> {
    let mut out = Vec::new();
    scan_recursive(root, &mut out)?;
    Ok(out)
}

fn scan_recursive(dir: &Path, out: &mut Vec<ScanEntry>) -> Result<(), ScanError> {
    let git = dir.join(".git");
    let (is_git, head) = if git.exists() {
        // Try HEAD; if it fails (mangled git), still report as git with no head.
        let head = std::fs::read_to_string(git.join("HEAD")).ok()
            .and_then(|s| s.trim().strip_prefix("ref: ").map(String::from));
        (true, head)
    } else {
        (false, None)
    };
    out.push(ScanEntry { path: dir.to_path_buf(), is_git, head_sha: head });

    // Recurse one level (avoid deep walk; P2 is a seed, not a full tree walker)
    if let Ok(rd) = std::fs::read_dir(dir) {
        for e in rd.flatten() {
            let p = e.path();
            if p.is_dir() && p.file_name().map(|n| n != ".git").unwrap_or(true) {
                let _ = scan_recursive(&p, out);
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    #[test] fn empty_dir() {
        let tmp = std::env::temp_dir().join(format!("scan_test_{}", std::process::id()));
        fs::create_dir_all(&tmp).unwrap();
        let r = scan_dir(&tmp).unwrap();
        assert!(!r.is_empty());
        assert!(r[0].path.ends_with(tmp.file_name().unwrap()));
        fs::remove_dir_all(&tmp).ok();
    }
}
