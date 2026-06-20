# ============================================================================
# TracerTM Development Container
# Multi-language environment: Go, Python, Node.js/Bun
# Optimized for faster builds with strategic layer caching
# ============================================================================

FROM ubuntu:22.04

LABEL maintainer="TracerTM Team"
LABEL description="TracerTM development environment with Go, Python, Node.js/Bun"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# ============================================================================
# LAYER 1: Base system dependencies (changes rarely)
# ============================================================================
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    ca-certificates \
    git \
    curl \
    wget \
    gnupg \
    lsb-release \
    software-properties-common \
    # Network tools (slim set)
    dnsutils \
    iputils-ping \
    # Database clients
    postgresql-client \
    # Process/system management
    procps \
    htop \
    # Text editors
    vim \
    # Utilities
    zip \
    jq \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# ============================================================================
# LAYER 2: Docker CLI (for docker-in-docker)
# ============================================================================
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh && \
    rm -rf /var/lib/apt/lists/*

# ============================================================================
# LAYER 3: Go language runtime (relatively stable version)
# ============================================================================
ENV GO_VERSION=1.23 \
    PATH="/usr/local/go/bin:/go/bin:${PATH}" \
    GOPATH="/go"

RUN wget -q https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz && \
    mkdir -p /go/bin && \
    go version

# ============================================================================
# LAYER 4: Python runtime (stable version)
# ============================================================================
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    && rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    python3 --version

# ============================================================================
# LAYER 5: uv (fast Python package installer)
# ============================================================================
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    rm -rf /root/.cache && \
    which uv && \
    uv --version

# ============================================================================
# LAYER 6: Node.js LTS (changes occasionally)
# ============================================================================
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    node --version && \
    npm --version

# ============================================================================
# LAYER 7: Bun JavaScript runtime
# ============================================================================
ENV PATH="/root/.bun/bin:${PATH}"
RUN curl -fsSL https://bun.sh/install | bash && \
    rm -rf /root/.bun/install && \
    /root/.bun/bin/bun --version

# ============================================================================
# LAYER 8: Development tools (Go, Python utilities)
# ============================================================================
RUN go install github.com/air-verse/air@latest && \
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest && \
    go install golang.org/x/tools/gopls@latest && \
    go install github.com/go-delve/delve/cmd/dlv@latest && \
    rm -rf /go/pkg

# ============================================================================
# LAYER 9: Process orchestration tools
# ============================================================================
RUN PROCESS_COMPOSE_VERSION="0.80.0" && \
    wget -q https://github.com/F1bonacc1/process-compose/releases/download/v${PROCESS_COMPOSE_VERSION}/process-compose_${PROCESS_COMPOSE_VERSION}_Linux_x86_64.tar.gz && \
    tar -xzf process-compose_${PROCESS_COMPOSE_VERSION}_Linux_x86_64.tar.gz && \
    mv process-compose /usr/local/bin/ && \
    chmod +x /usr/local/bin/process-compose && \
    rm process-compose_${PROCESS_COMPOSE_VERSION}_Linux_x86_64.tar.gz && \
    process-compose --version

# ============================================================================
# LAYER 10: File watching utility
# ============================================================================
RUN WATCHEXEC_VERSION="1.25.1" && \
    wget -q https://github.com/watchexec/watchexec/releases/download/v${WATCHEXEC_VERSION}/watchexec-${WATCHEXEC_VERSION}-x86_64-unknown-linux-musl.tar.xz && \
    tar -xf watchexec-${WATCHEXEC_VERSION}-x86_64-unknown-linux-musl.tar.xz && \
    mv watchexec-${WATCHEXEC_VERSION}-x86_64-unknown-linux-musl/watchexec /usr/local/bin/ && \
    chmod +x /usr/local/bin/watchexec && \
    rm -rf watchexec-${WATCHEXEC_VERSION}-x86_64-unknown-linux-musl* && \
    watchexec --version

# ============================================================================
# LAYER 11: Caddy reverse proxy
# ============================================================================
RUN curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg && \
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends caddy && \
    rm -rf /var/lib/apt/lists/* && \
    caddy version

# ============================================================================
# LAYER 12: Non-root user setup (changes rarely)
# ============================================================================
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    apt-get update && \
    apt-get install -y --no-install-recommends sudo && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    rm -rf /var/lib/apt/lists/*

# ============================================================================
# LAYER 13: User environment and workspace
# ============================================================================
WORKDIR /workspace

# Set up user environment
ENV PATH="/home/${USERNAME}/.bun/bin:/home/${USERNAME}/.cargo/bin:/home/${USERNAME}/go/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    GO_ENV=development \
    NODE_ENV=development

# Switch to non-root user
USER $USERNAME

# Install user-level Go tools (as vscode user)
RUN go install github.com/air-verse/air@latest && \
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest && \
    go install golang.org/x/tools/gopls@latest && \
    rm -rf /home/${USERNAME}/go/pkg

# Default command (keep container running)
CMD ["sleep", "infinity"]
