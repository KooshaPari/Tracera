# PhenoLang

Domain-specific language (DSL) for declarative workflow, policy, and automation specification in the Phenotype ecosystem.

## Overview

PhenoLang is a Rust-based DSL compiler that transforms human-readable workflow and policy definitions into executable, type-safe abstractions. It enables non-programmers to author complex agent workflows, conditional policies, and multi-stage automation without writing code. The language compiles to an intermediate representation (IR) that can be executed by the Phenotype runtime, with full debugging and observability support.

## Technology Stack

- **Parser**: LALRPOP (LR parser generator) for grammar definition and parsing
- **Compiler**: Rust with semantic analysis, type checking, IR generation
- **Type System**: Hindley-Milner inference with optional annotations
- **IR Execution**: Stack-based VM with instruction dispatch
- **Standard Library**: Built-in functions for strings, collections, temporal logic
- **LSP**: Language Server Protocol for editor integration (VS Code, Neovim)

## Key Features

- **Declarative Workflows**: Define multi-step processes with branching, loops, error handling
- **Policy Rules**: Express conditional logic with readable syntax (e.g., `if environment is prod then require approval`)
- **Type Safety**: Compile-time type checking with algebraic data types
- **Macro System**: Define reusable workflow templates and policy patterns
- **Debugging**: Source-level debugging, variable inspection, execution tracing
- **IDE Integration**: VS Code extension with syntax highlighting, autocomplete, error hints
- **Standard Functions**: Time/date logic, string manipulation, JSON/YAML parsing, HTTP calls
- **Error Messages**: Contextual compiler errors with source location and fix suggestions

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/PhenoLang.git
cd PhenoLang

# Review governance
cat CLAUDE.md

# Build the compiler and runtime
cargo build --all-features
cargo build --release

# Run tests (includes parser and codegen tests)
cargo test --all

# Install the VS Code extension (optional)
cd editors/vscode && npm install && npm run deploy

# Compile and run a sample workflow
echo 'workflow greet(name: string) -> string { "Hello, " + name }' > example.pheno
cargo run --bin phenolang -- compile example.pheno
cargo run --bin phenolang -- execute example.pheno
```

## Project Structure

```
PhenoLang/
  Cargo.toml                     # Workspace manifest
  crates/
    phenolang-parser/            # LALRPOP grammar + tokenizer
    phenolang-semantic/          # Type checker, symbol table
    phenolang-codegen/           # IR generation, optimizer
    phenolang-runtime/           # VM, executor, stdlib
    phenolang-lsp/               # Language Server Protocol impl
  editors/
    vscode/                      # VS Code extension
    neovim/                      # Neovim plugin (TreeSitter)
  examples/
    workflow_approval.pheno      # Multi-stage approval workflow
    policy_enforcement.pheno     # Conditional policy rules
    data_pipeline.pheno          # ETL pipeline definition
  tests/
    parser_tests/
    codegen_tests/
    execution_tests/
  stdlib/
    time.pheno                   # Temporal functions
    strings.pheno                # String operations
    http.pheno                   # HTTP client functions
```

## Related Phenotype Projects

- **[AgilePlus](../AgilePlus/)** — Uses PhenoLang for workflow definitions in task automation
- **[Tracera](../Tracera/)** — Runtime instrumentation for PhenoLang execution
- **[phenotype-policy-engine](../phenotype-shared/)** — Policy evaluation backend for PhenoLang rules

## Governance & Contributing

- **CLAUDE.md** — Language design decisions, dialect policies
- **Grammar Reference**: [docs/reference/grammar.md](docs/reference/grammar.md)
- **Language Guide**: [docs/guide/](docs/guide/)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

For compiler testing and spec traceability, see [AGENTS.md](AGENTS.md).
