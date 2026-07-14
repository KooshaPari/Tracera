FROM rust:1.88-slim AS builder

WORKDIR /workspace
COPY . .
RUN cargo build --release -p tracera-server

FROM debian:bookworm-slim AS runtime

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /usr/sbin/nologin tracera
COPY --from=builder /workspace/target/release/tracera-server /usr/local/bin/tracera-server

USER tracera
ENV TRACERA_BIND_ADDR=0.0.0.0:8080
EXPOSE 8080

CMD ["tracera-server"]
