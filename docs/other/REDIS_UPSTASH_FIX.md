# Redis Upstash Configuration Fix

## Problem
The backend was failing to connect to Redis with the error:
```
redis: connection pool: failed to dial after 5 attempts: dial tcp: address redis://localhost:6379: too many colons in address
```

## Root Causes
1. **Incorrect Redis URL parsing**: The infrastructure code was treating the Redis URL as a direct address instead of parsing it as a full Redis URL
2. **Missing Upstash configuration**: The .env file had Upstash REST API credentials but no native Redis URL
3. **No fallback mechanism**: When native Redis failed, there was no fallback to Upstash REST API

## Solution Implemented

### 1. Fixed Redis URL Parsing
**File**: `backend/internal/infrastructure/infrastructure.go`
- Changed from: `redis.NewClient(&redis.Options{Addr: cfg.RedisUrl})`
- Changed to: `redis.ParseURL(cfg.RedisUrl)` which properly parses the full Redis URL

### 2. Added Upstash REST API Support
**File**: `backend/internal/cache/upstash.go` (NEW)
- Created `UpstashCache` struct that uses Upstash REST API
- Implements the same cache interface as RedisCache
- Methods: Get, Set, Delete, InvalidatePattern, Close, ping

### 3. Created Cache Interface
**File**: `backend/internal/cache/interface.go` (NEW)
- Defined `Cache` interface for abstraction
- Allows both RedisCache and UpstashCache to be used interchangeably

### 4. Updated Configuration
**File**: `backend/internal/config/config.go`
- Added `UpstashRedisRestURL` field
- Added `UpstashRedisRestToken` field
- Reads from environment variables: `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`

### 5. Updated .env File
**File**: `.env`
- Added native Redis URL: `REDIS_URL="redis://default:password@host:port"`
- Kept existing Upstash REST credentials for fallback

### 6. Implemented Fallback Logic
**File**: `backend/internal/infrastructure/infrastructure.go`
- Try native Redis connection first
- If native Redis fails, automatically fall back to Upstash REST API
- Both Redis and Neo4j are now optional (log warnings instead of failing)

## Configuration

### Environment Variables
```bash
# Native Redis (optional)
REDIS_URL="redis://default:password@host:port"

# Upstash REST API (fallback)
UPSTASH_REDIS_REST_URL="https://vocal-hyena-36658.upstash.io"
UPSTASH_REDIS_REST_TOKEN="AY8yAAIncDJhZDIzMzdjZWUxNWQ0NDQzYTdjMDIxYjM5MGU4YmI5MnAyMzY2NTg"
```

## Result
✅ Backend now successfully initializes with Upstash REST API for caching
✅ Automatic fallback from native Redis to Upstash REST API
✅ Graceful degradation when services are unavailable

## Files Modified
1. `backend/internal/infrastructure/infrastructure.go` - Added fallback logic
2. `backend/internal/config/config.go` - Added Upstash config fields
3. `.env` - Added native Redis URL

## Files Created
1. `backend/internal/cache/upstash.go` - Upstash REST API implementation
2. `backend/internal/cache/interface.go` - Cache interface definition
3. `REDIS_UPSTASH_FIX.md` - This documentation

