//! Hexagonal Architecture Template for Zig
//!
//! This template provides a clean hexagonal (ports & adapters) architecture
//! following SOLID, KISS, DRY, and YAGNI principles.
//!
//! ## Architecture Layers
//!
//! 1. **Domain** (core): Pure business logic, no external dependencies
//! 2. **Application**: Use cases, ports (interfaces)
//! 3. **Infrastructure**: Adapters implementing ports
//!
//! ## Quick Start
//!
//! ```bash
//! zig build run
//! zig build test
//! ```

const std = @import("std");

pub fn main() void {
    std.debug.print("Hexagonal Architecture Template for Zig\n", .{});
    std.debug.print("=========================================\n\n", .{});

    std.debug.print("Layers:\n", .{});
    std.debug.print("  1. domain/        - Entities, Value Objects, Services\n", .{});
    std.debug.print("  2. application/   - Ports, Use Cases, DTOs\n", .{});
    std.debug.print("  3. infrastructure/ - Persistence, API, Messaging adapters\n\n", .{});

    std.debug.print("Run tests: zig build test\n", .{});
}
