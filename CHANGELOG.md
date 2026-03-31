# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Release Drafter** - Automated release notes generation via GitHub Actions (#262)
  - `.github/release-drafter.yml` config with categories: breaking, feat, fix, docs, chore
  - `.github/workflows/release-drafter.yml` triggered on push to main and PR events

### Changed
- Bumped `google.golang.org/grpc` dependency (#277)
- Bumped Go modules group (4 updates across 5 directories) (#276)
- Bumped npm/yarn group (15 updates across 43 directories) (#275)
- Bumped uv/Python group (7 updates) (#274)

## [2.0.0] - 2026-02-23

### Added
- **TraceRTM v2 Architecture** - Complete specification-driven development system
  - ADR-0001: Layered Transformation approach with 4 new layers
  - Specification Engine with ADR management, formal contracts, invariant engine
  - BDD Scenario Engine with Gherkin parser and step definitions
  - Visual UI Engine with graph canvas, RTM heat maps, coverage dashboards
  - MCP Native CLI using FastMCP 2.14+ for AI agent integration

- **FastMCP Integration** (ADR-0002)
  - MCP server with 50+ tools for AI agent interaction
  - Support for stdio, HTTP, and SSE transports
  - Bearer auth and JWT verification support

- **Frontend Implementation**
  - React/TypeScript application with MobX state management
  - Graph visualization using Cytoscape.js
  - Monaco code editor integration
  - MSW for API mocking in tests

- **Backend Services** (Go)
  - RESTful API with FastAPI
  - NATS messaging integration
  - MinIO object storage support
  - PostgreSQL database with SQLAlchemy ORM

- **Comprehensive Test Suite**
  - Phase 1-9 test coverage initiatives completed
  - 1,400+ tests across CLI, API, services, and E2E
  - Pytest-asyncio configuration for async testing
  - 92.6% pass rate achieved

- **Documentation System**
  - 15 Architecture Decision Records (ADR-0001 through ADR-0015)
  - Product Requirements Document (PRD)
  - Functional Requirements (FR-1 through FR-50+)
  - Organized docs/ structure with guides, reference, research, reports

- **Graph Data Structure** (ADR-0014)
  - NetworkX-based graph implementation
  - Impact analysis algorithms
  - Shortest path calculations
  - Coverage analysis

- **Import/Export Capabilities** (ADR-0015)
  - Multiple format support
  - Bulk operations
  - Data migration tools

### Changed
- Migrated from CRUD-based to specification-driven development
- Transitioned from basic CLI to MCP-native tooling
- Enhanced from simple list views to visual graph interfaces

### Deprecated
- Basic list/detail views (replaced by graph visualization)
- Standalone CLI commands (superseded by MCP tools)

### Removed
- Legacy non-MCP command structure

### Fixed
- 67+ failing tests fixed in Phase 1
- CLI command structure refactored
- Storage layer mocking patterns established
- Async test configuration issues resolved

### Security
- JWT authentication provider integration
- Bearer auth support for MCP server

## [1.1.0] - 2025-01-31

### Added
- Initial stable changelog release entry.

## [1.0.0] - 2025-11-29

### Added
- Initial project release.
