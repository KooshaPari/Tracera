/**
 * Outbound Ports (Secondary/Driven Ports)
 *
 * These ports define the interface that the application uses to interact
 * with external systems. They are "implemented" by adapters.
 *
 * Following Hexagonal Architecture:
 * - Outbound ports are the "secondary" or "driven" ports
 * - They define what the application needs from infrastructure
 * - Implementation is in the adapters layer
 */

import { Order } from '../entities';

/**
 * Port for order persistence operations.
 *
 * This port defines the contract for order storage.
 * Implementation can be PostgreSQL, MongoDB, in-memory, etc.
 */
export interface OrderRepositoryPort {
  save(order: Order): Promise<void>;
  findById(orderId: string): Promise<Order | null>;
  findByCustomer(customerId: string, limit?: number, offset?: number): Promise<Order[]>;
  delete(orderId: string): Promise<void>;
}

/**
 * Port for publishing domain events.
 *
 * This port defines the contract for event publishing.
 * Implementation can be Kafka, RabbitMQ, in-memory, etc.
 */
export interface EventBusPort {
  publish(event: DomainEvent): Promise<void>;
  publishBatch(events: DomainEvent[]): Promise<void>;
  subscribe<T extends DomainEvent>(
    eventType: string,
    handler: (event: T) => Promise<void>
  ): Promise<void>;
}

/**
 * Base interface for domain events.
 */
export interface DomainEvent {
  readonly eventType: string;
  readonly occurredAt: Date;
  readonly aggregateId: string;
}

/**
 * Port for caching operations.
 *
 * This port defines the contract for caching.
 * Implementation can be Redis, Memcached, in-memory, etc.
 */
export interface CachePort {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T, ttlSeconds?: number): Promise<void>;
  delete(key: string): Promise<void>;
  clear(): Promise<void>;
}

/**
 * Port for transactional operations.
 *
 * This port defines the contract for managing transactions.
 * It ensures atomic operations across multiple repositories.
 */
export interface UnitOfWorkPort {
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  getOrderRepository(): OrderRepositoryPort;
}
