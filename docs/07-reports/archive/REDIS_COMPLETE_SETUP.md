# Redis Complete Setup Guide

## Local Development (Docker)

```bash
# Start Redis
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine \
  redis-server --appendonly yes

# Test connection
redis-cli ping
# Output: PONG
```

## Production Setup (Upstash)

### 1. Create Upstash Account
- Go to https://console.upstash.com
- Sign up with GitHub/Google
- Create new Redis database

### 2. Get Connection String
```
Connection String: redis://default:password@host:port
```

### 3. Environment Variable
```bash
export REDIS_URL="redis://default:password@host:port"
```

## Go Integration

### 1. Install Package
```bash
go get github.com/redis/go-redis/v9
```

### 2. Create Redis Client

```go
// backend/internal/cache/redis.go
package cache

import (
    "context"
    "github.com/redis/go-redis/v9"
)

type RedisCache struct {
    client *redis.Client
}

func NewRedisCache(url string) (*RedisCache, error) {
    opt, err := redis.ParseURL(url)
    if err != nil {
        return nil, err
    }
    
    client := redis.NewClient(opt)
    
    // Test connection
    if err := client.Ping(context.Background()).Err(); err != nil {
        return nil, err
    }
    
    return &RedisCache{client: client}, nil
}

func (r *RedisCache) Get(ctx context.Context, key string) (string, error) {
    return r.client.Get(ctx, key).Result()
}

func (r *RedisCache) Set(ctx context.Context, key string, value string, ttl time.Duration) error {
    return r.client.Set(ctx, key, value, ttl).Err()
}

func (r *RedisCache) Delete(ctx context.Context, keys ...string) error {
    return r.client.Del(ctx, keys...).Err()
}

func (r *RedisCache) Close() error {
    return r.client.Close()
}
```

### 3. Initialize in main.go

```go
// backend/main.go
redisCache, err := cache.NewRedisCache(os.Getenv("REDIS_URL"))
if err != nil {
    log.Fatal("Failed to connect to Redis:", err)
}
defer redisCache.Close()
```

## Usage Patterns

### Cache-Aside Pattern
```go
func (h *ItemHandler) GetItems(c echo.Context) error {
    // Try cache first
    cached, err := h.cache.Get(c.Request().Context(), "items:all")
    if err == nil {
        return c.JSON(200, cached)
    }
    
    // Query database
    items, err := h.db.GetItems(c.Request().Context())
    if err != nil {
        return err
    }
    
    // Store in cache (5 minute TTL)
    data, _ := json.Marshal(items)
    h.cache.Set(c.Request().Context(), "items:all", string(data), 5*time.Minute)
    
    return c.JSON(200, items)
}
```

### Session Storage
```go
func (h *Handler) SetSession(c echo.Context, userID string, data interface{}) error {
    key := fmt.Sprintf("session:%s", userID)
    value, _ := json.Marshal(data)
    return h.cache.Set(c.Request().Context(), key, string(value), 24*time.Hour)
}
```

## Monitoring

### Redis CLI
```bash
# Connect to Redis
redis-cli -u redis://default:password@host:port

# Check memory usage
INFO memory

# Check connected clients
INFO clients

# Monitor commands
MONITOR

# Check key count
DBSIZE
```

### Upstash Dashboard
- Memory usage
- Commands per second
- Connected clients
- Key distribution

## Performance Tuning

### Connection Pooling
```go
opt := &redis.Options{
    Addr:         "localhost:6379",
    PoolSize:     10,
    MinIdleConns: 5,
}
client := redis.NewClient(opt)
```

### Key Expiration
```go
// Set with TTL
cache.Set(ctx, "key", "value", 5*time.Minute)

// Or use EXPIRE
client.Expire(ctx, "key", 5*time.Minute)
```

## Troubleshooting

### Connection Issues
```bash
# Test connection
redis-cli -u redis://default:password@host:port ping

# Check network
telnet host port
```

### Memory Issues
```bash
# Check memory usage
redis-cli INFO memory

# Clear cache
redis-cli FLUSHDB

# Set max memory policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Cost

- **Local**: Free (Docker)
- **Upstash Free Tier**: 
  - 10,000 commands/day
  - 256MB storage
  - Perfect for development/testing
- **Upstash Pro**: $0.20/GB/month

## Next Steps

1. Set up local Redis with Docker
2. Create RedisCache struct in Go
3. Integrate with handlers
4. Test cache-aside pattern
5. Deploy to Upstash for production

