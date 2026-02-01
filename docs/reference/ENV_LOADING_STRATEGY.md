# Environment Loading Strategy - Quick Reference

## Go Backend Environment Loading

### Loading Order
1. **Root `.env`** - Shared configuration (loaded first)
2. **`backend/.env`** - Backend-specific overrides (loaded second with `Overload()`)

### Implementation
```go
// backend/main.go
func main() {
    // Load root .env (shared config)
    if err := godotenv.Load("../.env"); err != nil {
        log.Println("No root .env file found")
    }

    // Load backend .env (overrides)
    if err := godotenv.Overload(".env"); err != nil {
        log.Println("No backend .env file found")
    }

    cfg := config.LoadConfig()
    // ...
}
```

### Variable Locations

**Root `.env` (Shared):**
- `WORKOS_CLIENT_ID` - WorkOS client identifier
- `WORKOS_API_KEY` - WorkOS API key
- `NEO4J_URI` - Neo4j connection string
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `REDIS_URL` - Redis connection string
- `NATS_URL` - NATS connection string

**`backend/.env` (Go-Specific):**
- `PORT` - Go server port (default: 8080)
- `DATABASE_URL` - PostgreSQL connection (Go format: `postgres://`)
- `CSRF_SECRET` - CSRF token secret
- `S3_*` - MinIO/S3 configuration

### Verification Commands

**Test Environment Loading:**
```bash
cd backend
source ../.env
source .env
echo "WORKOS_CLIENT_ID=$WORKOS_CLIENT_ID"
echo "NEO4J_PASSWORD=$NEO4J_PASSWORD"
```

**Test Go Backend:**
```bash
cd backend
go run main.go
# Should see:
# ✅ Neo4j initialized
# Initialized AuthKit adapter with WorkOS integration
```

### Troubleshooting

**Issue: Variables not loading**
- Check `.env` file exists in both locations
- Verify file permissions (readable)
- Check for syntax errors in .env files
- Ensure no trailing whitespace in variable values

**Issue: Wrong values loaded**
- Remember: `backend/.env` overrides root `.env`
- Check load order in main.go
- Verify `Overload()` is used for backend/.env

**Issue: WorkOS client-id-invalid**
- Ensure `WORKOS_CLIENT_ID` exists in root `.env`
- Verify value format: `client_XXXXX...`
- Check backend is loading root `.env` first

**Issue: Neo4j authentication failure**
- Ensure `NEO4J_PASSWORD` in root `.env`
- Verify Neo4j is running: `neo4j status`
- Check credentials match Neo4j configuration

### Best Practices

1. **Shared Config First:** Always load root `.env` before backend-specific
2. **Use Overload for Overrides:** Use `Overload()` for the second file to ensure override behavior
3. **Document Variables:** Keep `.env.example` updated in both locations
4. **Non-Fatal Loading:** Don't crash if .env files missing (use system env vars as fallback)
5. **Validate Critical Vars:** Check required variables exist after loading

### Common Patterns

**Development:**
```bash
# Both .env files present, backend/.env overrides
godotenv.Load("../.env")      # Loads shared config
godotenv.Overload(".env")     # Loads + overrides with backend config
```

**Production (Docker):**
```dockerfile
# Inject environment variables directly
ENV WORKOS_CLIENT_ID=${WORKOS_CLIENT_ID}
ENV NEO4J_PASSWORD=${NEO4J_PASSWORD}
# No .env files needed
```

**Testing:**
```go
// Use environment-specific .env
godotenv.Load("../.env.test")
godotenv.Overload(".env.test")
```

### Related Files

- `/.env` - Root shared configuration
- `/backend/.env` - Go backend configuration
- `/backend/.env.example` - Go backend example variables
- `/backend/main.go` - Environment loading implementation
- `/backend/internal/config/config.go` - Configuration struct

### References

- [godotenv Documentation](https://github.com/joho/godotenv)
- WorkOS Setup Guide
- Neo4j Connection Guide
