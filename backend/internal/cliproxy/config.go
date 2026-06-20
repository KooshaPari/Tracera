// Package cliproxy provides cliproxy functionality.
package cliproxy

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"gopkg.in/yaml.v3"
)

// isValidConfigPath validates that the config path is safe (absolute and within expected directories)
func isValidConfigPath(path string) error {
	// Path must be absolute
	if !filepath.IsAbs(path) {
		return fmt.Errorf("config path must be absolute: %s", path)
	}
	// Path must have a safe basename (no special characters that could cause issues)
	base := filepath.Base(path)
	if strings.Contains(base, "..") || strings.Contains(base, "/") || strings.Contains(base, "\\") {
		return fmt.Errorf("config path contains invalid characters: %s", path)
	}
	// Path should have a safe extension
	if filepath.Ext(path) != ".yaml" && filepath.Ext(path) != ".yml" {
		return fmt.Errorf("config file must have .yaml or .yml extension: %s", path)
	}
	return nil
}

type configFile struct {
	Server struct {
		Host string `yaml:"host"`
		Port int    `yaml:"port"`
	} `yaml:"server"`
	DefaultProvider string `yaml:"defaultProvider"`
	Providers       []struct {
		Name         string `yaml:"name"`
		Type         string `yaml:"type"`
		ClientID     string `yaml:"clientId"`
		ClientSecret string `yaml:"clientSecret"`
		RedirectURI  string `yaml:"redirectUri"`
		BaseURL      string `yaml:"baseUrl"`
	} `yaml:"providers"`
}

// LoadConfig loads CLIProxy configuration from a YAML file
func LoadConfig(path string) (*Config, error) {
	if err := isValidConfigPath(path); err != nil {
		return nil, fmt.Errorf("invalid config path: %w", err)
	}
	data, err := os.ReadFile(filepath.Clean(path))
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	// Expand environment variables in the YAML content
	expanded := expandEnvVars(string(data))

	var raw configFile
	if err := yaml.Unmarshal([]byte(expanded), &raw); err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	return buildConfigFromFile(&raw), nil
}

func buildConfigFromFile(raw *configFile) *Config {
	cfg := &Config{
		Host:            raw.Server.Host,
		Port:            raw.Server.Port,
		DefaultProvider: raw.DefaultProvider,
		Providers:       filterProviders(raw.Providers),
	}

	normalizeDefaultProvider(cfg)
	return cfg
}

func filterProviders(rawProviders []struct {
	Name         string `yaml:"name"`
	Type         string `yaml:"type"`
	ClientID     string `yaml:"clientId"`
	ClientSecret string `yaml:"clientSecret"`
	RedirectURI  string `yaml:"redirectUri"`
	BaseURL      string `yaml:"baseUrl"`
},
) []ProviderConfig {
	providers := make([]ProviderConfig, 0, len(rawProviders))
	for _, provider := range rawProviders {
		if provider.ClientID == "" {
			continue
		}
		providers = append(providers, ProviderConfig{
			Name:         provider.Name,
			Type:         provider.Type,
			ClientID:     provider.ClientID,
			ClientSecret: provider.ClientSecret,
			RedirectURI:  provider.RedirectURI,
			BaseURL:      provider.BaseURL,
		})
	}
	return providers
}

func normalizeDefaultProvider(cfg *Config) {
	if len(cfg.Providers) == 0 {
		cfg.DefaultProvider = ""
		return
	}

	for _, p := range cfg.Providers {
		if p.Name == cfg.DefaultProvider {
			return
		}
	}

	cfg.DefaultProvider = cfg.Providers[0].Name
}

// LoadConfigFromEnv loads CLIProxy configuration from environment variables
func LoadConfigFromEnv() *Config {
	host := getEnvOrDefault("CLIPROXY_HOST", "127.0.0.1")
	portStr := getEnvOrDefault("CLIPROXY_PORT", "8765")
	port, err := strconv.Atoi(portStr)
	if err != nil {
		port = 8765
	}
	defaultProvider := getEnvOrDefault("CLIPROXY_DEFAULT_PROVIDER", "claude")

	cfg := &Config{
		Host:            host,
		Port:            port,
		DefaultProvider: defaultProvider,
		Providers:       []ProviderConfig{},
	}

	// Add Claude provider if configured
	if clientID := os.Getenv("CLAUDE_OAUTH_CLIENT_ID"); clientID != "" {
		cfg.Providers = append(cfg.Providers, ProviderConfig{
			Name:         "claude",
			Type:         "anthropic",
			ClientID:     clientID,
			ClientSecret: os.Getenv("CLAUDE_OAUTH_CLIENT_SECRET"),
			RedirectURI:  getEnvOrDefault("CLAUDE_OAUTH_REDIRECT_URI", "http://localhost:8765/oauth/callback"),
			BaseURL:      getEnvOrDefault("CLAUDE_OAUTH_BASE_URL", "https://api.anthropic.com"),
		})
	}

	// Add Codex provider if configured
	if clientID := os.Getenv("CODEX_OAUTH_CLIENT_ID"); clientID != "" {
		cfg.Providers = append(cfg.Providers, ProviderConfig{
			Name:         "codex",
			Type:         "openai-codex",
			ClientID:     clientID,
			ClientSecret: os.Getenv("CODEX_OAUTH_CLIENT_SECRET"),
			RedirectURI:  getEnvOrDefault("CODEX_OAUTH_REDIRECT_URI", "http://localhost:8765/oauth/callback"),
			BaseURL:      getEnvOrDefault("CODEX_OAUTH_BASE_URL", "https://api.openai.com"),
		})
	}

	// Add OpenAI provider if configured
	if clientID := os.Getenv("OPENAI_OAUTH_CLIENT_ID"); clientID != "" {
		cfg.Providers = append(cfg.Providers, ProviderConfig{
			Name:         "openai",
			Type:         "openai",
			ClientID:     clientID,
			ClientSecret: os.Getenv("OPENAI_OAUTH_CLIENT_SECRET"),
			RedirectURI:  getEnvOrDefault("OPENAI_OAUTH_REDIRECT_URI", "http://localhost:8765/oauth/callback"),
			BaseURL:      getEnvOrDefault("OPENAI_OAUTH_BASE_URL", "https://api.openai.com"),
		})
	}

	return cfg
}

// expandEnvVars expands ${VAR} and $VAR in the string
func expandEnvVars(s string) string {
	return os.Expand(s, os.Getenv)
}

// getEnvOrDefault gets an environment variable or returns a default value
func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// Validate checks if the configuration is valid
func (config *Config) Validate() error {
	if err := validateHost(config.Host); err != nil {
		return err
	}
	if err := validatePort(config.Port); err != nil {
		return err
	}
	providerNames, err := validateProviders(config.Providers)
	if err != nil {
		return err
	}
	if err := validateDefaultProvider(config.DefaultProvider, providerNames); err != nil {
		return err
	}
	return nil
}

func validateHost(host string) error {
	if host == "" {
		return errors.New("host cannot be empty")
	}
	return nil
}

func validatePort(port int) error {
	if port <= 0 || port > 65535 {
		return fmt.Errorf("invalid port: %d", port)
	}
	return nil
}

func validateProviders(providers []ProviderConfig) (map[string]bool, error) {
	if len(providers) == 0 {
		return nil, errors.New("at least one provider must be configured")
	}

	providerNames := make(map[string]bool)
	for i, provider := range providers {
		if err := validateProvider(i, provider, providerNames); err != nil {
			return nil, err
		}
		providerNames[provider.Name] = true
	}

	return providerNames, nil
}

func validateProvider(index int, provider ProviderConfig, providerNames map[string]bool) error {
	if provider.Name == "" {
		return fmt.Errorf("provider %d: name cannot be empty", index)
	}
	if providerNames[provider.Name] {
		return fmt.Errorf("duplicate provider name: %s", provider.Name)
	}
	if provider.Type == "" {
		return fmt.Errorf("provider %s: type cannot be empty", provider.Name)
	}
	if provider.ClientID == "" {
		return fmt.Errorf("provider %s: client_id cannot be empty", provider.Name)
	}
	if provider.ClientSecret == "" {
		return fmt.Errorf("provider %s: client_secret cannot be empty", provider.Name)
	}
	if provider.RedirectURI == "" {
		return fmt.Errorf("provider %s: redirect_uri cannot be empty", provider.Name)
	}
	return nil
}

func validateDefaultProvider(defaultProvider string, providerNames map[string]bool) error {
	if defaultProvider == "" {
		return errors.New("default provider cannot be empty")
	}
	if !providerNames[defaultProvider] {
		return fmt.Errorf("default provider %s not found in providers list", defaultProvider)
	}
	return nil
}

// String returns a safe string representation (without secrets)
func (config *Config) String() string {
	var builder strings.Builder
	builder.WriteString("CLIProxy Config:\n")
	builder.WriteString("  Host: " + config.Host + "\n")
	builder.WriteString(fmt.Sprintf("  Port: %d\n", config.Port))
	builder.WriteString("  Default Provider: " + config.DefaultProvider + "\n")
	builder.WriteString("  Providers:\n")

	for _, p := range config.Providers {
		builder.WriteString(fmt.Sprintf("    - %s (%s)\n", p.Name, p.Type))
	}

	return builder.String()
}
