//! Compose-inspired `.env` file parsing.
//!
//! This parser accepts both `=` and `:` separators, `export` prefixes,
//! comments (inside and outside quoted values), double-quoted escape
//! sequences (`\a`, `\b`, `\c`, `\f`, `\n`, `\r`, `\t`, `\v`, `\\`, `\"`,
//! `\$`, and octal `\0NNN`), and single-quoted values with escape-aware
//! quote scanning.  It does **not** implement:
//!
//! - `${VAR}` variable interpolation (Compose `expandVariables`),
//! - multi-statement continuation after a closing quote on the same line,
//! - POSIX shell expansion beyond the above.
//!
//! A bare key with no separator (`KEY\n`) fails closed rather than
//! inheriting from the environment, which is a deliberate safety choice
//! for a credential file.
//!
//! Inline comments on an unquoted value are recognised only at the two
//! character sequence `" #"`, matching Docker Compose.  A `#` that is
//! not preceded by whitespace is part of the value, so a password such
//! as `pa#ss` keeps its `#`.
//!
//! Errors never echo the offending line or value, so a malformed
//! credential file cannot leak its secret through an error message.
use std::collections::HashMap;

/// Parse a single `.env` line, returning `Some((key, value))` or `None` for
/// blank / comment-only lines.  Returns `Err` only for genuinely malformed
/// lines (unterminated quote, no separator at all).  The error must never
/// echo the line content to avoid leaking secrets.
pub(crate) fn parse_env_line(line: &str) -> anyhow::Result<Option<(String, String)>> {
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
    if key.contains(char::is_whitespace) {
        anyhow::bail!("env line has a key containing whitespace");
    }
    let raw_val = rest[sep_idx + 1..].trim_start();

    let value = if let Some(after_opening) = raw_val.strip_prefix('\'') {
        // Single-quoted: literal content up to the next unescaped `'`.
        // Compose scans for the closing quote with escape awareness, so
        // `'a\'b'` is the three character value `a'b`.
        let (content, _) = scan_quoted(after_opening, '\'')?;
        content
    } else if let Some(after_opening) = raw_val.strip_prefix('"') {
        // Double-quoted: Compose expands standard shell escape sequences.
        // `#` is not a comment inside a quoted value.
        let (content, _) = scan_quoted(after_opening, '"')?;
        expand_escapes(&content)
    } else {
        // Unquoted: an inline comment starts at the sequence `" #"`.
        // A `#` without preceding whitespace is part of the value.
        // A value that is entirely a comment (`KEY= # note`) is treated as
        // absent and fails closed, which is stricter than Compose and
        // keeps a commented-out credential from being used verbatim.
        if raw_val.starts_with('#') {
            String::new()
        } else {
            let value = match raw_val.find(" #") {
                Some(pos) => &raw_val[..pos],
                None => raw_val,
            };
            value.trim_end().to_string()
        }
    };
    Ok(Some((key, value)))
}

/// Scan a quoted value body for its closing quote, honouring backslash
/// escapes.  Returns the raw content between the quotes and the bytes
/// that follow the closing quote.  The content is *not* escape-expanded;
/// that is [`expand_escapes`]' job for double-quoted values.
///
/// A backslash before the closing quote escapes it, so the quote becomes
/// a literal and the backslash is consumed.  A backslash before any other
/// character is preserved together with that character, which is how a
/// single-quoted value keeps a literal backslash.
fn scan_quoted(body: &str, quote: char) -> anyhow::Result<(String, &str)> {
    let mut out = String::with_capacity(body.len());
    let mut chars = body.char_indices();
    while let Some((idx, c)) = chars.next() {
        match c {
            '\\' => match chars.next() {
                Some((_, escaped)) if escaped == quote => out.push(escaped),
                Some((_, escaped)) => {
                    out.push('\\');
                    out.push(escaped);
                }
                None => anyhow::bail!("unterminated escape in env value"),
            },
            c if c == quote => {
                return Ok((out, &body[idx + c.len_utf8()..]));
            }
            c => out.push(c),
        }
    }
    anyhow::bail!("unterminated quoted value in env line");
}

/// Expand the standard shell escape sequences that Docker Compose
/// recognises inside a double-quoted value.  Unknown sequences are left
/// verbatim, matching Compose's `expandEscapes` behaviour.
fn expand_escapes(value: &str) -> String {
    let mut out = String::with_capacity(value.len());
    let mut chars = value.chars().peekable();
    while let Some(c) = chars.next() {
        if c != '\\' {
            out.push(c);
            continue;
        }
        match chars.next() {
            None => out.push('\\'),
            Some('a') => out.push('\u{7}'),
            Some('b') => out.push('\u{8}'),
            Some('c') => out.push('\u{3}'),
            Some('f') => out.push('\u{c}'),
            Some('n') => out.push('\n'),
            Some('r') => out.push('\r'),
            Some('t') => out.push('\t'),
            Some('v') => out.push('\u{b}'),
            Some('\\') => out.push('\\'),
            Some('"') => out.push('"'),
            Some('\'') => out.push('\''),
            Some('$') => out.push('$'),
            Some('0') => {
                // Octal escape: `\0NNN`, up to three octal digits after the
                // leading zero.  This mirrors Compose's `0\d{0,3}` form.
                let mut digits = String::new();
                for _ in 0..3 {
                    match chars.peek() {
                        Some(d) if ('0'..='7').contains(d) => {
                            digits.push(*d);
                            chars.next();
                        }
                        _ => break,
                    }
                }
                match u32::from_str_radix(&digits, 8) {
                    Ok(code) => match char::from_u32(code) {
                        Some(ch) => out.push(ch),
                        None => {
                            out.push('\\');
                            out.push('0');
                            out.push_str(&digits);
                        }
                    },
                    Err(_) => {
                        out.push('\\');
                        out.push('0');
                        out.push_str(&digits);
                    }
                }
            }
            Some(other) => {
                // Not a recognised escape: keep the backslash and the char.
                out.push('\\');
                out.push(other);
            }
        }
    }
    out
}

/// Parse all lines in an env file body, applying last-assignment-wins.
/// Returns `Err` if any line is genuinely malformed (unterminated quote,
/// no separator).  The error never echoes the offending value.
pub(crate) fn parse_env_entries(body: &str) -> anyhow::Result<HashMap<String, String>> {
    let mut map = HashMap::new();
    for line in body.lines() {
        if let Some((key, value)) = parse_env_line(line)? {
            map.insert(key, value);
        }
    }
    Ok(map)
}

#[cfg(test)]
mod tests;
