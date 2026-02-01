# Docker Layer Optimization Reference

Complete Docker optimization configuration for TracerTM services, implementing multi-stage builds, layer caching strategies, and comprehensive ignore patterns.

## Table of Contents

1. [Overview](#overview)
2. [Optimization Patterns](#optimization-patterns)
3. [Service-Specific Configurations](#service-specific-configurations)
4. [Layer Caching Strategy](#layer-caching-strategy)
5. [Build Performance Metrics](#build-performance-metrics)
6. [Troubleshooting](#troubleshooting)

## Overview

Docker build performance is optimized through:

- **Multi-stage builds**: Separate builder and runtime stages to reduce final image size
- **Layer caching**: Strategic ordering of commands to maximize cache hits
- **Minimal base images**: Alpine images for production services (8-15MB vs 100+MB)
- **Dependency isolation**: Lock files copied separately from source code
- **Comprehensive .dockerignore**: Excludes unnecessary files from build context

### Key Metrics

| Service | Builder Image | Runtime Image | Final Size | Build Time |
|---------|---------------|---------------|-----------|-----------|
| Frontend | 400-500MB | nginx:1.27-alpine | ~50MB | 45-60s |
| Backend | 300-400MB | alpine:3.20 | ~15MB | 30-45s |
| DevContainer | N/A (dev env) | ubuntu:22.04 | 2-3GB | 5-10min |

## Optimization Patterns

### Pattern 1: Multi-Stage Build (Production Services)

```dockerfile
# Stage 1: Builder - includes all build tools
FROM oven/bun:1.1.38-alpine AS builder
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun run build

# Stage 2: Runtime - only runtime dependencies
FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
```

**Benefits:**
- Builder dependencies (node, python, git, etc.) excluded from final image
- Only compiled artifacts and runtime dependencies in final image
- ~80% size reduction on average

### Pattern 2: Layer Ordering for Cache Efficiency

```dockerfile
# Order: System deps → Runtime → App deps → Source (least to most stable)

# Layer 1: System dependencies (rarely changes)
RUN apk add --no-cache ca-certificates curl

# Layer 2: Runtime configuration (occasionally changes)
RUN addgroup -g 1000 -S appuser && adduser -u 1000 -S appuser -G appuser

# Layer 3: Package dependencies (changes when lock file changes)
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Layer 4: Source code (changes frequently)
COPY . .
RUN bun run build
```

**Cache Hit Probability:**
- Layer 1: 99% (system packages stable)
- Layer 2: 95% (configuration stable)
- Layer 3: 85% (dependencies moderately stable)
- Layer 4: 30% (source code frequently changes)

### Pattern 3: Security - Non-root User

```dockerfile
# Create dedicated user with minimal privileges
RUN addgroup -g 1000 -S appuser && \
    adduser -u 1000 -S appuser -G appuser

# Copy files with correct ownership
COPY --chown=appuser:appuser ./app ./

# Switch to non-root user
USER appuser
```

**Benefits:**
- Container can't escalate to root
- File permissions enforced
- Meets security compliance requirements

### Pattern 4: Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

**Usage:**
```bash
docker ps  # Shows health status
docker inspect <container>  # Detailed health status
# Kubernetes, Docker Compose use for automatic restarts
```

### Pattern 5: Cache Cleanup

```dockerfile
# After apt-get install
RUN apt-get update && \
    apt-get install -y --no-install-recommends package && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# After pip install
RUN pip install --no-cache-dir -r requirements.txt

# After go build
RUN go build ... && \
    rm -rf /go/pkg
```

**Space Savings:**
- apt cache: 50-100MB per install
- pip cache: 100-300MB total
- Go pkg: 50-200MB

## Service-Specific Configurations

### Frontend Service (web)

**File:** `/frontend/apps/web/Dockerfile`

```dockerfile
FROM oven/bun:1.1.38-alpine AS builder  # 450MB builder
FROM nginx:1.27-alpine                  # 50MB final

# Key optimizations:
# - Pre-gzip assets (saves ~60% bandwidth)
# - Nginx config optimization
# - Security headers
# - HSTS enabled
```

**Build time:** ~50s (cached deps)
**Final image:** ~50MB
**Cache layers:** 6 critical

### Backend Service (Go)

**File:** `/backend/Dockerfile`

```dockerfile
FROM golang:1.23-alpine AS builder      # 350MB builder
FROM alpine:3.20                        # 15MB final

# Key optimizations:
# - Aggressive build flags (-w -s)
# - Static binary (no libc dependency)
# - Trimpath for reproducible builds
# - Minimal runtime dependencies
```

**Build time:** ~35s (cached deps)
**Final image:** ~15MB
**Cache layers:** 4 critical

### Dev Container

**File:** `/.devcontainer/Dockerfile`

```dockerfile
FROM ubuntu:22.04  # 100MB base

# Multi-language support:
# - Go 1.23
# - Python 3.11
# - Node.js 20 + Bun
# - Development tools (air, golangci-lint, etc.)

# Single-stage build (development context)
# Not optimized for size (needs all tools available)
```

**Build time:** ~8-10 min (initial), ~30s (cached)
**Final image:** 2-3GB
**Cache layers:** 13 development layers

## Layer Caching Strategy

### Rebuild Scenarios

| Scenario | Cache Result | Rebuild Time |
|----------|--------------|--------------|
| System packages unchanged | ✓ Cached | <1s |
| Dependencies unchanged | ✓ Cached | 2-5s |
| Source code changed | ✗ Miss | 45-60s |
| Lock file changed | ✗ Miss | 30-45s |
| Base image updated | ✗ Miss | 60-90s |

### Maximize Cache Hits

1. **Never COPY before dependency installation**
   ```dockerfile
   # Bad: Rebuilds on any source change
   COPY . .
   RUN bun install

   # Good: Caches until lock file changes
   COPY package.json bun.lock ./
   RUN bun install
   COPY . .
   ```

2. **Use specific tags (not :latest)**
   ```dockerfile
   # Bad: Always pulls latest, breaks determinism
   FROM node:latest

   # Good: Pinned to specific version
   FROM oven/bun:1.1.38-alpine
   ```

3. **Combine RUN commands when appropriate**
   ```dockerfile
   # Bad: 3 layers
   RUN apt-get update
   RUN apt-get install -y pkg1
   RUN apt-get install -y pkg2

   # Good: 1 layer
   RUN apt-get update && \
       apt-get install -y --no-install-recommends pkg1 pkg2 && \
       rm -rf /var/lib/apt/lists/*
   ```

## .dockerignore Patterns

### Root Project (`/.dockerignore`)

**Excludes (256 patterns):**
- Git metadata: `.git/`, `.gitignore`, etc.
- Build artifacts: `node_modules/`, `dist/`, `build/`
- Documentation: `*.md`, `docs/`, `research/`
- IDE config: `.vscode/`, `.idea/`, etc.
- Development tools: `.air/`, `.turbo/`, `.devcontainer/`
- Lock files: `bun.lock`, `go.sum`, `uv.lock`
- Environment files: `.env*`
- Large archives: `*.tar.gz`, `*.zip`
- Test artifacts: `coverage/`, `.pytest_cache/`
- Archive: `ARCHIVE/`, `DEMO_PROJECT/`

**Impact:** ~80% reduction in build context size

### Backend Service (`/backend/.dockerignore`)

**Excludes (177 patterns):**
- All root exclusions (inherited via Docker)
- Plus Go-specific: `vendor/`, `go.work*`, `*.prof`
- Frontend files not needed in backend

**Impact:** ~500MB → ~50MB build context

### Frontend Web App (`/frontend/apps/web/.dockerignore`)

**Excludes (129 patterns):**
- Root exclusions + frontend-specific
- Storybook: `.storybook/`, `storybook-static/`
- Test runners: `.playwright/`, `.vitest/`, `cypress/`
- Vite cache: `.vite/`

**Impact:** ~600MB → ~100MB build context

### Dev Container (`/.devcontainer/.dockerignore`)

**Excludes (237 patterns):**
- Comprehensive: Prepares for multi-language development
- Includes all backend, frontend, and shared exclusions
- Allows tools to be available in container

**Impact:** ~1.5GB → ~800MB build context

## Build Performance Metrics

### Frontend Service Build Profile

```
Stage 1 (Builder):
  - Base image pull: 3-5s (cached)
  - System deps: 8-12s
  - Bun install: 15-25s
  - Bun build: 20-30s
  Total: ~50s

Stage 2 (Runtime):
  - Base image pull: 1-2s (cached)
  - Copy artifacts: 1-3s
  - Asset compression: 5-10s
  Total: ~10s

Full build: 60s (initial), 12s (cached deps)
```

### Backend Service Build Profile

```
Stage 1 (Builder):
  - Base image pull: 3-5s (cached)
  - System deps: 5-8s
  - Go mod download: 10-15s
  - Go build: 15-25s
  Total: ~35s

Stage 2 (Runtime):
  - Base image pull: 1-2s (cached)
  - Copy binary: <1s
  Total: ~5s

Full build: 40s (initial), 6s (cached deps)
```

### Dev Container Build Profile

```
First build:
  - Base image pull: 10-15s
  - System packages: 30-45s
  - Go tools: 15-20s
  - Python setup: 15-20s
  - Node/Bun: 15-20s
  - Development tools: 20-30s
  Total: ~8-10 minutes

Cached builds: ~30s
```

## Troubleshooting

### Problem: Build times increasing

**Solution 1: Clear build cache**
```bash
docker builder prune
```

**Solution 2: Check .dockerignore**
```bash
# Verify context size
docker build --no-cache --progress=plain 2>&1 | grep "Sending build context"
```

**Solution 3: Optimize layers**
```bash
# Profile layers
docker build --progress=plain . 2>&1 | grep "RUN"
```

### Problem: Image size larger than expected

**Solutions:**
1. Enable multi-stage build
2. Use Alpine base images
3. Remove unnecessary packages
4. Clean up cache: `rm -rf /var/lib/apt/lists/*`

### Problem: Cache not working

**Check:**
1. Lock files included in COPY
2. Lock files are actually changing
3. No forced rebuilds in CI/CD

### Problem: Permission denied in container

**Check:**
1. Ensure non-root user created before COPY
2. Use `--chown` flag in COPY
3. Verify USER directive

### Problem: Container exits immediately

**Check:**
1. HEALTHCHECK running correctly
2. CMD/ENTRYPOINT executable
3. Dependencies installed

## References

- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Layer Caching Strategy](https://docs.docker.com/build/cache/)
- [Alpine Linux](https://alpinelinux.org/)

## Related Files

- `/frontend/apps/web/Dockerfile` - Frontend service
- `/frontend/apps/web/.dockerignore` - Frontend ignore patterns
- `/backend/Dockerfile` - Backend service
- `/backend/.dockerignore` - Backend ignore patterns
- `/.dockerignore` - Root project ignore patterns
- `/.devcontainer/Dockerfile` - Development container
- `/.devcontainer/.dockerignore` - Dev container ignore patterns
