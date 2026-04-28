package database

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestDefaultOptimizationConfig(t *testing.T) {
	t.Run("returns valid configuration", func(t *testing.T) {
		config := DefaultOptimizationConfig()
		assert.NotNil(t, config)
		assert.Equal(t, int32(25), config.MaxConnections)
		assert.Equal(t, int32(5), config.MinConnections)
		assert.Equal(t, 1*time.Hour, config.MaxConnLifetime)
		assert.Equal(t, 30*time.Minute, config.MaxConnIdleTime)
		assert.Equal(t, 1*time.Minute, config.HealthCheckPeriod)
		assert.Equal(t, 30*time.Second, config.StatementTimeout)
		assert.Equal(t, 5*time.Minute, config.IdleInTxTimeout)
		assert.True(t, config.PreparedStatements)
	})

	t.Run("multiple calls return consistent config", func(t *testing.T) {
		config1 := DefaultOptimizationConfig()
		config2 := DefaultOptimizationConfig()

		assert.Equal(t, config1.MaxConnections, config2.MaxConnections)
		assert.Equal(t, config1.MinConnections, config2.MinConnections)
		assert.Equal(t, config1.MaxConnLifetime, config2.MaxConnLifetime)
	})

	t.Run("config fields are properly initialized", func(t *testing.T) {
		config := DefaultOptimizationConfig()

		assert.Greater(t, config.MaxConnections, config.MinConnections)
		assert.Greater(t, config.MaxConnLifetime, time.Minute)
		assert.Greater(t, config.HealthCheckPeriod, time.Second)
		assert.Greater(t, config.StatementTimeout, time.Millisecond)
	})
}

func TestOptimizationConfigValues(t *testing.T) {
	t.Run("config has sensible defaults", func(t *testing.T) {
		config := DefaultOptimizationConfig()

		// Verify reasonable values
		assert.Equal(t, int32(25), config.MaxConnections)
		assert.Equal(t, int32(5), config.MinConnections)
		assert.True(t, config.PreparedStatements)
	})

	t.Run("all timeout values are positive", func(t *testing.T) {
		config := DefaultOptimizationConfig()

		assert.Greater(t, config.StatementTimeout, time.Duration(0))
		assert.Greater(t, config.IdleInTxTimeout, time.Duration(0))
		assert.Greater(t, config.MaxConnLifetime, time.Duration(0))
		assert.Greater(t, config.MaxConnIdleTime, time.Duration(0))
		assert.Greater(t, config.HealthCheckPeriod, time.Duration(0))
	})

	t.Run("config can be modified", func(t *testing.T) {
		config := DefaultOptimizationConfig()
		config.MaxConnections = 50

		assert.Equal(t, int32(50), config.MaxConnections)
	})

	t.Run("different config instances are independent", func(t *testing.T) {
		config1 := DefaultOptimizationConfig()
		config2 := DefaultOptimizationConfig()

		config1.MaxConnections = 100
		assert.Equal(t, int32(100), config1.MaxConnections)
		assert.Equal(t, int32(25), config2.MaxConnections)
	})
}

func TestSlowQueryStructure(t *testing.T) {
	t.Run("SlowQuery fields are properly defined", func(t *testing.T) {
		sq := SlowQuery{
			Query:          "SELECT * FROM items",
			Calls:          int64(100),
			TotalExecTime:  5000.0,
			MeanExecTime:   50.0,
			MaxExecTime:    200.0,
			StddevExecTime: 25.0,
		}

		assert.Equal(t, "SELECT * FROM items", sq.Query)
		assert.Equal(t, int64(100), sq.Calls)
		assert.InEpsilon(t, 50.0, sq.MeanExecTime, 1e-9)
		assert.Greater(t, sq.MaxExecTime, sq.MeanExecTime)
	})
}

func TestTableStatsStructure(t *testing.T) {
	t.Run("TableStats fields are properly defined", func(t *testing.T) {
		stats := TableStats{
			SchemaName:      "public",
			TableName:       "items",
			Size:            "100MB",
			Inserts:         int64(1000),
			Updates:         int64(500),
			Deletes:         int64(100),
			LiveTuples:      int64(1400),
			DeadTuples:      int64(50),
			LastVacuum:      nil,
			LastAutovacuum:  nil,
			LastAnalyze:     nil,
			LastAutoanalyze: nil,
		}

		assert.Equal(t, "items", stats.TableName)
		assert.Equal(t, int64(1400), stats.LiveTuples)
		assert.Nil(t, stats.LastVacuum)
	})

	t.Run("TableStats with populated timestamps", func(t *testing.T) {
		now := time.Now()
		stats := TableStats{
			SchemaName:      "public",
			TableName:       "items",
			Size:            "100MB",
			Inserts:         int64(1000),
			Updates:         int64(500),
			Deletes:         int64(100),
			LiveTuples:      int64(1400),
			DeadTuples:      int64(50),
			LastVacuum:      &now,
			LastAutovacuum:  &now,
			LastAnalyze:     &now,
			LastAutoanalyze: &now,
		}

		assert.NotNil(t, stats.LastVacuum)
		assert.Equal(t, now, *stats.LastVacuum)
	})
}

// Benchmark tests for configuration creation
func BenchmarkDefaultOptimizationConfig(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_ = DefaultOptimizationConfig()
	}
}
