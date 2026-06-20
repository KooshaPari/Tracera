// Package autoupdate handles version checks and update downloads.
package autoupdate

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"time"
)

const updateHTTPTimeout = 10 * time.Second

// UpdateConfig holds auto-update configuration
type UpdateConfig struct {
	UpdateServer   string
	CurrentVersion string
	CheckInterval  time.Duration
	Enabled        bool
}

// UpdateChecker handles automatic updates
type UpdateChecker struct {
	config UpdateConfig
	client *http.Client
}

// NewUpdateChecker creates a new update checker
func NewUpdateChecker(config UpdateConfig) *UpdateChecker {
	return &UpdateChecker{
		config: config,
		client: &http.Client{Timeout: updateHTTPTimeout},
	}
}

// Start begins checking for updates
func (uc *UpdateChecker) Start(ctx context.Context) {
	if !uc.config.Enabled {
		return
	}

	ticker := time.NewTicker(uc.config.CheckInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			uc.checkForUpdate(ctx)
		}
	}
}

// checkForUpdate checks if a new version is available
func (uc *UpdateChecker) checkForUpdate(ctx context.Context) {
	latestVersion, err := uc.fetchLatestVersion(ctx)
	if err != nil {
		slog.Error("Failed to check for updates", "error", err)
		return
	}

	if uc.isNewerVersion(latestVersion) {
		slog.Info("New version available (current )", "version", latestVersion, "detail", uc.config.CurrentVersion)
		if err := uc.downloadAndInstall(ctx, latestVersion); err != nil {
			slog.Error("Failed to update", "error", err)
		}
	}
}

// fetchLatestVersion fetches the latest version from update server
func (uc *UpdateChecker) fetchLatestVersion(ctx context.Context) (string, error) {
	url := uc.config.UpdateServer + "/latest?os=" + runtime.GOOS + "&arch=" + runtime.GOARCH
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return "", err
	}
	resp, err := uc.client.Do(req)
	if err != nil {
		return "", err
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("error closing update response", "error", err)
		}
	}()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("update server returned %d", resp.StatusCode)
	}

	// Parse version from response
	var version string
	if _, err := fmt.Fscanf(resp.Body, "%s", &version); err != nil {
		// Treat empty body as "no latest version" rather than an error.
		return "", nil
	}
	return version, nil
}

// isNewerVersion checks if latestVersion is newer than current
func (uc *UpdateChecker) isNewerVersion(latest string) bool {
	// Simple version comparison (e.g., "1.0.1" > "1.0.0")
	return latest > uc.config.CurrentVersion
}

// downloadAndInstall downloads and installs the new version
func (uc *UpdateChecker) downloadAndInstall(ctx context.Context, version string) error {
	exePath, err := os.Executable()
	if err != nil {
		return err
	}

	// Download new binary
	url := uc.config.UpdateServer + "/download/" + version + "?os=" + runtime.GOOS + "&arch=" + runtime.GOARCH
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return err
	}
	resp, err := uc.client.Do(req)
	if err != nil {
		return err
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("error closing update response", "error", err)
		}
	}()

	// Save to temporary file
	tmpDir := filepath.Dir(exePath)
	tmpPattern := filepath.Base(exePath) + ".new-*"
	tmpFileHandle, err := os.CreateTemp(tmpDir, tmpPattern)
	if err != nil {
		return err
	}
	tmpFile := tmpFileHandle.Name()
	defer func() {
		if err := tmpFileHandle.Close(); err != nil {
			slog.Error("error closing update file", "error", err)
		}
	}()

	if _, err := tmpFileHandle.ReadFrom(resp.Body); err != nil {
		return err
	}

	// Make executable
	const executableFilePerm = 0o755
	if err := os.Chmod(tmpFile, executableFilePerm); err != nil {
		return err
	}

	// Replace old binary with new one
	if err := os.Rename(tmpFile, exePath); err != nil {
		return err
	}

	slog.Info("Successfully updated to version", "version", version)
	return nil
}

// CheckNow performs an immediate update check
func (uc *UpdateChecker) CheckNow() error {
	uc.checkForUpdate(context.Background())
	return nil
}

// GetCurrentVersion returns the current version
func (uc *UpdateChecker) GetCurrentVersion() string {
	return uc.config.CurrentVersion
}

// SetUpdateServer sets the update server URL
func (uc *UpdateChecker) SetUpdateServer(url string) {
	uc.config.UpdateServer = url
}
