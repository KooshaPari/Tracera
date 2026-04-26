const std = @import("std");

/// Build script for hexagonal-zig template
/// Run: zig build
///
/// Dependencies are fetched via build.zig.zon
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Domain layer - pure business logic
    const domain = b.addModule("domain", .{
        .root_source_file = .{ .path = "src/domain/domain.zig" },
    });

    // Application layer - use cases
    const application = b.addModule("application", .{
        .root_source_file = .{ .path = "src/application/application.zig" },
        .dependencies = &.{
            .{ .name = "domain", .module = domain },
        },
    });

    // Infrastructure layer - adapters
    const infrastructure = b.addModule("infrastructure", .{
        .root_source_file = .{ .path = "src/infrastructure/infrastructure.zig" },
        .dependencies = &.{
            .{ .name = "domain", .module = domain },
            .{ .name = "application", .module = application },
        },
    });

    // Main application
    const main_module = b.addModule("hexagonal_zig", .{
        .root_source_file = .{ .path = "src/main.zig" },
        .dependencies = &.{
            .{ .name = "domain", .module = domain },
            .{ .name = "application", .module = application },
            .{ .name = "infrastructure", .module = infrastructure },
        },
    });

    const exe = b.addExecutable(.{
        .name = "hexagonal_zig",
        .root_module = main_module,
        .target = target,
        .optimize = optimize,
    });

    b.installArtifact(exe);

    // Unit tests
    const unit_tests = b.addTest(.{
        .root_module = domain,
        .target = target,
        .optimize = optimize,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.step.dependOn(b.step("test", "Run unit tests"));

    // Integration tests
    const integration_tests = b.addTest(.{
        .root_module = application,
        .target = target,
        .optimize = optimize,
    });

    const run_integration_tests = b.addRunArtifact(integration_tests);
    run_integration_tests.step.dependOn(b.step("integration_test", "Run integration tests"));
}
