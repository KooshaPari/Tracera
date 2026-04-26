//! Application Ports (Interfaces)
//!
//! Following Hexagonal Architecture (Ports & Adapters) pattern.
//! Ports define boundaries; adapters implement them.

const std = @import("std");
const entities = @import("../domain/entities.zig");
const dto = @import("../dto.zig");

/// Repository port following Interface Segregation Principle
pub const OrderRepository = struct {
    save: fn (order: *entities.Order) anyerror!void,
    findById: fn (id: []const u8) anyerror!?entities.Order,
    findAll: fn () anyerror![]entities.Order,
    delete: fn (id: []const u8) anyerror!void,
};

/// Event publisher port following Observer pattern
pub const EventPublisher = struct {
    publish: fn (event: dto.DomainEvent) anyerror!void,
    subscribe: fn (handler: fn (dto.DomainEvent) void) void,
};

/// Email service port
pub const EmailService = struct {
    send: fn (to: []const u8, subject: []const u8, body: []const u8) anyerror!void,
};

/// Logger port following Dependency Inversion Principle
pub const Logger = struct {
    info: fn (message: []const u8) void,
    error: fn (message: []const u8) void,
    debug: fn (message: []const u8) void,
};

/// Order use case input port
pub const CreateOrderInput = struct {
    customer_id: []const u8,
    items: []dto.OrderItemDTO,
};

/// Order use case output port
pub const CreateOrderOutput = struct {
    order_id: []const u8,
    status: []const u8,
    total: f64,
};
