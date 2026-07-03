FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src

RUN uv sync --frozen --no-dev

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=15s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uv", "run", "uvicorn", "tracertm.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
