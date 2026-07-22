FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Keep this image self-contained and scoped to the disposable oracle checkout.
COPY pyproject.toml README.md ./
COPY src ./src
COPY alembic ./alembic
COPY config ./config

RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "tracertm.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
