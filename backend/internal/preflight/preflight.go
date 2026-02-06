// Package preflight provides startup checks.
package preflight

import (
	"context"
	"fmt"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/config"
)

// Check represents a preflight health check to run
type Check struct {
	Name     string
	URL      string
	Required bool
	Kind     string // tcp, http, or env
	Path     string
	Timeout  time.Duration
}

// Result represents the outcome of a preflight check
type Result struct {
	Name     string
	OK       bool
	Message  string
	Required bool
}

const (
	defaultCheckTimeout = 2 * time.Second
	pythonCheckTimeout  = 5 * time.Second
	spinnerClearWidth   = 70
	hostPortParts       = 2
	defaultPostgresPort = "5432"
	defaultRedisPort    = "6379"
	defaultNatsPort     = "4222"
	defaultNeo4jPort    = "7687"
	defaultHTTPPort     = "80"
	defaultHTTPSPort    = "443"
)

// BuildBackendChecks creates a list of preflight checks for backend services
func BuildBackendChecks(cfg *config.Config) []Check {
	return []Check{
		{Name: "database", URL: cfg.DatabaseURL, Required: true, Kind: "tcp", Timeout: defaultCheckTimeout},
		{Name: "redis", URL: cfg.RedisURL, Required: true, Kind: "tcp", Timeout: defaultCheckTimeout},
		{Name: "nats", URL: cfg.NATSUrl, Required: true, Kind: "tcp", Timeout: defaultCheckTimeout},
		{Name: "neo4j", URL: cfg.Neo4jURI, Required: true, Kind: "tcp", Timeout: defaultCheckTimeout},
		{Name: "python-backend", URL: cfg.PythonBackendURL, Required: false, Kind: "http", Path: "/health", Timeout: pythonCheckTimeout},
		{Name: "s3-endpoint", URL: cfg.S3Endpoint, Required: true, Kind: "tcp", Timeout: defaultCheckTimeout},
		{Name: "s3-access-key", URL: cfg.S3AccessKeyID, Required: true, Kind: "env", Timeout: defaultCheckTimeout},
		{Name: "s3-secret", URL: cfg.S3SecretAccessKey, Required: true, Kind: "env", Timeout: defaultCheckTimeout},
		{Name: "s3-bucket", URL: cfg.S3Bucket, Required: true, Kind: "env", Timeout: defaultCheckTimeout},
		{Name: "temporal-host", URL: getEnv("TEMPORAL_HOST", ""), Required: true, Kind: "tcp", Timeout: defaultCheckTimeout},
		{Name: "temporal-namespace", URL: getEnv("TEMPORAL_NAMESPACE", ""), Required: true, Kind: "env", Timeout: defaultCheckTimeout},
		{Name: "workos-api", URL: getEnv("WORKOS_API_BASE_URL", "https://api.workos.com"), Required: true, Kind: "tcp", Timeout: defaultCheckTimeout},
		{Name: "workos-client-id", URL: cfg.WorkOSClientID, Required: true, Kind: "env", Timeout: defaultCheckTimeout},
		{Name: "workos-api-key", URL: cfg.WorkOSAPIKey, Required: true, Kind: "env", Timeout: defaultCheckTimeout},
		{Name: "workos-domain", URL: getEnv("WORKOS_AUTHKIT_DOMAIN", ""), Required: true, Kind: "env", Timeout: defaultCheckTimeout},
	}
}

// Run executes preflight checks once without retries.
func Run(ctx context.Context, checks []Check) error {
	return RunWithPoll(ctx, checks, nil, 0, 0)
}

// DefaultPollCheckNames returns check names that get wait-and-poll (retries) instead of single attempt.
// python-backend is not required; only temporal-host is polled.
func DefaultPollCheckNames() []string {
	return []string{"temporal-host"}
}

// RunWithPoll runs preflight checks. Checks in pollNames get retries with interval; others run once.
// If pollNames is nil or retries is 0, no polling is done (same as Run with single attempt per check).
func RunWithPoll(ctx context.Context, checks []Check, pollNames []string, retries int, interval time.Duration) error {
	pollSet := make(map[string]bool)
	for _, n := range pollNames {
		pollSet[n] = true
	}
	var failures []string

	for _, check := range checks {
		if strings.TrimSpace(check.URL) == "" {
			if check.Required {
				failures = append(failures, check.Name+" missing URL")
			}
			continue
		}

		if pollSet[check.Name] && retries > 0 && interval > 0 {
			ok, msg := runCheckWithRetry(ctx, check, retries, interval)
			if !ok {
				if check.Required {
					failures = append(failures, check.Name+": "+msg)
				}
			}
			continue
		}

		ok, msg := performCheck(ctx, check)
		if !ok {
			if check.Required {
				failures = append(failures, check.Name+": "+msg)
			}
		}
	}

	if len(failures) > 0 {
		return fmt.Errorf("preflight failed: %s", strings.Join(failures, "; "))
	}
	return nil
}

func runCheckWithRetry(ctx context.Context, check Check, retries int, interval time.Duration) (bool, string) {
	spinner := []string{"|", "/", "-", "\\"}
	var lastMsg string
	for attempt := 1; attempt <= retries; attempt++ {
		ok, msg := performCheck(ctx, check)
		if ok {
			fmt.Fprintf(os.Stderr, "\r%s\r", strings.Repeat(" ", spinnerClearWidth))
			if attempt > 1 {
				log.Printf("[preflight] %s ok (after %d/%d)", check.Name, attempt, retries)
			}
			return true, msg
		}
		lastMsg = msg
		idx := (attempt - 1) % len(spinner)
		fmt.Fprintf(os.Stderr, "\r[preflight] Waiting for %s... %s (%d/%d)   ", check.Name, spinner[idx], attempt, retries)
		if attempt < retries {
			select {
			case <-ctx.Done():
				return false, ctx.Err().Error()
			case <-time.After(interval):
			}
		}
	}
	fmt.Fprintf(os.Stderr, "\r%s\r", strings.Repeat(" ", spinnerClearWidth))
	return false, lastMsg
}

func performCheck(ctx context.Context, check Check) (bool, string) {
	if check.Kind == "env" {
		if strings.TrimSpace(check.URL) != "" {
			return true, "ok"
		}
		return false, "missing"
	}
	if check.Kind == "http" {
		path := check.Path
		if path == "" {
			path = "/health"
		}
		return httpCheck(ctx, check.URL, path, check.Timeout)
	}
	return tcpCheck(check.URL, check.Timeout)
}

func httpCheck(ctx context.Context, rawURL, path string, timeout time.Duration) (bool, string) {
	base := strings.TrimRight(rawURL, "/")
	fullURL := base + path

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, fullURL, nil)
	if err != nil {
		return false, err.Error()
	}

	client := &http.Client{Timeout: timeout}
	resp, err := client.Do(req)
	if err != nil {
		return false, err.Error()
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			log.Printf("error closing preflight response body: %v", err)
		}
	}()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return false, "status " + strconv.Itoa(resp.StatusCode)
	}

	return true, "ok"
}

func tcpCheck(rawURL string, timeout time.Duration) (bool, string) {
	parsed, err := url.Parse(rawURL)
	if err != nil {
		return false, err.Error()
	}

	host := parsed.Hostname()
	port := parsed.Port()
	if host == "" && !strings.Contains(rawURL, "://") && strings.Contains(rawURL, ":") {
		parts := strings.Split(rawURL, ":")
		if len(parts) == hostPortParts {
			host = parts[0]
			port = parts[1]
		}
	}
	if host == "" {
		return false, "missing host"
	}
	if port == "" {
		port = defaultPort(parsed.Scheme)
	}
	if port == "" {
		return false, "missing port"
	}

	addr := net.JoinHostPort(host, port)
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	dialer := net.Dialer{Timeout: timeout}
	conn, err := dialer.DialContext(ctx, "tcp", addr)
	if err != nil {
		return false, err.Error()
	}
	_ = conn.Close()

	return true, "ok"
}

func defaultPort(scheme string) string {
	switch strings.ToLower(scheme) {
	case "postgres", "postgresql", "postgresql+asyncpg":
		return defaultPostgresPort
	case "redis", "rediss":
		return defaultRedisPort
	case "nats":
		return defaultNatsPort
	case "neo4j", "bolt":
		return defaultNeo4jPort
	case "http":
		return defaultHTTPPort
	case "https":
		return defaultHTTPSPort
	default:
		return ""
	}
}

func getEnv(key, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(key)); value != "" {
		return value
	}
	return fallback
}
