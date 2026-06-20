package features

import (
	"context"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func setupTestRedis(t *testing.T) (*FlagStore, *miniredis.Miniredis) {
	mr := miniredis.RunT(t)

	client := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})

	return NewFlagStore(client), mr
}

func TestIsEnabled(t *testing.T) {
	fs, _ := setupTestRedis(t)
	ctx := context.Background()

	// Test non-existent flag (should default to false)
	assert.False(t, fs.IsEnabled(ctx, "nonexistent"))

	// Test enabled flag
	err := fs.EnableFlag(ctx, "test_flag")
	require.NoError(t, err)
	assert.True(t, fs.IsEnabled(ctx, "test_flag"))

	// Test disabled flag
	err = fs.DisableFlag(ctx, "test_flag")
	require.NoError(t, err)
	assert.False(t, fs.IsEnabled(ctx, "test_flag"))
}

func TestSetFlag(t *testing.T) {
	fs, _ := setupTestRedis(t)
	ctx := context.Background()

	err := fs.SetFlag(ctx, "test_flag", true)
	require.NoError(t, err)
	assert.True(t, fs.IsEnabled(ctx, "test_flag"))

	err = fs.SetFlag(ctx, "test_flag", false)
	require.NoError(t, err)
	assert.False(t, fs.IsEnabled(ctx, "test_flag"))
}

func TestGetFlag(t *testing.T) {
	fs, _ := setupTestRedis(t)
	ctx := context.Background()

	// Test non-existent flag
	value, exists, err := fs.GetFlag(ctx, "nonexistent")
	require.NoError(t, err)
	assert.False(t, exists)
	assert.False(t, value)

	// Test existing flag
	err = fs.EnableFlag(ctx, "test_flag")
	require.NoError(t, err)

	value, exists, err = fs.GetFlag(ctx, "test_flag")
	require.NoError(t, err)
	assert.True(t, exists)
	assert.True(t, value)
}

func TestDeleteFlag(t *testing.T) {
	fs, _ := setupTestRedis(t)
	ctx := context.Background()

	// Create and delete flag
	err := fs.EnableFlag(ctx, "test_flag")
	require.NoError(t, err)

	err = fs.DeleteFlag(ctx, "test_flag")
	require.NoError(t, err)

	_, exists, err := fs.GetFlag(ctx, "test_flag")
	require.NoError(t, err)
	assert.False(t, exists)
}

func TestListFlags(t *testing.T) {
	fs, _ := setupTestRedis(t)
	ctx := context.Background()

	// Create multiple flags
	err := fs.EnableFlag(ctx, "flag1")
	require.NoError(t, err)
	err = fs.DisableFlag(ctx, "flag2")
	require.NoError(t, err)
	err = fs.EnableFlag(ctx, "flag3")
	require.NoError(t, err)

	flags, err := fs.ListFlags(ctx)
	require.NoError(t, err)
	assert.Len(t, flags, 3)
	assert.True(t, flags["flag1"])
	assert.False(t, flags["flag2"])
	assert.True(t, flags["flag3"])
}

func TestSetFlagWithTTL(t *testing.T) {
	fs, mr := setupTestRedis(t)
	ctx := context.Background()

	// Set flag with TTL
	err := fs.SetFlagWithTTL(ctx, "temp_flag", true, 1*time.Second)
	require.NoError(t, err)
	assert.True(t, fs.IsEnabled(ctx, "temp_flag"))

	// Fast forward time
	mr.FastForward(2 * time.Second)

	// Flag should be expired
	assert.False(t, fs.IsEnabled(ctx, "temp_flag"))
}

func TestInitializeDefaultFlags(t *testing.T) {
	fs, _ := setupTestRedis(t)
	ctx := context.Background()

	// Initialize defaults
	err := fs.InitializeDefaultFlags(ctx)
	require.NoError(t, err)

	// Check that default flags are set
	assert.True(t, fs.IsEnabled(ctx, FlagNATSEvents))
	assert.True(t, fs.IsEnabled(ctx, FlagCrossBackendCalls))
	assert.True(t, fs.IsEnabled(ctx, FlagSharedCache))
	assert.True(t, fs.IsEnabled(ctx, FlagPythonSpecAnalytics))
	assert.True(t, fs.IsEnabled(ctx, FlagGoGraphAnalysis))

	// Manually set a flag
	err = fs.DisableFlag(ctx, FlagNATSEvents)
	require.NoError(t, err)

	// Re-initialize (should not override existing)
	err = fs.InitializeDefaultFlags(ctx)
	require.NoError(t, err)

	// Manual setting should be preserved
	assert.False(t, fs.IsEnabled(ctx, FlagNATSEvents))
}
