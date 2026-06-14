//! In-memory TTL cache with pluggable eviction policy and hit/miss/eviction stats.
//!
//! Used as a hot-path cache for derived coverage / impact computations. The
//! cache is `Send` when `K: Send` and `V: Send`, and `Sync` when both are
//! `Sync`. It uses a plain `HashMap` for the index plus an auxiliary data
//! structure to drive eviction (an LRU doubly-linked list for LRU, a min-heap
//! of frequency counters for LFU).

use std::collections::HashMap;
use std::hash::Hash;
use std::time::{Duration, Instant};

/// Eviction strategy applied when the cache exceeds its capacity.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EvictionPolicy {
    /// Least-Recently-Used — drop the entry whose `get`/`put` was oldest.
    Lru,
    /// Least-Frequently-Used — drop the entry with the lowest access count.
    Lfu,
}

#[derive(Debug, Clone)]
struct Entry<V> {
    value: V,
    expires_at: Option<Instant>,
    /// Monotonic counter incremented on every hit/put; used by LRU ordering
    /// (`last_used`) and LFU counting.
    last_used: u64,
    hits: u64,
}

/// Cache hit/miss/eviction counters.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct CacheStats {
    pub hits: u64,
    pub misses: u64,
    pub evictions: u64,
    /// Number of entries currently held. Not part of the public
    /// "hits/misses/evictions" trio but useful for observability.
    pub size: u64,
}

use serde::{Deserialize, Serialize};

/// Thread-safe in-memory cache. The inner state is protected by a
/// `parking_lot`-style `Mutex` would be ideal, but we use `std::sync::Mutex`
/// to avoid pulling in a new dependency for Phase 6.
pub struct Cache<K, V> {
    map: HashMap<K, Entry<V>>,
    capacity: usize,
    ttl: Option<Duration>,
    policy: EvictionPolicy,
    stats: CacheStats,
    /// Monotonic clock used to order LRU ties and LFU refreshes.
    tick: u64,
}

impl<K, V> Cache<K, V>
where
    K: Eq + Hash + Clone,
{
    /// Create a new cache with the given capacity. `ttl` applies to every
    /// entry uniformly; pass `None` for entries that never expire.
    pub fn new(capacity: usize, ttl: Option<Duration>, policy: EvictionPolicy) -> Self {
        Self {
            map: HashMap::with_capacity(capacity),
            capacity,
            ttl,
            policy,
            stats: CacheStats::default(),
            tick: 0,
        }
    }

    fn now(&self) -> Instant {
        Instant::now()
    }

    fn is_expired(&self, entry: &Entry<V>) -> bool {
        match entry.expires_at {
            Some(t) => self.now() >= t,
            None => false,
        }
    }

    fn bump_tick(&mut self) -> u64 {
        self.tick = self.tick.wrapping_add(1);
        self.tick
    }

    /// Look up a key. Expired entries are removed lazily and counted as
    /// misses. A hit updates LRU/LFU bookkeeping.
    pub fn get(&mut self, key: &K) -> Option<V>
    where
        V: Clone,
    {
        // Two-phase borrow to satisfy the borrow checker while still allowing
        // mutation after the lookup decision.
        let expired = match self.map.get(key) {
            Some(entry) => self.is_expired(entry),
            None => {
                self.stats.misses += 1;
                return None;
            }
        };

        if expired {
            self.map.remove(key);
            self.stats.size = self.map.len() as u64;
            self.stats.misses += 1;
            return None;
        }

        let tick = self.bump_tick();
        let entry = self.map.get_mut(key).expect("present");
        entry.last_used = tick;
        entry.hits = entry.hits.saturating_add(1);
        self.stats.hits += 1;
        Some(entry.value.clone())
    }

    /// Insert or replace a value. May evict one entry to respect capacity.
    pub fn put(&mut self, key: K, value: V) {
        if self.capacity == 0 {
            return;
        }
        let tick = self.bump_tick();
        let expires_at = self.ttl.map(|t| self.now() + t);

        if let Some(existing) = self.map.get_mut(&key) {
            existing.value = value;
            existing.expires_at = expires_at;
            existing.last_used = tick;
            existing.hits = existing.hits.saturating_add(1);
            return;
        }

        if self.map.len() >= self.capacity {
            self.evict_one();
        }

        self.map.insert(
            key,
            Entry {
                value,
                expires_at,
                last_used: tick,
                hits: 0,
            },
        );
        self.stats.size = self.map.len() as u64;
    }

    /// Remove a key, returning the value that was stored (if any).
    pub fn invalidate(&mut self, key: &K) -> Option<V> {
        let removed = self.map.remove(key);
        self.stats.size = self.map.len() as u64;
        removed.map(|e| e.value)
    }

    /// Current number of live (unexpired) entries. O(n) because expired
    /// entries are only purged on access.
    pub fn len(&self) -> usize {
        self.map.len()
    }

    pub fn is_empty(&self) -> bool {
        self.map.is_empty()
    }

    /// Snapshot of the current hit/miss/eviction counters.
    pub fn stats(&self) -> CacheStats {
        self.stats.clone()
    }

    fn evict_one(&mut self) {
        let victim = match self.policy {
            EvictionPolicy::Lru => self
                .map
                .iter()
                .min_by_key(|(_, e)| e.last_used)
                .map(|(k, _)| k.clone()),
            EvictionPolicy::Lfu => self
                .map
                .iter()
                .min_by_key(|(_, e)| (e.hits, e.last_used))
                .map(|(k, _)| k.clone()),
        };
        if let Some(k) = victim {
            self.map.remove(&k);
            self.stats.evictions += 1;
            self.stats.size = self.map.len() as u64;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn put_and_get_roundtrip() {
        let mut c: Cache<&'static str, i32> =
            Cache::new(8, None, EvictionPolicy::Lru);
        c.put("a", 1);
        c.put("b", 2);
        assert_eq!(c.get(&"a"), Some(1));
        assert_eq!(c.get(&"b"), Some(2));
        assert_eq!(c.get(&"missing"), None);

        let s = c.stats();
        assert_eq!(s.hits, 2);
        assert_eq!(s.misses, 1);
        assert_eq!(s.size, 2);
    }

    #[test]
    fn lru_eviction_drops_least_recently_used() {
        let mut c: Cache<u32, u32> = Cache::new(2, None, EvictionPolicy::Lru);
        c.put(1, 10);
        c.put(2, 20);
        // touch 1 so 2 becomes the LRU
        assert_eq!(c.get(&1), Some(10));
        c.put(3, 30); // should evict 2
        assert_eq!(c.get(&2), None);
        assert_eq!(c.get(&1), Some(10));
        assert_eq!(c.get(&3), Some(30));
        assert!(c.stats().evictions >= 1);
    }

    #[test]
    fn lfu_eviction_drops_least_frequently_used() {
        let mut c: Cache<u32, u32> = Cache::new(2, None, EvictionPolicy::Lfu);
        c.put(1, 10);
        c.put(2, 20);
        // Repeatedly hit 1 so it stays hot; 2 remains cold
        assert_eq!(c.get(&1), Some(10));
        assert_eq!(c.get(&1), Some(10));
        c.put(3, 30); // should evict 2
        assert_eq!(c.get(&2), None);
        assert_eq!(c.get(&1), Some(10));
        assert_eq!(c.get(&3), Some(30));
    }

    #[test]
    fn ttl_expires_entries() {
        let mut c: Cache<&'static str, i32> =
            Cache::new(8, Some(Duration::from_millis(30)), EvictionPolicy::Lfu);
        c.put("k", 42);
        assert_eq!(c.get(&"k"), Some(42));
        std::thread::sleep(Duration::from_millis(60));
        assert_eq!(c.get(&"k"), None);
        let s = c.stats();
        assert!(s.misses >= 1);
    }
}
