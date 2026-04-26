/**
 * Domain Errors - Pure domain errors with no external dependencies.
 *
 * Following ADR-001 dependency rule:
 * - domain/ contains ZERO external dependencies
 * - Only standard library imports allowed
 */

export class DomainError extends Error {
  public readonly code: string;
  public readonly context: Record<string, unknown>;

  constructor(message: string, code: string, context: Record<string, unknown> = {}) {
    super(message);
    this.name = 'DomainError';
    this.code = code;
    this.context = context;
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      context: this.context,
    };
  }
}

export class EntityNotFoundError extends DomainError {
  constructor(entityType: string, entityId: string) {
    super(
      `${entityType} with id '${entityId}' not found`,
      'ENTITY_NOT_FOUND',
      { entityType, entityId }
    );
    this.name = 'EntityNotFoundError';
  }
}

export class BusinessRuleViolationError extends DomainError {
  constructor(rule: string, details: string) {
    super(
      `Business rule violated: ${rule}`,
      'BUSINESS_RULE_VIOLATION',
      { rule, details }
    );
    this.name = 'BusinessRuleViolationError';
  }
}

export class ValidationError extends DomainError {
  constructor(field: string, value: unknown, constraint: string) {
    super(
      `Validation failed for field '${field}'`,
      'VALIDATION_ERROR',
      { field, value, constraint }
    );
    this.name = 'ValidationError';
  }
}

export class InvalidStateTransitionError extends DomainError {
  constructor(entityType: string, currentState: string, attemptedState: string) {
    super(
      `Invalid state transition for ${entityType}: ${currentState} -> ${attemptedState}`,
      'INVALID_STATE_TRANSITION',
      { entityType, currentState, attemptedState }
    );
    this.name = 'InvalidStateTransitionError';
  }
}
