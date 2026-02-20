// Package main builds distributable packages for tracertm-backend.
package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
)

const (
	configFilePerm = 0o644
	packageDirPerm = 0o755
)

func main() {
	const (
		minArgs      = 2
		targetIndex  = 1
		versionIndex = 2
	)

	if len(os.Args) < minArgs {
		printUsage()
		os.Exit(1)
	}

	target := os.Args[targetIndex]
	version := "1.0.0"
	if len(os.Args) > versionIndex {
		version = os.Args[versionIndex]
	}

	fmt.Println("\n╔════════════════════════════════════════════════════════════════╗")
	fmt.Println("║         TraceRTM - Multi-Platform Packaging                   ║")
	fmt.Println("╚════════════════════════════════════════════════════════════════╝")

	ctx := context.Background()
	switch target {
	case "macos":
		packageMacOS(ctx, version)
	case "linux":
		packageLinux(ctx, version)
	case "windows":
		packageWindows(ctx, version)
	case "all":
		packageAll(ctx, version)
	default:
		fmt.Printf("Unknown target: %s\n", target)
		printUsage()
		os.Exit(1)
	}
}

func packageMacOS(ctx context.Context, version string) {
	fmt.Printf("🍎 Packaging for macOS (v%s)...\n", version)

	const bundleDirPerm = 0o750

	// Create app bundle structure
	appDir := "dist/TraceRTM-" + version + ".app/Contents"
	ensureDir(filepath.Join(appDir, "MacOS"), bundleDirPerm)
	ensureDir(filepath.Join(appDir, "Resources"), bundleDirPerm)

	// Copy binary
	//nolint:gosec // G204: paths are controlled build paths, not user input
	cmd := exec.CommandContext(ctx, "cp", "../tracertm-backend", filepath.Join(appDir, "MacOS/tracertm"))
	if err := cmd.Run(); err != nil {
		log.Fatalf("Failed to copy binary: %v", err)
	}

	// Create Info.plist
	plist := fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>TraceRTM</string>
    <key>CFBundleVersion</key>
    <string>%s</string>
    <key>CFBundleExecutable</key>
    <string>tracertm</string>
    <key>CFBundleIdentifier</key>
    <string>com.tracertm.app</string>
</dict>
</plist>`, version)

	plistPath := filepath.Join(appDir, "Info.plist")
	if err := os.WriteFile(plistPath, []byte(plist), configFilePerm); err != nil {
		log.Fatalf("Failed to write Info.plist: %v", err)
	}

	fmt.Println("✅ macOS app bundle created")
}

func packageLinux(ctx context.Context, version string) {
	fmt.Printf("🐧 Packaging for Linux (v%s)...\n", version)

	// Create .deb package structure
	debDir := "dist/tracertm-" + version
	ensureDir(filepath.Join(debDir, "usr/local/bin"), packageDirPerm)
	ensureDir(filepath.Join(debDir, "etc/systemd/system"), packageDirPerm)

	// Copy binary
	//nolint:gosec // G204: paths are controlled build paths, not user input
	cmd := exec.CommandContext(ctx, "cp", "../tracertm-backend", filepath.Join(debDir, "usr/local/bin/tracertm"))
	if err := cmd.Run(); err != nil {
		log.Fatalf("Failed to copy binary: %v", err)
	}

	// Create systemd service
	service := `[Unit]
Description=TraceRTM Backend Service
After=network.target

[Service]
Type=simple
User=tracertm
ExecStart=/usr/local/bin/tracertm
Restart=on-failure

[Install]
WantedBy=multi-user.target
`

	servicePath := filepath.Join(debDir, "etc/systemd/system/tracertm.service")
	if err := os.WriteFile(servicePath, []byte(service), configFilePerm); err != nil {
		log.Fatalf("Failed to write service file: %v", err)
	}

	fmt.Println("✅ Linux package structure created")
}

func packageWindows(ctx context.Context, version string) {
	fmt.Printf("🪟 Packaging for Windows (v%s)...\n", version)

	// Create Windows installer structure
	winDir := "dist/tracertm-" + version + "-windows"
	ensureDir(winDir, packageDirPerm)

	// Copy binary
	//nolint:gosec // G204: paths are controlled build paths, not user input
	cmd := exec.CommandContext(ctx, "cp", "../tracertm-backend.exe", filepath.Join(winDir, "tracertm.exe"))
	if err := cmd.Run(); err != nil {
		log.Fatalf("Failed to copy binary: %v", err)
	}

	fmt.Println("✅ Windows package structure created")
}

func packageAll(ctx context.Context, version string) {
	fmt.Println("📦 Packaging for all platforms...")
	packageMacOS(ctx, version)
	packageLinux(ctx, version)
	packageWindows(ctx, version)
	fmt.Println("\n✅ All packages created successfully")
}

func ensureDir(path string, perm os.FileMode) {
	if err := os.MkdirAll(path, perm); err != nil {
		log.Fatalf("Failed to create directory %s: %v", path, err)
	}
}

func printUsage() {
	fmt.Println("Usage: tracertm-package <target> [version]\n" +
		"\nTargets:\n" +
		"  macos      - Package for macOS (.app bundle)\n" +
		"  linux      - Package for Linux (.deb structure)\n" +
		"  windows    - Package for Windows (.exe)\n" +
		"  all        - Package for all platforms\n" +
		"\nExamples:\n" +
		"  tracertm-package macos\n" +
		"  tracertm-package all 1.0.0")
}
