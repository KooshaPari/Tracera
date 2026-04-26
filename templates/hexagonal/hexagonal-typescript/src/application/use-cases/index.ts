/**
 * Create Order Use Case - Implementation of the create order use case.
 */

import { Order, OrderStatus } from '../../domain/entities';
import { DomainError, EntityNotFoundError } from '../../domain/errors';
import {
  CreateOrderUseCase,
  CreateOrderCommand,
  OrderResult,
} from '../../domain/ports/inbound';
import { OrderRepositoryPort, EventBusPort } from '../../domain/ports/outbound';

/**
 * Create Order Service - Application service for creating orders.
 *
 * This service implements the CreateOrderUseCase port.
 * It orchestrates the domain logic and infrastructure interactions.
 */
export class CreateOrderService implements CreateOrderUseCase {
  constructor(
    private readonly orderRepository: OrderRepositoryPort,
    private readonly eventBus: EventBusPort
  ) {}

  async execute(command: CreateOrderCommand): Promise<OrderResult> {
    // Create domain entity
    const order = Order.create(command.customerId, command.items);

    // Persist
    await this.orderRepository.save(order.toJSON() as any);

    // Publish event
    await this.eventBus.publish({
      eventType: 'OrderCreated',
      occurredAt: new Date(),
      aggregateId: order.id,
      orderId: order.id,
      customerId: order.customerId,
      total: order.total,
    } as any);

    return {
      orderId: order.id,
      status: order.status,
      total: order.total,
    };
  }
}

/**
 * Get Order Use Case - Implementation of the get order use case.
 */
export class GetOrderService {
  constructor(private readonly orderRepository: OrderRepositoryPort) {}

  async execute(orderId: string) {
    const order = await this.orderRepository.findById(orderId);
    if (!order) {
      throw new EntityNotFoundError('Order', orderId);
    }
    return order;
  }
}

/**
 * Cancel Order Use Case - Implementation of the cancel order use case.
 */
export class CancelOrderService {
  constructor(
    private readonly orderRepository: OrderRepositoryPort,
    private readonly eventBus: EventBusPort
  ) {}

  async execute(orderId: string, reason: string) {
    const order = await this.orderRepository.findById(orderId);
    if (!order) {
      throw new EntityNotFoundError('Order', orderId);
    }

    const domainOrder = Order.fromPersistence(order as any);
    domainOrder.cancel(reason);

    await this.orderRepository.save(domainOrder.toJSON() as any);

    await this.eventBus.publish({
      eventType: 'OrderCancelled',
      occurredAt: new Date(),
      aggregateId: orderId,
      orderId,
      reason,
    } as any);
  }
}
