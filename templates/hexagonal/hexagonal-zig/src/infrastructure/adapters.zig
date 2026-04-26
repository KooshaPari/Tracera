//! Infrastructure Adapters
//!
//! Implementations of the application ports.
//!
//! Following Dependency Inversion Principle - high-level modules don't depend on low-level modules.

const std = @import("std");
const ports = @import("../application/ports.zig");
const dto = @import("../dto.zig");

/// In-memory order repository adapter
pub const InMemoryOrderRepository = struct {
    orders: std.ArrayList(dto.OrderDTO),

    pub fn init(allocator: std.mem.Allocator) @This() {
        return .{
            .orders = std.ArrayList(dto.OrderDTO).init(allocator),
        };
    }

    pub fn deinit(self: *@This()) void {
        self.orders.deinit();
    }

    pub fn save(self: *@This(), order: dto.OrderDTO) !void {
        try self.orders.append(order);
    }

    pub fn findById(self: *@This(), id: []const u8) ?dto.OrderDTO {
        for (self.orders.items) |order| {
            if (std.mem.eql(u8, order.id, id)) {
                return order;
            }
        }
        return null;
    }

    pub fn findAll(self: *@This()) []dto.OrderDTO {
        return self.orders.items;
    }
};

/// Console logger adapter
pub const ConsoleLogger = struct {
    fn log(level: []const u8, message: []const u8) void {
        std.debug.print("[{s}] {s}\n", .{ level, message });
    }

    pub fn info(message: []const u8) void {
        log("INFO", message);
    }

    pub fn error(message: []const u8) void {
        log("ERROR", message);
    }

    pub fn debug(message: []const u8) void {
        log("DEBUG", message);
    }
};

/// Console event publisher adapter
pub const ConsoleEventPublisher = struct {
    pub fn publish(self: *@This(), event: dto.DomainEvent) !void {
        std.debug.print("EVENT: {s} - {s}\n", .{ event.event_type, event.payload });
    }
};

/// HTTP API adapter (example using std.http)
pub const HttpApiAdapter = struct {
    server: std.http.Server,
    use_case: *const ports.CreateOrderUseCase,

    pub fn handleRequest(self: *@This(), request: std.http.Server.Request) !void {
        // Handle POST /orders
        if (std.mem.eql(u8, request.method, .POST) and
            std.mem.startsWith(u8, request.target, "/orders")) {
            // Parse request body and call use case
            // This is a simplified example
            try request.respond(.{ .status = .created });
        }
    }
};
