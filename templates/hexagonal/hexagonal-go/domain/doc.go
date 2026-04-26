// Package domain contains the core business logic of the application.
//
// # Dependency Rule
//
// The domain package has ZERO external dependencies. All types are pure Go
// with no imports from external packages.
//
// # Architecture
//
// The domain layer follows Hexagonal Architecture principles:
//
//   - Entities: Domain objects with identity (e.g., Order, Customer)
//   - Value Objects: Immutable types without identity (e.g., OrderID, Money)
//   - Domain Events: Events that represent important business events
//   - Domain Errors: Errors that represent domain rule violations
//   - Ports: Interfaces that define contracts (implemented by adapters)
//
// # Ports
//
// Ports define interfaces (contracts) that are implemented by adapters:
//
//   - Inbound Ports: Use cases and commands (driving ports)
//   - Outbound Ports: Repositories and external services (driven ports)
//
// # Usage
//
// This package should be importable by both application and adapter layers.
// The domain layer should NEVER import from application or adapter layers.
//
//	package myapp
//
//	import "github.com/phenotype/myapp/domain"
//
//	// Use domain types
//	order := domain.NewOrder(customerID, items)
package domain
