const std = @import("std");

pub const Uuid = [16]u8;

pub fn generate() Uuid {
    var uuid: Uuid = undefined;
    std.crypto.random.bytes(&uuid);
    // Set version (4) and variant (RFC 4122)
    uuid[6] = (uuid[6] & 0x0F) | 0x40;
    uuid[8] = (uuid[8] & 0x3F) | 0x80;
    return uuid;
}

pub fn format(uuid: Uuid, buf: []u8) ![]const u8 {
    return try std.fmt.bufPrint(buf, "{x:02}{x:02}{x:02}{x:02}-{x:02}{x:02}-{x:02}{x:02}-{x:02}{x:02}-{x:02}{x:02}{x:02}{x:02}{x:02}{x:02}", .{
        uuid[0], uuid[1], uuid[2], uuid[3],
        uuid[4], uuid[5], uuid[6], uuid[7],
        uuid[8], uuid[9], uuid[10], uuid[11],
        uuid[12], uuid[13], uuid[14], uuid[15],
    });
}
