const std = @import("std");
const uuid = @import("uuid.zig");

pub const ExampleEntity = struct {
    id: uuid.Uuid,
    name: []const u8,
    created_at: i64,
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator, name: []const u8) ExampleEntity {
        return .{
            .id = uuid.generate(),
            .name = std.mem.Allocator.dupe(allocator, u8, name) catch unreachable,
            .created_at = std.time.timestamp(),
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *const ExampleEntity) void {
        self.allocator.free(self.name);
    }
};
