const std = @import("std");

pub const Config = struct {
    database_url: []const u8,
    server_port: u16,

    pub fn fromEnv(allocator: std.mem.Allocator) !Config {
        const database_url = std.process.getEnvVarOwned(allocator, "DATABASE_URL") catch 
            try allocator.dupe(u8, "data.db");
        errdefer allocator.free(database_url);

        const port_str = std.process.getEnvVarOwned(allocator, "SERVER_PORT") catch "3000";
        defer allocator.free(port_str);

        const server_port = try std.fmt.parseInt(u16, port_str, 10);

        return .{
            .database_url = database_url,
            .server_port = server_port,
        };
    }

    pub fn deinit(self: *const Config, allocator: std.mem.Allocator) void {
        allocator.free(self.database_url);
    }
};
