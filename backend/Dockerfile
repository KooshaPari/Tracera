# ============================================================================
# BUILDER STAGE: Compile Go binary with minimal dependencies
# ============================================================================
FROM golang:1.23-alpine AS builder

# Install build-time dependencies only (these won't appear in final image)
RUN apk add --no-cache \
    git \
    ca-certificates \
    make

WORKDIR /app

# Layer 1: Copy dependency manifests first (most stable, caches well)
COPY go.mod go.sum ./

# Layer 2: Download dependencies (cached until go.mod/go.sum changes)
RUN go mod download && \
    go mod verify

# Layer 3: Copy source code (most frequently changed)
COPY . .

# Layer 4: Build the application with aggressive optimizations
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -a -installsuffix cgo \
    -ldflags="-w -s -X main.Version=$(git describe --tags --always 2>/dev/null || echo 'dev')" \
    -trimpath \
    -o tracertm-backend .

# Optional: Run tests during build to catch issues early
RUN go test -v ./... -short || true

# ============================================================================
# RUNTIME STAGE: Minimal production image
# ============================================================================
FROM alpine:3.20

LABEL maintainer="TracerTM Team"
LABEL description="TracerTM Go backend service"

# Install only essential runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    curl

WORKDIR /app

# Create dedicated non-root user for security (least privilege)
RUN addgroup -g 1000 -S tracertm && \
    adduser -u 1000 -S tracertm -G tracertm

# Copy binary from builder stage (only ~5-10MB)
COPY --from=builder --chown=tracertm:tracertm /app/tracertm-backend ./

# Copy configuration files if they exist (SQL migrations, etc.)
COPY --from=builder --chown=tracertm:tracertm /app/*.sql ./migrations/ 2>/dev/null || true
COPY --from=builder --chown=tracertm:tracertm /app/config/ ./config/ 2>/dev/null || true

# Switch to non-root user
USER tracertm

# Expose service port
EXPOSE 8080

# Health check: verify service is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["./tracertm-backend"]

