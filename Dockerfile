# Multi-stage build for TraceRTM Go Backend

# Stage 1: Builder
FROM golang:1.22-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache git ca-certificates

# Copy go mod files
COPY backend/go.mod backend/go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY backend/ .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o tracertm-backend .

# Stage 2: Runtime
FROM alpine:latest

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache ca-certificates curl postgresql-client

# Copy binary from builder
COPY --from=builder /build/tracertm-backend .

# Create non-root user
RUN addgroup -g 1000 tracertm && \
    adduser -D -u 1000 -G tracertm tracertm

USER tracertm

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Default command
CMD ["./tracertm-backend"]

