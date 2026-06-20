// Package sentry provides error tracking and monitoring integration for TraceRTM backend
package sentry

import (
	"fmt"
	"log/slog"
	"time"

	"github.com/getsentry/sentry-go"
)

const (
	sentryFlushTimeout        = 2 * time.Second
	sentryTraceSampleProdRate = 0.1
	sentryTraceSampleDevRate  = 1.0
)

// Config holds Sentry configuration
type Config struct {
	DSN              string
	Environment      string
	Release          string
	TracesSampleRate float64
	Debug            bool
}

// Initialize initializes Sentry error tracking
//
// Only initializes if DSN is provided. Includes performance monitoring
// and automatic error capture.
// applySentryDefaults fills in zero-valued config fields with defaults.
func applySentryDefaults(cfg *Config) {
	if cfg.Environment == "" {
		cfg.Environment = "development"
	}
	if cfg.Release == "" {
		cfg.Release = "unknown"
	}
	if cfg.TracesSampleRate == 0 {
		if cfg.Environment == "production" {
			cfg.TracesSampleRate = sentryTraceSampleProdRate
		} else {
			cfg.TracesSampleRate = sentryTraceSampleDevRate
		}
	}
}

// sentryBeforeSend filters out known non-critical errors (context cancelled, EOF).
func sentryBeforeSend(event *sentry.Event, hint *sentry.EventHint) *sentry.Event {
	if hint.OriginalException != nil {
		errMsg := fmt.Sprint(hint.OriginalException)
		if errMsg == "context canceled" || errMsg == "context deadline exceeded" || errMsg == "EOF" {
			return nil
		}
	}
	return event
}

// Initialize sets up Sentry error reporting with the given configuration.
func Initialize(cfg Config) error {
	if cfg.DSN == "" {
		slog.Warn("[Sentry] Skipping initialization (no DSN provided)")
		return nil
	}

	applySentryDefaults(&cfg)

	err := sentry.Init(sentry.ClientOptions{
		Dsn:              cfg.DSN,
		Environment:      cfg.Environment,
		Release:          cfg.Release,
		Debug:            cfg.Debug,
		TracesSampleRate: cfg.TracesSampleRate,
		EnableTracing:    true,
		BeforeSend:       sentryBeforeSend,
	})
	if err != nil {
		return fmt.Errorf("failed to initialize Sentry: %w", err)
	}

	slog.Info("[Sentry] Initialized for environment (release )", "detail", cfg.Environment, "detail", cfg.Release)
	return nil
}

// Close flushes any buffered events and shuts down Sentry
func Close() {
	sentry.Flush(sentryFlushTimeout)
}

// CaptureException captures an exception and sends it to Sentry
func CaptureException(err error) {
	sentry.CaptureException(err)
}

// CaptureMessage captures a message and sends it to Sentry
func CaptureMessage(message string) {
	sentry.CaptureMessage(message)
}

// SetUser sets user context for error tracking
func SetUser(userID, email, username string) {
	sentry.ConfigureScope(func(scope *sentry.Scope) {
		scope.SetUser(sentry.User{
			ID:       userID,
			Email:    email,
			Username: username,
		})
	})
}

// ClearUser clears user context
func ClearUser() {
	sentry.ConfigureScope(func(scope *sentry.Scope) {
		scope.SetUser(sentry.User{})
	})
}

// SetContext sets custom context for error tracking
func SetContext(key string, value map[string]interface{}) {
	sentry.ConfigureScope(func(scope *sentry.Scope) {
		scope.SetContext(key, value)
	})
}

// AddBreadcrumb adds a breadcrumb for debugging
func AddBreadcrumb(message, category string, level sentry.Level) {
	sentry.AddBreadcrumb(&sentry.Breadcrumb{
		Message:   message,
		Category:  category,
		Level:     level,
		Timestamp: time.Now(),
	})
}

// WithScope runs a function with a custom Sentry scope
func WithScope(f func(*sentry.Scope)) {
	sentry.WithScope(f)
}

// RecoverAndCapture recovers from panics and captures them in Sentry
func RecoverAndCapture() {
	if err := recover(); err != nil {
		sentry.CurrentHub().Recover(err)
		sentry.Flush(sentryFlushTimeout)
		panic(err) // Re-panic after capturing
	}
}
