// Package env provides environment variable helpers.
package env

import (
	"fmt"
	"log/slog"
	"os"
	"strconv"
	"strings"
	"time"
)

const envSplitParts = 2

// Manager handles environment variable loading and validation
type Manager struct {
	vars map[string]string
}

// New creates a new environment manager
func New() *Manager {
	return &Manager{
		vars: make(map[string]string),
	}
}

// Load loads all environment variables into the manager
func (m *Manager) Load() {
	for _, env := range os.Environ() {
		parts := strings.SplitN(env, "=", envSplitParts)
		if len(parts) == envSplitParts {
			m.vars[parts[0]] = parts[1]
		}
	}
}

// Get retrieves a string environment variable
func (m *Manager) Get(key string) string {
	if val, exists := m.vars[key]; exists {
		return val
	}
	return os.Getenv(key)
}

// GetRequired retrieves a required string environment variable
func (m *Manager) GetRequired(key string) (string, error) {
	val := m.Get(key)
	if val == "" {
		return "", fmt.Errorf("required environment variable %s not set", key)
	}
	return val, nil
}

// GetOrDefault retrieves a string environment variable with a default value
func (m *Manager) GetOrDefault(key, defaultValue string) string {
	val := m.Get(key)
	if val == "" {
		return defaultValue
	}
	return val
}

// GetInt retrieves an integer environment variable
func (m *Manager) GetInt(key string) (int, error) {
	val := m.Get(key)
	if val == "" {
		return 0, fmt.Errorf("environment variable %s not set", key)
	}
	intVal, err := strconv.Atoi(val)
	if err != nil {
		return 0, fmt.Errorf("environment variable %s is not a valid integer: %w", key, err)
	}
	return intVal, nil
}

// GetIntOrDefault retrieves an integer environment variable with a default value
func (m *Manager) GetIntOrDefault(key string, defaultValue int) int {
	val, err := m.GetInt(key)
	if err != nil {
		return defaultValue
	}
	return val
}

// GetBool retrieves a boolean environment variable
func (m *Manager) GetBool(key string) (bool, error) {
	val := m.Get(key)
	if val == "" {
		return false, fmt.Errorf("environment variable %s not set", key)
	}
	boolVal, err := strconv.ParseBool(val)
	if err != nil {
		return false, fmt.Errorf("environment variable %s is not a valid boolean: %w", key, err)
	}
	return boolVal, nil
}

// GetBoolOrDefault retrieves a boolean environment variable with a default value
func (m *Manager) GetBoolOrDefault(key string, defaultValue bool) bool {
	val, err := m.GetBool(key)
	if err != nil {
		return defaultValue
	}
	return val
}

// GetDuration retrieves a duration environment variable
func (m *Manager) GetDuration(key string) (time.Duration, error) {
	val := m.Get(key)
	if val == "" {
		return 0, fmt.Errorf("environment variable %s not set", key)
	}
	duration, err := time.ParseDuration(val)
	if err != nil {
		return 0, fmt.Errorf("environment variable %s is not a valid duration: %w", key, err)
	}
	return duration, nil
}

// GetDurationOrDefault retrieves a duration environment variable with a default value
func (m *Manager) GetDurationOrDefault(key string, defaultValue time.Duration) time.Duration {
	val, err := m.GetDuration(key)
	if err != nil {
		return defaultValue
	}
	return val
}

// Set sets an environment variable
func (m *Manager) Set(key, value string) {
	m.vars[key] = value
	if err := os.Setenv(key, value); err != nil {
		slog.Error("error setting environment variable", "error", key, "error", err)
	}
}

// Validate validates that all required variables are set
func (m *Manager) Validate(requiredVars []string) error {
	var missing []string
	for _, key := range requiredVars {
		if m.Get(key) == "" {
			missing = append(missing, key)
		}
	}
	if len(missing) > 0 {
		return fmt.Errorf("missing required environment variables: %s", strings.Join(missing, ", "))
	}
	return nil
}
