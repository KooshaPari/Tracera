FROM rust:1.88-slim AS builder

WORKDIR /workspace
COPY . .
RUN cargo build --release -p tracera-server

FROM debian:bookworm-slim AS runtime

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /usr/sbin/nologin tracera
COPY --from=builder /workspace/target/release/tracera-server /usr/local/bin/tracera-server

USER tracera
ENV TRACERA_BIND_ADDR=0.0.0.0:8080
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD curl --fail --silent --show-error --max-time 2 http://127.0.0.1:8080/healthz || exit 1

CMD ["tracera-server"]
