# syntax=docker/dockerfile:1.7
# Tracera production image — Rust server + Go backend sidecar

ARG RUST_VERSION=1.83
ARG GO_VERSION=1.23
ARG NODE_VERSION=22
ARG PYTHON_VERSION=3.12

FROM rust:${RUST_VERSION}-slim AS rust-builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config libssl-dev ca-certificates && rm -rf /var/lib/apt/lists/*
COPY crates ./crates
COPY Cargo.toml Cargo.lock ./
RUN cargo build --release --bin tracera-server

FROM golang:${GO_VERSION}-alpine AS go-builder
WORKDIR /build
COPY backend/go.mod backend/go.sum ./
RUN go mod download
COPY backend/ ./
RUN CGO_ENABLED=0 go build -ldflags='-s -w' -o /out/tracera-backend ./cmd/main.go 2>/dev/null || \
    CGO_ENABLED=0 go build -ldflags='-s -w' -o /out/tracera-backend .

FROM node:${NODE_VERSION}-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package.json frontend/bun.lockb* ./
RUN corepack enable && bun install --frozen-lockfile || npm ci
COPY frontend/ ./
RUN bun run build || npm run build

FROM python:${PYTHON_VERSION}-slim AS final
WORKDIR /app
RUN pip install --no-cache-dir uv

# Copy all artifacts
COPY --from=rust-builder /build/target/release/tracera-server /app/tracera-server
COPY --from=go-builder   /out/tracera-backend                 /app/tracera-backend
COPY --from=frontend-builder /build/dist                       /app/frontend/dist
COPY pyproject.toml uv.lock* ./
COPY alembic ./alembic
COPY proto/tracera.proto /app/proto/

ENV RUST_LOG=info \
    TRACERA_RUST_BIN=/app/tracera-server \
    TRACERA_GO_BIN=/app/tracera-backend \
    FRONTEND_DIST=/app/frontend/dist \
    PORT=8080

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/health || exit 1

ENTRYPOINT ["/app/tracera-server"]
