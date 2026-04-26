// Package valueobjects contains immutable value types without identity.
//
// Value objects are immutable types that are defined by their attributes
// rather than a unique identity. Two value objects with the same attributes
// are considered equal.
//
// # Design Principles
//
//   - Value objects are immutable (no setters, all fields private)
//   - Value objects are created via factory methods or constructors
//   - Value objects should be validated at creation time
//   - Value objects should implement String() and MarshalBinary()
//
// # Examples
//
//   - Money: $10.00 == $10.00 (equal by value)
//   - Email: "user@example.com" == "user@example.com" (equal by value)
//   - Address: 123 Main St == 123 Main St (equal by value)
//
// Unlike entities (e.g., Order), value objects don't have unique IDs.
// If you need to track identity, use an entity instead.
package valueobjects
