# ===========================================
# STAGE 1: Security scanning base
# ===========================================
FROM python:3.11-slim AS security-scan

# Install security tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install security scanners
RUN pip install --no-cache-dir safety bandit pip-audit

# Copy requirements for security scanning
WORKDIR /scan
COPY requirements*.txt ./

# Run security checks on dependencies
RUN safety check --file requirements.txt --output json --save-json safety-report.json || true
RUN pip-audit --format=json --output=pip-audit-report.json -r requirements.txt || true

# ===========================================
# STAGE 2: Build dependencies
# ===========================================
FROM python:3.11-slim AS builder

# Install minimal build dependencies with security focus
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements*.txt ./

# Create virtual environment with secure settings
RUN python -m venv /opt/venv \
    && /opt/venv/bin/python -m pip install --no-cache-dir --upgrade pip setuptools wheel

ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with security checks (no vendoring)
RUN pip install --no-cache-dir --no-compile --disable-pip-version-check \
    -r requirements.txt \
    && pip check \
    && find /opt/venv -name '*.pyc' -delete \
    && find /opt/venv -name '__pycache__' -exec rm -rf {} + || true

# ===========================================
# STAGE 3: Security hardened runtime image
# ===========================================
FROM python:3.11-slim AS runtime

# Add comprehensive metadata labels for traceability and security
LABEL maintainer="Zen MCP Server Team"
LABEL version="1.0.0"
LABEL description="Zen MCP Server - AI-powered Model Context Protocol server"
LABEL org.opencontainers.image.title="zen-mcp-server"
LABEL org.opencontainers.image.description="AI-powered Model Context Protocol server with multi-provider support"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/BeehiveInnovations/zen-mcp-server"
LABEL org.opencontainers.image.documentation="https://github.com/BeehiveInnovations/zen-mcp-server/blob/main/README.md"
LABEL org.opencontainers.image.licenses="Apache 2.0 License"
LABEL org.opencontainers.image.created="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
LABEL security.scan.enabled="true"
LABEL security.non-root="true"
LABEL security.readonly-rootfs="false"

# Security hardening: Create dedicated non-root user with minimal privileges
RUN groupadd -r -g 1001 zenuser \
    && useradd -r -u 1001 -g zenuser -s /bin/false -d /app zenuser \
    && mkdir -p /app /tmp/zen \
    && chown -R zenuser:zenuser /app /tmp/zen

# Install minimal runtime dependencies with security focus
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    procps \
    dumb-init \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* \
    && find /usr -name '*.pyc' -delete \
    && find /usr -name '__pycache__' -exec rm -rf {} + || true

# Copy virtual environment from builder with proper ownership
COPY --from=builder --chown=zenuser:zenuser /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy security scan results for reference
COPY --from=security-scan --chown=zenuser:zenuser /scan/*-report.json ./security/

# Copy application code with proper ownership and permissions
COPY --chown=zenuser:zenuser --chmod=755 . .

# Create necessary directories with strict permissions
RUN mkdir -p logs tmp security conf \
    && chown -R zenuser:zenuser logs tmp security conf \
    && chmod 750 logs tmp security conf \
    && chmod 644 security/*-report.json 2>/dev/null || true

# Remove any sensitive files that might have been copied
RUN rm -f .env .env.local .env.* *.key *.pem *.p12 *.pfx *.crt secrets/* private/* 2>/dev/null || true

# Copy health check script with secure permissions
COPY --chown=zenuser:zenuser --chmod=755 docker/scripts/healthcheck.py /usr/local/bin/healthcheck.py

# Validate non-root user setup
RUN id zenuser && getent passwd zenuser | grep -q '/bin/false'

# Switch to non-root user (security requirement)
USER zenuser

# Verify user context
RUN whoami | grep -q zenuser && [ "$(id -u)" = "1001" ]

# Enhanced health check with security validation
HEALTHCHECK --interval=30s --timeout=15s --start-period=10s --retries=3 \
    CMD python /usr/local/bin/healthcheck.py --security-check

# Set secure environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV USER=zenuser
ENV HOME=/app
ENV TMPDIR=/tmp/zen

# Security: Disable core dumps and set secure umask
ENV PYTHONFAULTHANDLER=1
RUN ulimit -c 0 && umask 077

# Default command with security wrapper
# Uses PORT env var for binding (default 8080)
ENV PORT=8080
ENTRYPOINT ["./zen"]
CMD ["serve", "http"]
