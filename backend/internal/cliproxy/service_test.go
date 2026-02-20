package cliproxy

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

const (
	serviceRunStartupDelay    = 100 * time.Millisecond
	serviceRunShutdownTimeout = 2 * time.Second
)

func TestNewService(t *testing.T) {
	cfg := &Config{
		Host:            "127.0.0.1",
		Port:            8765,
		DefaultProvider: "claude",
		Providers: []ProviderConfig{
			{
				Name:         "claude",
				Type:         "anthropic",
				ClientID:     "test_client_id",
				ClientSecret: "test_client_secret",
				RedirectURI:  "http://localhost:8765/oauth/callback",
				BaseURL:      "https://api.anthropic.com",
			},
		},
	}

	service, err := NewService(cfg)
	if err != nil {
		t.Fatalf("Failed to create service: %v", err)
	}

	if service == nil {
		t.Fatal("Service is nil")
	}

	if service.config != cfg {
		t.Error("Config not set correctly")
	}
}

func TestConfigValidation(t *testing.T) {
	for _, tt := range configValidationCases() {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.config.Validate()
			if (err != nil) != tt.wantErr {
				t.Errorf("Config.Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

type configValidationCase struct {
	name    string
	config  *Config
	wantErr bool
}

func configValidationCases() []configValidationCase {
	return []configValidationCase{
		{
			name:    "valid config",
			config:  validConfig(),
			wantErr: false,
		},
		{
			name:    "missing host",
			config:  configWithHost(""),
			wantErr: true,
		},
		{
			name:    "invalid port",
			config:  configWithPort(0),
			wantErr: true,
		},
		{
			name:    "no providers",
			config:  configWithProviders([]ProviderConfig{}),
			wantErr: true,
		},
		{
			name:    "missing provider name",
			config:  configWithProviderName(""),
			wantErr: true,
		},
		{
			name:    "default provider not found",
			config:  configWithDefaultProvider("nonexistent"),
			wantErr: true,
		},
	}
}

func validConfig() *Config {
	return &Config{
		Host:            "127.0.0.1",
		Port:            8765,
		DefaultProvider: "claude",
		Providers: []ProviderConfig{
			{
				Name:         "claude",
				Type:         "anthropic",
				ClientID:     "test_id",
				ClientSecret: "test_secret",
				RedirectURI:  "http://localhost:8765/oauth/callback",
			},
		},
	}
}

func configWithHost(host string) *Config {
	cfg := validConfig()
	cfg.Host = host
	return cfg
}

func configWithPort(port int) *Config {
	cfg := validConfig()
	cfg.Port = port
	return cfg
}

func configWithProviders(providers []ProviderConfig) *Config {
	cfg := validConfig()
	cfg.Providers = providers
	return cfg
}

func configWithProviderName(name string) *Config {
	cfg := validConfig()
	if len(cfg.Providers) > 0 {
		cfg.Providers[0].Name = name
	}
	return cfg
}

func configWithDefaultProvider(name string) *Config {
	cfg := validConfig()
	cfg.DefaultProvider = name
	return cfg
}

func TestGetProvider(t *testing.T) {
	cfg := &Config{
		Host:            "127.0.0.1",
		Port:            8765,
		DefaultProvider: "claude",
		Providers: []ProviderConfig{
			{
				Name:         "claude",
				Type:         "anthropic",
				ClientID:     "claude_id",
				ClientSecret: "claude_secret",
				RedirectURI:  "http://localhost:8765/oauth/callback",
			},
			{
				Name:         "codex",
				Type:         "openai-codex",
				ClientID:     "codex_id",
				ClientSecret: "codex_secret",
				RedirectURI:  "http://localhost:8765/oauth/callback",
			},
		},
	}

	service, err := NewService(cfg)
	require.NoError(t, err)

	tests := []struct {
		name         string
		providerName string
		wantFound    bool
	}{
		{"found claude", "claude", true},
		{"found codex", "codex", true},
		{"not found", "nonexistent", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			provider := service.getProvider(tt.providerName)
			if (provider != nil) != tt.wantFound {
				t.Errorf("getProvider() found = %v, want %v", provider != nil, tt.wantFound)
			}
		})
	}
}

func TestDetermineProvider(t *testing.T) {
	cfg := &Config{
		Host:            "127.0.0.1",
		Port:            8765,
		DefaultProvider: "claude",
		Providers: []ProviderConfig{
			{Name: "claude", Type: "anthropic"},
			{Name: "codex", Type: "openai-codex"},
		},
	}

	service, err := NewService(cfg)
	require.NoError(t, err)

	tests := []struct {
		name     string
		req      map[string]interface{}
		expected string
	}{
		{
			name:     "claude model",
			req:      map[string]interface{}{"model": "claude-sonnet-4"},
			expected: "claude",
		},
		{
			name:     "codex model",
			req:      map[string]interface{}{"model": "gpt-5.2-codex"},
			expected: "codex",
		},
		{
			name:     "no model - use default",
			req:      map[string]interface{}{},
			expected: "claude",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			provider := service.determineProvider(tt.req)
			if provider != tt.expected {
				t.Errorf("determineProvider() = %v, want %v", provider, tt.expected)
			}
		})
	}
}

func TestServiceRunAndShutdown(t *testing.T) {
	cfg := &Config{
		Host:            "127.0.0.1",
		Port:            18765, // Use different port to avoid conflicts
		DefaultProvider: "claude",
		Providers: []ProviderConfig{
			{
				Name:         "claude",
				Type:         "anthropic",
				ClientID:     "test_id",
				ClientSecret: "test_secret",
				RedirectURI:  "http://localhost:18765/oauth/callback",
			},
		},
	}

	service, err := NewService(cfg)
	if err != nil {
		t.Fatalf("Failed to create service: %v", err)
	}

	ctx, cancel := context.WithCancel(context.Background())

	// Start service in goroutine
	errChan := make(chan error, 1)
	go func() {
		errChan <- service.Run(ctx)
	}()

	// Give it time to start
	time.Sleep(serviceRunStartupDelay)

	// Cancel context to trigger shutdown
	cancel()

	// Wait for service to stop
	select {
	case err := <-errChan:
		if err != nil && !errors.Is(err, context.Canceled) {
			t.Errorf("Service.Run() error = %v", err)
		}
	case <-time.After(serviceRunShutdownTimeout):
		t.Error("Service did not stop in time")
	}
}

func TestLoadConfigFromEnv(t *testing.T) {
	// Set test environment variables
	t.Setenv("CLIPROXY_HOST", "192.168.1.1")
	t.Setenv("CLIPROXY_PORT", "9999")
	t.Setenv("CLIPROXY_DEFAULT_PROVIDER", "test-provider")
	t.Setenv("CLAUDE_OAUTH_CLIENT_ID", "test_claude_id")
	t.Setenv("CLAUDE_OAUTH_CLIENT_SECRET", "test_claude_secret")

	cfg := LoadConfigFromEnv()

	if cfg.Host != "192.168.1.1" {
		t.Errorf("Host = %v, want %v", cfg.Host, "192.168.1.1")
	}

	if cfg.Port != 9999 {
		t.Errorf("Port = %v, want %v", cfg.Port, 9999)
	}

	if cfg.DefaultProvider != "test-provider" {
		t.Errorf("DefaultProvider = %v, want %v", cfg.DefaultProvider, "test-provider")
	}

	// Should have Claude provider configured
	claudeFound := false
	for _, p := range cfg.Providers {
		if p.Name == "claude" {
			claudeFound = true
			if p.ClientID != "test_claude_id" {
				t.Errorf("Claude ClientID = %v, want %v", p.ClientID, "test_claude_id")
			}
		}
	}

	if !claudeFound {
		t.Error("Claude provider not found in config")
	}
}

func TestConfigString(t *testing.T) {
	cfg := &Config{
		Host:            "127.0.0.1",
		Port:            8765,
		DefaultProvider: "claude",
		Providers: []ProviderConfig{
			{Name: "claude", Type: "anthropic"},
			{Name: "codex", Type: "openai-codex"},
		},
	}

	str := cfg.String()

	// Verify string contains expected information (but not secrets)
	expectedSubstrings := []string{
		"CLIProxy Config",
		"127.0.0.1",
		"8765",
		"claude",
		"anthropic",
		"codex",
	}

	for _, substr := range expectedSubstrings {
		if !containsSubstring(str, substr) {
			t.Errorf("Config.String() missing expected substring: %s", substr)
		}
	}

	// Should NOT contain secrets
	if containsSubstring(str, "client_secret") || containsSubstring(str, "client_id") {
		t.Error("Config.String() should not expose secrets")
	}
}

func containsSubstring(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > len(substr) && findSubstring(s, substr))
}

func findSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
