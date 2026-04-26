// Phenotype Hexagonal Go Template
//
// A production-ready Go project template following:
//   - Hexagonal Architecture (Ports & Adapters)
//   - Clean Architecture principles
//   - SOLID principles
//   - xDD methodologies (TDD, BDD, DDD, CDD, ADD)
//
// Architecture Overview:
//
//	┌─────────────────────────────────────────────────────────────────────┐
//	│                           ADAPTERS                                   │
//	│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
//	│  │   Inbound API    │  │   Inbound CLI    │  │  Inbound gRPC   │    │
//	│  │  (Echo/Fiber)    │  │   (Cobra/CLI)    │  │   (gRPC Server)  │    │
//	│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘    │
//	└───────────┼────────────────────┼───────────────────┼──────────────┘
//	            │                    │                   │
//	            v                    v                   v
//	┌─────────────────────────────────────────────────────────────────────┐
//	│                         PORTS (Interfaces)                         │
//	│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
//	│  │ Primary Ports   │  │ Secondary Ports │  │ Secondary Ports │    │
//	│  │ (Inbound)       │  │ (Outbound)      │  │ (Outbound)      │    │
//	│  │ - UseCases      │  │ - Repository    │  │ - EventBus      │    │
//	│  │ - Commands      │  │ - Persistence   │  │ - Cache         │    │
//	│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
//	└─────────────────────────────────────────────────────────────────────┘
//	            │                    │                   │
//	            v                    v                   v
//	┌─────────────────────────────────────────────────────────────────────┐
//	│                         DOMAIN (Pure Go)                             │
//	│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
//	│  │    Entities     │  │  Value Objects  │  │  Domain Events  │    │
//	│  │  - Order        │  │  - OrderID       │  │  - OrderCreated │    │
//	│  │  - Customer     │  │  - Money         │  │  - OrderShipped │    │
//	│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
//	│  ┌─────────────────┐  ┌─────────────────┐                        │
//	│  │ Domain Services  │  │   Domain Errors │                        │
//	│  │ - PricingService │  │ - DomainError   │                        │
//	│  └─────────────────┘  └─────────────────┘                        │
//	└─────────────────────────────────────────────────────────────────────┘
//	            │                    │                   │
//	            v                    v                   v
//	┌─────────────────────────────────────────────────────────────────────┐
//	│                      APPLICATION LAYER                              │
//	│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
//	│  │    Use Cases    │  │      DTOs       │  │   Commands/     │    │
//	│  │ - CreateOrder   │  │ - CreateOrderDTO│  │   Queries       │    │
//	│  │ - GetOrder      │  │ - OrderDTO      │  │ - CreateOrderCmd│    │
//	│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
//	└─────────────────────────────────────────────────────────────────────┘
//	            │                    │                   │
//	            v                    v                   v
//	┌─────────────────────────────────────────────────────────────────────┐
//	│                    OUTBOUND ADAPTERS                               │
//	│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
//	│  │   Persistence   │  │     Cache       │  │  External APIs  │    │
//	│  │  - PostgreSQL   │  │   - Redis       │  │  - HTTP Client  │    │
//	│  │  - MongoDB      │  │  - Memcached    │  │  - gRPC Client  │    │
//	│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
//	└─────────────────────────────────────────────────────────────────────┘
//
// Dependency Rule:
//   - Domain (ZERO external dependencies)
//   - Application (depends on Domain only)
//   - Adapters (implement Ports, no business logic)
//
// Project Structure:
//
//	.
//	├── cmd/
//	│   └── server/          # Application entry points
//	│       └── main.go
//	├── internal/
//	│   ├── domain/          # Pure domain (ZERO external deps)
//	│   ├── application/     # Use cases, DTOs
//	│   └── adapters/        # Infrastructure implementations
//	└── pkg/                # Public packages (can be imported)
//
// Usage:
//
//	# Run the server
//	go run cmd/server/main.go
//
//	# Run tests
//	go test ./...
//
//	# Run with coverage
//	go test -coverprofile=coverage.out ./...
//	go tool cover -html=coverage.out
//
//	# Run linter
//	golangci-lint run
//
// License: MIT
// Version: 0.1.0
