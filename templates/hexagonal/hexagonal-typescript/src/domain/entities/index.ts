/**
 * Domain Entities - Business objects with identity.
 *
 * Entities are objects that have a distinct identity that runs through time
 * and different representations of the same conceptual entity.
 */

import { DomainError, InvalidStateTransitionError } from '../errors';

export enum OrderStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  SHIPPED = 'SHIPPED',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED',
}

export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

export interface OrderProps {
  id: string;
  customerId: string;
  items: OrderItem[];
  status: OrderStatus;
  total: number;
  createdAt: Date;
  updatedAt: Date;
  cancellationReason?: string;
}

/**
 * Order entity - represents an order in the domain.
 *
 * Following DDD principles:
 * - Entity with identity
 * - Immutable state changes via methods
 * - Business rules encapsulated
 */
export class Order {
  private props: OrderProps;

  private constructor(props: OrderProps) {
    this.props = props;
  }

  static create(customerId: string, items: OrderItem[]): Order {
    if (!items || items.length === 0) {
      throw new DomainError(
        'Order must have at least one item',
        'INVALID_ORDER_ITEMS',
        { itemCount: items?.length || 0 }
      );
    }

    const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

    const now = new Date();
    return new Order({
      id: crypto.randomUUID(),
      customerId,
      items: [...items],
      status: OrderStatus.PENDING,
      total: Math.round(total * 100) / 100,
      createdAt: now,
      updatedAt: now,
    });
  }

  static fromPersistence(props: OrderProps): Order {
    return new Order({ ...props, items: [...props.items] });
  }

  get id(): string {
    return this.props.id;
  }

  get customerId(): string {
    return this.props.customerId;
  }

  get items(): OrderItem[] {
    return [...this.props.items];
  }

  get status(): OrderStatus {
    return this.props.status;
  }

  get total(): number {
    return this.props.total;
  }

  get createdAt(): Date {
    return new Date(this.props.createdAt);
  }

  get updatedAt(): Date {
    return new Date(this.props.updatedAt);
  }

  get cancellationReason(): string | undefined {
    return this.props.cancellationReason;
  }

  confirm(): void {
    if (this.props.status !== OrderStatus.PENDING) {
      throw new InvalidStateTransitionError(
        'Order',
        this.props.status,
        OrderStatus.CONFIRMED
      );
    }
    this.props.status = OrderStatus.CONFIRMED;
    this.props.updatedAt = new Date();
  }

  ship(): void {
    if (this.props.status !== OrderStatus.CONFIRMED) {
      throw new InvalidStateTransitionError('Order', this.props.status, OrderStatus.SHIPPED);
    }
    this.props.status = OrderStatus.SHIPPED;
    this.props.updatedAt = new Date();
  }

  deliver(): void {
    if (this.props.status !== OrderStatus.SHIPPED) {
      throw new InvalidStateTransitionError(
        'Order',
        this.props.status,
        OrderStatus.DELIVERED
      );
    }
    this.props.status = OrderStatus.DELIVERED;
    this.props.updatedAt = new Date();
  }

  cancel(reason: string): void {
    if (
      this.props.status === OrderStatus.SHIPPED ||
      this.props.status === OrderStatus.DELIVERED
    ) {
      throw new InvalidStateTransitionError('Order', this.props.status, OrderStatus.CANCELLED);
    }
    this.props.status = OrderStatus.CANCELLED;
    this.props.cancellationReason = reason;
    this.props.updatedAt = new Date();
  }

  toJSON(): OrderProps {
    return { ...this.props, items: [...this.props.items] };
  }

  equals(other: Order): boolean {
    if (!(other instanceof Order)) return false;
    return this.props.id === other.props.id;
  }
}
