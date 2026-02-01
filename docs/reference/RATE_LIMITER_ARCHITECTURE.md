# Rate Limiter Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     HTTP Request Flow                           │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ RateLimitMiddleware  │
                    └──────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          ┌─────────┐   ┌─────────┐   ┌────────────┐
          │ Redis?  │   │Skip?    │   │Check Limit │
          └─────────┘   └─────────┘   └────────────┘
              │              │              │
              ├─ Yes ──────┐  │              │
              │            ▼  │              │
              │       ┌──────────┐           │
              │       │Next/Err  │           │
              │       └──────────┘           │
              │                              │
              ├─ No ─────────────────────────┤
              │                              │
              └──► ┌──────────────────────┐  │
                   │ In-Memory Limiter    │  │
                   │                      │  │
                   │ 1. Get/Create Entry  │  │
                   │ 2. Update Timestamp  │  │
                   │ 3. Check Rate Limit  │  │
                   └──────────────────────┘  │
                          │                  │
                          ├─ Allowed ───────┤
                          │                  │
                          └─ Denied ────────►│
                                            │
                                    ┌───────┴───────┐
                                    │               │
                                    ▼               ▼
                            ┌─────────────┐  ┌──────────┐
                            │Continue     │  │429 Error │
                            │Processing   │  │Returned  │
                            └─────────────┘  └──────────┘
```

## Data Structure

```
LimiterConfig
├── RedisClient
├── RequestsPerSecond
├── BurstSize
├── LimiterTTL              ◄─── New: Configurable TTL
├── CleanupInterval         ◄─── New: Cleanup frequency
└── stopCleanupChannel      ◄─── New: Shutdown signal

limiterMap: map[clientID] ──┐
                            │
                            ▼
                    ┌──────────────────┐
                    │ limiterEntry     │ ◄─── New type
                    ├──────────────────┤
                    │ Limiter          │
                    │ LastAccessed     │ ◄─── New field
                    └──────────────────┘
```

## Cleanup Goroutine Lifecycle

```
Application Start
       │
       ▼
┌──────────────────────────┐
│ RateLimitMiddleware      │
│ called                   │
└──────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ Initialize cleanupStaleLimiters          │
│ go cleanupStaleLimiters(...)             │ ◄─── Goroutine spawned
└──────────────────────────────────────────┘
       │
       ▼
   Create Ticker ──┐
                  │ Tick every CleanupInterval
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
 Cleanup                   Stop Signal
    │                           │
    ▼                           ▼
 Lock mutex           Close stopCleanupChannel
    │                           │
    ▼                           ▼
 Iterate limiters      Exit gracefully
    │
    ▼
 Delete stale
 (now - lastAccessed > TTL)
    │
    ▼
 Log stats
    │
    ▼
 Unlock mutex
    │
    └──────────── Loop ────────────────┘

Application Shutdown
       │
       ▼
StopRateLimitCleanup()
       │
       ▼
Close stopCleanupChannel
       │
       ▼
Cleanup goroutine exits
```

## Request Processing Timeline

```
Time ──────────────────────────────────────────────────────────>

Request #1 arrives for Client A
│
├─ Lock mutex
├─ Check: Client A in limiters map? NO
├─ Create: limiterEntry {
│    Limiter: rate.NewLimiter(...)
│    LastAccessed: now()
│  }
├─ Add to map: limiters["192.168.1.1"] = entry
├─ Unlock mutex
├─ Check: Allow()? YES
└─ Return to handler


Request #2 arrives for Client B (500ms later)
│
├─ Lock mutex
├─ Check: Client B in limiters map? NO
├─ Create: New limiterEntry for Client B
├─ Add to map: limiters["192.168.1.2"] = entry
├─ Unlock mutex
├─ Check: Allow()? YES
└─ Return to handler


Request #3 arrives for Client A (1 second later)
│
├─ Lock mutex
├─ Check: Client A in limiters map? YES
├─ Update: entry.LastAccessed = now()  ◄─── CRUCIAL: Keep it fresh
├─ Unlock mutex
├─ Check: Allow()? YES/NO (based on rate)
└─ Return to handler


... 5 minutes pass with no requests from Client B ...

Cleanup cycle starts (runs every 1 minute)
│
├─ Lock mutex
├─ Check each entry:
│  ├─ Client A: now - lastAccessed = 1 min < 5 min TTL? KEEP
│  └─ Client B: now - lastAccessed = 5 min > 5 min TTL? DELETE ✓
├─ Remove Client B from map
├─ Log: "removed 1 stale limiters, 1 active limiters remaining"
├─ Unlock mutex
└─ Done, wait for next tick
```

## Memory Usage Over Time

```
WITHOUT CLEANUP (Before Fix):
Memory
  ^
  │                           ◆ OOM Crash
  │                    ◆ ◆ ◆
  │              ◆ ◆ ◆
  │        ◆ ◆ ◆
  │   ◆ ◆ ◆
  │ ◆
  └─────────────────────────────────> Time
     0   6h  12h  18h  24h  30h

Pattern: Linear growth with no recovery


WITH CLEANUP (After Fix):
Memory
  ^
  │    ┌─────────────────────────┐
  │    │ Equilibrium reached     │
  │ ┌──┤ at active client count  │
  │ │  │                         │
  │─┼──────────────────────────────
  │ │  │ Cleanup removes stale  │
  │ └──┤ entries periodically    │
  │    └─────────────────────────┘
  └─────────────────────────────> Time
     0   6h  12h  18h  24h  30h

Pattern: Stable bounded growth
```

## Configuration Impact

```
TTL Configuration Effects:

Short TTL (1 minute):
├─ Memory: Lower
├─ Cleanup: More aggressive
└─ Risk: Legitimate clients cleaned up

Medium TTL (5 minutes):
├─ Memory: Balanced
├─ Cleanup: Reasonable
└─ Recommended for most cases

Long TTL (30 minutes):
├─ Memory: Higher
├─ Cleanup: Less aggressive
└─ For low-churn environments


CleanupInterval Configuration Effects:

Frequent (30 seconds):
├─ CPU: Higher (cleanup more often)
├─ Memory: Lower (faster cleanup)
└─ Logs: More verbose

Moderate (1 minute):
├─ CPU: Balanced
├─ Memory: Good
└─ Logs: Reasonable

Infrequent (10 minutes):
├─ CPU: Lower
├─ Memory: Higher (longer before cleanup)
└─ Logs: Less frequent
```

## Thread Safety Model

```
Mutex Protection Pattern:

┌────────────────────────────────────┐
│ mu.Lock()                          │  Exclusive Lock
├────────────────────────────────────┤
│ Map Operation (read or write)       │
├────────────────────────────────────┤
│ limiter := entry.limiter            │  Extract reference
├────────────────────────────────────┤
│ mu.Unlock()                         │
├────────────────────────────────────┤
│ limiter.Allow()  (NO LOCK NEEDED)   │
└────────────────────────────────────┘

Why separate? Rate limiter object is thread-safe,
no need to hold map lock during rate check.
Minimizes lock contention.
```

## Environment Variable Flow

```
Application Start
       │
       ▼
RateLimitMiddleware() called
       │
       ├─ config.LimiterTTL == 0? YES
       │  │
       │  ├─ Read: os.Getenv("RATE_LIMITER_TTL_SECONDS")
       │  │
       │  ├─ Found? YES
       │  │  └─ Parse & use
       │  │
       │  └─ Not found?
       │     └─ Use default: 300 seconds
       │
       └─ config.CleanupInterval == 0? YES
          │
          ├─ Read: os.Getenv("RATE_LIMITER_CLEANUP_INTERVAL_SECONDS")
          │
          ├─ Found? YES
          │  └─ Parse & use
          │
          └─ Not found?
             └─ Use default: 60 seconds
```

## Monitoring Architecture

```
Application Runtime
       │
       ├─ Every request:
       │  └─ Update lastAccessed timestamp
       │
       └─ Every cleanup cycle:
          ├─ Log cleanup statistics:
          │  ├─ Count of removed stale limiters
          │  ├─ Count of active limiters
          │  └─ Example: "removed 5 stale, 45 active"
          │
          └─ This feeds into:
             ├─ Log aggregation system
             ├─ Alerts on unusual patterns
             └─ Metrics collection (optional Prometheus)


Log Analytics Pipeline:

Application Logs
       │
       ▼
Log Aggregator (ELK, Splunk, etc.)
       │
       ├─ Extract: "removed X stale limiters"
       ├─ Extract: "Y active limiters remaining"
       │
       ▼
Metrics Dashboard
       │
       ├─ Graph: Stale limiter removal rate
       ├─ Graph: Active limiter count trend
       └─ Alert: Abnormal removal patterns
```

## Performance Characteristics

```
Operation Complexity Analysis:

Per-Request Operations:
├─ Map lookup: O(1) average
├─ Limiter access: O(1)
├─ Timestamp update: O(1)
├─ Rate check: O(1)
└─ Total: O(1) constant time ✓

Cleanup Operations:
├─ Lock acquisition: O(1)
├─ Map iteration: O(n) where n = active limiters
├─ Staleness check: O(1) per entry
├─ Deletion: O(1) per entry
├─ Log write: O(1)
└─ Total: O(n) linear in limiter count ✓

Memory Usage:
├─ Per entry: ~224 bytes
│  ├─ Limiter object: ~200 bytes
│  └─ time.Time: ~24 bytes
└─ Bounded: O(m) where m = active clients in TTL window ✓
```

## Shutdown Sequence

```
Application receives shutdown signal (SIGTERM, etc.)
       │
       ▼
Graceful shutdown initiated
       │
       ├─ Handler 1: Close network connections
       ├─ Handler 2: Flush pending requests
       │
       ├─ Handler 3: ◄─── IMPORTANT
       │  │
       │  └─ StopRateLimitCleanup(&config)
       │     │
       │     └─ Close stopCleanupChannel
       │        │
       │        ▼
       │     Cleanup goroutine detects close
       │        │
       │        └─ Exit gracefully
       │           ├─ Deferred ticker.Stop() executes
       │           └─ Cleanup log: "Rate limiter cleanup goroutine stopped"
       │
       └─ Handler 4: Application terminates
          └─ All goroutines cleaned up ✓
```

## Success Indicators

```
Healthy Rate Limiter Status:

Memory Usage Pattern:
├─ Initial: Grows as clients make requests
├─ Equilibrium: Stabilizes after TTL × CleanupInterval
├─ Sustained: Remains stable under steady load ✓

Cleanup Logs:
├─ Frequency: Appears every CleanupInterval seconds
├─ Content: "removed X stale limiters, Y active"
├─ Pattern: X should be 0-10% of Y ✓

Shutdown:
├─ Graceful termination
├─ No goroutine warnings
├─ No panic or crashes ✓

Rate Limiting:
├─ Legitimate requests pass (< configured rate)
├─ Excessive requests blocked (429 response)
├─ Per-client isolation works ✓
```

## Failure Scenarios & Recovery

```
Scenario: Memory still growing

Diagnosis:
├─ TTL too long? Reduce RATE_LIMITER_TTL_SECONDS
├─ Cleanup not running? Check logs for cleanup messages
├─ Cleanup interval too long? Reduce RATE_LIMITER_CLEANUP_INTERVAL_SECONDS
└─ Legitimate client churn? Increase TTL

Recovery:
├─ Adjust environment variables
├─ Restart application
├─ Monitor memory again


Scenario: Rate limiting too aggressive

Diagnosis:
├─ RequestsPerSecond too low?
├─ BurstSize too small?
└─ Legitimate client patterns exceed limit?

Recovery:
├─ Increase RequestsPerSecond
├─ Increase BurstSize
├─ Restart application


Scenario: Cleanup logs missing

Diagnosis:
├─ Goroutine crashed? Check application logs
├─ StopCleanupChannel issue? Check shutdown logic
└─ CleanupInterval very large? Check configuration

Recovery:
├─ Check environment variables
├─ Review application startup logs
├─ Restart with correct configuration
```
