/**
 * Outbound Adapters - Implementations of outbound ports.
 */

import { Order, OrderProps } from '../../domain/entities';
import { OrderRepositoryPort, EventBusPort, CachePort, DomainEvent } from '../../domain/ports/outbound';

/**
 * In-Memory Order Repository - Simple in-memory implementation.
 *
 * This is a development/fallback implementation.
 * For production, use a database adapter.
 */
export class InMemoryOrderRepository implements OrderRepositoryPort {
  private orders: Map<string, OrderProps> = new Map();

  async save(order: OrderProps): Promise<void> {
    this.orders.set(order.id, { ...order, items: [...order.items] });
  }

  async findById(orderId: string): Promise<OrderProps | null> {
    const order = this.orders.get(orderId);
    if (!order) return null;
    return { ...order, items: [...order.items] };
  }

  async findByCustomer(customerId: string, limit = 100, offset = 0): Promise<OrderProps[]> {
    const orders = Array.from(this.orders.values())
      .filter((o) => o.customerId === customerId)
      .slice(offset, offset + limit)
      .map((o) => ({ ...o, items: [...o.items] }));
    return orders;
  }

  async delete(orderId: string): Promise<void> {
    this.orders.delete(orderId);
  }

  clear(): void {
    this.orders.clear();
  }
}

/**
 * In-Memory Event Bus - Simple in-memory implementation.
 *
 * This is a development/fallback implementation.
 * For production, use Kafka, RabbitMQ, or similar.
 */
export class InMemoryEventBus implements EventBusPort {
  private handlers: Map<string, Array<(event: DomainEvent) => Promise<void>>> = new Map();

  async publish(event: DomainEvent): Promise<void> {
    const handlers = this.handlers.get(event.eventType) || [];
    for (const handler of handlers) {
      await handler(event);
    }
  }

  async publishBatch(events: DomainEvent[]): Promise<void> {
    await Promise.all(events.map((e) => this.publish(e)));
  }

  async subscribe<T extends DomainEvent>(
    eventType: string,
    handler: (event: T) => Promise<void>
  ): Promise<void> {
    const handlers = this.handlers.get(eventType) || [];
    handlers.push(handler as (event: DomainEvent) => Promise<void>);
    this.handlers.set(eventType, handlers);
  }

  clear(): void {
    this.handlers.clear();
  }
}

/**
 * In-Memory Cache - Simple in-memory implementation.
 *
 * This is a development/fallback implementation.
 * For production, use Redis or Memcached.
 */
export class InMemoryCache implements CachePort {
  private cache: Map<string, { value: unknown; expiresAt?: number }> = new Map();

  async get<T>(key: string): Promise<T | null> {
    const entry = this.cache.get(key);
    if (!entry) return null;
    if (entry.expiresAt && entry.expiresAt < Date.now()) {
      this.cache.delete(key);
      return null;
    }
    return entry.value as T;
  }

  async set<T>(key: string, value: T, ttlSeconds?: number): Promise<void> {
    const expiresAt = ttlSeconds ? Date.now() + ttlSeconds * 1000 : undefined;
    this.cache.set(key, { value, expiresAt });
  }

  async delete(key: string): Promise<void> {
    this.cache.delete(key);
  }

  async clear(): Promise<void> {
    this.cache.clear();
  }
}
