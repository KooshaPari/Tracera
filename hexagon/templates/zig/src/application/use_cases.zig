const std = @import("std");
const entity = @import("../domain/entity.zig");
const errors = @import("../domain/errors.zig");
const ports = @import("ports.zig");

pub const CreateExampleUseCase = struct {
    repository: ports.Repository,
    repo_ctx: *anyopaque,
    allocator: std.mem.Allocator,

    pub fn init(repo: ports.Repository, repo_ctx: *anyopaque, allocator: std.mem.Allocator) CreateExampleUseCase {
        return .{
            .repository = repo,
            .repo_ctx = repo_ctx,
            .allocator = allocator,
        };
    }

    pub fn execute(self: *const CreateExampleUseCase, name: []const u8) errors.DomainError!entity.ExampleEntity {
        var e = entity.ExampleEntity.init(self.allocator, name);
        errdefer e.deinit();

        try self.repository.save(self.repo_ctx, e);
        return e;
    }
};
