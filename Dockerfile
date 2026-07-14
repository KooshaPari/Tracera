FROM rust:1.88-slim AS builder

WORKDIR /workspace
COPY . .
RUN cargo build --release -p tracera-server

FROM debian:bookworm-slim AS runtime

RUN useradd --create-home --shell /usr/sbin/nologin tracera
COPY --from=builder /workspace/target/release/tracera-server /usr/local/bin/tracera-server

USER tracera
ENV TRACERA_HOST=0.0.0.0
ENV TRACERA_PORT=8080
EXPOSE 8080

CMD ["tracera-server"]
