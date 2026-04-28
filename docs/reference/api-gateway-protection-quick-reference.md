# API Gateway Protection Quick Reference

**Version:** 1.0.0 | **Updated:** 2026-02-01

## At a Glance

### Default Limits

| Type | Limit | Window |
|------|-------|--------|
| **Authenticated Users** | 100 req/min | 1 minute |
| **Anonymous (IP)** | 20 req/min | 1 minute |
| **Auth Endpoints** | 5 req/min | 1 minute |
| **Expensive Ops** | 10 req/min | 1 minute |
| **Daily Quota** | 10,000 req | 24 hours |
| **Monthly Quota** | 100,000 req | 30 days |

### Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| **200 OK** | Request allowed | Continue |
| **429 Too Many Requests** | Rate limit exceeded | Check `Retry-After` header |
| **402 Payment Required** | Quota exceeded | Wait for reset or upgrade |
| **401 Unauthorized** | Invalid API key | Check credentials |
| **403 Forbidden** | Insufficient permissions | Request access |

## Common Operations

### Create API Key

```bash
curl -X POST http://localhost:8080/api/v1/api-keys \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "role": "read-write",
    "scopes": ["projects:*", "items:read"],
    "expires_at": "2027-01-01T00:00:00Z"
  }'

# Response: { "key": "trace_abc123...", "id": "..." }
# SAVE THIS KEY - it's only shown once!
```

### Use API Key

```bash
# Option 1: Authorization header
curl http://localhost:8080/api/v1/projects \
  -H "Authorization: Bearer trace_abc123..."

# Option 2: X-API-Key header
curl http://localhost:8080/api/v1/projects \
  -H "X-API-Key: trace_abc123..."
```

### Check Rate Limit Status

```bash
curl -I http://localhost:8080/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  | grep -E "X-RateLimit|X-Quota"
```

### Revoke API Key

```bash
curl -X DELETE http://localhost:8080/api/v1/api-keys/$KEY_ID \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"reason": "Key compromised"}'
```

## Response Headers

### Rate Limiting

```http
X-RateLimit-Limit: 100          # Total requests allowed
X-RateLimit-Remaining: 87       # Requests remaining
X-RateLimit-Reset: 1738454400   # Unix timestamp when limit resets
Retry-After: 45                 # Seconds until you can retry
```

### Quotas

```http
X-Quota-Daily-Limit: 10000
X-Quota-Daily-Remaining: 8432
X-Quota-Daily-Reset: 1738454400
X-Quota-Monthly-Limit: 100000
X-Quota-Monthly-Remaining: 76543
X-Quota-Monthly-Reset: 1741046400
```

## Error Responses

### Rate Limit Exceeded (429)

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Please try again later.",
  "reset_time": 1738454400,
  "retry_after": 45
}
```

### Quota Exceeded (402)

```json
{
  "error": "quota_exceeded",
  "message": "Your daily quota has been exceeded",
  "period": "daily",
  "reset_time": 1738454400,
  "retry_after": 3600
}
```

### Invalid API Key (401)

```json
{
  "error": "invalid_api_key",
  "message": "The provided API key is invalid or has been revoked"
}
```

### Insufficient Permissions (403)

```json
{
  "error": "insufficient_scope",
  "message": "API key does not have required scope",
  "required": "projects:write",
  "has_scopes": ["projects:read", "items:read"]
}
```

## API Key Roles

| Role | Can Read | Can Write | Can Delete | Can Manage Keys |
|------|----------|-----------|------------|-----------------|
| **read-only** | ✅ | ❌ | ❌ | ❌ |
| **read-write** | ✅ | ✅ | ✅ | ❌ |
| **admin** | ✅ | ✅ | ✅ | ✅ |

## Scopes

### Format
- `resource:action` - Specific permission
- `resource:*` - All actions on resource
- `*` - Full access (admin only)

### Common Scopes
```
projects:read       # Read projects
projects:write      # Create/update projects
projects:delete     # Delete projects
projects:*          # All project operations

items:read          # Read items
items:write         # Create/update items
items:*             # All item operations

graph:read          # View graph
graph:analyze       # Run analysis
graph:*             # All graph operations
```

## Priority Levels

Requests are queued by priority when backend is under load:

| Priority | Use Case | Timeout Multiplier | Capacity |
|----------|----------|-------------------|----------|
| **Admin** | System operations | 2.0x | 10% |
| **High** | Interactive UI | 1.5x | 30% |
| **Normal** | Standard API | 1.0x | 50% |
| **Low** | Batch jobs | 0.5x | 10% |

## Configuration

### Environment Variables

```bash
# Rate Limiting
RATE_LIMIT_AUTH_RPM=5
RATE_LIMIT_API_RPM=100
RATE_LIMIT_ANON_RPM=20

# Quotas
QUOTA_DAILY_DEFAULT=10000
QUOTA_MONTHLY_DEFAULT=100000
QUOTA_OVERAGE_ACTION=reject  # reject|throttle|bill

# Redis
REDIS_URL=redis://localhost:6379

# Throttling
THROTTLE_MAX_CONCURRENT=1000
THROTTLE_LOAD_THRESHOLD=0.8
```

## Monitoring Commands

### Check Redis Rate Limits

```bash
# List all rate limit keys
redis-cli --scan --pattern "ratelimit:*"

# Check specific user's rate limit
redis-cli ZCARD "ratelimit:sliding:user:123"

# View quota usage
redis-cli GET "quota:user:123:daily:2026-02-01"
```

### View API Key Usage

```bash
# Get API key statistics (last 7 days)
curl http://localhost:8080/api/v1/api-keys/$KEY_ID/stats?days=7 \
  -H "Authorization: Bearer $TOKEN"
```

### Monitor System Metrics

```bash
# Get throttler metrics
curl http://localhost:8080/metrics \
  | grep -E "throttle|ratelimit|quota"
```

## Troubleshooting

### "Rate limit exceeded" but I haven't made many requests

**Cause:** You may be sharing an IP with other users (NAT, proxy)

**Solution:** Use an authenticated API key to get per-user limits (100 req/min vs 20 req/min)

### API key returns 401 but it's valid

**Possible causes:**
1. Key has expired - check `expires_at`
2. Key has been revoked - check with admin
3. Wrong format - ensure `trace_` prefix

### Quota exceeded unexpectedly

**Check:**
```bash
# View quota usage
curl http://localhost:8080/api/v1/quotas/current \
  -H "Authorization: Bearer $TOKEN"
```

### Requests timing out under load

**Cause:** Backend overloaded, requests being throttled

**Check:** Priority level - use higher priority for interactive operations

## Best Practices

### DO ✅
- Store API keys securely (environment variables, secrets manager)
- Use specific scopes (least privilege principle)
- Monitor your rate limit headers
- Implement exponential backoff on 429 responses
- Use authenticated keys for higher limits
- Rotate keys regularly
- Set expiration dates on keys

### DON'T ❌
- Hardcode API keys in source code
- Share API keys between services
- Use `*` scope unless necessary
- Ignore rate limit headers
- Retry immediately on 429
- Use anonymous access for high-volume operations
- Keep revoked keys

## Rate Limit Retry Logic

```javascript
async function makeRequest(url, options) {
  const response = await fetch(url, options);

  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    const delay = parseInt(retryAfter) * 1000 || 60000;

    await new Promise(resolve => setTimeout(resolve, delay));
    return makeRequest(url, options); // Retry
  }

  return response;
}
```

## Support

- **Documentation:** `/docs/guides/api-gateway-protection-guide.md`
- **API Reference:** `https://api.tracertm.com/docs`
- **Issues:** `https://github.com/kooshapari/trace/issues`
- **Email:** `api-support@tracertm.com`

## Related Documentation

- [Full API Gateway Protection Guide](../guides/api-gateway-protection-guide.md)
- [Rate Limiting Package](../../backend/internal/ratelimit/README.md)
- [Authentication Guide](../guides/authentication-guide.md)
- [Redis Configuration](./redis-config.md)

---

**Quick Tips:**
- Use `curl -I` to check limits without consuming quota
- Set `X-Request-Priority: high` for interactive operations
- Monitor quota usage daily to avoid unexpected limits
- Use webhooks for quota alerts (coming soon)

**Version:** 1.0.0 | **Last Updated:** 2026-02-01
