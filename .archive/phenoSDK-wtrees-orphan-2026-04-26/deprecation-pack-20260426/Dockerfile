# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12-slim
FROM python:${PYTHON_VERSION} AS runtime

ARG GIT_REPOSITORY="https://github.com/unknown/pheno-sdk"

LABEL org.opencontainers.image.title="pheno-sdk"
LABEL org.opencontainers.image.description="Container image bundling the pheno-sdk runtime and CLI."
LABEL org.opencontainers.image.source="${GIT_REPOSITORY}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PHENO_SDK_HOME=/opt/pheno-sdk

WORKDIR ${PHENO_SDK_HOME}

ARG PHENO_SDK_VERSION=dev
ENV PHENO_SDK_VERSION=${PHENO_SDK_VERSION}

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-deps --editable . \
    && find ${PHENO_SDK_HOME} -name "__pycache__" -type d -exec rm -rf {} +

EXPOSE 8080

ENTRYPOINT ["python", "-m", "pheno.cli.app"]
CMD ["--help"]
