# PhenoEvents

Event-driven architecture primitives and distributed event bus for loosely-coupled service communication across Phenotype.

## Overview

PhenoEvents provides a unified event system for building event-driven applications within the Phenotype ecosystem. It abstracts message brokers (Kafka, RabbitMQ, AWS SNS/SQS), event serialization (Avro, Protobuf, JSON), and event sourcing patterns. Services publish typed events and subscribe to event streams without tight coupling, enabling scalable, reactive system design.

## Technology Stack

- **Core**: Rust with async/await
- **Message Brokers**: Kafka (rdkafka), RabbitMQ (lapin), AWS SQS/SNS (aws-sdk)
- **Serialization**: Avro, Protocol Buffers, serde JSON
- **Event Store**: Append-only ledger with SHA-256 hash chains (in-house phenotype-event-sourcing)
- **Async Runtime**: Tokio with batch processing
- **Schema Registry**: Confluent Schema Registry integration, local TOML fallback

## Key Features

- **Broker Abstraction**: Single trait for Kafka, RabbitMQ, cloud pub/sub
- **Event Schema Management**: Versioned event definitions with backward compatibility
- **Event Sourcing**: Append-only log with temporal queries and projections
- **Dead Letter Queues**: Automatic retry + DLQ routing for failed events
- **Fan-Out Subscriptions**: Multiple subscribers per event type with independent offsets
- **Filtering & Routing**: Content-based routing, event header predicates
- **Observability**: Structured event logging, trace correlation, metrics
- **Deduplication**: Idempotent event handling with distributed state

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/PhenoEvents.git
cd PhenoEvents

# Review CLAUDE.md for conventions
cat CLAUDE.md

# Build the core event system
cargo build --all-features
cargo build --release

# Run tests (includes broker integration tests)
cargo test --all -- --test-threads=1

# Start a local event broker (optional; requires Docker)
docker-compose -f examples/docker-compose.yml up -d

# Run an example producer and consumer
cargo run --example producer -- --broker kafka --topic events.test
cargo run --example consumer -- --broker kafka --topic events.test
```

## Project Structure

```
PhenoEvents/
  Cargo.toml                     # Workspace manifest
  crates/
    phenotype-events-core/       # Event trait, subscriber interface
    phenotype-events-kafka/      # Kafka producer/consumer impl
    phenotype-events-rabbitmq/   # RabbitMQ integration
    phenotype-events-cloud/      # AWS SNS/SQS, GCP Pub/Sub impl
    phenotype-events-sourcing/   # Event store, projections, snapshots
    phenotype-events-schema/     # Schema registry client, validation
  examples/
    producer.rs                  # Publish domain events
    consumer.rs                  # Subscribe and handle events
    event_sourcing.rs            # Event store snapshot & replay
  tests/
    integration/
      test_kafka_broker.rs       # Kafka end-to-end tests
      test_event_sourcing.rs     # Event store consistency
```

## Related Phenotype Projects

- **[phenotype-bus](../phenotype-bus/)** — Event bus implementation; primary consumer of PhenoEvents
- **[Tracera](../Tracera/)** — Distributed tracing; subscribes to PhenoEvents for trace correlation
- **[cloud](../cloud/)** — Multi-tenant platform; uses event sourcing for audit trail

## Governance & Contributing

- **CLAUDE.md** — Workspace conventions, broker integration policies
- **Event Catalog**: [docs/events/](docs/events/)
- **Schema Definitions**: [schemas/](schemas/)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

See [AGENTS.md](AGENTS.md) for testing requirements and spec traceability.
