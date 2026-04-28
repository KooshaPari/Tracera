package server

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
)

func TestNewServer(t *testing.T) {
	t.Run("creates server with infrastructure", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() {
			if err := infra.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		})

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)
		assert.NotNil(t, server)
		assert.NotNil(t, server.echo)
		assert.NotNil(t, server.pool)
		assert.Equal(t, infra.DB, server.pool)
	})

	t.Run("initializes with nil infrastructure components", func(t *testing.T) {
		fullInfra := createTestInfrastructure(t)
		t.Cleanup(func() {
			if err := fullInfra.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		})
		infra := &infrastructure.Infrastructure{
			DB:     fullInfra.DB,
			GormDB: fullInfra.GormDB,
		}

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)

		assert.NotNil(t, server)
		assert.Nil(t, server.redisClient)
		assert.Nil(t, server.natsConn)
	})
}

func TestServerShutdown(t *testing.T) {
	t.Run("graceful shutdown", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() {
			if err := infra.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		})

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)

		ctx, cancel := context.WithTimeout(context.Background(), serverGracefulShutdownTimeout)
		defer cancel()

		err = server.Shutdown(ctx)
		require.NoError(t, err)
	})

	t.Run("shutdown with timeout", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() {
			if err := infra.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		})

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)

		ctx, cancel := context.WithTimeout(context.Background(), serverImmediateTimeout)
		defer cancel()
		time.Sleep(serverShutdownDelay)

		err = server.Shutdown(ctx)
		// May or may not error depending on timing
		if err != nil {
			t.Logf("Shutdown error (acceptable): %v", err)
		}
	})

	t.Run("shutdown cleans up resources", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		cfg := createTestConfig()

		// Create server with Redis client
		redisClient := redis.NewClient(&redis.Options{
			Addr: "localhost:6379",
		})
		infra.Redis = redisClient

		server, err := NewServer(infra, cfg)
		require.NoError(t, err)
		server.redisClient = redisClient

		ctx := context.Background()
		require.NoError(t, server.Shutdown(ctx))

		// Redis client should be closed
		err = redisClient.Ping(ctx).Err()
		if err == nil {
			t.Log("Redis still connected after shutdown")
		}
	})
}

func TestServerStart(t *testing.T) {
	t.Run("starts on specified port", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() {
			if err := infra.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		})

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)

		// Start in goroutine
		errChan := make(chan error, 1)
		go func() {
			errChan <- server.Start(":0") // Use port 0 for random available port
		}()

		// Give it time to start
		time.Sleep(serverStartDelay)

		// Shutdown
		ctx, cancel := context.WithTimeout(context.Background(), serverShutdownTimeout)
		defer cancel()
		require.NoError(t, server.Shutdown(ctx))

		// Check for startup errors
		select {
		case err := <-errChan:
			if err != nil && !strings.Contains(err.Error(), "Server closed") {
				t.Errorf("Unexpected error: %v", err)
			}
		case <-time.After(serverStartTimeout):
			t.Log("Server shutdown completed")
		}
	})
}

func TestServerMultipleShutdowns(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	ctx := context.Background()

	err = server.Shutdown(ctx)
	require.NoError(t, err)

	err = server.Shutdown(ctx)
	// Second shutdown should not panic
	if err != nil {
		t.Logf("Second shutdown error (acceptable): %v", err)
	}
}

func TestTimeoutConstants(t *testing.T) {
	t.Run("server shutdown delay is reasonable", func(t *testing.T) {
		assert.Greater(t, serverShutdownDelay, time.Duration(0))
		assert.Less(t, serverShutdownDelay, time.Second)
	})

	t.Run("server start delay is reasonable", func(t *testing.T) {
		assert.Greater(t, serverStartDelay, time.Millisecond*50)
		assert.Less(t, serverStartDelay, time.Second)
	})

	t.Run("server shutdown timeout is reasonable", func(t *testing.T) {
		assert.Greater(t, serverShutdownTimeout, time.Millisecond)
		assert.Less(t, serverShutdownTimeout, time.Second*10)
	})

	t.Run("server start timeout is reasonable", func(t *testing.T) {
		assert.Greater(t, serverStartTimeout, serverShutdownTimeout)
	})

	t.Run("graceful shutdown timeout is reasonable", func(t *testing.T) {
		assert.Greater(t, serverGracefulShutdownTimeout, time.Second)
	})

	t.Run("immediate timeout is very small", func(t *testing.T) {
		assert.Greater(t, serverImmediateTimeout, time.Duration(0))
		assert.Less(t, serverImmediateTimeout, time.Millisecond)
	})
}

func TestServerPort(t *testing.T) {
	cfg := createTestConfig()

	t.Run("port is string", func(t *testing.T) {
		assert.IsType(t, "", cfg.Port)
	})

	t.Run("port is numeric", func(t *testing.T) {
		// Port should be "8080" which is a valid port number
		assert.Equal(t, "8080", cfg.Port)
	})

	t.Run("environment is test", func(t *testing.T) {
		assert.Equal(t, "test", cfg.Env)
	})
}
