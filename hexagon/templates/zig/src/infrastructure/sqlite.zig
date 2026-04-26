const std = @import("std");
const c = @cImport({
    @cInclude("sqlite3.h");
});
const entity = @import("../domain/entity.zig");
const errors = @import("../domain/errors.zig");
const app_ports = @import("../application/ports.zig");

pub const SqliteRepository = struct {
    db: ?*c.sqlite3,

    pub fn init(db_path: []const u8) !SqliteRepository {
        var db: ?*c.sqlite3 = null;
        const rc = c.sqlite3_open(db_path.ptr, &db);
        if (rc != c.SQLITE_OK) {
            return errors.DomainError.DatabaseError;
        }
        return .{ .db = db };
    }

    pub fn deinit(self: *SqliteRepository) void {
        if (self.db) |db| {
            _ = c.sqlite3_close(db);
        }
    }

    pub fn save(self: *SqliteRepository, e: entity.ExampleEntity) errors.DomainError!void {
        _ = self;
        _ = e;
        // TODO: Implement SQL insert
        return {};
    }

    pub fn findById(self: *SqliteRepository, id: [16]u8) errors.DomainError!?entity.ExampleEntity {
        _ = self;
        _ = id;
        // TODO: Implement SQL select
        return null;
    }

    pub fn repository(self: *SqliteRepository) app_ports.Repository {
        return .{
            .save = saveCallback,
            .findById = findByIdCallback,
        };
    }

    fn saveCallback(ctx: *anyopaque, e: entity.ExampleEntity) errors.DomainError!void {
        const self = @as(*SqliteRepository, @ptrCast(@alignCast(ctx)));
        return self.save(e);
    }

    fn findByIdCallback(ctx: *anyopaque, id: [16]u8) errors.DomainError!?entity.ExampleEntity {
        const self = @as(*SqliteRepository, @ptrCast(@alignCast(ctx)));
        return self.findById(id);
    }
};
