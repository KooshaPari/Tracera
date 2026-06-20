//go:build !integration

package preflight

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDefaultPort(t *testing.T) {
	tests := []struct {
		scheme string
		want   string
	}{
		{"postgres", defaultPostgresPort},
		{"postgresql", defaultPostgresPort},
		{"postgresql+asyncpg", defaultPostgresPort},
		{"redis", defaultRedisPort},
		{"rediss", defaultRedisPort},
		{"nats", defaultNatsPort},
		{"neo4j", defaultNeo4jPort},
		{"bolt", defaultNeo4jPort},
		{"http", defaultHTTPPort},
		{"https", defaultHTTPSPort},
		{"unknown", ""},
		{"", ""},
		{"POSTGRES", defaultPostgresPort},
		{"Http", defaultHTTPPort},
	}

	for _, tt := range tests {
		t.Run(tt.scheme, func(t *testing.T) {
			got := defaultPort(tt.scheme)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestPerformCheck_EnvKind(t *testing.T) {
	tests := []struct {
		name    string
		check   Check
		wantOK  bool
		wantMsg string
	}{
		{
			name:    "env with value",
			check:   Check{Name: "test-env", Kind: "env", URL: "some-value"},
			wantOK:  true,
			wantMsg: "ok",
		},
		{
			name:    "env with whitespace-only value",
			check:   Check{Name: "test-env", Kind: "env", URL: "   "},
			wantOK:  false,
			wantMsg: "missing",
		},
		{
			name:    "env with empty value",
			check:   Check{Name: "test-env", Kind: "env", URL: ""},
			wantOK:  false,
			wantMsg: "missing",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ok, msg := performCheck(context.Background(), tt.check)
			assert.Equal(t, tt.wantOK, ok)
			assert.Equal(t, tt.wantMsg, msg)
		})
	}
}

func TestPerformCheck_HTTPKind(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	ok, msg := performCheck(context.Background(), Check{
		Name:    "test-http",
		Kind:    "http",
		URL:     server.URL,
		Path:    "/health",
		Timeout: 2 * time.Second,
	})
	assert.True(t, ok)
	assert.Equal(t, "ok", msg)
}

func TestPerformCheck_HTTPKind_ServerError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusServiceUnavailable)
	}))
	defer server.Close()

	ok, msg := performCheck(context.Background(), Check{
		Name:    "test-http",
		Kind:    "http",
		URL:     server.URL,
		Path:    "/health",
		Timeout: 2 * time.Second,
	})
	assert.False(t, ok)
	assert.Contains(t, msg, "status 503")
}

func TestPerformCheck_HTTPKind_DefaultPath(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/health" {
			w.WriteHeader(http.StatusOK)
			return
		}
		w.WriteHeader(http.StatusNotFound)
	}))
	defer server.Close()

	ok, _ := performCheck(context.Background(), Check{
		Name:    "test",
		Kind:    "http",
		URL:     server.URL,
		Path:    "", // should default to /health
		Timeout: 2 * time.Second,
	})
	assert.True(t, ok)
}

func TestPerformCheck_TCPKind_Unreachable(t *testing.T) {
	ok, msg := performCheck(context.Background(), Check{
		Name:    "test-tcp",
		Kind:    "tcp",
		URL:     "tcp://127.0.0.1:19999",
		Timeout: 100 * time.Millisecond,
	})
	assert.False(t, ok)
	assert.NotEmpty(t, msg)
}

func TestRun_AllPassingEnvChecks(t *testing.T) {
	checks := []Check{
		{Name: "env1", Kind: "env", URL: "value1", Required: true},
		{Name: "env2", Kind: "env", URL: "value2", Required: true},
	}

	err := Run(context.Background(), checks)
	assert.NoError(t, err)
}

func TestRun_RequiredMissingURL(t *testing.T) {
	checks := []Check{
		{Name: "missing", Kind: "env", URL: "", Required: true},
	}

	err := Run(context.Background(), checks)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "preflight failed")
	assert.Contains(t, err.Error(), "missing")
}

func TestRun_OptionalMissingURL(t *testing.T) {
	checks := []Check{
		{Name: "optional", Kind: "env", URL: "", Required: false},
	}

	err := Run(context.Background(), checks)
	assert.NoError(t, err)
}

func TestRun_MixedChecks(t *testing.T) {
	checks := []Check{
		{Name: "good-env", Kind: "env", URL: "present", Required: true},
		{Name: "optional-missing", Kind: "env", URL: "", Required: false},
	}

	err := Run(context.Background(), checks)
	assert.NoError(t, err)
}

func TestRunWithPoll_NoPollNames(t *testing.T) {
	checks := []Check{
		{Name: "env1", Kind: "env", URL: "value", Required: true},
	}

	err := RunWithPoll(context.Background(), checks, nil, 0, 0)
	assert.NoError(t, err)
}

func TestRunWithPoll_WithPollOnEnv(t *testing.T) {
	checks := []Check{
		{Name: "polled", Kind: "env", URL: "present", Required: true},
	}

	err := RunWithPoll(context.Background(), checks, []string{"polled"}, 2, 50*time.Millisecond)
	assert.NoError(t, err)
}

func TestRunWithPoll_FailedRequired(t *testing.T) {
	checks := []Check{
		{Name: "fail-tcp", Kind: "tcp", URL: "tcp://127.0.0.1:19999", Required: true, Timeout: 50 * time.Millisecond},
	}

	err := RunWithPoll(context.Background(), checks, nil, 0, 0)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "fail-tcp")
}

func TestDefaultPollCheckNames(t *testing.T) {
	names := DefaultPollCheckNames()
	require.Len(t, names, 1)
	assert.Equal(t, "temporal-host", names[0])
}

func TestTcpCheck_MissingHost(t *testing.T) {
	ok, msg := tcpCheck(context.Background(), "://", 100*time.Millisecond)
	assert.False(t, ok)
	assert.NotEmpty(t, msg) // may be "missing host" or URL parse error depending on input
}

func TestTcpCheck_EmptyHost(t *testing.T) {
	// Use a scheme that won't cause a parse error but has no host
	ok, msg := tcpCheck(context.Background(), "tcp://", 100*time.Millisecond)
	assert.False(t, ok)
	assert.Equal(t, "missing host", msg)
}

func TestTcpCheck_MissingPort(t *testing.T) {
	ok, msg := tcpCheck(context.Background(), "unknown://somehost", 100*time.Millisecond)
	assert.False(t, ok)
	assert.Equal(t, "missing port", msg)
}

func TestTcpCheck_HostColonPort(t *testing.T) {
	ok, msg := tcpCheck(context.Background(), "127.0.0.1:19999", 50*time.Millisecond)
	assert.False(t, ok)
	assert.NotEmpty(t, msg)
}

func TestHttpCheck_InvalidURL(t *testing.T) {
	ok, msg := httpCheck(context.Background(), "://invalid", "/health", time.Second)
	assert.False(t, ok)
	assert.NotEmpty(t, msg)
}

func TestGetEnv_Fallback(t *testing.T) {
	result := getEnv("NONEXISTENT_TEST_VAR_PREFLIGHT_XYZ", "fallback")
	assert.Equal(t, "fallback", result)
}
