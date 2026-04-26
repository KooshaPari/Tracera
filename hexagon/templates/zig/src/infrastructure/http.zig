const std = @import("std");
const net = std.net;

pub const Server = struct {
    address: net.Address,

    pub fn init(port: u16) !Server {
        const address = try net.Address.parseIp4("0.0.0.0", port);
        return .{ .address = address };
    }

    pub fn run(self: *const Server) !void {
        var listener = try net.tcp.Listener.init(self.address, .{});
        defer listener.deinit();

        std.log.info("Server listening on {}", .{self.address});

        while (true) {
            const conn = try listener.accept();
            defer conn.stream.close();

            var buf: [1024]u8 = undefined;
            const n = try conn.stream.read(&buf);
            const request = buf[0..n];

            // Simple HTTP response
            const response = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK";
            _ = try conn.stream.write(response);
        }
    }
};
