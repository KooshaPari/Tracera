package config

import (
	"os"
	"strings"
	"time"
)

const Version = "0.1.0"

type Config struct {
	Enabled       bool
	APIBase       string
	PollInterval  time.Duration
	QueueEndpoint string

	// Control-plane (node agent) mode. All three must be set to activate.
	ControlPlaneBase string
	NodeID           string
	EnrollToken      string

	// StateDir is where per-service docker compose project dirs are created.
	StateDir string
	// ConvergeTimeout bounds a single docker compose invocation.
	ConvergeTimeout time.Duration
}

func boolEnv(name string, defaultValue bool) bool {
	v := strings.ToLower(strings.TrimSpace(os.Getenv(name)))
	switch v {
	case "1", "true", "yes", "on":
		return true
	case "0", "false", "no", "off":
		return false
	default:
		return defaultValue
	}
}

func getenv(name, fallback string) string {
	if v := strings.TrimSpace(os.Getenv(name)); v != "" {
		return v
	}
	return fallback
}

func getDuration(name string, fallback time.Duration) time.Duration {
	if v := strings.TrimSpace(os.Getenv(name)); v != "" {
		if d, err := time.ParseDuration(v); err == nil && d > 0 {
			return d
		}
	}
	return fallback
}

func InitializeContext() Config {
	return Config{
		Enabled:       boolEnv("TRACERA_SIDE_CAR_ENABLED", false),
		APIBase:       getenv("TRACERA_API_BASE", "http://127.0.0.1:8080"),
		PollInterval:  getDuration("TRACERA_SIDE_CAR_POLL_INTERVAL", 5*time.Second),
		QueueEndpoint: getenv("TRACERA_SIDE_CAR_QUEUE", "/var/run/tracera/dispatch.sock"),

		ControlPlaneBase: getenv("TRACERA_CONTROL_PLANE_URL", ""),
		NodeID:           getenv("TRACERA_NODE_ID", ""),
		EnrollToken:      getenv("TRACERA_ENROLL_TOKEN", ""),

		StateDir:        getenv("TRACERA_NODE_STATE_DIR", "/var/lib/tracera-node"),
		ConvergeTimeout: getDuration("TRACERA_NODE_CONVERGE_TIMEOUT", 5*time.Minute),
	}
}
