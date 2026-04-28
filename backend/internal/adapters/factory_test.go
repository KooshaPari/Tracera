//go:build !integration && !e2e

package adapters

import (
	"strings"
	"testing"

	"github.com/nats-io/nats.go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/kooshapari/tracertm-backend/internal/realtime"
)

// testGormDB returns a minimal *gorm.DB for adapter tests (in-memory sqlite).
func testGormDB(t *testing.T) *gorm.DB {
	t.Helper()
	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	require.NoError(t, err)
	return db
}

// TestNewAdapterFactory_AuthProviderSupabaseIsRemoved verifies that Supabase auth provider is no longer supported
func TestNewAdapterFactory_AuthProviderSupabaseIsRemoved(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "supabase",
		AuthKitSecret:    "",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory, err := NewAdapterFactory(cfg)
	if factory != nil {
		require.NoError(t, factory.Close())
	}

	require.Error(t, err)
	assert.Contains(t, err.Error(), "unknown auth provider")
}

// TestInitAuthProvider_AuthKit_Succeeds verifies AuthKit initialization succeeds
func TestInitAuthProvider_AuthKit_Succeeds(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "authkit",
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "",
		NATSConn:         nil,
	}

	factory := &AdapterFactory{config: cfg}
	err := factory.initAuthProvider()
	require.NoError(t, err)

	require.NotNil(t, factory.authProvider)
	_, ok := factory.authProvider.(*auth.KitAdapter)
	assert.True(t, ok, "expected authProvider to be *auth.KitAdapter")
}

type authProviderCreationCase struct {
	name          string
	config        AdapterConfig
	expectError   bool
	errorContains string
	providerType  string
}

func authProviderCreationCases(t *testing.T) []authProviderCreationCase {
	t.Helper()
	return []authProviderCreationCase{
		{
			name: "AuthKit with valid config",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "valid-secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         nil,
			},
			providerType: "authkit",
		},
		{
			name: "AuthKit with missing WorkOS Client ID",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "valid-secret",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         nil,
			},
			expectError:   true,
			errorContains: "WorkOS Client ID required",
		},
		{
			name: "AuthKit with missing GORM DB",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "valid-secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "nats",
				NATSConn:         nil,
			},
			expectError:   true,
			errorContains: "gorm DB required",
		},
		{
			name: "Supabase auth removed",
			config: AdapterConfig{
				AuthProvider:     "supabase",
				AuthKitSecret:    "",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
			expectError:   true,
			errorContains: "unknown auth provider",
		},
		{
			name: "Unknown auth provider",
			config: AdapterConfig{
				AuthProvider:     "unknown",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "nats",
				NATSConn:         nil,
			},
			expectError:   true,
			errorContains: "unknown auth provider",
		},
	}
}

func runAuthProviderCreationCase(t *testing.T, tc authProviderCreationCase) {
	t.Helper()
	factory := &AdapterFactory{config: tc.config}
	err := factory.initAuthProvider()

	if tc.expectError {
		require.Error(t, err)
		assert.Contains(t, err.Error(), tc.errorContains)
		return
	}

	require.NoError(t, err)
	assert.NotNil(t, factory.authProvider)
}

// TestAdapterFactory_AuthProvider_Creation verifies auth provider creation
func TestAdapterFactory_AuthProvider_Creation(t *testing.T) {
	for _, tc := range authProviderCreationCases(t) {
		t.Run(tc.name, func(t *testing.T) {
			runAuthProviderCreationCase(t, tc)
		})
	}
}

// TestAdapterFactory_AuthProvider_Switching verifies switching between auth providers
func TestAdapterFactory_AuthProvider_Switching(t *testing.T) {
	// Create factory with AuthKit
	cfg := AdapterConfig{
		AuthProvider:     "authkit",
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         nil,
	}

	factory := &AdapterFactory{config: cfg}
	err := factory.initAuthProvider()
	require.NoError(t, err)
	require.NotNil(t, factory.authProvider)

	// Verify it's AuthKit
	_, ok := factory.authProvider.(*auth.KitAdapter)
	assert.True(t, ok)

	// Close the factory
	err = factory.Close()
	require.NoError(t, err)

	// Create a new factory with empty provider (defaults to AuthKit)
	cfg2 := AdapterConfig{
		AuthProvider:     "", // Empty defaults to authkit
		AuthKitSecret:    "test-secret-2",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         nil,
	}

	factory2 := &AdapterFactory{config: cfg2}
	err = factory2.initAuthProvider()
	require.NoError(t, err)
	require.NotNil(t, factory2.authProvider)

	// Verify it's still AuthKit
	_, ok = factory2.authProvider.(*auth.KitAdapter)
	assert.True(t, ok)

	if err := factory2.Close(); err != nil {
		t.Logf("close error: %v", err)
	}
}

// TestAdapterFactory_AuthProvider_InvalidConfig verifies invalid config handling
func TestAdapterFactory_AuthProvider_InvalidConfig(t *testing.T) {
	tests := []struct {
		name          string
		config        AdapterConfig
		errorContains string
	}{
		{
			name: "Missing WorkOS Client ID",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "secret",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "",
				NATSConn:         nil,
			},
			errorContains: "WorkOS Client ID required",
		},
		{
			name: "Missing GORM DB",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "",
				NATSConn:         nil,
			},
			errorContains: "gorm DB required",
		},
		{
			name: "Invalid provider name",
			config: AdapterConfig{
				AuthProvider:     "invalid-provider",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "",
				NATSConn:         nil,
			},
			errorContains: "unknown auth provider",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			factory := &AdapterFactory{config: tt.config}
			err := factory.initAuthProvider()
			require.Error(t, err)
			assert.Contains(t, err.Error(), tt.errorContains)
		})
	}
}

// TestAdapterFactory_RealtimeProvider_Creation verifies realtime provider creation
func TestAdapterFactory_RealtimeProvider_Creation(t *testing.T) {
	tests := []struct {
		name          string
		config        AdapterConfig
		expectError   bool
		errorContains string
		providerType  string
	}{
		{
			name: "NATS with valid config",
			config: AdapterConfig{
				AuthProvider:     "",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
			expectError:  false,
			providerType: "nats",
		},
		{
			name: "NATS with missing connection",
			config: AdapterConfig{
				AuthProvider:     "",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "nats",
				NATSConn:         nil,
			},
			expectError:   true,
			errorContains: "NATS connection required",
		},
		{
			name: "Unknown realtime provider",
			config: AdapterConfig{
				AuthProvider:     "",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "unknown",
				NATSConn:         nil,
			},
			expectError:   true,
			errorContains: "unknown realtime provider",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			factory := &AdapterFactory{config: tt.config}
			err := factory.initRealtimeBroadcaster()

			if tt.expectError {
				require.Error(t, err)
				assert.Contains(t, err.Error(), tt.errorContains)
			} else {
				require.NoError(t, err)
				assert.NotNil(t, factory.realtimeBroadcaster)
			}
		})
	}
}

// TestAdapterFactory_RealtimeProvider_Switching verifies switching between realtime providers
func TestAdapterFactory_RealtimeProvider_Switching(t *testing.T) {
	// Create factory with NATS
	cfg1 := AdapterConfig{
		AuthProvider:     "",
		AuthKitSecret:    "",
		WorkOSClientID:   "",
		DBPool:           nil,
		GormDB:           nil,
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory1 := &AdapterFactory{config: cfg1}
	err := factory1.initRealtimeBroadcaster()
	require.NoError(t, err)
	require.NotNil(t, factory1.realtimeBroadcaster)

	// Verify it's NATS
	_, ok := factory1.realtimeBroadcaster.(*realtime.NATSRealtimeAdapter)
	assert.True(t, ok)

	if err := factory1.Close(); err != nil {
		t.Logf("close error: %v", err)
	}

	// Create factory with empty realtime provider (factory requires a provider)
	cfg2 := AdapterConfig{
		AuthProvider:     "",
		AuthKitSecret:    "",
		WorkOSClientID:   "",
		DBPool:           nil,
		GormDB:           nil,
		RealtimeProvider: "",
		NATSConn:         nil,
	}

	factory2 := &AdapterFactory{config: cfg2}
	err = factory2.initRealtimeBroadcaster()
	require.Error(t, err)
	assert.Contains(t, err.Error(), "realtime provider is required")

	if err := factory2.Close(); err != nil {
		t.Logf("close error: %v", err)
	}
}

// TestAdapterFactory_CacheProvider_Creation verifies cache provider handling
func TestAdapterFactory_CacheProvider_Creation(t *testing.T) {
	// Note: Currently the factory doesn't have a cache provider
	// This test documents expected behavior for future implementation
	cfg := AdapterConfig{
		AuthProvider:     "authkit",
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory := &AdapterFactory{config: cfg}

	// Initialize auth provider
	err := factory.initAuthProvider()
	require.NoError(t, err)

	// Initialize realtime provider
	err = factory.initRealtimeBroadcaster()
	require.NoError(t, err)

	// Verify both are initialized
	assert.NotNil(t, factory.authProvider)
	assert.NotNil(t, factory.realtimeBroadcaster)

	require.NoError(t, factory.Close())
}

// TestAdapterFactory_MultipleProviders_Independent verifies multiple providers work independently
func TestAdapterFactory_MultipleProviders_Independent(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "authkit",
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory := &AdapterFactory{config: cfg}

	// Initialize auth provider
	err := factory.initAuthProvider()
	require.NoError(t, err)
	assert.NotNil(t, factory.authProvider)

	// Initialize realtime provider
	err = factory.initRealtimeBroadcaster()
	require.NoError(t, err)
	assert.NotNil(t, factory.realtimeBroadcaster)

	// Verify they are different instances
	assert.NotEqual(t, factory.authProvider, factory.realtimeBroadcaster)

	// Verify both are accessible via getters
	authProvider := factory.GetAuthProvider()
	assert.NotNil(t, authProvider)

	realtimeBroadcaster := factory.GetRealtimeBroadcaster()
	assert.NotNil(t, realtimeBroadcaster)

	require.NoError(t, factory.Close())
}

// TestAdapterFactory_ProviderConfiguration_Validation verifies provider configuration validation
func TestAdapterFactory_ProviderConfiguration_Validation(t *testing.T) {
	for _, tc := range providerConfigValidationCases(t) {
		t.Run(tc.name, func(t *testing.T) {
			runProviderConfigValidationCase(t, tc)
		})
	}
}

// TestAdapterFactory_GetAuthProvider verifies GetAuthProvider returns correct instance
func TestAdapterFactory_GetAuthProvider(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "authkit",
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory, err := NewAdapterFactory(cfg)
	require.NoError(t, err)
	defer func() {
		require.NoError(t, factory.Close())
	}()

	provider := factory.GetAuthProvider()
	require.NotNil(t, provider)

	_, ok := provider.(*auth.KitAdapter)
	assert.True(t, ok, "expected AuthKit adapter")
}

// TestAdapterFactory_GetRealtimeBroadcaster verifies GetRealtimeBroadcaster returns correct instance
func TestAdapterFactory_GetRealtimeBroadcaster(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "authkit",
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory, err := NewAdapterFactory(cfg)
	require.NoError(t, err)
	defer func() {
		require.NoError(t, factory.Close())
	}()

	broadcaster := factory.GetRealtimeBroadcaster()
	require.NotNil(t, broadcaster)

	_, ok := broadcaster.(*realtime.NATSRealtimeAdapter)
	assert.True(t, ok, "expected NATS adapter")
}

// TestAdapterFactory_Close verifies proper cleanup
func TestAdapterFactory_Close(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "authkit",
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory, err := NewAdapterFactory(cfg)
	require.NoError(t, err)

	// Verify providers are initialized
	assert.NotNil(t, factory.authProvider)
	assert.NotNil(t, factory.realtimeBroadcaster)

	// Close factory
	err = factory.Close()
	require.NoError(t, err)
}

// TestAdapterFactory_SupabaseAuthRemoved verifies Supabase auth is no longer supported
func TestAdapterFactory_SupabaseAuthRemoved(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "supabase",
		AuthKitSecret:    "",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory, err := NewAdapterFactory(cfg)
	if factory != nil {
		defer func() {
			require.NoError(t, factory.Close())
		}()
	}

	require.Error(t, err)
	assert.Contains(t, err.Error(), "unknown auth provider")
}

// TestAdapterFactory_DefaultAuthProvider verifies empty auth provider defaults to authkit
func TestAdapterFactory_DefaultAuthProvider(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "", // Empty should default to authkit
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory, err := NewAdapterFactory(cfg)
	require.NoError(t, err)
	defer func() {
		require.NoError(t, factory.Close())
	}()

	provider := factory.GetAuthProvider()
	require.NotNil(t, provider)

	_, ok := provider.(*auth.KitAdapter)
	assert.True(t, ok, "expected default to be AuthKit adapter")
}

// TestAdapterFactory_ConcurrentAccess verifies thread-safe access to providers
func TestAdapterFactory_ConcurrentAccess(t *testing.T) {
	cfg := AdapterConfig{
		AuthProvider:     "authkit",
		AuthKitSecret:    "test-secret",
		WorkOSClientID:   "test-client-id",
		DBPool:           nil,
		GormDB:           testGormDB(t),
		RealtimeProvider: "nats",
		NATSConn:         &nats.Conn{},
	}

	factory, err := NewAdapterFactory(cfg)
	require.NoError(t, err)
	defer func() {
		require.NoError(t, factory.Close())
	}()

	// Access providers concurrently
	done := make(chan bool, 10)
	for i := 0; i < 10; i++ {
		go func() {
			authProvider := factory.GetAuthProvider()
			assert.NotNil(t, authProvider)

			realtimeBroadcaster := factory.GetRealtimeBroadcaster()
			assert.NotNil(t, realtimeBroadcaster)

			done <- true
		}()
	}

	// Wait for all goroutines to complete
	for i := 0; i < 10; i++ {
		<-done
	}
}

// TestAdapterFactory_ProviderTypeAssertions verifies correct provider types
func TestAdapterFactory_ProviderTypeAssertions(t *testing.T) {
	tests := []struct {
		name             string
		config           AdapterConfig
		expectedAuthType string
		expectedRTType   string
	}{
		{
			name: "AuthKit + NATS",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "test-secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
			expectedAuthType: "*auth.KitAdapter",
			expectedRTType:   "*realtime.NATSRealtimeAdapter",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			factory, err := NewAdapterFactory(tt.config)
			require.NoError(t, err)
			defer func() {
				require.NoError(t, factory.Close())
			}()

			// Verify auth provider type
			authProvider := factory.GetAuthProvider()
			require.NotNil(t, authProvider)

			// Verify realtime broadcaster type
			rtBroadcaster := factory.GetRealtimeBroadcaster()
			require.NotNil(t, rtBroadcaster)
		})
	}
}

// TestAdapterFactory_ErrorHandling verifies error handling in initialization
func TestAdapterFactory_ErrorHandling(t *testing.T) {
	tests := []struct {
		name        string
		config      AdapterConfig
		setupError  string
		expectError bool
	}{
		{
			name: "Auth init fails",
			config: AdapterConfig{
				AuthProvider:     "unknown-auth",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
			setupError:  "failed to initialize auth provider",
			expectError: true,
		},
		{
			name: "Realtime init fails",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "test-secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "unknown-realtime",
				NATSConn:         nil,
			},
			setupError:  "failed to initialize realtime broadcaster",
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			factory, err := NewAdapterFactory(tt.config)
			if factory != nil {
				defer func() {
					require.NoError(t, factory.Close())
				}()
			}

			if tt.expectError {
				require.Error(t, err)
				assert.Contains(t, err.Error(), tt.setupError)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

// TestAdapterConfig_Validation verifies AdapterConfig field validation
func TestAdapterConfig_Validation(t *testing.T) {
	for _, tc := range adapterConfigValidationCases(t) {
		t.Run(tc.name, func(t *testing.T) {
			runAdapterConfigValidationCase(t, tc)
		})
	}
}

type providerConfigValidationCase struct {
	name          string
	config        AdapterConfig
	expectError   bool
	errorContains string
}

func providerConfigValidationCases(t *testing.T) []providerConfigValidationCase {
	t.Helper()
	return []providerConfigValidationCase{
		{
			name: "Valid AuthKit and NATS config",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "valid-secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
		},
		{
			name: "Invalid auth provider",
			config: AdapterConfig{
				AuthProvider:     "invalid",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
			expectError:   true,
			errorContains: "unknown auth provider",
		},
		{
			name: "Invalid realtime provider",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "valid-secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "invalid",
				NATSConn:         nil,
			},
			expectError:   true,
			errorContains: "unknown realtime provider",
		},
		{
			name: "AuthKit missing WorkOS Client ID",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
			expectError:   true,
			errorContains: "WorkOS Client ID required",
		},
		{
			name: "NATS missing connection",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "valid-secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         nil,
			},
			expectError:   true,
			errorContains: "NATS connection required",
		},
	}
}

func runProviderConfigValidationCase(t *testing.T, tc providerConfigValidationCase) {
	t.Helper()
	factory, err := NewAdapterFactory(tc.config)
	if factory != nil {
		defer func() {
			require.NoError(t, factory.Close())
		}()
	}

	if tc.expectError {
		require.Error(t, err)
		assert.Contains(t, err.Error(), tc.errorContains)
		return
	}

	require.NoError(t, err)
	assert.NotNil(t, factory)
	assert.NotNil(t, factory.authProvider)
	assert.NotNil(t, factory.realtimeBroadcaster)
}

type adapterConfigValidationCase struct {
	name          string
	config        AdapterConfig
	expectError   bool
	errorContains string
}

func adapterConfigValidationCases(t *testing.T) []adapterConfigValidationCase {
	t.Helper()
	return []adapterConfigValidationCase{
		{
			name: "All required fields present",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
		},
		{
			name: "Missing WorkOS Client ID",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "secret",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
			expectError:   true,
			errorContains: "WorkOS Client ID required",
		},
		{
			name: "Missing GORM DB",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: "nats",
				NATSConn:         &nats.Conn{},
			},
			expectError:   true,
			errorContains: "gorm DB required",
		},
		{
			name: "Missing NATS connection",
			config: AdapterConfig{
				AuthProvider:     "authkit",
				AuthKitSecret:    "secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "nats",
				NATSConn:         nil,
			},
			expectError:   true,
			errorContains: "NATS connection",
		},
	}
}

func runAdapterConfigValidationCase(t *testing.T, tc adapterConfigValidationCase) {
	t.Helper()
	factory, err := NewAdapterFactory(tc.config)
	if factory != nil {
		defer func() {
			require.NoError(t, factory.Close())
		}()
	}

	if tc.expectError {
		require.Error(t, err)
		if tc.errorContains != "" {
			assert.Contains(t, err.Error(), tc.errorContains)
		}
		return
	}

	require.NoError(t, err)
}

// TestAdapterFactory_NilChecks verifies nil pointer handling
func TestAdapterFactory_NilChecks(t *testing.T) {
	factory := &AdapterFactory{}

	// GetAuthProvider should return nil if not initialized
	authProvider := factory.GetAuthProvider()
	assert.Nil(t, authProvider)

	// GetRealtimeBroadcaster should return nil if not initialized
	rtBroadcaster := factory.GetRealtimeBroadcaster()
	assert.Nil(t, rtBroadcaster)

	// Close should not panic with nil providers
	err := factory.Close()
	require.NoError(t, err)
}

// TestInitAuthProvider_EdgeCases verifies edge cases in auth provider init
func TestInitAuthProvider_EdgeCases(t *testing.T) {
	tests := []struct {
		name          string
		authProvider  string
		expectError   bool
		errorContains string
	}{
		{
			name:         "Empty string defaults to authkit",
			authProvider: "",
			expectError:  false,
		},
		{
			name:         "Case sensitive provider name",
			authProvider: "AuthKit", // Should be lowercase
			expectError:  true,
		},
		{
			name:          "Whitespace in provider name",
			authProvider:  " authkit ",
			expectError:   true,
			errorContains: "unknown auth provider",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cfg := AdapterConfig{
				AuthProvider:     tt.authProvider,
				AuthKitSecret:    "test-secret",
				WorkOSClientID:   "test-client-id",
				DBPool:           nil,
				GormDB:           testGormDB(t),
				RealtimeProvider: "",
				NATSConn:         nil,
			}

			factory := &AdapterFactory{config: cfg}
			err := factory.initAuthProvider()

			if tt.expectError {
				require.Error(t, err)
				if tt.errorContains != "" {
					assert.Contains(t, err.Error(), tt.errorContains)
				}
			} else {
				require.NoError(t, err)
			}
		})
	}
}

// TestInitRealtimeBroadcaster_EdgeCases verifies edge cases in realtime init
func TestInitRealtimeBroadcaster_EdgeCases(t *testing.T) {
	tests := []struct {
		name             string
		realtimeProvider string
		expectError      bool
		errorContains    string
	}{
		{
			name:             "Valid NATS",
			realtimeProvider: "nats",
			expectError:      false,
		},
		{
			name:             "Empty provider (required)",
			realtimeProvider: "",
			expectError:      true,
			errorContains:    "realtime provider is required",
		},
		{
			name:             "Invalid provider",
			realtimeProvider: "invalid",
			expectError:      true,
			errorContains:    "unknown realtime provider",
		},
		{
			name:             "Case sensitive provider",
			realtimeProvider: "NATS",
			expectError:      true,
			errorContains:    "unknown realtime provider",
		},
		{
			name:             "Whitespace in provider",
			realtimeProvider: " nats ",
			expectError:      true,
			errorContains:    "unknown realtime provider",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cfg := AdapterConfig{
				AuthProvider:     "",
				AuthKitSecret:    "",
				WorkOSClientID:   "",
				DBPool:           nil,
				GormDB:           nil,
				RealtimeProvider: tt.realtimeProvider,
				NATSConn:         &nats.Conn{},
			}

			factory := &AdapterFactory{config: cfg}
			err := factory.initRealtimeBroadcaster()

			if tt.expectError {
				require.Error(t, err)
				if tt.errorContains != "" {
					assert.Contains(t, strings.ToLower(err.Error()), strings.ToLower(tt.errorContains))
				}
			} else {
				require.NoError(t, err)
			}
		})
	}
}
