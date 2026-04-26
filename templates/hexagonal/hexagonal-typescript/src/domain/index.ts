/**
 * Domain Layer - Pure domain concepts with ZERO external dependencies.
 *
 * Following ADR-001 dependency rule:
 * - domain/ contains ZERO external dependencies (except standard library)
 * - Only type imports allowed from application layer
 *
 * @packageDocumentation
 */

// Ports (interfaces)
export * from './ports/inbound';
export * from './ports/outbound';

// Entities
export * from './entities';

// Value Objects
export * from './value-objects';

// Domain Services
export * from './services';

// Events
export * from './events';

// Errors
export * from './errors';
