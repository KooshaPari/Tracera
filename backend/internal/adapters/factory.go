// Package adapters provides integration adapter factories.
package adapters

import (
	"errors"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/kooshapari/tracertm-backend/internal/realtime"
	"github.com/nats-io/nats.go"
	"gorm.io/gorm"
)

// AdapterConfig holds configuration for all adapters
type AdapterConfig struct {
	// Auth provider selection: currently only "authkit" (WorkOS).
	AuthProvider string

	// AuthKit (WorkOS) configuration
	AuthKitSecret  string        // WorkOS JWT secret for HS256 service tokens (fallback)
	WorkOSClientID string        // WorkOS Client ID for JWKS URL construction (RS256 access tokens)
	DBPool         *pgxpool.Pool // Legacy; prefer GormDB for AuthKit
	GormDB         *gorm.DB      // GORM DB for AuthKit profile management (public.profiles)

	// Realtime configuration
	RealtimeProvider string // "nats" (Supabase removed)
	NATSConn         *nats.Conn
}

// AdapterFactory creates and manages all adapters
type AdapterFactory struct {
	config AdapterConfig

	// Adapters
	authProvider        auth.Provider
	realtimeBroadcaster realtime.Broadcaster
}

// NewAdapterFactory creates a new adapter factory
func NewAdapterFactory(config AdapterConfig) (*AdapterFactory, error) {
	factory := &AdapterFactory{
		config: config,
	}

	// Initialize auth provider
	if err := factory.initAuthProvider(); err != nil {
		return nil, fmt.Errorf("failed to initialize auth provider: %w", err)
	}

	// Initialize realtime broadcaster
	if err := factory.initRealtimeBroadcaster(); err != nil {
		return nil, fmt.Errorf("failed to initialize realtime broadcaster: %w", err)
	}

	return factory, nil
}

// initAuthProvider initializes the auth provider based on configuration.
func (factory *AdapterFactory) initAuthProvider() error {
	switch factory.config.AuthProvider {
	case "", "authkit":
		if factory.config.GormDB == nil {
			return errors.New("GORM DB required for AuthKit adapter (for public.profiles management)")
		}
		if factory.config.WorkOSClientID == "" {
			return errors.New("WorkOS Client ID required for AuthKit adapter (for JWKS validation)")
		}
		// AuthKitSecret is optional - used for HS256 service tokens (fallback)
		// WorkOS access tokens use RS256 and are validated via JWKS
		factory.authProvider = auth.NewKitAdapter(
			factory.config.WorkOSClientID,
			factory.config.AuthKitSecret,
			factory.config.GormDB,
		)
		return nil

	default:
		return fmt.Errorf("unknown auth provider: %s", factory.config.AuthProvider)
	}
}

// initRealtimeBroadcaster initializes the realtime broadcaster based on configuration
func (factory *AdapterFactory) initRealtimeBroadcaster() error {
	switch factory.config.RealtimeProvider {
	case "nats":
		if factory.config.NATSConn == nil {
			return errors.New("NATS connection required for realtime provider")
		}
		factory.realtimeBroadcaster = realtime.NewNATSRealtimeAdapter(factory.config.NATSConn)
		return nil

	case "":
		return errors.New("Realtime provider is required (set REALTIME_PROVIDER=nats)")

	default:
		return fmt.Errorf(
			"unknown realtime provider: %s (valid option: 'nats')",
			factory.config.RealtimeProvider,
		)
	}
}

// GetAuthProvider returns the auth provider
func (factory *AdapterFactory) GetAuthProvider() auth.Provider {
	return factory.authProvider
}

// GetRealtimeBroadcaster returns the realtime broadcaster
func (factory *AdapterFactory) GetRealtimeBroadcaster() realtime.Broadcaster {
	return factory.realtimeBroadcaster
}

// Close closes all adapters
func (factory *AdapterFactory) Close() error {
	if factory.authProvider != nil {
		if err := factory.authProvider.Close(); err != nil {
			log.Printf("Error closing auth provider: %v", err)
		}
	}

	if factory.realtimeBroadcaster != nil {
		if err := factory.realtimeBroadcaster.Close(); err != nil {
			log.Printf("Error closing realtime broadcaster: %v", err)
		}
	}

	log.Println("Adapter factory closed")
	return nil
}
