const entity = @import("entity.zig");
const errors = @import("errors.zig");

// Repository port (outbound)
pub const Repository = struct {
    findById: *const fn (ctx: *anyopaque, id: [16]u8) errors.DomainError!?entity.ExampleEntity,
    save: *const fn (ctx: *anyopaque, e: entity.ExampleEntity) errors.DomainError!void,
};

// Service port (inbound)
pub const Service = struct {
    create: *const fn (ctx: *anyopaque, name: []const u8) errors.DomainError!entity.ExampleEntity,
    get: *const fn (ctx: *anyopaque, id: [16]u8) errors.DomainError!?entity.ExampleEntity,
};
