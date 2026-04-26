/**
 * Value Objects - Immutable domain types.
 *
 * Value objects are defined by their attributes, not by identity.
 * They are immutable and can be freely shared.
 */

import { DomainError } from '../errors';

/**
 * Base interface for all value objects.
 */
export interface ValueObject<T> {
  equals(other: T): boolean;
  toString(): string;
  toJSON(): unknown;
}

/**
 * Email value object.
 */
export class Email implements ValueObject<Email> {
  private readonly _value: string;

  private constructor(value: string) {
    this._value = value;
  }

  static create(value: string): Email {
    const trimmed = value.trim().toLowerCase();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      throw new DomainError(
        `Invalid email address: ${value}`,
        'INVALID_EMAIL',
        { value }
      );
    }
    return new Email(trimmed);
  }

  static tryCreate(value: string): Email | null {
    try {
      return Email.create(value);
    } catch {
      return null;
    }
  }

  get value(): string {
    return this._value;
  }

  equals(other: Email): boolean {
    if (!(other instanceof Email)) return false;
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }

  toJSON(): string {
    return this._value;
  }
}

/**
 * Money value object.
 */
export class Money implements ValueObject<Money> {
  private readonly _amount: number;
  private readonly _currency: string;

  private constructor(amount: number, currency: string) {
    this._amount = Math.round(amount * 100) / 100; // Round to 2 decimal places
    this._currency = currency.toUpperCase();
  }

  static create(amount: number, currency: string = 'USD'): Money {
    if (amount < 0) {
      throw new DomainError(
        'Money amount cannot be negative',
        'INVALID_MONEY_AMOUNT',
        { amount }
      );
    }
    return new Money(amount, currency);
  }

  static zero(currency: string = 'USD'): Money {
    return new Money(0, currency);
  }

  get amount(): number {
    return this._amount;
  }

  get currency(): string {
    return this._currency;
  }

  equals(other: Money): boolean {
    if (!(other instanceof Money)) return false;
    return this._amount === other._amount && this._currency === other._currency;
  }

  add(other: Money): Money {
    if (this._currency !== other._currency) {
      throw new DomainError(
        'Cannot add money with different currencies',
        'CURRENCY_MISMATCH',
        { left: this._currency, right: other._currency }
      );
    }
    return new Money(this._amount + other._amount, this._currency);
  }

  subtract(other: Money): Money {
    if (this._currency !== other._currency) {
      throw new DomainError(
        'Cannot subtract money with different currencies',
        'CURRENCY_MISMATCH',
        { left: this._currency, right: other._currency }
      );
    }
    const result = this._amount - other._amount;
    if (result < 0) {
      throw new DomainError(
        'Money amount cannot be negative',
        'INVALID_MONEY_AMOUNT',
        { result }
      );
    }
    return new Money(result, this._currency);
  }

  multiply(factor: number): Money {
    return new Money(this._amount * factor, this._currency);
  }

  toString(): string {
    return `${this._currency} ${this._amount.toFixed(2)}`;
  }

  toJSON(): { amount: number; currency: string } {
    return { amount: this._amount, currency: this._currency };
  }
}

/**
 * Unique identifier value object.
 */
export class UniqueId implements ValueObject<UniqueId> {
  private readonly _value: string;

  private constructor(value: string) {
    this._value = value;
  }

  static create(): UniqueId {
    return new UniqueId(crypto.randomUUID());
  }

  static fromString(value: string): UniqueId {
    if (!value || value.trim().length === 0) {
      throw new DomainError(
        'UniqueId cannot be empty',
        'INVALID_UNIQUE_ID',
        { value }
      );
    }
    return new UniqueId(value);
  }

  get value(): string {
    return this._value;
  }

  equals(other: UniqueId): boolean {
    if (!(other instanceof UniqueId)) return false;
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }

  toJSON(): string {
    return this._value;
  }
}
