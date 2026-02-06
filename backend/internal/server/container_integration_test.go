package server

import (
	"context"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestServiceContainerIntegration_Required verifies that ServiceContainer is required.
func TestServiceContainerIntegration_Required(t *testing.T) {
	t.Run("NewServer returns error when GormDB is nil", func(t *testing.T) {
		infra := &infrastructure.Infrastructure{
			DB:     nil,
			GormDB: nil,
		}
		cfg := &config.Config{}
		srv, err := NewServer(infra, cfg)
		assert.Error(t, err)
		assert.Nil(t, srv)
		assert.Contains(t, err.Error(), "GormDB is nil")
	})

	t.Run("NewServer succeeds when infra has GormDB", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() { _ = infra.Close(context.Background()) })
		cfg := createTestConfig()
		srv, err := NewServer(infra, cfg)
		require.NoError(t, err)
		assert.NotNil(t, srv)
		assert.NotNil(t, srv.serviceContainer)
	})
}

// TestServerStructHasServiceContainer verifies that Server struct has serviceContainer field
func TestServerStructHasServiceContainer(t *testing.T) {
	// Create a Server instance with nil fields (just for structure verification)
	s := &Server{
		serviceContainer: nil,
	}

	// Verify the field exists and can be accessed
	assert.Nil(t, s.serviceContainer, "serviceContainer field should exist and be accessible")

	// Verify we can set it (simulating what happens in NewServer)
	// This would be set to a real *services.ServiceContainer in production
	s.serviceContainer = nil          // In production: services.NewServiceContainer(...)
	assert.Nil(t, s.serviceContainer) // Would be non-nil in production with real container
}
