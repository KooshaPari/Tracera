//! Rate limiting primitives for inbound bus traffic.
//!
//! Three classic strategies are provided, all synchronous and `Send + Sync`:
//!
//! * [`TokenBucket`] — refills at a fixed rate, allows bursts up to capacity.
//! * [`SlidingWindow`] — counts acquisitions within a rolling time window.
//! * [`LeakyBucket`] — drains at a fixed rate; bursts are queued (or dropped
//!   once the bucket is full).
//!
//! All three expose the same `try_acquire() -> bool` surface so callers can
//! swap strategies behind a uniform interface.

use std::time::{Duration, Instant};

// ---------------------------------------------------------------------------
// Token bucket
// ---------------------------------------------------------------------------

/// Classic token-bucket rate limiter.
///
/// The bucket holds at most `capacity` tokens. Tokens accrue at
/// `refill_per_sec` per second. Each `try_acquire` consumes one token. A full
/// bucket is refilled lazily on each call (no background thread).
#[derive(Debug)]
pub struct TokenBucket {
    capacity: f64,
    refill_per_sec: f64,
    tokens: f64,
    last_refill: Instant,
}

impl TokenBucket {
    /// Create a new bucket. The bucket starts full.
    pub fn new(capacity: u32, refill_per_sec: f64) -> Self {
        let cap = capacity as f64;
        Self {
            capacity: cap,
            refill_per_sec,
            tokens: cap,
            last_refill: Instant::now(),
        }
    }

    fn refill(&mut self) {
        let now = Instant::now();
        let elapsed = now.duration_since(self.last_refill).as_secs_f64();
        if elapsed > 0.0 {
            self.tokens = (self.tokens + elapsed * self.refill_per_sec).min(self.capacity);
            self.last_refill = now;
        }
    }

    /// Try to consume one token. Returns `true` on success, `false` if the
    /// bucket is empty.
    pub fn try_acquire(&mut self) -> bool {
        self.refill();
        if self.tokens >= 1.0 {
            self.tokens -= 1.0;
            true
        } else {
            false
        }
    }

    /// Current token count (rounded down). Useful for tests and metrics.
    pub fn available(&mut self) -> u32 {
        self.refill();
        self.tokens as u32
    }
}

// ---------------------------------------------------------------------------
// Sliding window
// ---------------------------------------------------------------------------

/// Sliding-window counter.
///
/// Records the timestamps of the most recent `limit` successful acquisitions
/// and rejects new calls if `limit` are already inside the trailing
/// `window`.
#[derive(Debug)]
pub struct SlidingWindow {
    limit: u32,
    window: Duration,
    hits: Vec<Instant>,
}

impl SlidingWindow {
    /// Create a new sliding window allowing `limit` acquisitions per `window`.
    pub fn new(limit: u32, window: Duration) -> Self {
        Self {
            limit,
            window,
            hits: Vec::with_capacity(limit as usize),
        }
    }

    fn prune(&mut self) {
        let cutoff = Instant::now() - self.window;
        // `hits` is in insertion order (oldest first); drop the prefix that
        // has fallen out of the window.
        let drop = self.hits.partition_point(|t| *t < cutoff);
        if drop > 0 {
            self.hits.drain(..drop);
        }
    }

    /// Try to record one acquisition in the current window.
    pub fn try_acquire(&mut self) -> bool {
        self.prune();
        if (self.hits.len() as u32) < self.limit {
            self.hits.push(Instant::now());
            true
        } else {
            false
        }
    }

    /// Number of acquisitions currently inside the window.
    pub fn current(&mut self) -> u32 {
        self.prune();
        self.hits.len() as u32
    }
}

// ---------------------------------------------------------------------------
// Leaky bucket
// ---------------------------------------------------------------------------

/// Leaky-bucket rate limiter.
///
/// The bucket holds at most `capacity` units. It drains at `leak_per_sec`
/// units/second. `try_acquire(n=1)` adds one unit; calls succeed while there
/// is headroom and fail once the bucket is full.
#[derive(Debug)]
pub struct LeakyBucket {
    capacity: f64,
    leak_per_sec: f64,
    level: f64,
    last_leak: Instant,
}

impl LeakyBucket {
    /// Create a new leaky bucket. The bucket starts empty.
    pub fn new(capacity: u32, leak_per_sec: f64) -> Self {
        Self {
            capacity: capacity as f64,
            leak_per_sec,
            level: 0.0,
            last_leak: Instant::now(),
        }
    }

    fn leak(&mut self) {
        let now = Instant::now();
        let elapsed = now.duration_since(self.last_leak).as_secs_f64();
        if elapsed > 0.0 {
            self.level = (self.level - elapsed * self.leak_per_sec).max(0.0);
            self.last_leak = now;
        }
    }

    /// Try to push one unit into the bucket. Returns `true` if it fit.
    pub fn try_acquire(&mut self) -> bool {
        self.leak();
        if self.level + 1.0 <= self.capacity {
            self.level += 1.0;
            true
        } else {
            false
        }
    }

    /// Current fill level (rounded up so a partially-filled slot counts as full).
    pub fn level(&mut self) -> u32 {
        self.leak();
        self.level.ceil() as u32
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn token_bucket_starts_full_and_eventually_empties() {
        let mut b = TokenBucket::new(3, 1_000.0); // huge refill
        assert!(b.try_acquire());
        assert!(b.try_acquire());
        assert!(b.try_acquire());
        assert!(!b.try_acquire());
    }

    #[test]
    fn sliding_window_enforces_limit_then_recovers() {
        let mut w = SlidingWindow::new(2, Duration::from_millis(50));
        assert!(w.try_acquire());
        assert!(w.try_acquire());
        assert!(!w.try_acquire());
        std::thread::sleep(Duration::from_millis(70));
        assert!(w.try_acquire());
    }

    #[test]
    fn leaky_bucket_rejects_when_full_then_drains() {
        let mut b = LeakyBucket::new(2, 1_000.0); // huge drain rate
        assert!(b.try_acquire());
        assert!(b.try_acquire());
        assert!(!b.try_acquire());
        // wait so it fully drains
        std::thread::sleep(Duration::from_millis(20));
        assert!(b.try_acquire());
    }

    #[test]
    fn token_bucket_zero_capacity_rejects_all() {
        let mut b = TokenBucket::new(0, 1_000.0);
        assert!(!b.try_acquire());
    }

    #[test]
    fn token_bucket_refills_over_time() {
        let mut b = TokenBucket::new(1, 200.0); // 1 token / 5ms
        assert!(b.try_acquire());
        assert!(!b.try_acquire());
        std::thread::sleep(Duration::from_millis(20));
        assert!(b.try_acquire());
    }
}
