const entity = @import("../domain/entity.zig");
const errors = @import("../domain/errors.zig");

// Inbound port
pub const CreateExample = struct {
    execute: *const fn (ctx: *anyopaque, name: []const u8) errors.DomainError!entity.ExampleEntity,
};

// Outbound port
pub const Repository = struct {
    save: *const fn (ctx: *anyopaque, e: entity.ExampleEntity) errors.DomainError!void,
    findById: *const fn (ctx: *anyopaque, id: [16]u8) errors.DomainError!?entity.ExampleEntity,
};
