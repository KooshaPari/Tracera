package config

import (
	"testing"
	"time"
)

func TestInitializeContextDefaults(t *testing.T) {
	t.Setenv("TRACERA_SIDE_CAR_ENABLED", "false")
	t.Setenv("TRACERA_API_BASE", "")
	cfg := InitializeContext()
	if cfg.Enabled {
		t.Fatalf("expected sidecar disabled by default env fixture")
	}
	if cfg.APIBase != "http://127.0.0.1:8080" {
		t.Fatalf("expected default API base, got: %q", cfg.APIBase)
	}
	if cfg.PollInterval != 5*time.Second {
		t.Fatalf("expected default poll interval, got: %s", cfg.PollInterval)
	}
	if cfg.QueueEndpoint == "" {
		t.Fatalf("expected default queue endpoint")
	}
}

func TestInitializeContextEnabled(t *testing.T) {
	t.Setenv("TRACERA_SIDE_CAR_ENABLED", "1")
	t.Setenv("TRACERA_API_BASE", "http://server:8080")
	t.Setenv("TRACERA_SIDE_CAR_POLL_INTERVAL", "3s")
	cfg := InitializeContext()
	if !cfg.Enabled {
		t.Fatalf("expected sidecar enabled")
	}
	if cfg.APIBase != "http://server:8080" {
		t.Fatalf("expected override API base, got: %q", cfg.APIBase)
	}
	if cfg.PollInterval != 3*time.Second {
		t.Fatalf("expected custom poll interval, got: %s", cfg.PollInterval)
	}
}

func TestInitializeContextRejectsNonPositivePollInterval(t *testing.T) {
	for _, value := range []string{"0s", "-1s", "not-a-duration"} {
		t.Run(value, func(t *testing.T) {
			t.Setenv("TRACERA_SIDE_CAR_POLL_INTERVAL", value)
			cfg := InitializeContext()
			if cfg.PollInterval != 5*time.Second {
				t.Fatalf("expected safe default for %q, got: %s", value, cfg.PollInterval)
			}
		})
	}
}
