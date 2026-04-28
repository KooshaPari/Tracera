#!/bin/bash

# Generate Development Secrets for TraceRTM
# Use ONLY for local development - never use in production
# Run: ./scripts/generate-dev-secrets.sh

set -e

echo "======================================================================"
echo "  TraceRTM Development Secrets Generator"
echo "======================================================================"
echo ""
echo "This script generates secure random secrets for local development."
echo "These secrets are NOT suitable for production."
echo ""

# Check if openssl is available
if ! command -v openssl &> /dev/null; then
    echo "ERROR: openssl is not installed"
    echo "Install with: brew install openssl (macOS) or apt-get install openssl (Linux)"
    exit 1
fi

# Create output file
OUTPUT_FILE="backend/.env.local"

echo "Generating secrets..."
echo ""

# Generate JWT Secret (64 bytes = 512 bits)
JWT_SECRET=$(openssl rand -base64 64)
echo "JWT_SECRET=$JWT_SECRET"

# Generate CSRF Secret (64 bytes = 512 bits)
CSRF_SECRET=$(openssl rand -base64 64)
echo "CSRF_SECRET=$CSRF_SECRET"

# Generate a random port (for development isolation)
DEV_PORT=$((8000 + RANDOM % 100))

# Write to .env.local
cat > "$OUTPUT_FILE" << EOF
# ============================================================================
# TraceRTM Development Environment Configuration
# Generated: $(date)
# ============================================================================
# IMPORTANT: This file contains development secrets only
# NEVER commit this file to version control
# NEVER use these secrets in production

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================
PORT=$DEV_PORT
ENV=development
LOG_LEVEL=debug

# ============================================================================
# AUTHENTICATION & SECURITY
# ============================================================================
# JWT Secret for token signing/validation
JWT_SECRET=$JWT_SECRET

# CSRF Secret (if using CSRF protection)
CSRF_SECRET=$CSRF_SECRET

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
# PostgreSQL local development (assumes postgres running locally)
# To start PostgreSQL:
#   - macOS: brew services start postgresql (if installed via homebrew)
#   - Docker: docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
#
# Default credentials for development:
# - User: postgres
# - Password: password
# - Database: tracertm
DATABASE_URL=postgresql://postgres:password@localhost:5432/tracertm

# Supabase (optional - for cloud development)
# Get these from https://supabase.com/dashboard
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your_local_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_local_service_role_key_here

# ============================================================================
# DRAGONFLY REDIS-COMPATIBLE CONFIGURATION
# ============================================================================
# Dragonfly local development (Redis-compatible protocol on port 6379)
# To start Dragonfly:
#   - Native/process-compose: REDIS_COMPAT_PROVIDER=dragonfly
#   - Docker: docker run -p 6379:6379 docker.dragonflydb.io/dragonflydb/dragonfly:latest
# Redis remains an explicit fallback only: REDIS_COMPAT_PROVIDER=redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_COMPAT_PROVIDER=dragonfly

# ============================================================================
# NATS CONFIGURATION
# ============================================================================
# NATS local development (assumes nats-server running locally)
# To start NATS:
#   - Docker: docker run -p 4222:4222 nats:latest
NATS_URL=nats://localhost:4222
NATS_CREDS=

# ============================================================================
# NEO4J GRAPH DATABASE
# ============================================================================
# Neo4j local development
# To start Neo4j:
#   - Docker: docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
#   - Desktop: Download from https://neo4j.com/download/
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
# Allow local development origins (no wildcards in development)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000

# ============================================================================
# STORAGE CONFIGURATION (S3/R2)
# ============================================================================
# Local MinIO or S3-compatible storage (optional)
# To start MinIO:
#   - Docker: docker run -p 9000:9000 -p 9001:9001 minio/minio:latest
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET=tracertm-dev
S3_REGION=us-east-1

# ============================================================================
# FEATURE FLAGS
# ============================================================================
# Enable development features
ENABLE_WEBSOCKET=true
ENABLE_EVENTS=true
ENABLE_SEARCH=true
ENABLE_VECTOR_SEARCH=false
ENABLE_NATS=false
ENABLE_REDIS_CACHE=true

# ============================================================================
# EMBEDDINGS CONFIGURATION
# ============================================================================
# Use local embeddings for development (no API calls)
EMBEDDING_PROVIDER=local

# Optional: Use actual providers for testing
# EMBEDDING_PROVIDER=voyage
# VOYAGE_API_KEY=your_voyageai_api_key_here
# VOYAGE_MODEL=voyage-3.5
# VOYAGE_DIMENSIONS=1024

# ============================================================================
# EXTERNAL SERVICES (Optional for Development)
# ============================================================================
# WorkOS OAuth (optional - leave empty to skip)
# Get from: https://dashboard.workos.com
WORKOS_CLIENT_ID=
WORKOS_API_KEY=

# VoyageAI Embeddings (optional - leave empty to skip)
# Get from: https://www.voyageai.com/
VOYAGE_API_KEY=

# OpenRouter Embeddings (optional - leave empty to skip)
# Get from: https://openrouter.ai/
OPENROUTER_API_KEY=

# Hatchet Workflow (optional - leave empty to skip)
HATCHET_CLIENT_TOKEN=

# ============================================================================
# LOGGING
# ============================================================================
# Development logging is verbose for debugging
LOG_LEVEL=debug
LOG_FORMAT=json

# ============================================================================
# NOTE
# ============================================================================
# Start local services before running the application:
#
# Option 1: Using Docker Compose (recommended)
#   docker-compose -f backend/docker-compose.dev.yml up -d
#
# Option 2: Individual services
#   - PostgreSQL: docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
#   - Dragonfly:  docker run -p 6379:6379 docker.dragonflydb.io/dragonflydb/dragonfly:latest
#   - NATS:       docker run -p 4222:4222 nats:latest
#   - Neo4j:      docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
#   - MinIO:      docker run -p 9000:9000 -p 9001:9001 minio/minio:latest
#
# Then run the application:
#   cd backend && go run main.go
#
# ============================================================================
EOF

echo ""
echo "======================================================================"
echo "Development secrets generated successfully!"
echo "======================================================================"
echo ""
echo "Environment file created: $OUTPUT_FILE"
echo "Development server port: $DEV_PORT"
echo ""
echo "IMPORTANT REMINDERS:"
echo "1. Never commit this file to version control"
echo "2. These secrets are for LOCAL DEVELOPMENT ONLY"
echo "3. Start local services before running the application"
echo ""
echo "Start services with Docker Compose:"
echo "  docker-compose -f backend/docker-compose.dev.yml up -d"
echo ""
echo "Run the application:"
echo "  cd backend && go run main.go"
echo ""
echo "======================================================================"
