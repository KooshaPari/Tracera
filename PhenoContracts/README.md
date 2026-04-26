# PhenoContracts

**Smart Contracts & Decentralized Agreement Framework**

## Overview

PhenoContracts is a blockchain-agnostic smart contract development framework and contract lifecycle management system. It provides a unified abstraction for writing, deploying, and monitoring contracts across Ethereum, Solana, Polkadot, and other blockchain networks, with built-in compliance, audit logging, and formal verification support.

**Core Mission**: Enable rapid, secure, and auditable smart contract development with zero-knowledge proofs, formal verification, and cross-chain composability.

## Technology Stack

- **Contract Languages**: Rust (via Anchor), Solidity (Hardhat), Move (Sui/Aptos), Cairo (StarkNet)
- **Blockchain Runtimes**: Ethereum (EVM, solc), Solana (onchain program runtime), Polkadot (substrate pallets)
- **Development Framework**: Hardhat + Foundry (Solidity), Anchor (Rust/Solana), Clarity (Stacks)
- **Formal Verification**: Z3 SMT solver, Certora formal verification, property-based testing (Proptest)
- **Deployment & Monitoring**: ethers-rs, web3.py, substrate-node CLI; event indexing via Subgraph/Indexer
- **Cross-Chain**: LayerZero OmniChain SDK, Wormhole token bridge adapters
- **Security**: MythX static analysis, Slither vulnerability scanning, audit trail + gas optimization

## Key Features

- **Multi-Chain Contracts** — Write once, deploy to Ethereum, Solana, Polkadot, and Cosmos chains
- **Formal Verification** — Automated property checking with SMT solvers and formal proof generation
- **Compliance Framework** — Built-in KYC/AML integration, regulatory audit trails, DAO governance hooks
- **Upgradeable Patterns** — Proxy patterns, timelock governance, role-based access control (RBAC)
- **Cross-Chain Messaging** — LayerZero and Wormhole adapters for atomic cross-chain swaps and settlements
- **Event Indexing** — Subgraph and custom indexer integration for contract event streaming and analytics
- **Gas Optimization** — Inline gas profiling, cost estimation, and bytecode size reduction
- **Test Frameworks** — Foundry for Solidity, Anchor Test for Rust, property-based testing libraries

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/PhenoContracts
cd PhenoContracts

# Review project configuration
cat CLAUDE.md

# Install dependencies
npm install              # Hardhat + ethers.js
cargo install anchor-cli # Solana development

# Build contracts
npm run build             # Solidity contracts
cargo build              # Rust/Solana contracts

# Run tests with coverage
npm run test:coverage
cargo test --workspace

# Deploy to testnet
npm run deploy:goerli
anchor deploy --provider.cluster devnet

# Format and lint
cargo fmt
cargo clippy -- -D warnings
npm run lint
```

## Project Structure

```
contracts/
  ├─ ethereum/          # Solidity smart contracts (ERC-20, ERC-721, governance)
  ├─ solana/            # Rust-based Solana programs (SPL token extensions, vaults)
  ├─ polkadot/          # Substrate pallets (custom runtime modules)
  ├─ cross-chain/       # LayerZero OmniChain and Wormhole bridge contracts
  └─ staking/           # Staking and DeFi primitives

src/
  ├─ framework/         # Contract scaffolding and trait-based abstraction
  ├─ formal-verify/     # Z3 property checker and proof generator
  ├─ compliance/        # Audit trail, regulatory reporting, DAO voting
  ├─ gas-optimize/      # Gas profiler and bytecode size reducer
  └─ indexer/           # Event indexing and contract state tracking

tests/
  ├─ unit/              # Property-based tests and SMT verification
  ├─ integration/       # Multi-chain deployment and cross-chain messaging tests
  └─ fuzz/              # Fuzzing with Echidna and Medusa
```

## Status

**Active Development** — Solidity and Rust/Solana contracts complete; formal verification and cross-chain expansion in progress.

- ✓ ERC-20, ERC-721 implementations with extensions
- ✓ Solana program library (SPL token adapters)
- ✓ Governance and timelock contracts
- ✓ Event indexing and monitoring
- WIP: LayerZero cross-chain messaging
- WIP: Zero-knowledge proof circuits (zkSNARK, zkSTARK)

## Related Phenotype Projects

- **phenotype-journeys** — User flows for DeFi onboarding and contract interaction
- **PhenoSchema** — Schema evolution and data modeling for contract state
- **cloud** — Deployment and infrastructure for smart contract platforms

## Governance & Architecture

- **Documentation**: See `CLAUDE.md` for development setup and testing guidelines
- **Specification**: `docs/spec/pheno-contracts-framework.md` — Architecture and component contracts
- **Audit**: Annual formal verification and security audits logged in `AUDIT.md`
- **License**: MIT (contracts), Proprietary (framework)

---

**Maintained by**: Phenotype DeFi Team  
**Last Updated**: 2026-04-25
