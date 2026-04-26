/**
 * Inbound Ports (Primary/Driving Ports)
 *
 * These ports define the interface that drives the application.
 * They represent use cases from the perspective of the outside world.
 *
 * Following Hexagonal Architecture:
 * - Inbound ports are the "primary" or "driving" ports
 * - They define what the application can do (use cases)
 * - Implementation is in the application layer
 */

/**
 * Port for creating orders.
 */
export interface CreateOrderUseCase {
  execute(command: CreateOrderCommand): Promise<OrderResult>;
}

/**
 * Command for creating an order.
 */
export interface CreateOrderCommand {
  customerId: string;
  items: OrderItemCommand[];
  shippingAddress: AddressCommand;
}

/**
 * Order item in command form.
 */
export interface OrderItemCommand {
  productId: string;
  quantity: number;
  price: number;
}

/**
 * Address in command form.
 */
export interface AddressCommand {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

/**
 * Result of order creation.
 */
export interface OrderResult {
  orderId: string;
  status: OrderStatus;
  total: number;
}

/**
 * Order status enum.
 */
export enum OrderStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  SHIPPED = 'SHIPPED',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED',
}

/**
 * Port for retrieving orders.
 */
export interface GetOrderUseCase {
  execute(orderId: string): Promise<Order>;
}

/**
 * Order representation.
 */
export interface Order {
  id: string;
  customerId: string;
  items: OrderItem[];
  status: OrderStatus;
  total: number;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Order item representation.
 */
export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

/**
 * Port for cancelling orders.
 */
export interface CancelOrderUseCase {
  execute(orderId: string, reason: string): Promise<void>;
}
