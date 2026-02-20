package server

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
)

func TestServerWithFullInfrastructure(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	t.Run("server with all services", func(t *testing.T) {
		ctx := context.Background()
		cfg := createTestConfig()

		infra, err := infrastructure.InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Failed to initialize infrastructure: %v", err)
		}
		t.Cleanup(func() { require.NoError(t, infra.Close(ctx)) })

		server, err := NewServer(infra, cfg)
		require.NoError(t, err)
		assert.NotNil(t, server)

		assert.NotNil(t, server.pool)
		assert.NotNil(t, server.searchEngine)
		assert.NotNil(t, server.searchIndexer)
	})
}
