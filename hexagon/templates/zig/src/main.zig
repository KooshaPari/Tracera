const std = @import("std");
const domain = @import("domain/entity.zig");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    std.log.info("Starting hexagonal Zig application", .{});

    // Example: Create a domain entity
    const entity = domain.ExampleEntity.init(allocator, "Example");
    defer entity.deinit();

    std.log.info("Created entity: {s}", .{entity.name});
}

test "basic test" {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const entity = domain.ExampleEntity.init(allocator, "Test");
    defer entity.deinit();

    try std.testing.expectEqualStrings("Test", entity.name);
}
