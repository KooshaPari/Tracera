// Package executor converges a node's docker compose state to a desired set
// of services. Phase 1 keeps this deliberately boring: for each desired
// service, run `docker compose up -d --pull always` in a directory named for
// the service, with an image override. Failure of one service does not stop
// the others.
package executor

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// Result maps a service name to a short outcome string.
type Result map[string]string

// ComposeRunner executes the convergence. It is an interface so tests can
// stub out docker.
type ComposeRunner interface {
	Run(ctx context.Context, service, image string) error
}

// DockerCompose runs real docker compose commands.
type DockerCompose struct {
	// StateDir is where per-service compose project directories live.
	StateDir string
	// Timeout bounds a single compose invocation.
	Timeout time.Duration
}

// NewDockerCompose creates a runner rooted at stateDir.
func NewDockerCompose(stateDir string, timeout time.Duration) *DockerCompose {
	return &DockerCompose{StateDir: stateDir, Timeout: timeout}
}

// Run brings service up to image (or down if image is empty).
func (d *DockerCompose) Run(ctx context.Context, service, image string) error {
	dir := filepath.Join(d.StateDir, service)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return fmt.Errorf("mkdir %s: %w", dir, err)
	}
	ctx, cancel := context.WithTimeout(ctx, d.Timeout)
	defer cancel()

	if image == "" {
		cmd := exec.CommandContext(ctx, "docker", "compose", "down", "-v")
		cmd.Dir = dir
		if out, err := cmd.CombinedOutput(); err != nil {
			return fmt.Errorf("compose down %s: %v: %s", service, err, strings.TrimSpace(string(out)))
		}
		return nil
	}

	// The compose project is a minimal one-service file referencing the
	// requested image. We write it fresh on every convergence so the desired
	// image always wins.
	composeYAML := fmt.Sprintf("services:\n  %s:\n    image: %s\n    restart: unless-stopped\n", service, image)
	if err := os.WriteFile(filepath.Join(dir, "docker-compose.yml"), []byte(composeYAML), 0o644); err != nil {
		return fmt.Errorf("write compose file: %w", err)
	}
	cmd := exec.CommandContext(ctx, "docker", "compose", "up", "-d", "--pull", "always")
	cmd.Dir = dir
	if out, err := cmd.CombinedOutput(); err != nil {
		return fmt.Errorf("compose up %s: %v: %s", service, err, strings.TrimSpace(string(out)))
	}
	return nil
}

// Converge applies the desired state. It always processes every service and
// aggregates results, so a single failure does not block the rest.
func Converge(ctx context.Context, runner ComposeRunner, desired map[string]string) Result {
	results := Result{}
	for service, image := range desired {
		if err := runner.Run(ctx, service, image); err != nil {
			results[service] = "failed:" + err.Error()
			continue
		}
		results[service] = "ok"
	}
	return results
}
