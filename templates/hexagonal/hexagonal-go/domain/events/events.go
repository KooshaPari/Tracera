// Package events contains domain event types.
//
// Domain events represent important business events that have occurred.
// They are immutable and contain all relevant information about the event.
//
// # Design Principles
//
//   - Events are immutable value types
//   - Events should be serializable
//   - Events should be self-contained (no references to entities)
//   - Events follow past-tense naming (OrderCreated, not CreateOrder)
//
// # Example
//
//	type OrderCreated struct {
//		EventBase
//		OrderID    string
//		CustomerID string
//		Total      decimal.Decimal
//	}
package events
