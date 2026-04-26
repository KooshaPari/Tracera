//! Domain Entity: Order
//!
//! Entities have identity and lifecycle.
//! Following DDD (Domain-Driven Design) principles.

const std = @import("std");
const uuid = @import("uuid");

/// Order entity with identity
pub const Order = struct {
    id: []const u8,
    customer_id: []const u8,
    items: []OrderItem,
    status: OrderStatus,
    total: f64,
    created_at: i64,

    pub const OrderStatus = enum {
        pending,
        confirmed,
        shipped,
        delivered,
        cancelled,
    };

    pub const OrderItem = struct {
        product_id: []const u8,
        quantity: u32,
        price: f64,
    };

    /// Factory method following Factory pattern
    pub fn create(customer_id: []const u8) Order {
        return Order{
            .id = uuid.generate(),
            .customer_id = customer_id,
            .items = &.{},
            .status = .pending,
            .total = 0.0,
            .created_at = std.time.timestamp(),
        };
    }

    /// Add item following Single Responsibility Principle
    pub fn addItem(self: *Order, item: OrderItem) void {
        self.items = self.items ++ .{item};
        self.total += @as(f64, item.quantity) * item.price;
    }

    /// Domain logic following KISS principle
    pub fn confirm(self: *Order) void {
        if (self.status == .pending) {
            self.status = .confirmed;
        }
    }

    /// Domain logic
    pub fn cancel(self: *Order) void {
        if (self.status != .shipped and self.status != .delivered) {
            self.status = .cancelled;
        }
    }

    /// Validation following Fail Fast principle
    pub fn isValid(self: *const Order) bool {
        return self.customer_id.len > 0 and self.items.len > 0;
    }
};

test "Order creation and lifecycle" {
    var order = Order.create("customer-123");
    try std.testing.expectEqualStrings("customer-123", order.customer_id);
    try std.testing.expect(order.status == .pending);
    try std.testing.expect(order.isValid() == false); // No items yet

    order.addItem(.{ .product_id = "prod-1", .quantity = 2, .price = 10.0 });
    try std.testing.expect(order.isValid() == true);
    try std.testing.expect(order.total == 20.0);

    order.confirm();
    try std.testing.expect(order.status == .confirmed);

    order.cancel();
    try std.testing.expect(order.status == .cancelled);
}
