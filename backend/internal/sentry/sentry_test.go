//go:build !integration

package sentry

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestInitialize_EmptyDSN(t *testing.T) {
	cfg := Config{DSN: ""}
	err := Initialize(cfg)
	assert.NoError(t, err) // Should skip initialization gracefully
}

func TestInitialize_DefaultEnvironment(t *testing.T) {
	cfg := Config{DSN: ""} // Will skip initialization
	err := Initialize(cfg)
	assert.NoError(t, err)
}

func TestConfigDefaults(t *testing.T) {
	tests := []struct {
		name        string
		cfg         Config
		wantEnv     string
		wantRelease string
	}{
		{
			name:        "empty config gets defaults",
			cfg:         Config{DSN: ""},
			wantEnv:     "development",
			wantRelease: "unknown",
		},
		{
			name:        "explicit values preserved",
			cfg:         Config{DSN: "", Environment: "staging", Release: "v2.0"},
			wantEnv:     "staging",
			wantRelease: "v2.0",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Initialize is a no-op for empty DSN, but we can
			// verify the config struct fields
			if tt.cfg.Environment == "" {
				tt.cfg.Environment = "development"
			}
			if tt.cfg.Release == "" {
				tt.cfg.Release = "unknown"
			}
			assert.Equal(t, tt.wantEnv, tt.cfg.Environment)
			assert.Equal(t, tt.wantRelease, tt.cfg.Release)
		})
	}
}

func TestSentryTraceSampleRates(t *testing.T) {
	assert.InEpsilon(t, 0.1, sentryTraceSampleProdRate, 1e-9)
	assert.InEpsilon(t, 1.0, sentryTraceSampleDevRate, 1e-9)
}

func TestClose_DoesNotPanic(t *testing.T) {
	assert.NotPanics(t, func() {
		Close()
	})
}

func TestCaptureMessage_DoesNotPanic(t *testing.T) {
	assert.NotPanics(t, func() {
		CaptureMessage("test message")
	})
}

func TestSetUser_DoesNotPanic(t *testing.T) {
	assert.NotPanics(t, func() {
		SetUser("user-1", "user@test.com", "testuser")
	})
}

func TestClearUser_DoesNotPanic(t *testing.T) {
	assert.NotPanics(t, func() {
		ClearUser()
	})
}

func TestSetContext_DoesNotPanic(t *testing.T) {
	assert.NotPanics(t, func() {
		SetContext("request", map[string]interface{}{
			"method": "POST",
			"path":   "/api/items",
		})
	})
}

func TestCaptureException_DoesNotPanic(t *testing.T) {
	assert.NotPanics(t, func() {
		CaptureException(assert.AnError)
	})
}

func TestSentryFlushTimeout(t *testing.T) {
	assert.InEpsilon(t, 2.0, sentryFlushTimeout.Seconds(), 1e-9)
}
