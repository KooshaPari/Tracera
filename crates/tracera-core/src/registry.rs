// SPDX-License-Identifier: MIT OR Apache-2.0
// Copyright 2026 Koosha Pari

//! Content-addressed model registry.
//!
//! Phase 4 of the 2026-06-09 Tracera decouple plan.
//! Ported from `Tracera/backend/internal/ml/registry.go` (247 LOC).
//!
//! Provides:
//! - `ModelRegistry` with disk-backed index + per-blob content addressing (SHA-256)
//! - `Save(name, version, format, bytes) -> ModelEntry` (rejects overwrite)
//! - `Load(name, version_or_empty)` (uses pin if version is empty)
//! - `Get(name, version)` (validates against pin when version is empty)
//! - `List(name)` (all versions, sorted newest-first)
//! - `Pin(name, version)`
//! - Per-format extensions: sklearn (.joblib), pytorch (.pt), onnx (.onnx)
//! - Name + version validation: kebab/snake + semver

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use thiserror::Error;

/// Format of the serialized model artifact.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ModelFormat {
    Sklearn,
    Pytorch,
    Onnx,
}

impl ModelFormat {
    pub fn extension(&self) -> &'static str {
        match self {
            Self::Sklearn => ".joblib",
            Self::Pytorch => ".pt",
            Self::Onnx => ".onnx",
        }
    }
}

/// One persisted model entry.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ModelEntry {
    pub name: String,
    pub version: String,
    pub sha256: String,
    pub format: ModelFormat,
    pub artifact_path: String,
    pub metadata: BTreeMap<String, serde_json::Value>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct PinnedVersion {
    version: String,
    sha256: String,
}

#[derive(Debug, Default, Clone, PartialEq, Serialize, Deserialize)]
struct RegistryIndex {
    #[serde(default)]
    models: BTreeMap<String, BTreeMap<String, ModelEntry>>,
    #[serde(default)]
    pins: BTreeMap<String, PinnedVersion>,
}

#[derive(Debug, Error)]
pub enum RegistryError {
    #[error("invalid model name: {0}")]
    InvalidName(String),
    #[error("invalid model version (must be semver): {0}")]
    InvalidVersion(String),
    #[error("unsupported format: {0:?}")]
    UnsupportedFormat(ModelFormat),
    #[error("model {name} version {version} already exists")]
    AlreadyExists { name: String, version: String },
    #[error("model {0} is not registered")]
    NotFound(String),
    #[error("model {0} has no pinned version")]
    NoPin(String),
    #[error("model {name} version {version} is not registered")]
    VersionNotFound { name: String, version: String },
    #[error("pinned model SHA256 mismatch for {0}")]
    PinShaMismatch(String),
    #[error("artifact SHA256 mismatch (expected {expected}, got {actual})")]
    ShaMismatch { expected: String, actual: String },
    #[error("io: {0}")]
    Io(#[from] io::Error),
    #[error("json: {0}")]
    Json(#[from] serde_json::Error),
}

const INDEX_FILE: &str = "registry.json";

/// On-disk model registry.
pub struct ModelRegistry {
    root: PathBuf,
}

impl ModelRegistry {
    /// Open or create a registry rooted at `root`.
    pub fn open(root: impl Into<PathBuf>) -> Result<Self, RegistryError> {
        let root = root.into();
        fs::create_dir_all(&root)?;
        Ok(Self { root })
    }

    pub fn root(&self) -> &Path {
        &self.root
    }

    /// Save a new model version. Errors if the (name, version) pair already exists.
    pub fn save(
        &self,
        name: &str,
        version: &str,
        format: ModelFormat,
        bytes: &[u8],
        metadata: BTreeMap<String, serde_json::Value>,
    ) -> Result<ModelEntry, RegistryError> {
        validate_name(name)?;
        validate_version(version)?;

        let mut index = self.read_index()?;
        if index
            .models
            .get(name)
            .and_then(|v| v.get(version))
            .is_some()
        {
            return Err(RegistryError::AlreadyExists {
                name: name.to_string(),
                version: version.to_string(),
            });
        }

        let digest = sha256_hex(bytes);
        let blob_dir = self
            .root
            .join("models")
            .join(name)
            .join(version)
            .join("blobs");
        fs::create_dir_all(&blob_dir)?;
        let artifact = blob_dir.join(format!("{digest}{}", format.extension()));
        fs::write(&artifact, bytes)?;

        let rel = relative_to_root(&self.root, &artifact)?;

        let entry = ModelEntry {
            name: name.to_string(),
            version: version.to_string(),
            sha256: digest,
            format,
            artifact_path: rel,
            metadata,
            created_at: Utc::now(),
        };
        index
            .models
            .entry(name.to_string())
            .or_default()
            .insert(version.to_string(), entry.clone());
        // Auto-pin first version
        index.pins.entry(name.to_string()).or_insert(PinnedVersion {
            version: entry.version.clone(),
            sha256: entry.sha256.clone(),
        });
        self.write_index(&index)?;
        Ok(entry)
    }

    /// Load model bytes for `name` and `version` (or the pinned version if empty).
    /// Validates SHA-256 on read.
    pub fn load(&self, name: &str, version: &str) -> Result<(Vec<u8>, ModelEntry), RegistryError> {
        let entry = self.get(name, version)?;
        let path = self.root.join(&entry.artifact_path);
        let bytes = fs::read(&path)?;
        let actual = sha256_hex(&bytes);
        if actual != entry.sha256 {
            return Err(RegistryError::ShaMismatch {
                expected: entry.sha256.clone(),
                actual,
            });
        }
        Ok((bytes, entry))
    }

    /// Get metadata for a (name, version-or-empty) pair.
    pub fn get(&self, name: &str, version: &str) -> Result<ModelEntry, RegistryError> {
        let index = self.read_index()?;
        let versions = index
            .models
            .get(name)
            .ok_or_else(|| RegistryError::NotFound(name.to_string()))?;
        if versions.is_empty() {
            return Err(RegistryError::NotFound(name.to_string()));
        }
        let resolved = if version.is_empty() {
            let pin = index
                .pins
                .get(name)
                .ok_or_else(|| RegistryError::NoPin(name.to_string()))?;
            pin.version.clone()
        } else {
            version.to_string()
        };
        let entry = versions
            .get(&resolved)
            .ok_or_else(|| RegistryError::VersionNotFound {
                name: name.to_string(),
                version: resolved.clone(),
            })?
            .clone();
        if version.is_empty() {
            let pin = index.pins.get(name).expect("pin checked above");
            if entry.sha256 != pin.sha256 {
                return Err(RegistryError::PinShaMismatch(name.to_string()));
            }
        }
        Ok(entry)
    }

    /// List all entries, sorted newest-first. If `name` is provided, filter to that model.
    pub fn list(&self, name: &str) -> Result<Vec<ModelEntry>, RegistryError> {
        let index = self.read_index()?;
        let mut entries: Vec<ModelEntry> = Vec::new();
        for (model_name, versions) in &index.models {
            if !name.is_empty() && model_name != name {
                continue;
            }
            for entry in versions.values() {
                entries.push(entry.clone());
            }
        }
        entries.sort_by(|a, b| b.created_at.cmp(&a.created_at));
        Ok(entries)
    }

    /// Pin a specific version of a model.
    pub fn pin(&self, name: &str, version: &str) -> Result<ModelEntry, RegistryError> {
        let entry = self.get(name, version)?;
        let mut index = self.read_index()?;
        index.pins.insert(
            name.to_string(),
            PinnedVersion {
                version: entry.version.clone(),
                sha256: entry.sha256.clone(),
            },
        );
        self.write_index(&index)?;
        Ok(entry)
    }

    fn read_index(&self) -> Result<RegistryIndex, RegistryError> {
        let path = self.root.join(INDEX_FILE);
        match fs::read(&path) {
            Ok(bytes) => Ok(serde_json::from_slice(&bytes)?),
            Err(e) if e.kind() == io::ErrorKind::NotFound => Ok(RegistryIndex::default()),
            Err(e) => Err(RegistryError::Io(e)),
        }
    }

    fn write_index(&self, index: &RegistryIndex) -> Result<(), RegistryError> {
        let bytes = serde_json::to_vec_pretty(index)?;
        let path = self.root.join(INDEX_FILE);
        fs::write(path, bytes)?;
        Ok(())
    }
}

/// Strict character whitelist: kebab/snake + digits + dot + underscore + dash.
pub fn is_valid_name(value: &str) -> bool {
    !value.is_empty()
        && value
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_' || b == b'.')
}

/// Strict semver: `MAJOR.MINOR.PATCH[-pre][+build]` where pre/build are
/// dot-separated `[0-9A-Za-z-]` tokens.
pub fn is_valid_semver(value: &str) -> bool {
    let mut parts = value.splitn(2, '+');
    let main = parts.next().unwrap_or("");
    let build = parts.next();
    if let Some(b) = build {
        if !is_valid_semver_tail(b) {
            return false;
        }
    }
    let mut parts = main.splitn(2, '-');
    let version = parts.next().unwrap_or("");
    let pre = parts.next();
    if let Some(p) = pre {
        if !is_valid_semver_tail(p) {
            return false;
        }
    }
    let mut nums = version.splitn(3, '.');
    let major = nums.next().unwrap_or("");
    let minor = nums.next().unwrap_or("");
    let patch = nums.next().unwrap_or("");
    if nums.next().is_some() {
        return false;
    }
    is_all_digits(major) && is_all_digits(minor) && is_all_digits(patch)
}

fn is_valid_semver_tail(s: &str) -> bool {
    if s.is_empty() {
        return false;
    }
    s.split('.')
        .all(|t| !t.is_empty() && t.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-'))
}

fn is_all_digits(s: &str) -> bool {
    !s.is_empty() && s.bytes().all(|b| b.is_ascii_digit())
}

fn validate_name(value: &str) -> Result<(), RegistryError> {
    if !is_valid_name(value) {
        return Err(RegistryError::InvalidName(value.to_string()));
    }
    Ok(())
}

fn validate_version(value: &str) -> Result<(), RegistryError> {
    if !is_valid_semver(value) {
        return Err(RegistryError::InvalidVersion(value.to_string()));
    }
    Ok(())
}

fn sha256_hex(bytes: &[u8]) -> String {
    use sha2::{Digest, Sha256};
    let mut h = Sha256::new();
    h.update(bytes);
    let digest = h.finalize();
    let mut out = String::with_capacity(64);
    for byte in digest.iter() {
        use std::fmt::Write;
        write!(out, "{:02x}", byte).unwrap();
    }
    out
}

fn relative_to_root(root: &Path, path: &Path) -> Result<String, RegistryError> {
    let rel = path.strip_prefix(root).unwrap_or(path);
    Ok(rel.to_string_lossy().replace('\\', "/"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    fn sample_entry(name: &str, version: &str) -> ModelEntry {
        ModelEntry {
            name: name.to_string(),
            version: version.to_string(),
            sha256: "deadbeef".to_string(),
            format: ModelFormat::Sklearn,
            artifact_path: format!("models/{name}/{version}/blobs/x.joblib"),
            metadata: BTreeMap::new(),
            created_at: Utc::now(),
        }
    }

    #[test]
    fn safe_name_pattern_matches_valid() {
        assert!(is_valid_name("foo"));
        assert!(is_valid_name("foo-bar_baz"));
        assert!(is_valid_name("v1.0.0"));
        assert!(is_valid_name("a"));
        assert!(is_valid_name("m"));
        assert!(!is_valid_name("foo bar"));
        assert!(!is_valid_name("foo/bar"));
        assert!(!is_valid_name(""));
    }

    #[test]
    fn semver_pattern_matches_valid() {
        assert!(is_valid_semver("1.0.0"));
        assert!(is_valid_semver("1.0.0-rc.1"));
        assert!(is_valid_semver("1.0.0+build.42"));
        assert!(is_valid_semver("1.0.0-rc.1+build.42"));
        assert!(!is_valid_semver("1.0"));
        assert!(!is_valid_semver("v1.0.0"));
        assert!(!is_valid_semver("1.0.0.0"));
        assert!(!is_valid_semver(""));
    }

    #[test]
    fn save_load_roundtrip() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        let bytes = b"fake-model-payload";
        let entry = reg
            .save(
                "my-model",
                "1.0.0",
                ModelFormat::Sklearn,
                bytes,
                BTreeMap::new(),
            )
            .unwrap();
        assert_eq!(entry.name, "my-model");
        assert_eq!(entry.version, "1.0.0");
        let (loaded, lentry) = reg.load("my-model", "1.0.0").unwrap();
        assert_eq!(loaded, bytes);
        assert_eq!(entry.sha256, lentry.sha256);
    }

    #[test]
    fn save_rejects_duplicate() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        reg.save("m", "1.0.0", ModelFormat::Onnx, b"a", BTreeMap::new())
            .unwrap();
        let err = reg
            .save("m", "1.0.0", ModelFormat::Onnx, b"a", BTreeMap::new())
            .unwrap_err();
        assert!(matches!(err, RegistryError::AlreadyExists { .. }));
    }

    #[test]
    fn get_uses_pin_when_version_empty() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        reg.save("m", "1.0.0", ModelFormat::Pytorch, b"a", BTreeMap::new())
            .unwrap();
        reg.save("m", "2.0.0", ModelFormat::Pytorch, b"b", BTreeMap::new())
            .unwrap();
        // Auto-pin is the first version saved (1.0.0)
        let entry = reg.get("m", "").unwrap();
        assert_eq!(entry.version, "1.0.0");
        // Pin to 2.0.0
        reg.pin("m", "2.0.0").unwrap();
        let entry = reg.get("m", "").unwrap();
        assert_eq!(entry.version, "2.0.0");
    }

    #[test]
    fn list_returns_all_versions_newest_first() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        reg.save("a", "1.0.0", ModelFormat::Sklearn, b"x", BTreeMap::new())
            .unwrap();
        std::thread::sleep(std::time::Duration::from_millis(10));
        reg.save("a", "1.1.0", ModelFormat::Sklearn, b"y", BTreeMap::new())
            .unwrap();
        std::thread::sleep(std::time::Duration::from_millis(10));
        reg.save("a", "2.0.0", ModelFormat::Sklearn, b"z", BTreeMap::new())
            .unwrap();
        let entries = reg.list("a").unwrap();
        assert_eq!(entries.len(), 3);
        assert_eq!(entries[0].version, "2.0.0");
        assert_eq!(entries[2].version, "1.0.0");
    }

    #[test]
    fn list_filters_by_name() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        reg.save("a", "1.0.0", ModelFormat::Sklearn, b"x", BTreeMap::new())
            .unwrap();
        reg.save("b", "1.0.0", ModelFormat::Sklearn, b"y", BTreeMap::new())
            .unwrap();
        assert_eq!(reg.list("a").unwrap().len(), 1);
        assert_eq!(reg.list("").unwrap().len(), 2);
    }

    #[test]
    fn invalid_name_rejected() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        let err = reg
            .save("foo bar", "1.0.0", ModelFormat::Onnx, b"x", BTreeMap::new())
            .unwrap_err();
        assert!(matches!(err, RegistryError::InvalidName(_)));
    }

    #[test]
    fn invalid_version_rejected() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        let err = reg
            .save("foo", "1.0", ModelFormat::Onnx, b"x", BTreeMap::new())
            .unwrap_err();
        assert!(matches!(err, RegistryError::InvalidVersion(_)));
    }

    #[test]
    fn not_found_errors() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        let err = reg.get("missing", "").unwrap_err();
        assert!(matches!(err, RegistryError::NotFound(_)));
    }

    #[test]
    fn version_not_found_errors() {
        let dir = tempdir().unwrap();
        let reg = ModelRegistry::open(dir.path()).unwrap();
        reg.save("m", "1.0.0", ModelFormat::Onnx, b"x", BTreeMap::new())
            .unwrap();
        let err = reg.get("m", "9.9.9").unwrap_err();
        assert!(matches!(err, RegistryError::VersionNotFound { .. }));
    }

    #[test]
    fn model_format_extension() {
        assert_eq!(ModelFormat::Sklearn.extension(), ".joblib");
        assert_eq!(ModelFormat::Pytorch.extension(), ".pt");
        assert_eq!(ModelFormat::Onnx.extension(), ".onnx");
    }

    #[test]
    fn sample_entry_helper() {
        let e = sample_entry("a", "1.0.0");
        assert_eq!(e.name, "a");
        assert_eq!(e.version, "1.0.0");
    }
}
