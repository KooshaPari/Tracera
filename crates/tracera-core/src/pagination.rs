//! Pagination primitives: offset, cursor, and keyset (seek) pagination.
//!
//! Three strategies are exposed, each appropriate to a different query shape:
//!
//! * [`OffsetRequest`] — simple `?page=N&size=M`. Easy to use, but O(offset)
//!   on the server and unstable when rows are inserted mid-iteration.
//! * [`Cursor`] — opaque base64url-encoded cursor, stable across inserts,
//!   suitable for append-only or monotonically-ordered feeds.
//! * [`KeysetRequest`] — explicit `(last_id, last_sort_key)` tuple, the most
//!   efficient strategy when the underlying table has a covering index.
//!
//! All three are `Send + Sync` and free of I/O so they can be unit-tested
//! without a database.

use serde::{Deserialize, Serialize};
use std::fmt;
use thiserror::Error;

// ---------------------------------------------------------------------------
// Tiny base64url codec (no external dep). Standard RFC 4648 §5 alphabet with
// URL-safe substitutions, no padding. Used only for cursor encoding.
// ---------------------------------------------------------------------------

const B64URL_ALPHABET: &[u8; 64] =
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

fn b64url_encode(input: &[u8]) -> String {
    let mut out = String::with_capacity((input.len() + 2) / 3 * 4);
    let mut i = 0;
    while i + 3 <= input.len() {
        let n = ((input[i] as u32) << 16) | ((input[i + 1] as u32) << 8) | (input[i + 2] as u32);
        out.push(B64URL_ALPHABET[((n >> 18) & 0x3F) as usize] as char);
        out.push(B64URL_ALPHABET[((n >> 12) & 0x3F) as usize] as char);
        out.push(B64URL_ALPHABET[((n >> 6) & 0x3F) as usize] as char);
        out.push(B64URL_ALPHABET[(n & 0x3F) as usize] as char);
        i += 3;
    }
    match input.len() - i {
        1 => {
            let n = (input[i] as u32) << 16;
            out.push(B64URL_ALPHABET[((n >> 18) & 0x3F) as usize] as char);
            out.push(B64URL_ALPHABET[((n >> 12) & 0x3F) as usize] as char);
        }
        2 => {
            let n = ((input[i] as u32) << 16) | ((input[i + 1] as u32) << 8);
            out.push(B64URL_ALPHABET[((n >> 18) & 0x3F) as usize] as char);
            out.push(B64URL_ALPHABET[((n >> 12) & 0x3F) as usize] as char);
            out.push(B64URL_ALPHABET[((n >> 6) & 0x3F) as usize] as char);
        }
        _ => {}
    }
    out
}

fn b64url_decode(input: &str) -> Result<Vec<u8>, ()> {
    let mut table = [-1i16; 256];
    for (i, &b) in B64URL_ALPHABET.iter().enumerate() {
        table[b as usize] = i as i16;
    }
    let bytes = input.as_bytes();
    if bytes.len() % 4 == 1 {
        return Err(());
    }
    let mut out = Vec::with_capacity(bytes.len() / 4 * 3);
    let mut buf: u32 = 0;
    let mut bits: u32 = 0;
    for &b in bytes {
        let v = table[b as usize];
        if v < 0 {
            return Err(());
        }
        buf = (buf << 6) | v as u32;
        bits += 6;
        if bits >= 8 {
            bits -= 8;
            out.push(((buf >> bits) & 0xFF) as u8);
            buf &= (1 << bits) - 1;
        }
    }
    Ok(out)
}

/// `?page=N&page_size=M` style pagination request.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct OffsetRequest {
    /// 1-indexed page number. Saturates to 1 if 0.
    pub page: u32,
    /// Number of rows per page. Saturates to a safe minimum/maximum.
    pub page_size: u32,
}

impl Default for OffsetRequest {
    fn default() -> Self {
        Self {
            page: 1,
            page_size: 20,
        }
    }
}

impl OffsetRequest {
    pub const MIN_PAGE_SIZE: u32 = 1;
    pub const MAX_PAGE_SIZE: u32 = 500;

    /// Build a request, clamping `page_size` into a safe range.
    pub fn new(page: u32, page_size: u32) -> Self {
        let page = page.max(1);
        let page_size = page_size.clamp(Self::MIN_PAGE_SIZE, Self::MAX_PAGE_SIZE);
        Self { page, page_size }
    }

    /// Zero-based offset suitable for `LIMIT/OFFSET` SQL.
    pub fn offset(&self) -> u32 {
        (self.page - 1).saturating_mul(self.page_size)
    }

    /// Page metadata for an empty/partial result.
    pub fn page_info(&self, total: u64) -> OffsetPageInfo {
        let page_size = self.page_size as u64;
        let total_pages = if total == 0 {
            0
        } else {
            total.div_ceil(page_size)
        };
        OffsetPageInfo {
            page: self.page,
            page_size: self.page_size,
            total,
            total_pages,
            has_next: (self.page as u64) < total_pages,
            has_prev: self.page > 1,
        }
    }
}

/// Lightweight metadata returned alongside an offset page of rows.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct OffsetPageInfo {
    pub page: u32,
    pub page_size: u32,
    pub total: u64,
    pub total_pages: u64,
    pub has_next: bool,
    pub has_prev: bool,
}

/// Opaque, base64url-encoded cursor. The wire format is intentionally
/// versioned so the server can evolve the underlying tuple shape without
/// breaking outstanding cursors.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Cursor(pub String);

impl Cursor {
    /// Encode `(offset, sort_key)` into a stable opaque token.
    pub fn encode(offset: u64, sort_key: i64) -> Self {
        let raw = format!("v1:{}:{}", offset, sort_key);
        Self(b64url_encode(raw.as_bytes()))
    }

    /// Decode a cursor produced by [`Cursor::encode`]. Returns an error if
    /// the cursor is malformed or uses an unsupported version.
    pub fn decode(&self) -> Result<CursorPosition, PaginationError> {
        let bytes = b64url_decode(&self.0)
            .map_err(|_| PaginationError::InvalidCursor("not base64url".into()))?;
        let s = std::str::from_utf8(&bytes)
            .map_err(|_| PaginationError::InvalidCursor("not utf-8".into()))?;
        let mut parts = s.splitn(3, ':');
        let version = parts
            .next()
            .ok_or_else(|| PaginationError::InvalidCursor("missing version".into()))?;
        if version != "v1" {
            return Err(PaginationError::InvalidCursor(format!(
                "unsupported version: {}",
                version
            )));
        }
        let offset: u64 = parts
            .next()
            .ok_or_else(|| PaginationError::InvalidCursor("missing offset".into()))?
            .parse()
            .map_err(|_| PaginationError::InvalidCursor("bad offset".into()))?;
        let sort_key: i64 = parts
            .next()
            .ok_or_else(|| PaginationError::InvalidCursor("missing sort_key".into()))?
            .parse()
            .map_err(|_| PaginationError::InvalidCursor("bad sort_key".into()))?;
        Ok(CursorPosition { offset, sort_key })
    }
}

impl fmt::Display for Cursor {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

/// Decoded position carried inside a cursor.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CursorPosition {
    pub offset: u64,
    pub sort_key: i64,
}

/// Cursor-paginated request.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, Default)]
pub struct CursorRequest {
    /// Optional `page_size`. Defaults to 20 and is clamped on the server.
    pub page_size: Option<u32>,
    /// Optional cursor returned by a previous response. `None` means "first
    /// page".
    pub cursor: Option<Cursor>,
}

impl CursorRequest {
    pub fn first(page_size: u32) -> Self {
        Self {
            page_size: Some(page_size),
            cursor: None,
        }
    }

    pub fn next(page_size: u32, last: &Cursor) -> Self {
        Self {
            page_size: Some(page_size),
            cursor: Some(last.clone()),
        }
    }

    /// Effective page size after clamping to a safe range.
    pub fn effective_page_size(&self) -> u32 {
        let ps = self.page_size.unwrap_or(20);
        ps.clamp(OffsetRequest::MIN_PAGE_SIZE, OffsetRequest::MAX_PAGE_SIZE)
    }
}

/// Cursor-paginated response.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CursorResponse<T> {
    pub items: Vec<T>,
    pub next_cursor: Option<Cursor>,
    /// True if the server believes more pages exist. Conservative — `false`
    /// when `items.len() < page_size` or when the underlying query ran out
    /// of rows.
    pub has_more: bool,
}

/// Keyset pagination — seek to `(last_id, last_score)` and return the next
/// page. The most efficient strategy on indexed data.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct KeysetRequest<K: Ord + Copy, S: Ord + Copy> {
    pub page_size: u32,
    /// `None` for the first page; set to the last item of the previous
    /// page to fetch the next one.
    pub after: Option<(K, S)>,
}

impl<K: Ord + Copy, S: Ord + Copy> Default for KeysetRequest<K, S> {
    fn default() -> Self {
        Self {
            page_size: 20,
            after: None,
        }
    }
}

/// Apply a keyset page filter over an in-memory slice. Production code
/// would push this down to SQL as
/// `WHERE (score, id) > (last_score, last_id) ORDER BY score, id LIMIT N`.
pub fn keyset_slice<T, K, S, F>(
    rows: &[T],
    req: &KeysetRequest<K, S>,
    mut key_of: F,
) -> Vec<T>
where
    K: Ord + Copy,
    S: Ord + Copy,
    F: FnMut(&T) -> (K, S),
    T: Clone,
{
    let page_size = req
        .page_size
        .clamp(OffsetRequest::MIN_PAGE_SIZE, OffsetRequest::MAX_PAGE_SIZE)
        as usize;

    let iter = rows
        .iter()
        .filter(|r| match req.after {
            Some(after) => key_of(r) > after,
            None => true,
        })
        .take(page_size)
        .cloned();
    iter.collect()
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum PaginationError {
    #[error("invalid pagination cursor: {0}")]
    InvalidCursor(String),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn offset_clamps_page_size() {
        let r = OffsetRequest::new(0, 10_000);
        assert_eq!(r.page, 1);
        assert_eq!(r.page_size, OffsetRequest::MAX_PAGE_SIZE);

        let r2 = OffsetRequest::new(3, 0);
        assert_eq!(r2.page_size, OffsetRequest::MIN_PAGE_SIZE);
        assert_eq!(r2.offset(), 2);
    }

    #[test]
    fn offset_page_info_handles_empty_and_partial() {
        let r = OffsetRequest::new(1, 10);
        assert_eq!(r.page_info(0).total_pages, 0);
        assert!(!r.page_info(0).has_next);

        let info = r.page_info(95);
        assert_eq!(info.total_pages, 10);
        assert!(info.has_next);
        assert!(!info.has_prev);

        let r2 = OffsetRequest::new(2, 10);
        let info2 = r2.page_info(95);
        assert!(info2.has_next && info2.has_prev);
    }

    #[test]
    fn cursor_roundtrips_position() {
        let c = Cursor::encode(42, -7);
        let pos = c.decode().unwrap();
        assert_eq!(pos.offset, 42);
        assert_eq!(pos.sort_key, -7);
    }

    #[test]
    fn cursor_rejects_bad_payloads() {
        let bad = Cursor("!!!not base64!!!".into());
        assert!(matches!(bad.decode(), Err(PaginationError::InvalidCursor(_))));

        let wrong_version = Cursor(b64url_encode(b"v2:1:2"));
        assert!(matches!(
            wrong_version.decode(),
            Err(PaginationError::InvalidCursor(_))
        ));
    }

    #[test]
    fn keyset_filter_skips_to_after_tuple() {
        let rows: Vec<(u32, i32)> = (0..10).map(|i| (i, -(i as i32))).collect();
        let req = KeysetRequest {
            page_size: 5,
            after: Some((3, -3)),
        };
        let page = keyset_slice(&rows, &req, |r| *r);
        assert_eq!(page.len(), 5);
        assert_eq!(page[0], (4, -4));
        assert_eq!(page[4], (8, -8));
    }
}
