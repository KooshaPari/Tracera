# thegent-jsonl

**JSONL Schema & Codec Library for Phenotype Workflows**

A lightweight library providing JSONL (JSON Lines) schema definition, validation, and efficient streaming codecs for the thegent dotfiles ecosystem. It enables schema-driven serialization and deserialization of streaming JSON data with strong type safety and minimal overhead.

## Overview

thegent-jsonl decouples schema definition from serialization logic. Services define schemas in TOML; the library generates language-specific codecs that can serialize/deserialize millions of records with predictable performance. Built for high-throughput logging, event streaming, and workflow state management across the Phenotype organization.

## Technology Stack

- **Languages**: Rust (primary codec), Python (secondary), Go (reference)
- **Format**: JSONL (one valid JSON object per line, newline-delimited)
- **Schema**: TOML-based schema language with type system
- **Core Dependencies**: serde (Rust), pydantic (Python), json-iterator (Go)
- **Performance**: Zero-copy deserialization, streaming writers, configurable buffering

## Key Features

- **Schema-Driven Codecs**: Define schemas once, generate optimized codecs for all languages
- **Type Safety**: Strong typing at compile time; runtime validation for untrusted input
- **Streaming Support**: Efficient line-by-line reading/writing for 100GB+ datasets
- **Schema Evolution**: Add fields, rename types with backward compatibility
- **Compression**: Optional gzip/zstd compression on-the-fly
- **Validation**: Custom validators for domain-specific constraints
- **Error Recovery**: Graceful handling of malformed lines with detailed diagnostics
- **Performance**: Single-pass deserialization, configurable memory buffering
- **CLI Tools**: `jsonl-validate`, `jsonl-convert`, `jsonl-sample` for ad-hoc operations

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/thegent-jsonl.git
cd thegent-jsonl

# Review the schema language
cat docs/SCHEMA_LANGUAGE.md

# Define a schema (example)
cat examples/schemas/event.toml

# Generate codecs from schema
jsonl-codegen examples/schemas/event.toml --output-rust src/codecs/event.rs

# Use generated codec in Rust
cargo build

# Run examples
cargo run --example read-stream < examples/data/events.jsonl

# Validate a JSONL file
jsonl-validate examples/schemas/event.toml examples/data/events.jsonl

# Run tests
cargo test --workspace
pytest tests/
```

## Project Structure

```
thegent-jsonl/
├── src/
│   ├── schema/                    # Schema parser and type system
│   ├── codecs/                    # Generated codecs for each schema
│   │   ├── event.rs               # Example: event schema codec
│   │   ├── workflow.rs            # Example: workflow state codec
│   │   └── log_entry.rs           # Example: structured log codec
│   ├── validation/                # Runtime validation engine
│   ├── compression/               # gzip/zstd compression support
│   └── stream/                    # Streaming reader/writer
├── tools/
│   ├── jsonl-codegen/             # Schema → codec generator
│   ├── jsonl-validate/            # JSONL file validator
│   ├── jsonl-convert/             # JSONL format converter
│   └── jsonl-sample/              # Extract sample records
├── python/
│   ├── thegent_jsonl/             # Python library
│   └── tests/
├── examples/
│   ├── schemas/
│   │   ├── event.toml             # Event schema (workflow logs)
│   │   ├── workflow.toml          # Workflow state schema
│   │   └── metric.toml            # Metrics schema
│   ├── data/
│   │   ├── events.jsonl           # Sample event stream
│   │   ├── events.jsonl.gz        # Compressed version
│   │   └── corrupted.jsonl        # Error recovery test
│   ├── read-stream.rs             # Example: stream reader
│   ├── write-stream.rs            # Example: stream writer
│   └── validate.py                # Example: Python validation
├── tests/
│   ├── integration/               # End-to-end codec tests
│   ├── performance/               # Throughput benchmarks
│   └── regression/                # Schema evolution tests
└── docs/
    ├── SCHEMA_LANGUAGE.md         # Full syntax reference
    ├── CODECS.md                  # Generated codec usage
    ├── STREAMING.md               # High-throughput patterns
    ├── EVOLUTION.md               # Schema versioning
    └── PERFORMANCE.md             # Optimization guide
```

## Related Phenotype Projects

- **thegent** — Workflow definitions use thegent-jsonl for execution logs
- **Tracera** — Exports traces as JSONL for streaming to datalakes
- **DataKit** — ETL pipelines consume thegent-jsonl codec-validated data
- **pheno-cli** — Command output streamed as JSONL

## Quality & Testing

Comprehensive test coverage across codec generation, streaming, and error cases:
- Unit tests for schema parsing and validation
- Integration tests comparing Rust/Python/Go codecs
- Benchmarks tracking codec overhead vs. hand-written code
- Regression tests for schema evolution scenarios

```bash
cargo test --workspace --all-features
pytest tests/ -v
go test ./...

# Benchmark codec performance
cargo bench --bench codec-throughput
```

## Performance Characteristics

- **Parsing**: ~500K records/sec (single-threaded Rust)
- **Validation**: ~200K records/sec (with schema checks)
- **Compression**: ~1M records/sec (gzip, on-the-fly)
- **Memory**: Streaming reader O(1) per record (not entire file)

See `docs/PERFORMANCE.md` for detailed benchmarks and tuning guide.

## Governance

All work tracked in AgilePlus. Changes must:
- Maintain backward compatibility (schema versioning)
- Include codec generation tests
- Document performance impact
- Validate across all supported languages

---

**Version**: v0.1.0  
**Last Updated**: 2026-04-25
