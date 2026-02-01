# ============================================================================
# BUILDER STAGE: Build React/Vite application with minimal dependencies
# ============================================================================
FROM oven/bun:1.1.38-alpine AS builder

LABEL stage=builder

WORKDIR /app

# Install build dependencies only (won't be in final image)
RUN apk add --no-cache \
    ca-certificates \
    python3 \
    make

# Layer 1: Copy monorepo root package files first (most stable)
COPY ../../package.json ../../bun.lock ../../.bun* ./../../

# Layer 2: Copy workspace package files
COPY package.json bun.lock ./

# Layer 3: Install dependencies (cached until lock file changes)
# Use frozen-lockfile to ensure reproducible builds
RUN bun install --frozen-lockfile --no-progress

# Layer 4: Copy source code (most frequently changed)
COPY . .

# Layer 5: Build application with optimizations
ARG VITE_API_URL=http://localhost:8080
ARG VITE_ENABLE_PROFILING=false
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_ENABLE_PROFILING=${VITE_ENABLE_PROFILING}
ENV NODE_ENV=production

RUN bun run build

# Optional: Verify build artifacts
RUN test -d dist && ls -lh dist || (echo "Build failed: dist directory not found" && exit 1)

# ============================================================================
# RUNTIME STAGE: Lightweight Nginx server (~50MB total)
# ============================================================================
FROM nginx:1.27-alpine

LABEL maintainer="TracerTM Team"
LABEL description="TracerTM web frontend service"

# Install runtime dependencies only
RUN apk add --no-cache \
    curl \
    ca-certificates

WORKDIR /app

# Create nginx user with restricted permissions
RUN addgroup -g 1001 -S nginx-app && \
    adduser -u 1001 -S nginx-app -G nginx-app

# Copy optimized Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder --chown=nginx-app:nginx-app /app/dist /usr/share/nginx/html

# Create necessary directories with proper permissions
RUN mkdir -p /var/run/nginx && \
    chown -R nginx-app:nginx-app /var/run/nginx /var/log/nginx /var/cache/nginx

# Create cache directory for pre-gzipped assets
RUN mkdir -p /usr/share/nginx/html/.gzip && \
    chown -R nginx-app:nginx-app /usr/share/nginx/html

# Pre-compress commonly requested static assets
RUN cd /usr/share/nginx/html && \
    find . -type f \( -name "*.js" -o -name "*.css" -o -name "*.svg" -o -name "*.json" \) \
    -exec gzip -9 -k {} \; 2>/dev/null || true

# Switch to non-root user for security
USER nginx-app

# Expose port
EXPOSE 8080

# Health check with curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
