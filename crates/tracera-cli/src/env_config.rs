//! Non-clobbering local configuration preparation.
//!
//! The env-file parser here is a minimal Compose-compatible implementation
//! that accepts both `=` and `:` separators, `export` prefixes, comments
//! (inside and outside quoted values), double-quoted escape sequences
//! (`\n`, `\t`, `\r`, `\\`), and single-quoted literal values.  It does
//! **not** attempt full POSIX shell expansion; it covers precisely the
//! subset that Docker Compose `--env-file` accepts.
use anyhow::Context;
use std::collections::HashMap;
use std::io::Write;
use std::path::Path;

/// Parse a single `.env` line, returning `Some((key, value))` or `None` for
/// blank / comment-only lines.  Returns `Err` only for genuinely malformed
/// lines (unterminated quote, no separator at all).  The error must never
/// echo the line content to avoid leaking secrets.
fn parse_env_line(line: &str) -> anyhow::Result<Option<(String, String)>> {
    let trimmed = line.trim();
    if trimmed.is_empty() || trimmed.starts_with('#') {
        return Ok(None);
    }
    // Strip optional `export` prefix.
    let rest = if let Some(r) = trimmed.strip_prefix("export ") {
        r.trim_start()
    } else {
        trimmed
    };
    // Find first `=` or `:` separator.
    let sep = rest.find(['=', ':']);
    let sep_idx = match sep {
        Some(i) => i,
        None => {
            anyhow::bail!("env line has no key-value separator");
        }
    };
    let key = rest[..sep_idx].trim().to_string();
    if key.is_empty() {
        anyhow::bail!("env line has empty key");
    }
    let raw_val = rest[sep_idx + 1..].trim_start();

    let value = if let Some(after_opening) = raw_val.strip_prefix('\'') {
        // Single-quoted: content up to next `'`; no escape processing.
        match after_opening.find('\'') {
            Some(end) => after_opening[..end].to_string(),
            None => anyhow::bail!("unterminated single quote in env value"),
        }
    } else if let Some(after_opening) = raw_val.strip_prefix('"') {
        // Double-quoted: process `\n`, `\t`, `\r`, `\\`; `#` is not a comment.
        let mut chars = after_opening.chars();
        let mut out = String::new();
        loop {
            match chars.next() {
                None => anyhow::bail!("unterminated double quote in env value"),
                Some('"') => break,
                Some('\\') => {
                    match chars.next() {
                        None => anyhow::bail!("unterminated escape in env value"),
                        Some('\\') => out.push('\\'),
                        Some('n') => out.push('\n'),
                        Some('t') => out.push('\t'),
                        Some('r') => out.push('\r'),
                        Some(c) => {
                            out.push('\\');
                            out.push(c);
                        }
                    }
                }
                Some(c) => out.push(c),
            }
        }
        // Everything after the closing `"` is a trailing comment — ignore it.
        out
    } else {
        // Unquoted: strip trailing inline comment (`# ...`).
        match raw_val.find('#') {
            Some(pos) => raw_val[..pos].trim_end().to_string(),
            None => raw_val.trim_end().to_string(),
        }
    };
    Ok(Some((key, value)))
}

/// Parse all lines in an env file body, applying last-assignment-wins.
/// Returns `Err` if any line is genuinely malformed (unterminated quote,
/// no separator).  The error never echoes the offending value.
fn parse_env_entries(body: &str) -> anyhow::Result<HashMap<String, String>> {
    let mut map = HashMap::new();
    for line in body.lines() {
        if let Some((key, value)) = parse_env_line(line)? {
            map.insert(key, value);
        }
    }
    Ok(map)
}

pub fn validate_env_file(path: &Path) -> anyhow::Result<()> {
    let metadata = std::fs::metadata(path).with_context(|| format!("configuration {} is missing or unreadable; initialize an absent file with `tracera init`", path.display()))?;
    anyhow::ensure!(
        metadata.is_file(),
        "configuration {} is not a regular file",
        path.display()
    );
    let body = std::fs::read_to_string(path)
        .with_context(|| format!("reading configuration {}", path.display()))?;
    let entries = parse_env_entries(&body).map_err(|_| {
        anyhow::anyhow!(
            "configuration {} has invalid env syntax; edit it explicitly",
            path.display()
        )
    })?;
    let password = entries.get("POSTGRES_PASSWORD");
    anyhow::ensure!(
        password.is_some_and(|value: &String| !value.trim().is_empty()),
        "configuration {} requires nonempty POSTGRES_PASSWORD; edit the existing file explicitly",
        path.display()
    );
    Ok(())
}

/// Create only an absent configuration; preserve every existing entry.
pub fn ensure_env_file(env_file: &Path, local_port: u16) -> anyhow::Result<()> {
    match std::fs::symlink_metadata(env_file) {
        Ok(_) => return validate_env_file(env_file),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
        Err(error) => {
            return Err(error).with_context(|| format!("checking {}", env_file.display()))
        }
    }
    if let Some(parent) = env_file.parent() {
        std::fs::create_dir_all(parent)
            .with_context(|| format!("creating {}", parent.display()))?;
    }
    let mut options = std::fs::OpenOptions::new();
    options.write(true).create_new(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.mode(0o600);
    }
    let mut file = options
        .open(env_file)
        .with_context(|| format!("creating absent configuration {}", env_file.display()))?;
    let body = format!("# Generated by Tracera\nPOSTGRES_PASSWORD={}\nTRACERA_LOCAL_PORT={}\nTRACERA_LOCAL_BIND_ADDR=127.0.0.1\n", generate_password(), local_port);
    file.write_all(body.as_bytes())
        .with_context(|| format!("writing {}", env_file.display()))?;
    Ok(())
}

fn generate_password() -> String {
    let bytes: [u8; 24] = rand::random();
    // Avoid shell-quoting issues — keep it URL-safe ASCII.
    use std::fmt::Write;
    let mut s = String::with_capacity(32);
    for b in bytes {
        let _ = write!(s, "{b:02x}");
    }
    s
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_valid_existing_bytes() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join(".env.local");
        let body = "# fixture\nPOSTGRES_PASSWORD=nonsecret-sentinel\nCUSTOM=preserved\n";
        std::fs::write(&path, body).unwrap();
        ensure_env_file(&path, 1234).unwrap();
        assert_eq!(std::fs::read_to_string(&path).unwrap(), body);
    }

    #[test]
    fn rejects_invalid_existing_without_clobber_or_secret_errors() {
        for body in [
            "CUSTOM=nonsecret-sentinel\n",
            "POSTGRES_PASSWORD=\n",
            "POSTGRES_PASSWORD=\"\"\n",
            "POSTGRES_PASSWORD= # comment\n",
            "POSTGRES_PASSWORD=nonsecret-sentinel\nPOSTGRES_PASSWORD=\n",
            "POSTGRES_PASSWORD='unterminated-nonsecret-sentinel\n",
        ] {
            let root = tempfile::tempdir().unwrap();
            let path = root.path().join(".env.local");
            std::fs::write(&path, body).unwrap();
            let error = ensure_env_file(&path, 1234).unwrap_err().to_string();
            assert!(!error.contains("nonsecret-sentinel"));
            assert_eq!(std::fs::read_to_string(&path).unwrap(), body);
        }
    }

    #[test]
    fn supports_quoted_hash_crlf_export_and_last_assignment() {
        for body in [
            "POSTGRES_PASSWORD='hash#inside'\r\n",
            "export POSTGRES_PASSWORD=valid # trailing comment\n",
            "POSTGRES_PASSWORD=\"quoted value\"\n",
            "POSTGRES_PASSWORD=\nPOSTGRES_PASSWORD=valid\n",
        ] {
            let root = tempfile::tempdir().unwrap();
            let path = root.path().join(".env.local");
            std::fs::write(&path, body).unwrap();
            validate_env_file(&path).unwrap();
            assert_eq!(std::fs::read_to_string(path).unwrap(), body);
        }
    }

    // Compose-valid colon syntax and double-quoted \t/\r escapes are now
    // accepted by the custom parser.  Bytes must be preserved on disk.
    #[test]
    fn compose_colon_and_quoted_escapes_accepted_preserves_bytes() {
        for body in [
            "POSTGRES_PASSWORD: valid\n",
            "POSTGRES_PASSWORD=\"valid\\tvalue\"\n",
            "POSTGRES_PASSWORD=\"valid\\rvalue\"\n",
        ] {
            let root = tempfile::tempdir().unwrap();
            let path = root.path().join(".env.local");
            std::fs::write(&path, body).unwrap();
            ensure_env_file(&path, 1234).unwrap();
            assert_eq!(std::fs::read_to_string(path).unwrap(), body);
        }
    }

    // Gap A: colon syntax must be accepted and the password extracted correctly.
    #[test]
    fn colon_syntax_validates_password() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join(".env.local");
        // Colon separator, no quotes.
        let body = "POSTGRES_PASSWORD: my-secret-value\n";
        std::fs::write(&path, body).unwrap();
        validate_env_file(&path).unwrap();
        assert_eq!(std::fs::read_to_string(&path).unwrap(), body);

        // Colon separator, empty value must still fail.
        let body_empty = "POSTGRES_PASSWORD:\n";
        std::fs::write(&path, body_empty).unwrap();
        assert!(validate_env_file(&path).is_err());
    }

    // Gap B: double-quoted \t and \r must be accepted; single-quoted literal.
    #[test]
    fn quoted_escape_sequences_accepted_and_round_tripped() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join(".env.local");

        // Double-quoted with \t.
        let body_tab = "POSTGRES_PASSWORD=\"a\\tb\"\n";
        std::fs::write(&path, body_tab).unwrap();
        validate_env_file(&path).unwrap();
        assert_eq!(std::fs::read_to_string(&path).unwrap(), body_tab);

        // Double-quoted with \r.
        let body_cr = "POSTGRES_PASSWORD=\"a\\rb\"\n";
        std::fs::write(&path, body_cr).unwrap();
        validate_env_file(&path).unwrap();
        assert_eq!(std::fs::read_to_string(&path).unwrap(), body_cr);

        // Single-quoted literal (backslash is literal, not escape).
        let body_sq = "POSTGRES_PASSWORD='a\\tb'\n";
        std::fs::write(&path, body_sq).unwrap();
        validate_env_file(&path).unwrap();
        assert_eq!(std::fs::read_to_string(&path).unwrap(), body_sq);
    }

    // Gap B: parser-level verification that escape sequences produce correct values.
    #[test]
    fn parse_env_line_escape_values() {
        // Double-quoted \t becomes a literal tab character.
        let (_, val) = parse_env_line("KEY=\"a\\tb\"").unwrap().unwrap();
        assert_eq!(val, "a\tb");

        // Double-quoted \r becomes a literal carriage return.
        let (_, val) = parse_env_line("KEY=\"a\\rb\"").unwrap().unwrap();
        assert_eq!(val, "a\rb");

        // Double-quoted \\ becomes a literal backslash.
        let (_, val) = parse_env_line("KEY=\"a\\\\b\"").unwrap().unwrap();
        assert_eq!(val, "a\\b");

        // Single-quoted: backslash is literal.
        let (_, val) = parse_env_line("KEY='a\\tb'").unwrap().unwrap();
        assert_eq!(val, "a\\tb");

        // Gap A: colon separator.
        let (key, val) = parse_env_line("MY_KEY: my value").unwrap().unwrap();
        assert_eq!(key, "MY_KEY");
        assert_eq!(val, "my value");
    }

    // Gap C: last-assignment-wins with colon and mixed separators.
    #[test]
    fn last_wins_with_mixed_separators() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join(".env.local");
        let body = "POSTGRES_PASSWORD=first\nPOSTGRES_PASSWORD: second\n";
        std::fs::write(&path, body).unwrap();
        validate_env_file(&path).unwrap();
        assert_eq!(std::fs::read_to_string(&path).unwrap(), body);
        // Verify the parsed value is "second" (last wins).
        let entries = parse_env_entries(body).unwrap();
        assert_eq!(entries["POSTGRES_PASSWORD"], "second");
    }

    // Fail-closed: genuinely invalid input must produce errors that do NOT
    // echo the offending value (no secret leakage).
    #[test]
    fn fail_closed_no_secret_leakage_in_errors() {
        // Unterminated single quote.
        let err = parse_env_line("POSTGRES_PASSWORD='top-secret-unterminated").unwrap_err();
        assert!(!err.to_string().contains("top-secret"), "error leaked secret: {err}");

        // Unterminated double quote.
        let err = parse_env_line("POSTGRES_PASSWORD=\"top-secret-unterminated").unwrap_err();
        assert!(!err.to_string().contains("top-secret"), "error leaked secret: {err}");

        // No separator at all.
        let err = parse_env_line("MALFORMED_LINE_NO_SEP").unwrap_err();
        assert!(!err.to_string().contains("MALFORMED"), "error echoed line: {err}");

        // End-to-end: ensure_env_file with invalid file does not leak.
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join(".env.local");
        std::fs::write(&path, "POSTGRES_PASSWORD='secret-unterminated\n").unwrap();
        let error = ensure_env_file(&path, 1234).unwrap_err().to_string();
        assert!(!error.contains("secret-unterminated"), "error leaked secret: {error}");
    }

    #[test]
    fn missing_validation_does_not_create_parent() {
        let root = tempfile::tempdir().unwrap();
        let parent = root.path().join("absent");
        assert!(validate_env_file(&parent.join(".env.local")).is_err());
        assert!(!parent.exists());
    }

    #[test]
    fn creates_absent_and_rejects_directory() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join(".env.local");
        ensure_env_file(&path, 1234).unwrap();
        validate_env_file(&path).unwrap();
        assert!(ensure_env_file(root.path(), 1234).is_err());
    }

    #[cfg(unix)]
    #[test]
    fn preserves_valid_and_dangling_symlinks() {
        let root = tempfile::tempdir().unwrap();
        let target = root.path().join("target");
        let path = root.path().join(".env.local");
        std::os::unix::fs::symlink(&target, &path).unwrap();
        assert!(ensure_env_file(&path, 1234).is_err());
        assert_eq!(std::fs::read_link(&path).unwrap(), target);
        assert!(!target.exists());
        std::fs::write(&target, "POSTGRES_PASSWORD=nonsecret-sentinel\n").unwrap();
        ensure_env_file(&path, 1234).unwrap();
        assert_eq!(std::fs::read_link(&path).unwrap(), target);
    }
}
