//! Use Cases
//!
//! Following Single Responsibility Principle - one use case per struct.

const std = @import("std");
const entities = @import("../domain/entities.zig");
const ports = @import("./ports.zig");
const dto = @import("../dto.zig");

/// Create Order use case
pub const CreateOrderUseCase = struct {
    repository: *const ports.OrderRepository,
    event_publisher: *const ports.EventPublisher,
    logger: *const ports.Logger,

    pub fn execute(self: *const @This(), input: ports.CreateOrderInput) !dto.OrderDTO {
        self.logger.info("Creating order...");

        // Create order entity
        var order = entities.Order.create(input.customer_id);

        // Add items
        for (input.items) |item| {
            order.addItem(item.product_id, item.quantity, item.price) catch {
                self.logger.error("Failed to add item to order");
                return error.InvalidOrder;
            };
        }

        // Persist
        self.repository.save(&order) catch |err| {
            self.logger.error("Failed to save order");
            return err;
        };

        // Publish event
        const event = dto.DomainEvent{
            .event_type = "OrderCreated",
            .payload = try std.json.stringifyAlloc(std.heap.page_allocator, order.toDTO()),
        };
        self.event_publisher.publish(event);

        self.logger.info("Order created successfully");
        return order.toDTO();
    }
};

/// Get Order use case
pub const GetOrderUseCase = struct {
    repository: *const ports.OrderRepository,
    logger: *const ports.Logger,

    pub fn execute(self: *const @This(), id: []const u8) !dto.OrderDTO {
        self.logger.info("Getting order...");

        const order = self.repository.findById(id) catch |err| {
            self.logger.error("Failed to get order");
            return err;
        };

        if (order) |o| {
            return o.toDTO();
        } else {
            return error.OrderNotFound;
        }
    }
};

/// List Orders use case
pub const ListOrdersUseCase = struct {
    repository: *const ports.OrderRepository,
    logger: *const ports.Logger,

    pub fn execute(self: *const @This()) ![]dto.OrderDTO {
        self.logger.info("Listing orders...");
        return self.repository.findAll();
    }
};
